import { showToast } from '../components/toast.js';
import { api } from '../utils/subpagesAPI.js';


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

                await api.contact.toggleSection(business, {
                    fieldName: section,
                    value: isEnabled
                });

                showToast('Changes saved successfully!');
                
            } catch (error) {
                console.error('Update failed:', error);
                // Revert the toggle if the update failed
                this.checked = !this.checked;
                if (contentDiv) {
                    contentDiv.classList.toggle('hidden', !this.checked);
                }
                showToast('Failed to update setting. Please try again.', 'error');
            } finally {
                this.disabled = false;
            }
        });
    });

    // Description save functionality
    const saveDescription = document.querySelector('[data-section="save-description"]');

    if (saveDescription) {
        saveDescription.addEventListener('click', async function() {
            const descriptionInput = document.getElementById('id_description');
            const originalText = this.textContent;

            try {
                this.textContent = 'Saving...';
                this.disabled = true;

                await api.contact.updateSettings(business, {
                    fieldName: 'description',
                    description: descriptionInput.value
                });

                showToast('Description saved successfully!');
            } catch (error) {
                console.error('Save failed:', error);
                showToast('Failed to save description. Please try again.', 'error');
            } finally {
                this.textContent = originalText;
                this.disabled = false;
            }
        });
    }
});