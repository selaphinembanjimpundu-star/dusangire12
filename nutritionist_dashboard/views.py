from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count, Q
from orders.models import Order
from .models import NutritionistProfile, ClientAssignment, Consultation, MealPlan

@login_required
def dashboard(request):
    try:
        profile = NutritionistProfile.objects.get(user=request.user)
    except NutritionistProfile.DoesNotExist:
        return redirect('nutritionist_dashboard:create_profile')
    
    # Get active assignments
    active_assignments = ClientAssignment.objects.filter(
        nutritionist=request.user,
        status='active'
    ).select_related('client')
    
    # Get upcoming consultations
    upcoming_consultations = Consultation.objects.filter(
        nutritionist=request.user,
        scheduled_at__gte=timezone.now(),
        status='scheduled'
    ).select_related('client').order_by('scheduled_at')[:5]
    
    # Get recent meal plans
    recent_plans = MealPlan.objects.filter(
        nutritionist=request.user
    ).select_related('client').order_by('-created_at')[:5]
    
    # Get recent orders from assigned clients
    client_ids = active_assignments.values_list('client_id', flat=True)
    recent_orders = Order.objects.filter(
        user_id__in=client_ids
    ).order_by('-created_at')[:5]
    
    # Calculate statistics
    stats = {
        'active_assignments': active_assignments.count(),
        'max_clients': profile.max_clients,
        'monthly_consultations': Consultation.objects.filter(
            nutritionist=request.user,
            scheduled_at__month=timezone.now().month,
            status='completed'
        ).count(),
        'pending_plans': MealPlan.objects.filter(
            nutritionist=request.user,
            status='draft'
        ).count(),
        'adherence_rate': 85, # Placeholder for now
    }
    
    return render(request, 'nutritionist_dashboard/dashboard.html', {
        'title': _('Nutritionist Dashboard'),
        'profile': profile,
        'active_assignments': active_assignments,
        'upcoming_consultations': upcoming_consultations,
        'recent_plans': recent_plans,
        'recent_orders': recent_orders,
        'stats': stats,
    })

@login_required
def create_profile(request):
    from .forms import NutritionistProfileForm
    
    try:
        # Check if profile already exists
        profile = NutritionistProfile.objects.get(user=request.user)
        messages.info(request, _('You already have a nutritionist profile.'))
        return redirect('nutritionist_dashboard:dashboard')
    except NutritionistProfile.DoesNotExist:
        pass
    
    if request.method == 'POST':
        # Ensure required fields with defaults are present (form expects 'status')
        post_data = request.POST.copy()
        post_data.setdefault('status', 'active')
        form = NutritionistProfileForm(post_data)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, _('Nutritionist profile created successfully!'))
            return redirect('nutritionist_dashboard:dashboard')
    else:
        form = NutritionistProfileForm()
    
    return render(request, 'nutritionist_dashboard/create_profile.html', {
        'form': form,
        'title': _('Create Nutritionist Profile')
    })

@login_required
def update_profile(request):
    from .forms import NutritionistProfileForm
    
    try:
        profile = NutritionistProfile.objects.get(user=request.user)
    except NutritionistProfile.DoesNotExist:
        messages.error(request, _('Please create a nutritionist profile first.'))
        return redirect('nutritionist_dashboard:create_profile')
    
    if request.method == 'POST':
        form = NutritionistProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _('Profile updated successfully!'))
            return redirect('nutritionist_dashboard:dashboard')
    else:
        form = NutritionistProfileForm(instance=profile)
    
    return render(request, 'nutritionist_dashboard/update_profile.html', {
        'form': form,
        'title': _('Update Profile')
    })

@login_required
def no_profile(request):
    return render(request, 'nutritionist_dashboard/no_profile.html', {
        'title': _('No Profile')
    })

@login_required
def manage_clients(request):
    return render(request, 'nutritionist_dashboard/manage_clients.html', {
        'title': _('Manage Clients')
    })

@login_required
def consultations(request):
    return render(request, 'nutritionist_dashboard/consultations.html', {
        'title': _('Consultations')
    })

@login_required
def meal_plans(request):
    return render(request, 'nutritionist_dashboard/meal_plans.html', {
        'title': _('Meal Plans')
    })

@login_required
def diet_recommendations(request):
    return render(request, 'nutritionist_dashboard/diet_recommendations.html', {
        'title': _('Diet Recommendations')
    })

@login_required
def reports(request):
    return render(request, 'nutritionist_dashboard/reports.html', {
        'title': _('Reports')
    })

@login_required
def settings(request):
    return render(request, 'nutritionist_dashboard/settings.html', {
        'title': _('Settings')
    })

# Simple placeholder views for other URL patterns
def simple_dashboard(request):
    return redirect('nutritionist_dashboard:dashboard')

