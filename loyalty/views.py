from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import LoyaltyPoints, PointsTransaction, PointsRedemption
from orders.models import Order


@login_required
def loyalty_dashboard(request):
    """Display user's loyalty points dashboard"""
    loyalty_points, created = LoyaltyPoints.objects.get_or_create(user=request.user)
    
    # Get recent transactions
    recent_transactions = PointsTransaction.objects.filter(
        user=request.user
    ).select_related('order')[:10]
    
    # Get available redemptions
    available_redemptions = PointsRedemption.objects.filter(
        is_active=True,
        points_required__lte=loyalty_points.total_points
    ).order_by('points_required')
    
    # Get statistics
    stats = {
        'total_points': loyalty_points.total_points,
        'lifetime_points': loyalty_points.lifetime_points,
        'points_redeemed': loyalty_points.points_redeemed,
        'transactions_count': PointsTransaction.objects.filter(user=request.user).count(),
        'earned_this_month': PointsTransaction.objects.filter(
            user=request.user,
            transaction_type='earned',
            created_at__gte=timezone.now().replace(day=1)
        ).aggregate(total=Sum('points'))['total'] or 0,
    }
    
    context = {
        'loyalty_points': loyalty_points,
        'recent_transactions': recent_transactions,
        'available_redemptions': available_redemptions,
        'stats': stats,
    }
    return render(request, 'loyalty/dashboard.html', context)


@login_required
def points_history(request):
    """Display full points transaction history"""
    transactions = PointsTransaction.objects.filter(
        user=request.user
    ).select_related('order').order_by('-created_at')
    
    # Filtering
    transaction_type = request.GET.get('type', '')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    context = {
        'transactions': transactions,
        'current_filter': transaction_type,
    }
    return render(request, 'loyalty/history.html', context)


@login_required
def redeem_points(request, redemption_id):
    """Redeem points for a reward"""
    redemption = get_object_or_404(
        PointsRedemption,
        id=redemption_id,
        is_active=True
    )
    
    loyalty_points, _ = LoyaltyPoints.objects.get_or_create(user=request.user)
    
    if loyalty_points.total_points < redemption.points_required:
        messages.error(
            request,
            f"You don't have enough points. You need {redemption.points_required} points, but you only have {loyalty_points.total_points}."
        )
        return redirect('loyalty:dashboard')
    
    if request.method == 'POST':
        # Redeem points
        if loyalty_points.redeem_points(
            points=redemption.points_required,
            reason=f"Redeemed: {redemption.name}"
        ):
            messages.success(
                request,
                f"Successfully redeemed {redemption.points_required} points for {redemption.name}!"
            )
            
            # Create notification
            from notifications.models import Notification
            Notification.create_loyalty_notification(
                user=request.user,
                title="Points Redeemed",
                message=f"You have redeemed {redemption.points_required} points for {redemption.name}. Your new balance is {loyalty_points.total_points} points."
            )
            
            return redirect('loyalty:dashboard')
        else:
            messages.error(request, "Failed to redeem points. Please try again.")
    
    # Calculate new balance after redemption
    new_balance = loyalty_points.total_points - redemption.points_required
    
    context = {
        'redemption': redemption,
        'loyalty_points': loyalty_points,
        'new_balance': new_balance,
    }
    return render(request, 'loyalty/redeem.html', context)
