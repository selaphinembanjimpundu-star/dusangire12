# reviews/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from menu.models import MenuItem
from orders.models import Order


class Review(models.Model):
    """Customer reviews for menu items - Professional review system"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews',
        help_text="Order this review is associated with (if applicable)"
    )
    
    # Rating (1-5 stars)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    
    # Review content
    title = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Optional review title"
    )
    comment = models.TextField(
        help_text="Your review comment (minimum 10 characters)",
        max_length=2000
    )
    
    # Status
    is_approved = models.BooleanField(
        default=True,
        help_text="Whether this review is approved and visible to others"
    )
    is_verified_purchase = models.BooleanField(
        default=False,
        help_text="Whether this review is from a verified purchase"
    )
    
    # Moderation
    is_flagged = models.BooleanField(
        default=False,
        help_text="Whether this review has been flagged for moderation"
    )
    moderation_notes = models.TextField(
        blank=True,
        help_text="Admin notes for moderation"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at', '-is_verified_purchase']
        unique_together = ['user', 'menu_item']
        indexes = [
            models.Index(fields=['menu_item', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['menu_item', 'is_approved', '-created_at']),
            models.Index(fields=['is_verified_purchase', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.menu_item.name} - {self.rating} stars"
    
    def clean(self):
        """Validate review data"""
        # Validate comment length
        if self.comment and len(self.comment.strip()) < 10:
            raise ValidationError({
                'comment': 'Review comment must be at least 10 characters long.'
            })
        
        # Validate title if provided
        if self.title and len(self.title.strip()) < 3:
            raise ValidationError({
                'title': 'Review title must be at least 3 characters long if provided.'
            })
    
    def save(self, *args, **kwargs):
        # Validate before saving
        self.full_clean()
        
        # Mark as verified purchase if order is provided and belongs to user
        if self.order and self.order.user == self.user:
            # Verify order contains this menu item
            if self.order.items.filter(menu_item=self.menu_item).exists():
                self.is_verified_purchase = True
        
        super().save(*args, **kwargs)
        
        # Update menu item average rating
        self.menu_item.update_average_rating()
    
    @property
    def rating_stars(self):
        """Return rating as star display"""
        return '★' * self.rating + '☆' * (5 - self.rating)
    
    @property
    def is_recent(self):
        """Check if review is recent (within 30 days)"""
        from django.utils import timezone
        from datetime import timedelta
        return self.created_at >= timezone.now() - timedelta(days=30)
    
    @property
    def helpful_count(self):
        """Count of helpful votes"""
        return self.helpful_votes.filter(is_helpful=True).count()
    
    def is_helpful_by_user(self, user):
        """Check if user has marked this review as helpful"""
        if not user.is_authenticated:
            return False
        return self.helpful_votes.filter(user=user, is_helpful=True).exists()


class ReviewHelpful(models.Model):
    """Track which reviews users found helpful"""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='helpful_votes'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='helpful_votes'
    )
    is_helpful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['review', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.review.menu_item.name} - {'Helpful' if self.is_helpful else 'Not Helpful'}"


# Signal handlers for updating menu item ratings
@receiver(post_save, sender=Review)
def update_rating_on_save(sender, instance, created, **kwargs):
    """Update menu item rating when review is saved"""
    if instance.menu_item:
        instance.menu_item.update_average_rating()


@receiver(post_delete, sender=Review)
def update_rating_on_delete(sender, instance, **kwargs):
    """Update menu item rating when review is deleted"""
    if instance.menu_item:
        instance.menu_item.update_average_rating()
        

