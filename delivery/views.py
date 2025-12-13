from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DeliveryAddress, DeliveryZone
from .forms import DeliveryAddressForm


@login_required
def address_list(request):
    """List all delivery addresses for user"""
    addresses = DeliveryAddress.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    
    context = {
        'addresses': addresses,
    }
    return render(request, 'delivery/address_list.html', context)


@login_required
def address_create(request):
    """Create new delivery address"""
    if request.method == 'POST':
        form = DeliveryAddressForm(request.POST, user=request.user)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, f'Delivery address "{address.label}" added successfully!')
            return redirect('delivery:address_list')
    else:
        form = DeliveryAddressForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Add Delivery Address',
    }
    return render(request, 'delivery/address_form.html', context)


@login_required
def address_edit(request, address_id):
    """Edit delivery address"""
    address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = DeliveryAddressForm(request.POST, instance=address, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Delivery address "{address.label}" updated successfully!')
            return redirect('delivery:address_list')
    else:
        form = DeliveryAddressForm(instance=address, user=request.user)
    
    context = {
        'form': form,
        'address': address,
        'title': 'Edit Delivery Address',
    }
    return render(request, 'delivery/address_form.html', context)


@login_required
def address_delete(request, address_id):
    """Delete delivery address"""
    address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        label = address.label
        address.delete()
        messages.success(request, f'Delivery address "{label}" deleted successfully!')
        return redirect('delivery:address_list')
    
    context = {
        'address': address,
    }
    return render(request, 'delivery/address_confirm_delete.html', context)


@login_required
def address_set_default(request, address_id):
    """Set address as default"""
    address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, f'"{address.label}" set as default delivery address!')
    return redirect('delivery:address_list')
