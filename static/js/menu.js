// Menu filtering and search functionality

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('id_search');
    const filterForm = document.getElementById('filter-form');
    const categorySelect = document.getElementById('id_category');
    const dietaryCheckboxes = document.querySelectorAll('input[name="dietary_tags"]');
    
    // Auto-submit form on category change
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            // Don't auto-submit, let user click Apply Filters
            // filterForm.submit();
        });
    }
    
    // Real-time search (optional - debounced)
    let searchTimeout;
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            // Uncomment below for auto-search as you type (with 500ms delay)
            // searchTimeout = setTimeout(function() {
            //     filterForm.submit();
            // }, 500);
        });
    }
    
    // Highlight active filters
    const urlParams = new URLSearchParams(window.location.search);
    const activeCategory = urlParams.get('category');
    const activeTags = urlParams.getAll('dietary_tags');
    const searchQuery = urlParams.get('search');
    
    if (activeCategory) {
        categorySelect.value = activeCategory;
    }
    
    if (activeTags.length > 0) {
        activeTags.forEach(tagId => {
            const checkbox = document.getElementById('tag_' + tagId);
            if (checkbox) {
                checkbox.checked = true;
            }
        });
    }
    
    if (searchQuery) {
        searchInput.value = searchQuery;
    }
    
    // Show filter count badge
    updateFilterCount();
    
    // Update filter count when filters change
    filterForm.addEventListener('change', function() {
        updateFilterCount();
    });
    
    function updateFilterCount() {
        let count = 0;
        if (searchInput && searchInput.value) count++;
        if (categorySelect && categorySelect.value) count++;
        dietaryCheckboxes.forEach(cb => {
            if (cb.checked) count++;
        });
        const minPrice = document.getElementById('id_min_price');
        const maxPrice = document.getElementById('id_max_price');
        if (minPrice && minPrice.value) count++;
        if (maxPrice && maxPrice.value) count++;
        
        // You can add a badge here to show active filter count
        // console.log('Active filters:', count);
    }
    
    // Smooth scroll to results after filter
    if (urlParams.toString()) {
        const menuSection = document.querySelector('.col-lg-9');
        if (menuSection) {
            menuSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
});

// Price range validation
document.addEventListener('DOMContentLoaded', function() {
    const minPrice = document.getElementById('id_min_price');
    const maxPrice = document.getElementById('id_max_price');
    
    if (minPrice && maxPrice) {
        const validatePriceRange = function() {
            const min = parseFloat(minPrice.value);
            const max = parseFloat(maxPrice.value);
            
            if (min && max && min > max) {
                maxPrice.setCustomValidity('Maximum price must be greater than minimum price');
            } else {
                maxPrice.setCustomValidity('');
            }
        };
        
        minPrice.addEventListener('change', validatePriceRange);
        maxPrice.addEventListener('change', validatePriceRange);
    }
});







