from django.db.models import Count, Avg
from .models import MenuItem
from orders.models import Order

def get_recommendations(user, limit=6):
    """Get personalized menu item recommendations based on user's order history"""
    if not user.is_authenticated:
        # Return featured items for non-authenticated users
        return MenuItem.objects.filter(
            is_available=True,
            is_featured=True
        ).select_related('category').prefetch_related('dietary_tags')[:limit]

    # Get user's order history
    user_orders = Order.objects.filter(
        user=user,
        status__in=['delivered', 'ready']
    ).prefetch_related('items__menu_item__category', 'items__menu_item__dietary_tags')

    if not user_orders.exists():
        # No order history, return featured items
        return MenuItem.objects.filter(
            is_available=True,
            is_featured=True
        )[:limit]

    # Gather ordered item IDs, categories, and dietary tags
    ordered_items = set()
    ordered_categories = set()
    ordered_dietary_tags = set()

    for order in user_orders:
        for order_item in order.items.all():
            menu_item = order_item.menu_item
            ordered_items.add(menu_item.id)
            ordered_categories.add(menu_item.category_id)
            ordered_dietary_tags.update(menu_item.dietary_tags.values_list('id', flat=True))

    # Base queryset (all available items excluding already ordered)
    base_qs = MenuItem.objects.filter(is_available=True).exclude(id__in=ordered_items)

    # Get IDs for category and dietary recommendations
    category_ids = set(base_qs.filter(category_id__in=ordered_categories).values_list('id', flat=True))
    dietary_ids = set(base_qs.filter(dietary_tags__id__in=ordered_dietary_tags).values_list('id', flat=True))

    # Combine recommendation IDs
    recommended_ids = category_ids | dietary_ids

    # If not enough, add featured items
    if len(recommended_ids) < limit:
        featured_ids = set(base_qs.filter(is_featured=True).values_list('id', flat=True))
        recommended_ids |= featured_ids

    # If still not enough, add popular items by order count
    if len(recommended_ids) < limit:
        popular_ids = list(
            base_qs.annotate(order_count=Count('orderitem'))
            .order_by('-order_count')
            .values_list('id', flat=True)
        )
        recommended_ids |= set(popular_ids)

    # Fetch final queryset
    final_qs = MenuItem.objects.filter(id__in=recommended_ids)\
        .select_related('category')\
        .prefetch_related('dietary_tags')[:limit]

    return final_qs


def get_popular_items(limit=6):
    """Get popular menu items based on order count"""
    return MenuItem.objects.filter(
        is_available=True
    ).select_related('category').prefetch_related('dietary_tags').annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count', '-is_featured')[:limit]


def get_highly_rated_items(limit=6):
    """Get highly rated menu items"""
    from reviews.models import Review

    return MenuItem.objects.filter(
        is_available=True
    ).select_related('category').prefetch_related('dietary_tags').annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).filter(
        review_count__gte=1,
        avg_rating__gte=4.0
    ).order_by('-avg_rating', '-review_count')[:limit]
