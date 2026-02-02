from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.utils import timezone
from django.views.decorators.http import condition
from django.contrib.auth.decorators import login_required
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
    
    # Check if any filters are active
    has_active_filters = bool(
        search_query or category_id or dietary_tag_ids or 
        min_price or max_price or max_calories or 
        min_protein or max_carbs or max_fat
    )
    
    # Get recommendations for authenticated users
    recommendations = None
    if request.user.is_authenticated:
        recommendations = get_recommendations(request.user, limit=6)
    
    # Get popular and highly rated items
    popular_items = get_popular_items(limit=6)
    highly_rated_items = get_highly_rated_items(limit=6)
    
    # When filters are active, show only filtered results (not all menu items)
    if has_active_filters:
        # Pagination for filtered results
        paginator = Paginator(list(menu_items), 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Group paginated items by category
        menu_by_category = {}
        for item in page_obj:
            if item.category not in menu_by_category:
                menu_by_category[item.category] = []
            menu_by_category[item.category].append(item)
    else:
        # No filters active - show all items grouped by category
        # Pagination for all items
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
        'selected_category_id': str(category_id) if category_id else "",
        'selected_dietary_tags': [int(tag_id) for tag_id in dietary_tag_ids],
        'recommendations': recommendations,
        'popular_items': popular_items,
        'highly_rated_items': highly_rated_items,
        'has_active_filters': has_active_filters,
        'page_obj': page_obj,
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
    
    # Get review statistics (use cached values from model)
    from reviews.models import Review
    # Use cached average_rating and total_reviews from MenuItem
    # But also get detailed stats for display
    review_stats = {
        'avg_rating': float(menu_item.average_rating),
        'total_reviews': menu_item.total_reviews,
        'rating_distribution': Review.objects.filter(
            menu_item=menu_item,
            is_approved=True
        ).values('rating').annotate(count=Count('id')).order_by('-rating')
    }
    
    # Get recent approved reviews for preview
    recent_reviews = Review.objects.filter(
        menu_item=menu_item,
        is_approved=True
    ).select_related('user').order_by('-created_at', '-is_verified_purchase')[:5]
    
    context = {
        'menu_item': menu_item,
        'related_items': related_items,
        'recommendations': recommendations,
        'review_stats': review_stats,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'menu/menu_detail.html', context)


@login_required
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
    
    # Get review statistics (use cached values from model)
    from reviews.models import Review
    # Use cached average_rating and total_reviews from MenuItem
    # But also get detailed stats for display
    review_stats = {
        'avg_rating': float(menu_item.average_rating),
        'total_reviews': menu_item.total_reviews,
        'rating_distribution': Review.objects.filter(
            menu_item=menu_item,
            is_approved=True
        ).values('rating').annotate(count=Count('id')).order_by('-rating')
    }
    
    # Get recent approved reviews for preview
    recent_reviews = Review.objects.filter(
        menu_item=menu_item,
        is_approved=True
    ).select_related('user').order_by('-created_at', '-is_verified_purchase')[:5]
    
    context = {
        'menu_item': menu_item,
        'related_items': related_items,
        'recommendations': recommendations,
        'review_stats': review_stats,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'menu/menu_detail.html', context)




def health_check(request):
    """
    Health check endpoint for monitoring and load balancers
    Returns JSON with application status
    """
    status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'checks': {}
    }
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            status['checks']['database'] = 'ok'
    except Exception as e:
        status['checks']['database'] = f'error: {str(e)}'
        status['status'] = 'unhealthy'
    
    # Basic model check
    try:
        menu_count = MenuItem.objects.count()
        status['checks']['models'] = 'ok'
        status['menu_items_count'] = menu_count
    except Exception as e:
        status['checks']['models'] = f'error: {str(e)}'
        status['status'] = 'unhealthy'
    
    # Return appropriate HTTP status
    http_status = 200 if status['status'] == 'healthy' else 503
    
    return JsonResponse(status, status=http_status)


def favicon(request):
    """Serve favicon - prevents 404 errors for missing favicon.ico"""
    # Return empty response with correct content type
    return HttpResponse(status=204)

