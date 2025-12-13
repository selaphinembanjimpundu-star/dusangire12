# Image Upload Guide - Phase 2

## ✅ Image Upload Functionality Added

### Features Implemented

1. **Image Validation**
   - File size validation (max 5MB)
   - Format validation (JPEG, PNG, WEBP only)
   - Dimension validation (min 100x100px, max 4000x4000px)

2. **Image Optimization**
   - Automatic image resizing (max 1200px on longest side)
   - Automatic format conversion (RGBA to RGB for JPEG compatibility)
   - Quality optimization (85% JPEG quality)
   - Automatic thumbnail generation

3. **Admin Panel Enhancements**
   - Image preview in admin list view
   - Image preview in admin form
   - Real-time preview when selecting image
   - Helpful upload instructions

4. **Automatic Cleanup**
   - Old images automatically deleted when menu item is deleted
   - Prevents orphaned files in media directory

## Files Created/Modified

### New Files
- `menu/validators.py` - Image validation functions
- `menu/signals.py` - Image optimization and cleanup signals
- `static/admin/css/image_preview.css` - Admin preview styling
- `static/admin/js/image_upload.js` - Client-side validation and preview

### Modified Files
- `menu/models.py` - Added validators to ImageField
- `menu/admin.py` - Added image preview and enhanced admin interface
- `menu/apps.py` - Registered signals

## How to Use

### In Admin Panel

1. **Upload Image**
   - Go to Admin Panel → Menu → Menu Items
   - Click "Add Menu Item" or edit existing item
   - Click "Choose File" in the Image field
   - Select an image (JPEG, PNG, or WEBP)
   - Image will be automatically validated and optimized

2. **View Image Preview**
   - After selecting an image, preview appears below the upload field
   - In list view, thumbnail appears in the "Image Preview" column

3. **Image Requirements**
   - **Format**: JPEG, PNG, or WEBP
   - **Size**: Maximum 5MB
   - **Dimensions**: Minimum 100x100px, Maximum 4000x4000px
   - **Recommended**: 800x600px for best display

### Image Storage

- Images are stored in: `media/menu_items/`
- File naming: Django automatically generates unique filenames
- Images are optimized on upload (resized if too large)

## Technical Details

### Validation Process

1. **Client-Side (JavaScript)**
   - File size check (5MB limit)
   - File type check (JPEG, PNG, WEBP)
   - Immediate preview

2. **Server-Side (Django)**
   - File size validation
   - Format validation using PIL
   - Dimension validation
   - Image optimization on save

### Image Optimization

When an image is uploaded:
1. Image is opened with PIL (Pillow)
2. RGBA/LA/P mode converted to RGB (for JPEG compatibility)
3. If image is larger than 1200px, it's resized maintaining aspect ratio
4. Image is saved with 85% quality and optimization enabled

### Automatic Cleanup

When a menu item is deleted:
- The associated image file is automatically deleted from the filesystem
- Prevents accumulation of unused image files

## Testing Image Upload

1. **Test Valid Image**
   - Upload a JPEG/PNG/WEBP image under 5MB
   - Should upload successfully
   - Preview should appear

2. **Test Invalid Format**
   - Try uploading a PDF or other non-image file
   - Should show error message

3. **Test Large File**
   - Try uploading an image larger than 5MB
   - Should show error message

4. **Test Small Image**
   - Try uploading an image smaller than 100x100px
   - Should show error message

## Troubleshooting

### Images Not Displaying

1. **Check MEDIA_URL and MEDIA_ROOT in settings.py**
   - Should be configured correctly (already done in Phase 1)

2. **Check File Permissions**
   - Ensure `media/` directory is writable

3. **Check Static Files**
   - Run `python manage.py collectstatic` if needed

### Image Upload Fails

1. **Check File Size**
   - Ensure image is under 5MB

2. **Check File Format**
   - Only JPEG, PNG, WEBP are allowed

3. **Check Pillow Installation**
   - Run `pip install Pillow` if not installed

## Next Steps

Image upload is now fully functional! You can:
- Upload menu item images through admin panel
- Images are automatically optimized
- Preview images in admin and on the website
- Old images are automatically cleaned up

Phase 2 is now complete with full image upload support! 🎉




