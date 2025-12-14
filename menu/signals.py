from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver
from PIL import Image
import os
from pathlib import Path
from .models import MenuItem


@receiver(pre_save, sender=MenuItem)
def optimize_image(sender, instance, **kwargs):
    """Optimize and resize image before saving"""
    if instance.image and hasattr(instance.image, 'path'):
        try:
            # Open the image
            img = Image.open(instance.image.path)
            
            # Convert RGBA to RGB if necessary (for JPEG compatibility)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize if image is too large (max 1200px on longest side)
            max_size = 1200
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(instance.image.path, 'JPEG', quality=85, optimize=True)
            
        except Exception as e:
            # If optimization fails, continue with original image
            print(f"Image optimization failed: {str(e)}")


@receiver(post_save, sender=MenuItem)
def generate_thumbnail(sender, instance, **kwargs):
    """Generate thumbnail after saving menu item"""
    if instance.image and hasattr(instance.image, 'path') and os.path.exists(instance.image.path):
        try:
            # Open the image
            img = Image.open(instance.image.path)
            
            # Create thumbnail directory if it doesn't exist
            thumbnail_path = instance.image.path.replace('.jpg', '_thumb.jpg').replace('.jpeg', '_thumb.jpeg').replace('.png', '_thumb.jpg')
            thumbnail_dir = os.path.dirname(thumbnail_path)
            
            if not os.path.exists(thumbnail_dir):
                os.makedirs(thumbnail_dir, exist_ok=True)
            
            # Generate thumbnail (300x300 max, maintaining aspect ratio)
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Save thumbnail
            img.save(thumbnail_path, 'JPEG', quality=80, optimize=True)
            
        except Exception as e:
            # If thumbnail generation fails, continue without it
            print(f"Thumbnail generation failed: {str(e)}")


@receiver(post_delete, sender=MenuItem)
def delete_image_file(sender, instance, **kwargs):
    """Delete image file when menu item is deleted"""
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)






