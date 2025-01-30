import { showToast } from '../components/toast.js';
import { api } from '../utils/subpagesAPI.js';
import { createServiceFormHTML } from '../utils/placeholders.js';

document.addEventListener('DOMContentLoaded', function() {
    const business = JSON.parse(document.getElementById('business').textContent);
    const formContainer = document.getElementById('service-form-container');
    const addButton = document.getElementById('add-service');
    const descriptionButton = document.getElementById('toggle-description-edit');
    const descriptionForm = document.getElementById('description-form');
    const descriptionDisplay = document.getElementById('description-display');

    descriptionButton?.addEventListener('click', () => {
        const descriptionHidden = descriptionForm.classList.contains('hidden');
        
        if (descriptionHidden) {
            // Show form, hide display
            descriptionForm.classList.remove('hidden');
            descriptionDisplay.classList.add('hidden');
            descriptionButton.textContent = 'Cancel';
            // Change button style to indicate cancel action
            descriptionButton.classList.remove('bg-indigo-600', 'hover:bg-indigo-700');
            descriptionButton.classList.add('bg-gray-500', 'hover:bg-gray-600');
        } else {
            // Hide form, show display
            descriptionForm.classList.add('hidden');
            descriptionDisplay.classList.remove('hidden');
            descriptionButton.textContent = 'Edit Description';
            // Restore original button style
            descriptionButton.classList.remove('bg-gray-500', 'hover:bg-gray-600');
            descriptionButton.classList.add('bg-indigo-600', 'hover:bg-indigo-700');
            // Optional: Reset form
            const form = descriptionForm.querySelector('form');
            if (form) form.reset();
        }
    });
    // Show/hide form handlers
    addButton?.addEventListener('click', () => {
        const isHidden = formContainer.classList.contains('hidden');
        
        if (isHidden) {
            // Show form
            formContainer.classList.remove('hidden');
            addButton.textContent = 'Cancel';
            addButton.classList.remove('bg-emerald-500', 'hover:bg-emerald-600');
            addButton.classList.add('bg-gray-500', 'hover:bg-gray-600');
        } else {
            formContainer.classList.add('hidden');
            addButton.textContent = 'Add New Service';
            addButton.classList.remove('bg-gray-500', 'hover:bg-gray-600');
            addButton.classList.add('bg-emerald-500', 'hover:bg-emerald-600');
            const form = formContainer.querySelector('form');
            if (form) form.reset();
        }
    });

    document.querySelector('.cancel-add')?.addEventListener('click', () => {
        formContainer.classList.add('hidden');
        addButton.style.display = 'block';
        document.getElementById('createService').reset();
    });

    document.querySelector('[data-section="save-description"]')?.addEventListener('click', async () => {
        const descriptionInput = document.getElementById('id_description');
        const descriptionText = descriptionInput.value;

        try {
            await api.services.updateSettings(business, {
                fieldName: 'description',
                description: descriptionText  // Send the actual text value
            });
            
            // Update the displayed description
            const descriptionDisplay = document.getElementById('description-display');
            descriptionDisplay.innerHTML = descriptionText 
                ? descriptionText.replace(/\n/g, '<br>') 
                : '<p class="text-gray-500 italic">No description added yet.</p>';

            // Hide form, show display
            descriptionForm.classList.add('hidden');
            descriptionDisplay.classList.remove('hidden');
            
            // Reset button
            descriptionButton.textContent = 'Edit Description';
            descriptionButton.classList.remove('bg-gray-500', 'hover:bg-gray-600');
            descriptionButton.classList.add('bg-indigo-600', 'hover:bg-indigo-700');

            showToast('Changes saved successfully!');
        } catch (error) {
            console.error('Error:', error);
            showToast('Failed to update setting. Please try again.', 'error');
        }
    });

    // Form submission
    document.getElementById('createService')?.addEventListener('submit', async (event) => {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        
        const errorDisplay = document.getElementById('form-error-message');
        errorDisplay.textContent = '';
        errorDisplay.classList.add('hidden');
    
        try {
            const response = await api.services.createService(business, formData);
            
            if (response.success) {
                showToast('Service created successfully!');
                // Success - refresh the services list
                location.reload();
            }
    
        } catch (error) {
            console.error('Error:', error);
            errorDisplay.textContent = error.message || 'An unexpected error occurred. Please try again.';
            errorDisplay.classList.remove('hidden');
        }
    });

    // Edit/Delete handlers
    document.querySelectorAll('.editService').forEach(button => {
        button.addEventListener('click', () => {
            const serviceId = button.id.substring(1);
            editService(business, serviceId);
        });
    });

    document.querySelectorAll('.deleteService').forEach(button => {
        button.addEventListener('click', () => {
            const serviceId = button.id.substring(1);
            deleteService(business, serviceId);
        });
    });
});

