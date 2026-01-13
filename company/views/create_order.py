from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal
from company.forms.draft_order import DraftOrderItemForm, CreateOrderForm
from company.models.order import Order, OrderItem
from company.models import Company, Supplier, Product, ProductMeasurement

@login_required(login_url="/")
def add_draft_order_item(request):
    """Add items to a draft order (stored in session)"""
    companies = Company.objects.filter(user_id=request.user.id)
    
    if not companies.exists():
        messages.error(request, 'You do not have any company profiles.')
        return redirect('dashboard')
    
    # Initialize session draft items if not exists
    if 'draft_order_items' not in request.session:
        request.session['draft_order_items'] = []
    
    if request.method == "POST":
        form = DraftOrderItemForm(request.POST, user=request.user)
        if form.is_valid():
            item_data = {
                'company_id': form.cleaned_data['company_id'].id,
                'supplier_id': form.cleaned_data['supplier_id'].id,
                'product_id': form.cleaned_data['product_id'].id,
                'quantity': str(form.cleaned_data['quantity']),
                'product_measurement_id': form.cleaned_data['product_measurement_id'].id,
                'price': str(form.cleaned_data['price']),
                'total': str(form.cleaned_data.get('total', 0))
            }
            request.session['draft_order_items'].append(item_data)
            request.session.modified = True
            messages.success(request, 'Item added to draft order!')
            return redirect('company:view_draft_order_items')
    else:
        form = DraftOrderItemForm(user=request.user)
    
    context = {'form': form}
    return render(request, "order/add_draft_order_item.html", context=context)

@login_required(login_url="/")
def view_draft_order_items(request):
    """View all draft order items"""
    draft_items = request.session.get('draft_order_items', [])
    
    if not draft_items:
        messages.info(request, 'No items in draft order. Add some items first.')
        return redirect('company:add_draft_order_item')
    
    # Get full details for each item
    items_with_details = []
    total_amount = Decimal('0')
    companies_set = set()
    suppliers_set = set()
    
    for item in draft_items:
        try:
            product = Product.objects.get(id=item['product_id'])
            supplier = Supplier.objects.get(id=item['supplier_id'])
            measurement = ProductMeasurement.objects.get(id=item['product_measurement_id'])
            company = Company.objects.get(id=item['company_id'])
            
            companies_set.add(company.id)
            suppliers_set.add(supplier.id)
            
            item_total = Decimal(item['total'])
            total_amount += item_total
            
            items_with_details.append({
                'product': product,
                'supplier': supplier,
                'measurement': measurement,
                'company': company,
                'quantity': item['quantity'],
                'price': item['price'],
                'total': item_total,
                'index': len(items_with_details)
            })
        except (Product.DoesNotExist, Supplier.DoesNotExist, ProductMeasurement.DoesNotExist, Company.DoesNotExist):
            continue
    
    # Check if all items have same company and supplier
    has_multiple_companies = len(companies_set) > 1
    has_multiple_suppliers = len(suppliers_set) > 1
    
    if request.method == "POST":
        if 'create_order' in request.POST:
            form = CreateOrderForm(request.POST)
            if form.is_valid():
                return create_order_from_draft(request, form.cleaned_data.get('order_notes', ''))
        elif 'remove_item' in request.POST:
            index = int(request.POST.get('remove_item'))
            if 0 <= index < len(request.session['draft_order_items']):
                request.session['draft_order_items'].pop(index)
                request.session.modified = True
                messages.success(request, 'Item removed from draft order.')
                return redirect('company:view_draft_order_items')
        elif 'clear_draft' in request.POST:
            request.session['draft_order_items'] = []
            request.session.modified = True
            messages.success(request, 'Draft order cleared.')
            return redirect('company:add_draft_order_item')
    else:
        form = CreateOrderForm()
    
    context = {
        'items': items_with_details,
        'total_amount': total_amount,
        'form': form,
        'has_multiple_companies': has_multiple_companies,
        'has_multiple_suppliers': has_multiple_suppliers
    }
    return render(request, "order/view_draft_order_items.html", context=context)

