/**
 * Lazy Loading for Images
 * Improves page load performance by loading images only when they're about to enter the viewport
 */

(function() {
    'use strict';

    // Check if IntersectionObserver is supported
    if ('IntersectionObserver' in window) {
        // Create observer
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    
                    // Check if image has data-src attribute (lazy loading)
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.classList.add('loaded');
                        img.removeAttribute('data-src');
                    }
                    
                    // Check if image has data-srcset attribute
                    if (img.dataset.srcset) {
                        img.srcset = img.dataset.srcset;
                        img.removeAttribute('data-srcset');
                    }
                    
                    // Stop observing this image
                    observer.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px' // Start loading 50px before image enters viewport
        });

        // Observe all images with loading="lazy" or data-src
        document.addEventListener('DOMContentLoaded', function() {
            const lazyImages = document.querySelectorAll('img[loading="lazy"], img[data-src]');
            lazyImages.forEach(img => {
                imageObserver.observe(img);
            });
        });

        // Also observe dynamically added images
        const originalAppendChild = Node.prototype.appendChild;
        Node.prototype.appendChild = function(child) {
            if (child.tagName === 'IMG' && (child.hasAttribute('loading') || child.hasAttribute('data-src'))) {
                imageObserver.observe(child);
            }
            return originalAppendChild.call(this, child);
        };
    } else {
        // Fallback for browsers without IntersectionObserver
        document.addEventListener('DOMContentLoaded', function() {
            const lazyImages = document.querySelectorAll('img[data-src]');
            lazyImages.forEach(img => {
                img.src = img.dataset.src;
                if (img.dataset.srcset) {
                    img.srcset = img.dataset.srcset;
                }
                img.classList.add('loaded');
            });
        });
    }
})();

