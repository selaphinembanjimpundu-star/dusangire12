// Admin image upload preview
document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.querySelector('input[type="file"][name="image"]');
    
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validate file size (5MB)
                const maxSize = 5 * 1024 * 1024; // 5MB
                if (file.size > maxSize) {
                    alert('Image file is too large. Maximum size is 5MB.');
                    e.target.value = '';
                    return;
                }
                
                // Validate file type
                const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
                if (!allowedTypes.includes(file.type)) {
                    alert('Invalid image format. Allowed formats: JPEG, PNG, WEBP');
                    e.target.value = '';
                    return;
                }
                
                // Show preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.querySelector('.field-image_preview');
                    if (preview) {
                        preview.innerHTML = '<img src="' + e.target.result + '" style="max-width: 300px; max-height: 300px; border-radius: 8px; margin-top: 10px;" />';
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }
});




