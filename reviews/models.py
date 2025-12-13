from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from menu.models import MenuItem
from orders.models import Order


class Review(models.Model):
    """Customer reviews for menu items"""
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
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField(help_text="Your review comment")
    
    # Status
    is_approved = models.BooleanField(
        default=True,
        help_text="Whether this review is approved and visible to others"
    )
    is_verified_purchase = models.BooleanField(
        default=False,
        help_text="Whether this review is from a verified purchase"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'menu_item', 'order']
        indexes = [
            models.Index(fields=['menu_item', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.menu_item.name} - {self.rating} stars"
    
    def save(self, *args, **kwargs):
        # Mark as verified purchase if order is provided
        if self.order and self.order.user == self.user:
            self.is_verified_purchase = True
        super().save(*args, **kwargs)
    
    @property
    def rating_stars(self):
        """Return rating as star display"""
        return '★' * self.rating + '☆' * (5 - self.rating)


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
