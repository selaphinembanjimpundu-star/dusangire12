// Cart functionality JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Update cart item quantity
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                // Show loading state
                this.disabled = true;
                form.submit();
            }
        });
    });
    
    // Add to cart with AJAX (optional enhancement)
    const addToCartForms = document.querySelectorAll('form[action*="add_to_cart"]');
    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Allow normal form submission for now
            // Can be enhanced with AJAX later
        });
    });
    
    // Remove from cart confirmation
    const removeButtons = document.querySelectorAll('button[type="submit"][onclick*="confirm"]');
    removeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Remove this item from cart?')) {
                e.preventDefault();
            }
        });
    });
});

// Update cart count in navbar (if using AJAX)
function updateCartCount(count) {
    const cartBadge = document.querySelector('.nav-link[href*="cart"] .badge');
    if (cartBadge) {
        if (count > 0) {
            cartBadge.textContent = count;
            cartBadge.style.display = 'inline-block';
        } else {
            cartBadge.style.display = 'none';
        }
    }
}




















