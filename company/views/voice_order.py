import difflib
import os
import re
import tempfile
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from decimal import Decimal
import whisper
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional
from company.models import Company, Product

# --- Whisper (speech-to-text): lazy-loaded so server starts fast ---
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = whisper.load_model("tiny")
    return _whisper_model

# --- OpenAI: used to parse transcript into company + product codes + quantities ---
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# --- Shape of parsed voice order (company + items by product code, optional notes) ---
class OrderItem(BaseModel):
    product_code: str  # e.g. "100", "205"
    quantity: float

class DraftOrder(BaseModel):
    company_name: str
    items: List[OrderItem]
    notes: Optional[str] = None

# --- Company name matching: turn "two" -> "2" so "company two" matches "Company 2" ---
_NUMBER_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12",
}

def _normalize_for_fuzzy(s: str) -> str:
    """Lowercase + replace number words with digits for matching."""
    if not s:
        return ""
    s = s.lower().strip()
    for word, digit in _NUMBER_WORDS.items():
        s = re.subn(rf"\b{re.escape(word)}\b", digit, s, flags=re.IGNORECASE)[0]
    return s

def _fuzzy_best_match(spoken: str, candidates: list, *, key: str = "name", cutoff: float = 0.55):
    """Best match from candidates by string similarity (e.g. 'unifar' -> 'Uniphar')."""
    if not spoken or not candidates:
        return None, 0.0
    norm_spoken = _normalize_for_fuzzy(spoken)
    best_match, best_ratio = None, 0.0
    for c in candidates:
        name = getattr(c, key, str(c))
        ratio = difflib.SequenceMatcher(None, norm_spoken, _normalize_for_fuzzy(name)).ratio()
        if ratio > best_ratio:
            best_ratio, best_match = ratio, c
    return (best_match, best_ratio) if best_ratio >= cutoff else (None, best_ratio)

def _resolve_company_by_name(user_id: int, company_name: str):
    """Resolve spoken company name: exact -> contains -> fuzzy. Returns (company, error_msg)."""
    if not (company_name and company_name.strip()):
        return None, None
    name = company_name.strip()
    user_companies = list(Company.objects.filter(user_id=user_id))
    if not user_companies:
        return None, "You have no companies."
    company = next((c for c in user_companies if c.name.lower() == name.lower()), None)
    if company:
        return company, None
    company = next((c for c in user_companies if name.lower() in c.name.lower()), None)
    if company:
        return company, None
    company, ratio = _fuzzy_best_match(name, user_companies, key="name", cutoff=0.55)
    if company:
        return company, None
    return None, f"Company '{company_name}' not found. Your companies: {', '.join(c.name for c in user_companies[:5])}."


@login_required(login_url="/")
def create_voice_order(request):
    """Create draft order from voice: company + product codes and quantities (e.g. 'For company X, order 1 of product code 100')."""
    # Validate: POST with audio file
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    if not request.FILES.get('audio_order'):
        return JsonResponse({'error': 'No audio file provided'}, status=400)

    try:
        # Save uploaded audio to temp file, transcribe with Whisper, then delete temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp_file:
            for chunk in request.FILES['audio_order'].chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name
        try:
            raw_text = get_whisper_model().transcribe(tmp_path)['text']
        finally:
            os.unlink(tmp_path)

        if not raw_text.strip():
            return JsonResponse({'error': 'No speech detected in audio'}, status=400)
        if not client:
            return JsonResponse({'error': 'OpenAI API key not configured', 'transcript': raw_text}, status=500)

        # Parse transcript into structured order (company_name, items with product_code + quantity, notes)
        try:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """Extract from this voice order transcript:
1) REQUIRED company_name: the company the user is ordering for (e.g. "for company X", "company X").
2) items: list of product_code and quantity. User says product by CODE (e.g. "order 1 of product code 100", "product code 205 quantity 3"). product_code is always a number (digits). quantity is a number. If quantity not said, use 1.
3) notes: optional delivery/urgency/other instructions. Otherwise leave empty.
Return JSON: company_name (required), items (list of {product_code: string of digits, quantity: number}), notes (optional)."""
                    },
                    {"role": "user", "content": raw_text},
                ],
                response_format=DraftOrder,
            )
            structured_order = completion.choices[0].message.parsed
        except Exception as e:
            return JsonResponse({'error': f'Failed to parse order: {str(e)}', 'transcript': raw_text}, status=400)

        # Resolve company by name (exact / contains / fuzzy); require success
        company, err = _resolve_company_by_name(request.user.id, structured_order.company_name)
        if err:
            return JsonResponse({'error': err, 'transcript': raw_text}, status=400)
        if not company:
            msg = 'Company name is required (e.g. "For company Acme, order 1 of product code 100").' if not (structured_order.company_name or "").strip() else f'Company "{structured_order.company_name}" not found.'
            return JsonResponse({'error': msg, 'transcript': raw_text}, status=400)

        # Look up each product by company + product_code; supplier comes from product
        draft_items = []
        products_not_found = []
        for order_item in structured_order.items:
            code_str = (order_item.product_code or "").strip().replace(" ", "")
            if not code_str or not code_str.isdigit():
                products_not_found.append(order_item.product_code or "?")
                continue
            try:
                product = Product.objects.filter(company=company, product_code=int(code_str)).select_related('product_measurement').first()
            except ValueError:
                product = None
            if not product:
                products_not_found.append(code_str)
                continue
            quantity = float(order_item.quantity)
            price = product.product_price_with_vat
            total = Decimal(str(price)) * Decimal(str(quantity))
            draft_items.append({
                'company_id': company.id,
                'supplier_id': product.supplier_id,
                'product_id': product.id,
                'quantity': str(quantity),
                'product_measurement_id': product.product_measurement.id,
                'price': str(price),
                'total': str(total),
            })

        if not draft_items:
            return JsonResponse({
                'error': 'No valid products found in order',
                'transcript': raw_text,
                'products_not_found': products_not_found,
            }, status=400)

        # Append to session draft; merge voice notes if any
        if 'draft_order_items' not in request.session:
            request.session['draft_order_items'] = []
        request.session['draft_order_items'].extend(draft_items)
        if structured_order.notes and structured_order.notes.strip():
            existing = (request.session.get('draft_order_notes') or '').strip()
            new_note = structured_order.notes.strip()
            request.session['draft_order_notes'] = f"{existing}\n{new_note}".strip() if existing else new_note
        request.session.modified = True

        # Build success JSON (items added, optional warning for product codes not found)
        response_data = {
            'success': True,
            'items_added': len(draft_items),
            'transcript': raw_text,
            'company_id': company.id,
            'items': [{'product_name': Product.objects.get(id=it['product_id']).product_name, 'quantity': it['quantity']} for it in draft_items],
        }
        if products_not_found:
            response_data['products_not_found'] = products_not_found
            response_data['warning'] = f"Could not find product code(s): {', '.join(products_not_found)}"
        if structured_order.notes:
            response_data['notes'] = structured_order.notes
        return JsonResponse(response_data)

    except Exception as e:
        # Catch-all for e.g. disk/network/Whisper errors
        return JsonResponse({'error': f'Error processing voice order: {str(e)}', 'type': type(e).__name__}, status=500)
