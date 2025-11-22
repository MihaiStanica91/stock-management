from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Company, ProductMeasurement
from ..forms import TypeOfMeasurementForm


@login_required(login_url="/")
def measurement_register(request):
    form = TypeOfMeasurementForm(user=request.user)

    if request.method == "POST":
        form = TypeOfMeasurementForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Measurement has been registered successfully!')
            return redirect('company:measurement_list')
    
    context = {'type_of_measurement_form':form}
    return render(request, "product/measurement_register.html", context=context)

@login_required(login_url="/")
def measurement_list(request):
    # Get all companies for the current user
    companies = Company.objects.filter(user_id=request.user.id)
    
    if not companies.exists():
        messages.error(request, 'You do not have any company profiles.')
        return redirect('dashboard')
    
    # Get all measurements for the user's companies
    measurements = ProductMeasurement.objects.filter(company_id__in=companies)
    
    context = {'measurements': measurements}
    return render(request, "product/measurement_list.html", context=context)

@login_required(login_url="/")
def delete_measurement(request):
    # Get all measurements for the current user's companies
    measurements = ProductMeasurement.objects.filter(company_id__user_id=request.user.id)
    
    if not measurements.exists():
        messages.error(request, 'You do not have any measurements.')
        return redirect('dashboard')

    # Get the measurement_id from POST
    measurement_id = request.POST.get('measurement_id')
    
    if not measurement_id:
        messages.error(request, 'No measurement selected for deletion.')
        return redirect('company:measurement_list')
    
    try:
        measurement = measurements.get(id=measurement_id)
        measurement.delete()
        messages.success(request, 'Measurement successfully deleted!')
    except ProductMeasurement.DoesNotExist:
        messages.error(request, 'Selected measurement does not exist.')
    
    return redirect('company:measurement_list')

@login_required(login_url="/")
def delete_measurement_confirm(request):
    # Get all measurements for the current user's companies
    measurements = ProductMeasurement.objects.filter(company_id__user_id=request.user.id)
    
    if not measurements.exists():
        messages.error(request, 'You do not have any measurements.')
        return redirect('dashboard')

    # Get the measurement_id from GET
    measurement_id = request.GET.get('measurement_id')
    
    if not measurement_id:
        messages.error(request, 'No measurement selected for deletion.')
        return redirect('company:measurement_list')
    
    try:
        measurement = measurements.get(id=measurement_id)
        return render(request, 'product/delete_measurement_confirm.html', {
            'measurement': measurement
        })
    except ProductMeasurement.DoesNotExist:
        messages.error(request, 'Selected measurement does not exist.')
        return redirect('company:measurement_list')

