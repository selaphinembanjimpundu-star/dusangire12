from django.shortcuts import render
from .models import Category, MenuItem


def home(request):
    """Homepage view"""
    featured_items = MenuItem.objects.filter(is_featured=True, is_available=True)[:6]
    categories = Category.objects.filter(is_active=True)[:4]
    
    context = {
        'featured_items': featured_items,
        'categories': categories,
    }
    return render(request, 'menu/home.html', context)


def menu_list(request):
    """Display all menu items grouped by category"""
    categories = Category.objects.filter(is_active=True).prefetch_related('menu_items')
    menu_items = MenuItem.objects.filter(is_available=True).select_related('category')
    
    # Group items by category
    menu_by_category = {}
    for category in categories:
        items = menu_items.filter(category=category)
        if items.exists():
            menu_by_category[category] = items
    
    context = {
        'menu_by_category': menu_by_category,
        'categories': categories,
    }
    return render(request, 'menu/menu_list.html', context)


def menu_detail(request, item_id):
    """Display detailed view of a menu item"""
    menu_item = MenuItem.objects.select_related('category').prefetch_related('dietary_tags').get(id=item_id)
    context = {
        'menu_item': menu_item,
    }
    return render(request, 'menu/menu_detail.html', context)