@login_required
def client_detail(request, assignment_id):
    """View detailed client information including health profile"""
    assignment = get_object_or_404(ClientAssignment, id=assignment_id, nutritionist=request.user)
    client = assignment.client
    
    # Get health profile
    from health_profiles.models import HealthProfile, PatientNutritionStatus, RecoveryMetrics, MedicalPrescription
    health_profile = HealthProfile.objects.filter(user=client).first()
    
    nutrition_history = []
    recovery_metrics = []
    prescriptions = []
    
    if health_profile:
        nutrition_history = PatientNutritionStatus.objects.filter(health_profile=health_profile).order_by('-assessment_date')
        recovery_metrics = RecoveryMetrics.objects.filter(health_profile=health_profile).order_by('-hospital_admission_date')
        prescriptions = MedicalPrescription.objects.filter(health_profile=health_profile).order_by('-prescription_date')
    
    # Get client's meal plans
    meal_plans = MealPlan.objects.filter(client=client, nutritionist=request.user).order_by('-created_at')
    
    # Get client's recent orders
    recent_orders = Order.objects.filter(user=client).order_by('-created_at')[:10]
    
    context = {
        'assignment': assignment,
        'client': client,
        'health_profile': health_profile,
        'nutrition_history': nutrition_history,
        'recovery_metrics': recovery_metrics,
        'prescriptions': prescriptions,
        'meal_plans': meal_plans,
        'recent_orders': recent_orders,
        'title': _('Client Details')
    }
    
    return render(request, 'nutritionist_dashboard/client_detail.html', context)

def schedule_consultation(request, client_id=None):
    return render(request, 'nutritionist_dashboard/schedule_consultation.html', {
        'title': _('Schedule Consultation')
    })

def create_meal_plan(request, client_id=None):
    return render(request, 'nutritionist_dashboard/create_meal_plan.html', {
        'title': _('Create Meal Plan')
    })

def meal_plan_detail(request, plan_id):
    return render(request, 'nutritionist_dashboard/meal_plan_detail.html', {
        'title': _('Meal Plan Details')
    })

def create_recommendation(request, client_id=None):
    return render(request, 'nutritionist_dashboard/create_recommendation.html', {
        'title': _('Create Recommendation')
    })

@login_required
def book_consultation_list(request):
    """List available nutritionists for booking"""
    nutritionists = NutritionistProfile.objects.filter(status='active').select_related('user')
    
    return render(request, 'nutritionist_dashboard/book_list.html', {
        'nutritionists': nutritionists,
        'title': _('Book a Consultation')
    })

@login_required
def book_consultation_detail(request, nutritionist_id):
    """Show availability and book a consultation"""
    nutritionist_profile = get_object_or_404(NutritionistProfile, id=nutritionist_id, status='active')
    from .models import NutritionistAvailability
    availability = NutritionistAvailability.objects.filter(nutritionist=nutritionist_profile.user, is_active=True)
    
    if request.method == 'POST':
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        consultation_type = request.POST.get('consultation_type', 'routine')
        
        try:
            scheduled_at = timezone.make_aware(datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M"))
            
            # Check if slot is already taken
            if Consultation.objects.filter(nutritionist=nutritionist_profile.user, scheduled_at=scheduled_at, status='scheduled').exists():
                messages.error(request, _('This slot is already booked. Please choose another one.'))
            else:
                Consultation.objects.create(
                    nutritionist=nutritionist_profile.user,
                    client=request.user,
                    consultation_type=consultation_type,
                    scheduled_at=scheduled_at,
                    status='scheduled'
                )
                messages.success(request, _('Consultation booked successfully!'))
                return redirect('customer_dashboard:my_consultations')
        except Exception as e:
            messages.error(request, _(f'Error booking consultation: {e}'))
    
    # Generate next 7 days of slots based on availability
    slots = []
    today = timezone.now().date()
    for i in range(1, 8):
        current_date = today + timedelta(days=i)
        day_avail = availability.filter(day_of_week=current_date.weekday())
        for avail in day_avail:
            # Simple logic: 30 min slots
            curr_time = datetime.combine(current_date, avail.start_time)
            end_time = datetime.combine(current_date, avail.end_time)
            while curr_time + timedelta(minutes=30) <= end_time:
                # Check if already booked
                is_booked = Consultation.objects.filter(
                    nutritionist=nutritionist_profile.user, 
                    scheduled_at=timezone.make_aware(curr_time),
                    status='scheduled'
                ).exists()
                
                if not is_booked:
                    slots.append(curr_time)
                curr_time += timedelta(minutes=30)

    return render(request, 'nutritionist_dashboard/book_detail.html', {
        'nutritionist': nutritionist_profile,
        'slots': slots,
        'title': _('Book Consultation with ') + nutritionist_profile.user.get_full_name()
    })

def get_client_stats(request, client_id):
    from django.http import JsonResponse
    return JsonResponse({'success': True, 'message': 'Client stats endpoint'})