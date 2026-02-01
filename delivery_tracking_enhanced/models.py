from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class DeliveryZone(models.Model):
    """Hospital wards and external delivery areas"""
    
    ZONE_TYPE_CHOICES = [
        ('WARD', 'Hospital Ward'),
        ('EXTERNAL', 'External Location'),
        ('OFFICE', 'Corporate Office'),
    ]
    
    name = models.CharField(max_length=100)
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    # Location details
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    address = models.TextField(blank=True)
    
    # Delivery info
    average_delivery_time_minutes = models.IntegerField(default=30, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_zone_type_display()})"


class DeliveryTracking(models.Model):
    """Real-time GPS tracking and delivery status"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PREPARING', 'Preparing'),
        ('READY_FOR_DELIVERY', 'Ready for Delivery'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='delivery_tracking')
    delivery_zone = models.ForeignKey(DeliveryZone, on_delete=models.SET_NULL, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Location tracking
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    destination_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    destination_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    preparing_start = models.DateTimeField(null=True, blank=True)
    out_for_delivery_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Delivery notes
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Delivery - Order #{self.order.id}"
    
    @property
    def delivery_duration_minutes(self):
        """Calculate total delivery duration"""
        if self.delivered_at and self.out_for_delivery_at:
            return int((self.delivered_at - self.out_for_delivery_at).total_seconds() / 60)
        return None


class DeliveryStatusHistory(models.Model):
    """Track status changes and location updates"""
    
    delivery_tracking = models.ForeignKey(DeliveryTracking, on_delete=models.CASCADE, related_name='status_history')
    
    status = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.delivery_tracking.order.id} - {self.status}"


class DeliveryPersonnelMetrics(models.Model):
    """Delivery personnel performance tracking"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='delivery_metrics')
    
    total_deliveries = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    successful_deliveries = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    failed_deliveries = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Performance metrics
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    on_time_delivery_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    average_delivery_time_minutes = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    total_distance_km = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-average_rating']
    
    def __str__(self):
        return f"Metrics - {self.user.get_full_name()}"
    
    @property
    def success_rate(self):
        """Calculate delivery success rate"""
        total = self.total_deliveries
        if total == 0:
            return 0
        return round((self.successful_deliveries / total) * 100, 2)


class DeliveryRating(models.Model):
    """Customer ratings for delivery personnel"""
    
    delivery_tracking = models.ForeignKey(DeliveryTracking, on_delete=models.CASCADE, related_name='ratings')
    delivery_personnel = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_ratings')
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('delivery_tracking', 'delivery_personnel')
    
    def __str__(self):
        return f"{self.rating}★ - {self.delivery_personnel.username}"