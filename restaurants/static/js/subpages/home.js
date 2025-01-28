import { showToast } from '../components/toast.js';
import { makeRequest } from '../utils/subpagesAPI.js';

document.addEventListener('DOMContentLoaded', function() {
    const business = JSON.parse(document.getElementById('business').textContent);
    // Accordion functionality
    const accordionHeaders = document.querySelectorAll('.accordion-header');
    
    accordionHeaders.forEach(header => {
        header.addEventListener('click', function(e) {
            // Don't trigger accordion if clicking the toggle switch
            if (e.target.type === 'checkbox' || e.target.closest('.relative')) {
                return;
            }
            
            const targetId = this.dataset.target;
            const content = document.getElementById(targetId);
            const icon = this.querySelector('.accordion-icon');
            const isExpanded = this.dataset.expanded === 'true';
            
            // Toggle content visibility
            content.classList.toggle('hidden');
            
            // Update expanded state and rotate icon
            this.dataset.expanded = (!isExpanded).toString();
            icon.style.transform = isExpanded ? 'rotate(0deg)' : 'rotate(180deg)';
        });
    });

    // Toggle switch functionality
    const toggles = document.querySelectorAll('input[type="checkbox"]');
    
    toggles.forEach(toggle => {
        toggle.addEventListener('change', async function() {
            const section = this.name;
            const isEnabled = this.checked;            
            const contentDiv = document.querySelector(`[data-section="${section}"]`);
            
            try {
                // Show loading state
                this.disabled = true;

                if (contentDiv) {
                    contentDiv.classList.toggle('hidden', !isEnabled);
                }
                // Get CSRF token
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                // Send update to server
                const response = await fetch(`/${business}/home/settings/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        fieldType: 'boolean',
                        fieldName: section,
                        value: isEnabled,
                        page_type: 'home'
                    })
                });

                if (!response.ok) throw new Error('Update failed');

                // Show success message
                showToast('Changes saved successfully!');
                
            } catch (error) {
                console.error('Update failed:', error);
                // Revert the toggle if the update failed
                this.checked = !this.checked;
                showNotification('Failed to update setting. Please try again.', 'error');
                if (contentDiv) {
                    contentDiv.style.opacity = isEnabled ? '0' : '1';
                    contentDiv.style.height = isEnabled ? '0' : 'auto';
                    contentDiv.style.visibility = isEnabled ? 'hidden' : 'visible';
                }
            } finally {
                this.disabled = false;
            }
        });
    });

    const saveButtons = document.querySelectorAll('.save-button');
    saveButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const section = this.dataset.section;
            const container = this.closest('div');
            const originalText = this.textContent;
            try {
                // Show loading state
                this.textContent = 'Saving...';
                this.disabled = true;
                
                // Get CSRF token
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                // Prepare the data based on section
                let data = {
                    fieldName: section
                };
                
                // Add section-specific data
                if (section === 'show_welcome') {
                    const titleInput = container.querySelector('[name="welcome_title"]');
                    const messageInput = container.querySelector('[name="welcome_message"]');
                    data = {
                        ...data,
                        welcome_title: titleInput.value,
                        welcome_message: messageInput.value
                    };
                }
                
                // Send update to server
                const response = await fetch(`/${business}/home/settings/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(data)
                });
    
                if (!response.ok) throw new Error('Update failed');
    
                // Show success message using the toast
                showToast('Changes saved successfully!');
                
            } catch (error) {
                console.error('Save failed:', error);
                showToast('Failed to save changes. Please try again.');
            } finally {
                // Reset button state
                this.textContent = originalText;
                this.disabled = false;
            }
        });
    });
    document.getElementById('id_image').addEventListener('change', function(e) {
        const previewContainer = document.getElementById('image-preview-container');
        const preview = document.getElementById('image-preview');
        const file = e.target.files[0];
    
        if (file) {
            // Show the preview container
            previewContainer.classList.remove('hidden');
            
            // Create a URL for the file
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
            };
            reader.readAsDataURL(file);
        } else {
            // Hide the preview container if no file is selected
            previewContainer.classList.add('hidden');
            preview.src = '';
        }
    });
    // Remove image functionality
    document.getElementById('remove-image').addEventListener('click', function() {
        const imageInput = document.getElementById('id_image');
        const previewContainer = document.getElementById('image-preview-container');
        const preview = document.getElementById('image-preview');
        
        // Clear the file input
        imageInput.value = '';
        
        // Hide the preview
        previewContainer.classList.add('hidden');
        preview.src = '';
    });
    // Update your existing save-news-post event listener to handle the case when image is removed
    document.getElementById('save-news-post').addEventListener('click', async function() {
        const formData = new FormData();
        formData.append('title', document.getElementById('id_title').value);
        formData.append('content', document.getElementById('id_content').value);
        
        const imageInput = document.getElementById('id_image');
        if (imageInput.files.length > 0) {
            formData.append('image', imageInput.files[0]);
        }

        try {
            const response = await fetch(`/api/${business}/news-post/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                body: formData
            });

            const data = await response.json();
            if (response.ok) {
                showToast('News post created successfully!', 'success');
                // Clear the form and preview
                document.getElementById('id_title').value = '';
                document.getElementById('id_content').value = '';
                imageInput.value = '';
                document.getElementById('image-preview-container').classList.add('hidden');
                document.getElementById('image-preview').src = '';
            } else {
                showToast(data.message || 'Error creating news post', 'error');
            }
        } catch (error) {
            showToast('Error creating news post', 'error');
            console.error('Error:', error);
        }
    });
});

// Notification helper function
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 left-5 p-4 rounded-lg shadow-lg ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } text-white`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

