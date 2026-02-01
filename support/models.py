from django.db import models
from django.contrib.auth.models import User


class SupportTicket(models.Model):
    """Customer support tickets"""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='support_tickets'
    )
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    
    # Staff assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        limit_choices_to={'is_staff': True}
    )
    
    # Related objects
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='support_tickets',
        help_text="Related order if ticket is about an order"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Ticket #{self.id} - {self.subject} - {self.user.username}"
    
    def mark_resolved(self):
        """Mark ticket as resolved"""
        from django.utils import timezone
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()


class SupportMessage(models.Model):
    """Messages in support tickets"""
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='support_messages'
    )
    message = models.TextField()
    is_internal = models.BooleanField(
        default=False,
        help_text="Internal note (only visible to staff)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message #{self.id} - Ticket #{self.ticket.id}"


class FAQ(models.Model):
    """Frequently Asked Questions"""
    
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('ordering', 'Ordering'),
        ('payment', 'Payment'),
        ('delivery', 'Delivery'),
        ('health', 'Health & Nutrition'),
        ('account', 'Account'),
        ('subscription', 'Subscriptions'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.IntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'order', '-created_at']
        verbose_name_plural = "FAQs"
    
    def __str__(self):
        return f"[{self.get_category_display()}] {self.question}"


class AboutUsPage(models.Model):
    """Store About Us page content"""
    title = models.CharField(max_length=200, default="About Dusangire")
    description = models.TextField()
    mission = models.TextField(help_text="Mission statement")
    vision = models.TextField(help_text="Vision statement")
    values = models.TextField(help_text="Core values (comma-separated)")
    team_intro = models.TextField(blank=True)
    image = models.ImageField(upload_to='about/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "About Us Page"
        verbose_name_plural = "About Us Pages"
    
    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    """General contact form messages"""
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
