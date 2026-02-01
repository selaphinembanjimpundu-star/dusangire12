from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from menu.models import MenuItem
from orders.models import Order
from .models import Review, ReviewHelpful
from .forms import ReviewForm


@login_required
def add_review(request, item_id):
    """Add a review for a menu item"""
    menu_item = get_object_or_404(MenuItem, id=item_id)
    
    # Check if user has already reviewed this item
    existing_review = Review.objects.filter(user=request.user, menu_item=menu_item).first()
    
    # Get user's orders that include this item
    user_orders = Order.objects.filter(
        user=request.user,
        items__menu_item=menu_item,
        status__in=['delivered', 'ready']
    ).distinct()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Check if review already exists
            if existing_review:
                # Update existing review
                existing_review.rating = form.cleaned_data['rating']
                existing_review.title = form.cleaned_data.get('title', '')
                existing_review.comment = form.cleaned_data['comment']
                order_id = form.cleaned_data.get('order_id')
                if order_id:
                    try:
                        existing_review.order = Order.objects.get(id=order_id, user=request.user)
                    except Order.DoesNotExist:
                        pass
                existing_review.save()
                messages.success(request, "Your review has been updated!")
                return redirect('reviews:item_reviews', item_id=item_id)
            else:
                # Create new review
                review = form.save(commit=False)
                review.user = request.user
                review.menu_item = menu_item
                order_id = form.cleaned_data.get('order_id')
                if order_id:
                    try:
                        review.order = Order.objects.get(id=order_id, user=request.user)
                    except Order.DoesNotExist:
                        pass
                review.save()
                messages.success(request, "Thank you for your review!")
                return redirect('reviews:item_reviews', item_id=item_id)
    else:
        initial_data = {}
        if existing_review:
            initial_data = {
                'rating': existing_review.rating,
                'title': existing_review.title,
                'comment': existing_review.comment,
            }
        form = ReviewForm(initial=initial_data)
    
    context = {
        'menu_item': menu_item,
        'form': form,
        'existing_review': existing_review,
        'existing_review_order_id': str(existing_review.order_id) if existing_review and existing_review.order_id else "",
        'user_orders': user_orders,
    }
    return render(request, 'reviews/add_review.html', context)


# reviews/views.py - Update the item_reviews function
def item_reviews(request, item_id):
    """Display reviews for a menu item"""
    menu_item = get_object_or_404(MenuItem, id=item_id)
    
    # Get approved reviews
    reviews = Review.objects.filter(
        menu_item=menu_item,
        is_approved=True
    ).select_related('user').order_by('-created_at')
    
    # Get helpful votes for the current user
    helpful_review_ids = []
    if request.user.is_authenticated:
        helpful_review_ids = list(
            ReviewHelpful.objects.filter(
                user=request.user,
                is_helpful=True,
                review__in=reviews
            ).values_list('review_id', flat=True)
        )
    
    # Statistics
    stats = reviews.aggregate(
        average_rating=Avg('rating'),
        total_reviews=Count('id')
    )
    
    # Calculate rating distribution
    rating_distribution = {}
    for rating in range(1, 6):
        count = reviews.filter(rating=rating).count()
        rating_distribution[str(rating)] = count
    
    # Pagination
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Check if user has reviewed
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(user=request.user, menu_item=menu_item).first()
    
    context = {
        'menu_item': menu_item,
        'reviews': page_obj,
        'page_obj': page_obj,
        'stats': stats,
        'user_review': user_review,
        'helpful_review_ids': helpful_review_ids,
        'rating_distribution': rating_distribution,  # Add this
    }
    return render(request, 'reviews/item_reviews.html', context)


@login_required
def my_reviews(request):
    """Display user's reviews"""
    reviews = Review.objects.filter(
        user=request.user
    ).select_related('menu_item').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(reviews, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'reviews/my_reviews.html', context)


@login_required
def mark_helpful(request, review_id):
    """Mark a review as helpful (AJAX)"""
    review = get_object_or_404(Review, id=review_id)
    
    # Check if user already voted
    helpful_vote, created = ReviewHelpful.objects.get_or_create(
        review=review,
        user=request.user,
        defaults={'is_helpful': True}
    )
    
    if not created:
        # Toggle helpful status
        helpful_vote.is_helpful = not helpful_vote.is_helpful
        helpful_vote.save()
    
    helpful_count = review.helpful_votes.filter(is_helpful=True).count()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'action': 'added' if helpful_vote.is_helpful else 'removed',
            'helpful_count': helpful_count
        })
    
    messages.success(request, f"Review marked as {'helpful' if helpful_vote.is_helpful else 'not helpful'}.")
    return redirect('reviews:item_reviews', item_id=review.menu_item.id)

# reviews/views.py - Add this function
@login_required
def edit_review(request, review_id):
    """Edit an existing review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Your review has been updated!")
            return redirect('reviews:item_reviews', item_id=review.menu_item.id)
    else:
        form = ReviewForm(instance=review)
    
    context = {
        'menu_item': review.menu_item,
        'form': form,
        'existing_review': review,
        'existing_review_order_id': str(review.order_id) if review.order_id else "",
    }
    return render(request, 'reviews/add_review.html', context)