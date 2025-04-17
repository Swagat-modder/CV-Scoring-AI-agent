// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Enhanced file input for the upload form
    const fileInput = document.getElementById('resume-file');
    const fileLabel = document.querySelector('.custom-file-label');
    
    if (fileInput && fileLabel) {
        fileInput.addEventListener('change', function() {
            let fileName = '';
            if (this.files && this.files.length > 1) {
                fileName = (this.getAttribute('data-multiple-caption') || '').replace('{count}', this.files.length);
            } else {
                fileName = this.files[0].name;
            }
            
            if (fileName) {
                fileLabel.textContent = fileName;
            } else {
                fileLabel.textContent = 'Choose file...';
            }
        });
    }

    // Drag and drop functionality for uploads
    const uploadArea = document.querySelector('.upload-area');
    
    if (uploadArea && fileInput) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            uploadArea.classList.add('drag-over');
        }
        
        function unhighlight() {
            uploadArea.classList.remove('drag-over');
        }
        
        uploadArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            fileInput.files = files;
            
            // Trigger change event
            const event = new Event('change');
            fileInput.dispatchEvent(event);
        }
    }

    // Confirmation dialogs for delete actions
    const deleteButtons = document.querySelectorAll('.delete-resume-btn');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this resume? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Job description text area auto-resize
    const jobDescTextarea = document.getElementById('job-description');
    
    if (jobDescTextarea) {
        jobDescTextarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }

    // Toggle feedback details
    const toggleButtons = document.querySelectorAll('.toggle-feedback');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const feedbackId = this.getAttribute('data-target');
            const feedbackElement = document.getElementById(feedbackId);
            
            if (feedbackElement) {
                if (feedbackElement.classList.contains('d-none')) {
                    feedbackElement.classList.remove('d-none');
                    this.textContent = 'Hide Feedback';
                } else {
                    feedbackElement.classList.add('d-none');
                    this.textContent = 'Show Feedback';
                }
            }
        });
    });
});