async function deleteService(business, serviceId) {
    if (!confirm('Are you sure you want to delete this service?')) {
        return;
    }

    const serviceElement = document.getElementById(`service${serviceId}`);
    if (!serviceElement) {
        console.error('Could not find service element');
        return;
    }

    // Add loading state with transition
    serviceElement.style.transition = 'all 0.3s ease-out';
    serviceElement.style.opacity = '0.5';
    const buttons = serviceElement.querySelectorAll('button');
    buttons.forEach(button => button.disabled = true);

    try {
        const response = await api.services.deleteService(business, serviceId);

        if (!response.success) {
            throw new Error(response.error || 'Failed to delete service');
        }

        if (response.success) {
            // Animate the removal
            serviceElement.style.transform = 'translateX(100%)';
            serviceElement.style.opacity = '0';
            
            setTimeout(() => {
                serviceElement.remove();
                
                // Check if this was the last service
                const servicesList = document.getElementById('services-list');
                if (servicesList && servicesList.children.length === 0) {
                    servicesList.innerHTML = '<p class="col-span-3 text-center text-gray-500 py-8">No services added yet.</p>';
                }
            }, 300);
        }

    } catch (error) {
        console.error('Error:', error);
        serviceElement.style.opacity = '1';
        serviceElement.style.transform = 'translateX(0)';
        buttons.forEach(button => button.disabled = false);
        alert(error.message || 'Error deleting service. Please try again.');
    }
}

async function editService(business, serviceId) {
    const serviceElement = document.getElementById(`service${serviceId}`);
    if (!serviceElement) {
        console.error(`Could not find service element for ID: service${serviceId}`);
        return;
    }

    try {
        // Fetch the pre-populated form from Django
        const response = await api.services.getEditForm(business, serviceId);
        
        // Create edit container
        const editDiv = document.createElement('div');
        editDiv.className = 'p-4 bg-white rounded-lg shadow';
        editDiv.innerHTML = response.form_html;
        editDiv.originalService = serviceElement;

        // Replace service with form
        serviceElement.replaceWith(editDiv);

        // Handle image preview
        const imageInput = editDiv.querySelector('input[type="file"]');
        if (imageInput) {
            imageInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        // Find existing preview or create new one
                        let previewDiv = imageInput.closest('.space-y-2').querySelector('.mt-4');
                        if (!previewDiv) {
                            previewDiv = document.createElement('div');
                            previewDiv.className = 'mt-4';
                            imageInput.closest('.space-y-2').appendChild(previewDiv);
                        }
                        
                        previewDiv.innerHTML = `
                            <h4 class="text-sm font-medium text-gray-700 mb-2">Selected Image Preview</h4>
                            <div class="relative">
                                <img src="${e.target.result}" 
                                     alt="Selected image preview" 
                                     class="max-w-full h-auto rounded-lg shadow-sm">
                            </div>
                        `;
                    };
                    reader.readAsDataURL(file);
                }
            });
        }

        // Add cancel button functionality
        editDiv.querySelector('.cancel-edit').addEventListener('click', () => {
            editDiv.replaceWith(serviceElement);
        });
        // Add form submission handler
        const editForm = editDiv.querySelector(`#editService${serviceId}`);
        editForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            try {
                const response = await api.services.updateService(business, serviceId, formData);
                
                if (response.success) {
                    showToast('Service updated successfully!');
                    location.reload();
                }
            } catch (error) {
                console.error('Error updating service:', error);
                showToast('Failed to update service. Please try again.', 'error');
            }
        });

    } catch (error) {
        console.error('Error:', error);
        showToast('Error loading edit form. Please try again.', 'error');
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}