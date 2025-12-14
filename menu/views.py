from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from .models import Category, MenuItem, DietaryTag
from .forms import MenuFilterForm
from .utils import get_recommendations, get_popular_items, get_highly_rated_items


def menu_list(request):
    """Display all menu items with search and filter functionality"""
    menu_items = MenuItem.objects.filter(is_available=True).select_related('category').prefetch_related('dietary_tags')
    
    # Get all categories and dietary tags for filter form
    categories = Category.objects.filter(is_active=True)
    dietary_tags = DietaryTag.objects.all()
    
    # Initialize filter form
    filter_form = MenuFilterForm(request.GET)
    
    # Apply search filter (including ingredients)
    search_query = request.GET.get('search', '')
    if search_query:
        menu_items = menu_items.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(ingredients__icontains=search_query)
        )
    
    # Apply category filter
    category_id = request.GET.get('category')
    if category_id:
        menu_items = menu_items.filter(category_id=category_id)
    
    # Apply dietary tags filter
    dietary_tag_ids = request.GET.getlist('dietary_tags')
    if dietary_tag_ids:
        menu_items = menu_items.filter(dietary_tags__id__in=dietary_tag_ids).distinct()
    
    # Apply price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        menu_items = menu_items.filter(price__gte=min_price)
    if max_price:
        menu_items = menu_items.filter(price__lte=max_price)
    
    # Apply nutrition filters
    max_calories = request.GET.get('max_calories')
    if max_calories:
        menu_items = menu_items.filter(calories__lte=max_calories)
    
    min_protein = request.GET.get('min_protein')
    if min_protein:
        menu_items = menu_items.filter(protein__gte=min_protein)
    
    max_carbs = request.GET.get('max_carbs')
    if max_carbs:
        menu_items = menu_items.filter(carbs__lte=max_carbs)
    
    max_fat = request.GET.get('max_fat')
    if max_fat:
        menu_items = menu_items.filter(fat__lte=max_fat)
    
    # Group items by category for display
    menu_by_category = {}
    for category in categories:
        items = menu_items.filter(category=category)
        if items.exists():
            menu_by_category[category] = items
    
    # If no category filter, show all items grouped
    # If category filter is applied, show only that category
    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        menu_by_category = {selected_category: menu_items.filter(category=selected_category)}
    
    # Get recommendations for authenticated users
    recommendations = None
    if request.user.is_authenticated:
        recommendations = get_recommendations(request.user, limit=6)
    
    # Get popular and highly rated items
    popular_items = get_popular_items(limit=6)
    highly_rated_items = get_highly_rated_items(limit=6)
    
    # Pagination for menu items (if not grouped by category)
    # If category filter is applied, paginate within that category
    if category_id:
        paginator = Paginator(list(menu_items), 12)  # 12 items per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        menu_by_category = {selected_category: page_obj}
    else:
        # For all items, paginate the flat list
        paginator = Paginator(list(menu_items), 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        # Group paginated items by category
        menu_by_category = {}
        for item in page_obj:
            if item.category not in menu_by_category:
                menu_by_category[item.category] = []
            menu_by_category[item.category].append(item)
    
    context = {
        'menu_by_category': menu_by_category,
        'categories': categories,
        'dietary_tags': dietary_tags,
        'filter_form': filter_form,
        'search_query': search_query,
        'selected_category_id': category_id,
        'selected_dietary_tags': [int(tag_id) for tag_id in dietary_tag_ids],
        'recommendations': recommendations,
        'popular_items': popular_items,
        'highly_rated_items': highly_rated_items,
        'page_obj': page_obj if category_id or search_query or dietary_tag_ids or min_price or max_price or max_calories or min_protein or max_carbs or max_fat else None,
    }
    return render(request, 'menu/menu_list.html', context)


def menu_detail(request, item_id):
    """Display detailed view of a menu item"""
    menu_item = get_object_or_404(
        MenuItem.objects.select_related('category').prefetch_related('dietary_tags'),
        id=item_id,
        is_available=True
    )
    
    # Get related items from the same category
    related_items = MenuItem.objects.filter(
        category=menu_item.category,
        is_available=True
    ).exclude(id=item_id)[:4]
    
    # Get recommendations
    recommendations = None
    if request.user.is_authenticated:
        recommendations = get_recommendations(request.user, limit=4)
    
    # Get review statistics
    from reviews.models import Review
    review_stats = Review.objects.filter(
        menu_item=menu_item,
        is_approved=True
    ).aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id')
    )
    
    context = {
        'menu_item': menu_item,
        'related_items': related_items,
        'recommendations': recommendations,
        'review_stats': review_stats,
    }
    return render(request, 'menu/menu_detail.html', context)
