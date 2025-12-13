from django.contrib import admin
from .models import Review, ReviewHelpful


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'menu_item', 'rating', 'title', 'is_approved', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_verified_purchase', 'created_at']
    search_fields = ['user__username', 'menu_item__name', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Review Details', {
            'fields': ('user', 'menu_item', 'order', 'rating', 'title', 'comment')
        }),
        ('Status', {
            'fields': ('is_approved', 'is_verified_purchase')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} review(s) approved.")
    approve_reviews.short_description = "Approve selected reviews"
    
    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} review(s) disapproved.")
    disapprove_reviews.short_description = "Disapprove selected reviews"


@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'is_helpful', 'created_at']
    list_filter = ['is_helpful', 'created_at']
    search_fields = ['review__menu_item__name', 'user__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
