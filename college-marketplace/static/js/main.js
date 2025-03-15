// Main JavaScript file for College Marketplace

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Image preview for file uploads
    const imageInput = document.getElementById('image');
    if (imageInput) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                const imagePreview = document.createElement('img');
                imagePreview.className = 'img-thumbnail mt-2';
                imagePreview.style.maxHeight = '200px';
                
                // Remove any existing preview
                const existingPreview = this.parentElement.querySelector('.img-thumbnail');
                if (existingPreview) {
                    existingPreview.remove();
                }
                
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imageInput.parentElement.appendChild(imagePreview);
                }
                
                reader.readAsDataURL(file);
            }
        });
    }

    // Price formatting
    const priceInput = document.getElementById('price');
    if (priceInput) {
        priceInput.addEventListener('blur', function() {
            if (this.value) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    }

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Search form enhancements
    const searchForm = document.querySelector('form[action="/search"]');
    if (searchForm) {
        const categorySelect = searchForm.querySelector('#category_id');
        const typeSelect = searchForm.querySelector('#listing_type');
        
        // Auto-submit on select change
        if (categorySelect) {
            categorySelect.addEventListener('change', function() {
                searchForm.submit();
            });
        }
        
        if (typeSelect) {
            typeSelect.addEventListener('change', function() {
                searchForm.submit();
            });
        }
    }

    // Listing card hover effects
    const listingCards = document.querySelectorAll('.card');
    listingCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('shadow');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('shadow');
        });
    });

    // Message character counter
    const messageTextarea = document.getElementById('message');
    if (messageTextarea) {
        const maxLength = 500;
        const counterElement = document.createElement('small');
        counterElement.className = 'text-muted d-block text-end';
        counterElement.textContent = `0/${maxLength} characters`;
        
        messageTextarea.parentElement.appendChild(counterElement);
        
        messageTextarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            counterElement.textContent = `${currentLength}/${maxLength} characters`;
            
            if (currentLength > maxLength) {
                counterElement.classList.add('text-danger');
                this.value = this.value.substring(0, maxLength);
            } else {
                counterElement.classList.remove('text-danger');
            }
        });
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});
