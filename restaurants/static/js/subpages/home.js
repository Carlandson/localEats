import { showToast } from '../components/toast.js';
import { api } from '../utils/subpagesAPI.js';


document.addEventListener('DOMContentLoaded', function() {
    const business = JSON.parse(document.getElementById('business').textContent);
    const toggleWelcomeBtn = document.getElementById('toggle-welcome-edit');
    const saveWelcomeBtn = document.getElementById('save-welcome-button');
    const welcomeContentDisplay = document.getElementById('welcome-content-display');
    const welcomeFormContainer = document.getElementById('welcome-form-container');
    const accordionHeaders = document.querySelectorAll('.accordion-header');
    const welcomeContent = document.getElementById('welcome-content');
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
                // Send update to server
                await api.home.toggleSection(business, {
                    fieldName: section,
                    value: isEnabled
                });

                // Show success message
                showToast(`${section} has been ${isEnabled ? 'enabled' : 'disabled'} successfully!`);
                
            } catch (error) {
                console.error('Update failed:', error);
                showToast(`Failed to update ${section}. Please try again. test`);
            } finally {
                this.disabled = false;
            }
        });
    });
    // Welcome section functionality
    if (toggleWelcomeBtn) {
        toggleWelcomeBtn.onclick = () => {
            welcomeContentDisplay.classList.toggle('hidden');
            welcomeFormContainer.classList.toggle('hidden');
            saveWelcomeBtn.classList.toggle('hidden');
        };
    }
    saveWelcomeBtn.onclick = async () => {
        const titleInput = welcomeFormContainer.querySelector('[name="welcome_title"]');
        const welcomeMessageInput = welcomeFormContainer.querySelector('[name="welcome_message"]');
        try {
            this.disabled = true;
            await api.home.updateSettings(business, {
                fieldName: 'show_welcome',
                welcome_title: titleInput.value,
                welcome_message: welcomeMessageInput.value
            });
            showToast('Welcome section has been saved successfully!');
                            //update the display
            welcomeContentDisplay.innerHTML = `
                <h2 class="text-xl font-semibold">${titleInput.value}</h2>
                <p class="text-gray-600">${welcomeMessageInput.value}</p>
            `;
            welcomeContentDisplay.classList.toggle('hidden');
            welcomeFormContainer.classList.toggle('hidden');
            saveWelcomeBtn.classList.toggle('hidden');
        } catch (error) {
            console.error('Save failed:', error);
            showToast('Failed to save welcome section. Please try again.');
        } finally {
            this.disabled = false;
        }
    };
    // image preview, use gallery for reference
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