@login_required(login_url="/")
def create_order_from_draft(request, order_notes=''):
    """Create order from draft items"""
    draft_items = request.session.get('draft_order_items', [])
    
    if not draft_items:
        messages.error(request, 'No items in draft order.')
        return redirect('company:add_draft_order_item')
    
    try:
        # Validate all items have same company and supplier
        first_item = draft_items[0]
        company_id = first_item['company_id']
        supplier_id = first_item['supplier_id']
        
        for item in draft_items:
            if item['company_id'] != company_id:
                messages.error(request, 'All items must belong to the same company.')
                return redirect('company:view_draft_order_items')
            if item['supplier_id'] != supplier_id:
                messages.error(request, 'All items must belong to the same supplier.')
                return redirect('company:view_draft_order_items')
        
        with transaction.atomic():
            company = Company.objects.get(id=company_id)
            supplier = Supplier.objects.get(id=supplier_id)
            
            # Calculate total
            total_amount = sum(Decimal(item['total']) for item in draft_items)
            
            # Create order
            order = Order.objects.create(
                order_id=company,
                supplier_id=supplier,
                order_total=total_amount,
                order_notes=order_notes,
                order_created_by=request.user
            )
            
            # Create order items
            for item in draft_items:
                OrderItem.objects.create(
                    order=order,
                    product_id=Product.objects.get(id=item['product_id']),
                    supplier_id=Supplier.objects.get(id=item['supplier_id']),
                    product_measurement_id=ProductMeasurement.objects.get(id=item['product_measurement_id']),
                    quantity=item['quantity'],
                    price=item['price'],
                    total=item['total'],
                    user=request.user
                )
            
            # Clear draft items
            request.session['draft_order_items'] = []
            request.session.modified = True
            
            messages.success(request, f'Order #{order.order_number} created successfully with {len(draft_items)} item(s)!')
            return redirect('company:order_list')
    except Exception as e:
        messages.error(request, f'Error creating order: {str(e)}')
        return redirect('company:view_draft_order_items')

@login_required(login_url="/")
def order_list(request):
    """Display list of orders for the current user's companies"""
    companies = Company.objects.filter(user_id=request.user.id)
    
    if not companies.exists():
        messages.error(request, 'You do not have any company profiles.')
        return redirect('dashboard')
    
    # Get all orders for the user's companies
    orders = Order.objects.filter(order_id__in=companies)
    
    context = {'orders': orders}
    return render(request, "order/order_list.html", context=context)

@login_required(login_url="/")
def order_detail(request, order_id):
    """Display order details with all order items"""
    companies = Company.objects.filter(user_id=request.user.id)
    
    if not companies.exists():
        messages.error(request, 'You do not have any company profiles.')
        return redirect('dashboard')
    
    # Get the order and validate it belongs to user's companies
    order = get_object_or_404(Order, id=order_id, order_id__in=companies)
    
    # Get all order items for this order
    order_items = order.order_items.all().select_related('product_id', 'supplier_id', 'product_measurement_id')
    
    context = {
        'order': order,
        'order_items': order_items
    }
    return render(request, "order/order_detail.html", context=context)

@login_required(login_url="/")
def delete_order(request):
    """Delete an order"""
    companies = Company.objects.filter(user_id=request.user.id)
    
    if not companies.exists():
        messages.error(request, 'You do not have any company profiles.')
        return redirect('dashboard')
    
    # Get the order_id from POST
    order_id = request.POST.get('order_id')
    
    if not order_id:
        messages.error(request, 'No order selected for deletion.')
        return redirect('company:order_list')
    
    try:
        order = Order.objects.filter(order_id__in=companies, id=order_id).first()
        if not order:
            messages.error(request, 'Selected order does not exist or you do not have permission to delete it.')
            return redirect('company:order_list')
        
        order_number = order.order_number
        order.delete()  # This will cascade delete all order items
        messages.success(request, f'Order #{order_number} successfully deleted!')
    except Exception as e:
        messages.error(request, f'Error deleting order: {str(e)}')
    
    return redirect('company:order_list')

@login_required(login_url="/")
def get_company_options_for_draft(request):
    """AJAX endpoint to get filtered options for a selected company (for draft orders)"""
    company_id = request.GET.get('company_id')
    
    if not company_id:
        return JsonResponse({
            'suppliers': [],
            'products': [],
            'product_measurements': []
        })
    
    try:
        company = Company.objects.filter(user_id=request.user.id, id=company_id).first()
        if not company:
            return JsonResponse({'error': 'Company not found'}, status=404)
        
        return JsonResponse({
            'suppliers': [{'id': s.id, 'name': s.name} for s in Supplier.objects.filter(company_id=company)],
            'product_measurements': [{'id': m.id, 'type_of_measurement': m.type_of_measurement} for m in ProductMeasurement.objects.filter(company_id=company)]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required(login_url="/")
def get_supplier_products(request):
    """AJAX endpoint to get products for a selected supplier and company"""
    supplier_id = request.GET.get('supplier_id')
    company_id = request.GET.get('company_id')
    
    if not supplier_id or not company_id:
        return JsonResponse({'products': []})
    
    try:
        # Validate company belongs to user
        company = Company.objects.filter(user_id=request.user.id, id=company_id).first()
        if not company:
            return JsonResponse({'error': 'Company not found'}, status=404)
        
        # Validate supplier belongs to the company
        supplier = Supplier.objects.filter(company_id=company, id=supplier_id).first()
        if not supplier:
            return JsonResponse({'error': 'Supplier not found or does not belong to the selected company'}, status=404)
        
        # Filter products by both supplier AND company to handle duplicate names across companies
        products = Product.objects.filter(supplier=supplier, company=company)
        return JsonResponse({
            'products': [{
                'id': p.id, 
                'product_name': p.product_name,
                'price_without_vat': str(p.product_price_without_vat),
                'price_with_vat': str(p.product_price_with_vat),
                'measurement_id': p.product_measurement.id,
                'measurement_name': p.product_measurement.type_of_measurement
            } for p in products]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

