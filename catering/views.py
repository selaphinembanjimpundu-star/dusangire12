from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import CateringPackage, CateringBooking

def package_list(request):
    """List available catering packages"""
    packages = CateringPackage.objects.filter(is_active=True)
    return render(request, 'catering/package_list.html', {
        'packages': packages,
        'title': _('Catering Services')
    })

@login_required
def book_catering(request, package_id=None):
    """Book a catering service"""
    package = None
    if package_id:
        package = get_object_or_404(CateringPackage, id=package_id, is_active=True)
    
    if request.method == 'POST':
        event_name = request.POST.get('event_name')
        event_date = request.POST.get('event_date')
        event_time = request.POST.get('event_time')
        location = request.POST.get('location')
        number_of_people = int(request.POST.get('number_of_people', 0))
        special_requests = request.POST.get('special_requests')
        
        if not package_id:
            package_id = request.POST.get('package_id')
            if package_id:
                package = get_object_or_404(CateringPackage, id=package_id)

        booking = CateringBooking.objects.create(
            user=request.user,
            package=package,
            event_name=event_name,
            event_date=event_date,
            event_time=event_time,
            location=location,
            number_of_people=number_of_people,
            special_requests=special_requests,
            status='pending'
        )
        
        messages.success(request, _('Catering booking submitted successfully! We will contact you shortly to confirm.'))
        return redirect('customer_dashboard:dashboard') # Or a specific catering bookings view

    packages = CateringPackage.objects.filter(is_active=True)
    return render(request, 'catering/book_catering.html', {
        'selected_package_id': str(package.id) if package else "",
        'selected_package': package,
        'packages': packages,
        'title': _('Book Catering')
    })
