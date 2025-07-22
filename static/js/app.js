document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.querySelector('.browse-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const uploadForm = document.querySelector('.upload-form');

    // File upload handling
    if (uploadArea && fileInput) {
        // Click to browse
        uploadArea.addEventListener('click', () => fileInput.click());
        browseBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });

        // Drag and drop functionality
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);

        // File input change
        fileInput.addEventListener('change', handleFileSelect);
    }

    // Form submission handling
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleFormSubmit);
    }

    function handleDragOver(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    }

    function handleDragLeave(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    }

    function handleDrop(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            displaySelectedFile(files[0]);
        }
    }

    function handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            displaySelectedFile(file);
        }
    }

    function displaySelectedFile(file) {
        // Validate file type
        const allowedTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif'];
        if (!allowedTypes.includes(file.type)) {
            showError('Please select a valid image file (PNG, JPG, JPEG, or GIF).');
            return;
        }

        // Validate file size (16MB max)
        const maxSize = 16 * 1024 * 1024;
        if (file.size > maxSize) {
            showError('File size must be less than 16MB.');
            return;
        }

        // Update upload area to show selected file
        const uploadIcon = uploadArea.querySelector('.upload-icon');
        const uploadText = uploadArea.querySelector('h3');
        const uploadDescription = uploadArea.querySelector('p');
        
        // Create preview
        const reader = new FileReader();
        reader.onload = function(e) {
            uploadIcon.innerHTML = `<img src="${e.target.result}" alt="Selected Image" style="width: 100px; height: 100px; object-fit: cover; border-radius: 10px;">`;
            uploadText.textContent = 'Image Selected';
            uploadDescription.textContent = `${file.name} (${formatFileSize(file.size)})`;
        };
        reader.readAsDataURL(file);

        // Enable analyze button
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.style.opacity = '1';
        }
    }

    function handleFormSubmit(e) {
        // Show loading state
        if (analyzeBtn) {
            const originalText = analyzeBtn.innerHTML;
            analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            analyzeBtn.disabled = true;
            
            // Add loading class to form
            uploadForm.classList.add('loading');
        }
    }

    function showError(message) {
        // Create or update error message
        let errorDiv = document.querySelector('.error-message');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.style.cssText = `
                background: #fee;
                color: #c53030;
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
                border: 1px solid #feb2b2;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            `;
            uploadArea.parentNode.insertBefore(errorDiv, uploadArea);
        }
        
        errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Form validation
    function validateForm() {
        const requiredFields = document.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.style.borderColor = '#e53e3e';
                isValid = false;
            } else {
                field.style.borderColor = '#ddd';
            }
        });

        return isValid;
    }

    // Real-time validation
    const formInputs = document.querySelectorAll('input, select, textarea');
    formInputs.forEach(input => {
        input.addEventListener('blur', validateForm);
        input.addEventListener('input', function() {
            this.style.borderColor = '#ddd';
        });
    });

    // Age validation
    const ageInput = document.getElementById('age');
    if (ageInput) {
        ageInput.addEventListener('input', function() {
            const age = parseInt(this.value);
            if (age < 13 || age > 100) {
                this.style.borderColor = '#e53e3e';
                showError('Age must be between 13 and 100 years.');
            } else {
                this.style.borderColor = '#ddd';
            }
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Results page specific functionality
    if (window.location.pathname.includes('results')) {
        // Add animation to results cards
        const cards = document.querySelectorAll('.measurement-card, .meal-card, .day-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'all 0.6s ease';
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });

        // Image modal functionality
        const analysisImage = document.getElementById('analyzed-image');
        if (analysisImage) {
            analysisImage.addEventListener('click', function() {
                openImageModal(this.src);
            });
        }
    }

    function openImageModal(imageSrc) {
        // Create modal
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            cursor: pointer;
        `;

        const img = document.createElement('img');
        img.src = imageSrc;
        img.style.cssText = `
            max-width: 90%;
            max-height: 90%;
            object-fit: contain;
            border-radius: 10px;
        `;

        modal.appendChild(img);
        document.body.appendChild(modal);

        // Close modal on click
        modal.addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        // Close modal on escape key
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                document.body.removeChild(modal);
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);
    }

    // Utility functions for results page
    window.printResults = function() {
        window.print();
    };

    window.downloadResults = function() {
        // This would require additional implementation
        // For now, we'll show a message
        alert('PDF download feature is coming soon! Please use the print function for now.');
    };

    // Progressive Web App features
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + U to focus upload area
        if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
            e.preventDefault();
            if (fileInput) {
                fileInput.click();
            }
        }
        
        // Ctrl/Cmd + Enter to submit form
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            if (uploadForm && validateForm()) {
                uploadForm.submit();
            }
        }
    });

    // Accessibility improvements
    function addAccessibilityFeatures() {
        // Add skip links
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.textContent = 'Skip to main content';
        skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: #000;
            color: #fff;
            padding: 8px;
            text-decoration: none;
            border-radius: 4px;
            z-index: 10000;
        `;
        skipLink.addEventListener('focus', () => {
            skipLink.style.top = '6px';
        });
        skipLink.addEventListener('blur', () => {
            skipLink.style.top = '-40px';
        });
        document.body.insertBefore(skipLink, document.body.firstChild);

        // Add main content landmark
        const mainContent = document.querySelector('.main-content, .results-content');
        if (mainContent) {
            mainContent.setAttribute('id', 'main-content');
            mainContent.setAttribute('role', 'main');
        }

        // Improve form accessibility
        const formGroups = document.querySelectorAll('.form-group');
        formGroups.forEach(group => {
            const label = group.querySelector('label');
            const input = group.querySelector('input, select, textarea');
            if (label && input && !input.getAttribute('id')) {
                const id = 'field_' + Math.random().toString(36).substr(2, 9);
                input.setAttribute('id', id);
                label.setAttribute('for', id);
            }
        });
    }

    // Initialize accessibility features
    addAccessibilityFeatures();

    // Performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', () => {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log(`Page load time: ${perfData.loadEventEnd - perfData.loadEventStart}ms`);
        });
    }

    // Error tracking
    window.addEventListener('error', (e) => {
        console.error('JavaScript error:', e.error);
        // In production, you might want to send this to an error tracking service
    });

    // Unhandled promise rejection tracking
    window.addEventListener('unhandledrejection', (e) => {
        console.error('Unhandled promise rejection:', e.reason);
        // In production, you might want to send this to an error tracking service
    });
});
