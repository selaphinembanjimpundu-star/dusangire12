from django import template

register = template.Library()

@register.simple_tag
def get_cart_count(user):
    """Get cart item count for user"""
    if user.is_authenticated:
        try:
            return user.cart.get_item_count()
        except:
            return 0
    return 0






