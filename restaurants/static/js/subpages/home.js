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
});
