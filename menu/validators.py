from django.core.exceptions import ValidationError
from PIL import Image
import os


def validate_image_size(image):
    """Validate that image is not too large (max 5MB)"""
    max_size = 5 * 1024 * 1024  # 5MB
    if image.size > max_size:
        raise ValidationError(f'Image file too large. Maximum size is 5MB. Current size: {image.size / (1024*1024):.2f}MB')


def validate_image_format(image):
    """Validate that image is in allowed formats"""
    allowed_formats = ['JPEG', 'JPG', 'PNG', 'WEBP']
    try:
        img = Image.open(image)
        format_name = img.format
        if format_name not in allowed_formats:
            raise ValidationError(
                f'Image format not allowed. Allowed formats: {", ".join(allowed_formats)}. '
                f'Uploaded format: {format_name}'
            )
    except Exception as e:
        raise ValidationError(f'Invalid image file: {str(e)}')


def validate_image_dimensions(image):
    """Validate that image dimensions are reasonable (optional)"""
    try:
        img = Image.open(image)
        width, height = img.size
        
        # Minimum dimensions
        if width < 100 or height < 100:
            raise ValidationError('Image dimensions too small. Minimum size is 100x100 pixels.')
        
        # Maximum dimensions (optional - can be removed if not needed)
        if width > 4000 or height > 4000:
            raise ValidationError('Image dimensions too large. Maximum size is 4000x4000 pixels.')
            
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f'Error reading image dimensions: {str(e)}')




