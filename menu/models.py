from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
import os
from .validators import validate_image_size, validate_image_format, validate_image_dimensions


class Category(models.Model):
    """Menu categories (Breakfast, Lunch, Dinner, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DietaryTag(models.Model):
    """Dietary tags (diabetic, low-sodium, high-protein, etc.)"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class or emoji")
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """Menu items with details"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_items')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    image = models.ImageField(
        upload_to='menu_items/',
        blank=True,
        null=True,
        help_text='Upload an image for this menu item. Recommended size: 800x600px. Max size: 5MB. Formats: JPEG, PNG, WEBP',
        validators=[validate_image_size, validate_image_format, validate_image_dimensions]
    )
    dietary_tags = models.ManyToManyField(DietaryTag, blank=True, related_name='menu_items')
    ingredients = models.TextField(
        blank=True,
        help_text="List of ingredients (comma-separated or one per line)"
    )
    
    # Nutrition information
    calories = models.PositiveIntegerField(blank=True, null=True, help_text="Calories per serving")
    protein = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Protein in grams")
    carbs = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Carbs in grams")
    fat = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Fat in grams")
    
    # Availability
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
    
    def __str__(self):
        return f"{self.name} - {self.category.name}"
    
    def get_thumbnail_url(self):
        """Get thumbnail URL if exists, otherwise return original image URL"""
        if not self.image:
            return None
        
        try:
            # Try to find thumbnail
            if hasattr(self.image, 'path') and os.path.exists(self.image.path):
                image_path = str(self.image.path)
                # Generate thumbnail path
                base_path = os.path.splitext(image_path)[0]
                ext = os.path.splitext(image_path)[1]
                thumbnail_path = f"{base_path}_thumb.jpg"
                
                if os.path.exists(thumbnail_path):
                    # Return thumbnail URL
                    image_url = str(self.image.url)
                    base_url = os.path.splitext(image_url)[0]
                    return f"{base_url}_thumb.jpg"
        except Exception:
            pass
        
        # Fallback to original image
        return self.image.url if self.image else None
