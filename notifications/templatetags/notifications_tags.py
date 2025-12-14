from django import template
from notifications.models import Notification

register = template.Library()


@register.simple_tag
def get_unread_notification_count(user):
    """Get count of unread notifications for user"""
    if not user.is_authenticated:
        return 0
    return Notification.get_unread_count(user)



