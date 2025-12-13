from django.db.models import Q, Count, Avg
from .models import MenuItem
from orders.models import Order, OrderItem


def get_recommendations(user, limit=6):
    """Get personalized menu item recommendations based on user's order history"""
    if not user.is_authenticated:
        # Return featured items for non-authenticated users
        return MenuItem.objects.filter(
            is_available=True,
            is_featured=True
        )[:limit]
    
    # Get user's order history
    user_orders = Order.objects.filter(
        user=user,
        status__in=['delivered', 'ready']
    ).select_related('user').prefetch_related('items__menu_item')
    
    if not user_orders.exists():
        # No order history, return featured items
        return MenuItem.objects.filter(
            is_available=True,
            is_featured=True
        )[:limit]
    
    # Get categories and dietary tags from user's orders
    ordered_categories = set()
    ordered_dietary_tags = set()
    ordered_items = set()
    
    for order in user_orders:
        for order_item in order.items.all():
            menu_item = order_item.menu_item
            ordered_items.add(menu_item.id)
            ordered_categories.add(menu_item.category_id)
            ordered_dietary_tags.update(menu_item.dietary_tags.values_list('id', flat=True))
    
    # Get recommendations based on:
    # 1. Same category as ordered items
    # 2. Same dietary tags as ordered items
    # 3. Exclude already ordered items
    recommendations = MenuItem.objects.filter(
        is_available=True
    ).exclude(id__in=ordered_items)
    
    # Prioritize items from same categories
    category_recommendations = recommendations.filter(
        category_id__in=ordered_categories
    ).distinct()
    
    # Also include items with same dietary tags
    dietary_recommendations = recommendations.filter(
        dietary_tags__id__in=ordered_dietary_tags
    ).distinct()
    
    # Combine and get unique items
    all_recommendations = (category_recommendations | dietary_recommendations).distinct()
    
    # If we don't have enough recommendations, add featured items
    if all_recommendations.count() < limit:
        featured_items = MenuItem.objects.filter(
            is_available=True,
            is_featured=True
        ).exclude(id__in=ordered_items)
        all_recommendations = (all_recommendations | featured_items).distinct()
    
    # If still not enough, add popular items (by order count)
    if all_recommendations.count() < limit:
        popular_items = MenuItem.objects.filter(
            is_available=True
        ).exclude(id__in=ordered_items).annotate(
            order_count=Count('orderitem')
        ).order_by('-order_count')[:limit]
        all_recommendations = (all_recommendations | popular_items).distinct()
    
    return all_recommendations[:limit]


def get_popular_items(limit=6):
    """Get popular menu items based on order count"""
    return MenuItem.objects.filter(
        is_available=True
    ).annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count', '-is_featured')[:limit]


def get_highly_rated_items(limit=6):
    """Get highly rated menu items"""
    from reviews.models import Review
    
    return MenuItem.objects.filter(
        is_available=True
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).filter(
        review_count__gte=1,
        avg_rating__gte=4.0
    ).order_by('-avg_rating', '-review_count')[:limit]

