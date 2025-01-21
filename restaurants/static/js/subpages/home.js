import { showToast } from '../components/toast.js';

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
            
            // Toggle content visibility
            content.classList.toggle('hidden');
            
            // Rotate icon
            if (content.classList.contains('hidden')) {
                icon.style.transform = 'rotate(0deg)';
            } else {
                icon.style.transform = 'rotate(180deg)';
            }
        });
    });

    // Toggle switch functionality
    const toggles = document.querySelectorAll('input[type="checkbox"]');
    
    toggles.forEach(toggle => {
        toggle.addEventListener('change', async function() {
            const section = this.name;
            const isEnabled = this.checked;
            
            try {
                // Show loading state
                this.disabled = true;
                
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