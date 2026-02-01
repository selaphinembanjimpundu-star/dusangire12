# reviews/templatetags/review_filters.py
from django import template
from reviews.models import ReviewHelpful

register = template.Library()

@register.filter
def is_helpful(user, review):
    """Check if a user has marked a review as helpful"""
    if not user or not user.is_authenticated:
        return False
    
    try:
        return ReviewHelpful.objects.filter(
            user=user,
            review=review,
            is_helpful=True
        ).exists()
    except:
        return False

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    try:
        return dictionary.get(str(key), 0)
    except:
        return 0