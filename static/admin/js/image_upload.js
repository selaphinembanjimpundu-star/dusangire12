// Admin image upload preview with enhanced functionality
document.addEventListener('DOMContentLoaded', function () {
    const imageInput = document.querySelector('input[type="file"][name="image"]');

    if (imageInput) {
        // Create preview container if it doesn't exist
        let previewContainer = document.querySelector('.field-image_preview') ||
            document.querySelector('.image-preview-container');

        if (!previewContainer) {
            // Find the image field wrapper
            const imageFieldWrapper = imageInput.closest('.form-row') ||
                imageInput.closest('div') ||
                imageInput.parentElement;

            if (imageFieldWrapper) {
                previewContainer = document.createElement('div');
                previewContainer.className = 'image-preview-container';
                previewContainer.style.cssText = 'margin-top: 15px; padding: 15px; background: #f8f9fa; border-radius: 8px; border: 2px dashed #dee2e6;';
                imageFieldWrapper.appendChild(previewContainer);
            }
        }

        // Show existing image if available
        const existingImage = document.querySelector('.field-image_preview img');
        if (existingImage && previewContainer) {
            const existingImg = existingImage.cloneNode(true);
            existingImg.style.cssText = 'max-width: 300px; max-height: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); display: block;';
            previewContainer.innerHTML = '<p style="margin: 0 0 10px 0; font-weight: bold; color: #495057;">Current Image:</p>';
            previewContainer.appendChild(existingImg);
        }

        imageInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                // Validate file size (5MB)
                const maxSize = 5 * 1024 * 1024; // 5MB
                if (file.size > maxSize) {
                    alert('Image file is too large. Maximum size is 5MB.');
                    e.target.value = '';
                    if (previewContainer) {
                        previewContainer.innerHTML = '<p style="color: #dc3545; margin: 0;">❌ File too large. Maximum size is 5MB.</p>';
                    }
                    return;
                }

                // Validate file type
                const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
                if (!allowedTypes.includes(file.type)) {
                    alert('Invalid image format. Allowed formats: JPEG, PNG, WEBP');
                    e.target.value = '';
                    if (previewContainer) {
                        previewContainer.innerHTML = '<p style="color: #dc3545; margin: 0;">❌ Invalid format. Allowed: JPEG, PNG, WEBP</p>';
                    }
                    return;
                }

                // Show loading indicator
                if (previewContainer) {
                    previewContainer.innerHTML = '<p style="margin: 0; color: #0d6efd;">⏳ Loading preview...</p>';
                }

                // Show preview
                const reader = new FileReader();
                reader.onload = function (event) {
                    if (previewContainer) {
                        const img = document.createElement('img');
                        img.src = event.target.result;
                        img.style.cssText = 'max-width: 100%; max-height: 400px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); display: block; margin: 10px auto; border: 2px solid #0d6efd;';
                        img.alt = 'Image Preview';

                        const infoDiv = document.createElement('div');
                        infoDiv.style.cssText = 'margin-top: 10px; padding: 10px; background: #d1ecf1; border-radius: 4px; font-size: 12px; color: #0c5460;';
                        infoDiv.innerHTML = `
                            <strong>✓ Image Selected:</strong><br>
                            Name: ${file.name}<br>
                            Size: ${(file.size / 1024).toFixed(2)} KB<br>
                            Type: ${file.type}
                        `;

                        previewContainer.innerHTML = '';
                        previewContainer.appendChild(img);
                        previewContainer.appendChild(infoDiv);

                        // Add success animation
                        previewContainer.style.borderColor = '#28a745';
                        previewContainer.style.background = '#d4edda';
                    }

                    // Also update the readonly image_preview field if it exists
                    const readonlyPreview = document.querySelector('.field-image_preview');
                    if (readonlyPreview && readonlyPreview !== previewContainer) {
                        readonlyPreview.innerHTML = '<img src="' + event.target.result + '" style="max-width: 300px; max-height: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />';
                    }
                };

                reader.onerror = function () {
                    if (previewContainer) {
                        previewContainer.innerHTML = '<p style="color: #dc3545; margin: 0;">❌ Error reading file. Please try again.</p>';
                    }
                };

                reader.readAsDataURL(file);
            } else {
                // No file selected, clear preview
                if (previewContainer && !existingImage) {
                    previewContainer.innerHTML = '<p style="color: #6c757d; margin: 0; font-style: italic;">No image selected. Choose a file to see preview.</p>';
                    previewContainer.style.borderColor = '#dee2e6';
                    previewContainer.style.background = '#f8f9fa';
                }
            }
        });

        // Enhance file input styling
        imageInput.style.cssText += 'padding: 10px; border: 2px dashed #0d6efd; border-radius: 8px; background: #f0f7ff; cursor: pointer; transition: all 0.3s;';

        imageInput.addEventListener('mouseenter', function () {
            this.style.borderColor = '#0056b3';
            this.style.background = '#e7f1ff';
        });

        imageInput.addEventListener('mouseleave', function () {
            this.style.borderColor = '#0d6efd';
            this.style.background = '#f0f7ff';
        });
    }
});






