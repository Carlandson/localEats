import { api } from '../utils/subpagesAPI.js';
import { showToast } from '../components/toast.js';

document.addEventListener('DOMContentLoaded', function() {
    const business = JSON.parse(document.getElementById('business').textContent);
    const formContainer = document.getElementById('event-form-container');
    const addButton = document.getElementById('add-event');

    // Show/hide form handlers
    addButton?.addEventListener('click', () => {
        formContainer.classList.remove('hidden');
        addButton.style.display = 'none';
    });

    document.querySelector('.cancel-add')?.addEventListener('click', () => {
        formContainer.classList.add('hidden');
        addButton.style.display = 'block';
        document.getElementById('createEvent').reset();
    });

    // Form submission
    document.getElementById('createEvent')?.addEventListener('submit', async (event) => {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
    
        // Get form values
        const startDate = new Date(formData.get('start_date') + 'T' + formData.get('start_time'));
        const endDate = formData.get('end_date') && formData.get('end_time') ? 
            new Date(formData.get('end_date') + 'T' + formData.get('end_time')) : null;
        
        const errorDisplay = document.getElementById('form-error-message');
        errorDisplay.textContent = '';
        errorDisplay.classList.add('hidden');
    
        // Validate dates
        if (endDate && endDate <= startDate) {
            errorDisplay.textContent = 'End date and time must be after start date and time';
            errorDisplay.classList.remove('hidden');
            return;
        }
    
        try {
            await api.events.create(business, formData);
    
            // Success - refresh the events list
            location.reload();
    
        } catch (error) {
            console.error('Error:', error);
            errorDisplay.textContent = 'An unexpected error occurred. Please try again.';
            errorDisplay.classList.remove('hidden');
        }
    });
    // Image preview for create form (same logic as edit form)
    const createForm = document.getElementById('createEvent');
    const createImageInput = createForm?.querySelector('input[type="file"]');
    if (createImageInput) {
        createImageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Find existing preview or create new one
                    let previewDiv = createForm.querySelector('.image-preview');
                    if (!previewDiv) {
                        previewDiv = document.createElement('div');
                        previewDiv.className = 'image-preview mt-2';
                        createImageInput.parentNode.appendChild(previewDiv);
                    }
                    
                    previewDiv.innerHTML = `
                        <p class="text-sm text-gray-600 mb-2">Image Preview:</p>
                        <img src="${e.target.result}" 
                             alt="Preview" 
                             class="h-32 w-32 object-cover rounded-lg border border-gray-200">
                    `;
                };
                reader.readAsDataURL(file);
            }
        });
    }
    // Edit/Delete handlers
    document.querySelectorAll('.editEvent').forEach(button => {
        button.addEventListener('click', () => {
            const eventId = button.id.substring(1);
            console.log(eventId)
            editEvent(business, eventId);
        });
    });

    document.querySelectorAll('.deleteEvent').forEach(button => {
        button.addEventListener('click', () => {
            const eventId = button.id.substring(1);
            deleteEvent(business, eventId);
        });
    });
});


async function deleteEvent(business, eventId) {

    const confirmed = window.confirm('Are you sure you want to delete this event?');
    if (!confirmed) {
        return; // User cancelled, exit early
    }

    const eventElement = document.getElementById(`event${eventId}`);
    if (!eventElement) {
        console.error(`Could not find event element for ID: event${eventId}`);
        return;
    }
    const originalElementClone = eventElement.cloneNode(true);
    // Add loading state with transition
    eventElement.style.transition = 'all 0.3s ease-out';
    eventElement.style.opacity = '0.5';
    const buttons = eventElement.querySelectorAll('button');
    buttons.forEach(button => button.disabled = true);

    try {
        await api.events.delete(business, eventId);

        // Animate the removal
        eventElement.style.transform = 'translateX(100%)';
        eventElement.style.opacity = '0';
        
        // Remove element after animation
        setTimeout(() => {
            eventElement.remove();
            
            // Check if this was the last event in any list
            const upcomingList = document.getElementById('upcoming-events-list');
            const currentList = document.getElementById('current-events-list');
            const pastList = document.getElementById('past-events-list');
            
            const hasEvents = (upcomingList && upcomingList.children.length > 0) ||
                             (currentList && currentList.children.length > 0) ||
                             (pastList && pastList.children.length > 0);
            
            if (!hasEvents) {
                const noEventsMessage = document.getElementById('no-upcoming-events-message');
                if (noEventsMessage) {
                    noEventsMessage.classList.remove('hidden');
                }
            }
        }, 300);

    } catch (error) {
        console.error('Error:', error);
        // Reset the element state if there's an error
        eventElement.style.transition = 'all 0.3s ease-out';
        eventElement.style.opacity = '1';
        eventElement.style.transform = 'translateX(0)';
        buttons.forEach(button => button.disabled = false);
        alert(error.message || 'Error deleting event. Please try again.');
    }
}

async function editEvent(business, eventId) {
    const eventElement = document.getElementById(`event${eventId}`);
    if (!eventElement) {
        console.error(`Could not find event element for ID: event${eventId}`);
        return;
    }

    const originalElementClone = eventElement.cloneNode(true);

    try {
        // Fetch the pre-populated form from Django
        const data = await api.events.getEditForm(business, eventId);

        // Create edit container
        const editDiv = document.createElement('div');
        editDiv.className = 'p-4';
        editDiv.innerHTML = data.form_html;
        editDiv.originalEvent = eventElement;

        // Replace event with form
        eventElement.replaceWith(editDiv);
        const imageInput = editDiv.querySelector('input[type="file"]');
        if (imageInput) {
            imageInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        // Find existing preview or create new one
                        let previewDiv = editDiv.querySelector('.image-preview');
                        if (!previewDiv) {
                            previewDiv = document.createElement('div');
                            previewDiv.className = 'image-preview mt-2';
                            imageInput.parentNode.appendChild(previewDiv);
                        }
                        
                        previewDiv.innerHTML = `
                            <p class="text-sm text-gray-600 mb-2">New Image Preview:</p>
                            <img src="${e.target.result}" 
                                 alt="Preview" 
                                 class="h-32 w-32 object-cover rounded-lg border border-gray-200">
                        `;
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
        // Add cancel button functionality
        editDiv.querySelector('.cancel-edit').addEventListener('click', () => {
            editDiv.replaceWith(originalElementClone);
        });

        // Add form submission handler
        const editForm = editDiv.querySelector(`#editEvent${eventId}`);
        editForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(editForm);

            try {
                await api.events.update(business, eventId, formData);
                showToast('Event updated successfully!');
                // Refresh the page to show updated event
                location.reload();

            } catch (error) {
                console.error('Error:', error);
                alert(error.message || 'Error updating event. Please try again.');
            }
        });

    } catch (error) {
        console.error('Error:', error);
        alert('Error loading edit form. Please try again.');
    }
}
