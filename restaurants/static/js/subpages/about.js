import { showToast } from '../components/toast.js';
// do we need this? convert if needed
import { makeRequest } from '../utils/subpagesAPI.js';
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
                
                await api.aboutUs.toggleSection(business, {
                    fieldName: section,
                    value: isEnabled
                });
                
                // Change this to a temporary message that doesn't interrupt the user
                showToast(`${section} has been ${isEnabled ? 'enabled' : 'disabled'} successfully!`);
                
            } catch (error) {
                console.error('Update failed:', error);
                // Revert the toggle if the update failed
                this.checked = !this.checked;
                showToast('Failed to update setting. Please try again.', 'error');
                if (contentDiv) {
                    contentDiv.classList.toggle('hidden', !this.checked);
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
                
                // Prepare the data based on section
                let data = {
                    fieldName: section
                };
                
                // Add section-specific data
                switch(section) {
                    case 'content':
                        data = {
                            ...data,
                            content: container.querySelector('[name="content"]').value
                        };
                        break;
                    case 'history':
                        data = {
                            ...data,
                            history: container.querySelector('[name="history"]').value
                        };
                        break;
                    case 'team_members':
                        data = {
                            ...data,
                            team_members: container.querySelector('[name="team_members"]').value
                        };
                        break;
                    case 'mission_values':
                        const missionInput = container.querySelector('[name="mission_statement"]');
                        const valuesInput = container.querySelector('[name="core_values"]');
                        data = {
                            ...data,
                            mission_statement: missionInput?.value || '',
                            core_values: valuesInput?.value || ''
                        };
                        break;
                }
                console.log("data", data);
                
                await api.aboutUs.updateSettings(business, data);

                showToast(`${section} has been saved successfully!`);
                
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

    // Image preview functionality
    document.getElementById('id_image')?.addEventListener('change', function(e) {
        const previewContainer = document.getElementById('image-preview-container');
        const preview = document.getElementById('image-preview');
        const file = e.target.files[0];
    
        if (file) {
            previewContainer?.classList.remove('hidden');
            const reader = new FileReader();
            reader.onload = function(e) {
                if (preview) preview.src = e.target.result;
            };
            reader.readAsDataURL(file);
        } else {
            previewContainer?.classList.add('hidden');
            if (preview) preview.src = '';
        }
    });
});