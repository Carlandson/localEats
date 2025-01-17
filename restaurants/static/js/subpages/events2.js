// let business;

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

        try {
            const response = await fetch(`/${business}/events/add/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to create event');
            }

            // Refresh the events list
            location.reload();

        } catch (error) {
            console.error('Error:', error);
            alert(error.message || 'Error creating event. Please try again.');
        }
    });

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
            if (confirm('Are you sure you want to delete this event?')) {
                deleteEvent(business, eventId);
            }
        });
    });
});


async function deleteEvent(business, eventId) {
    if (!confirm('Are you sure you want to delete this event?')) {
        return;
    }

    const eventElement = document.getElementById(`event${eventId}`);
    if (!eventElement) {
        console.error('Could not find event element');
        return;
    }

    // Add loading state with transition
    eventElement.style.transition = 'all 0.3s ease-out';
    eventElement.style.opacity = '0.5';
    const buttons = eventElement.querySelectorAll('button');
    buttons.forEach(button => button.disabled = true);

    try {
        const response = await fetch(`/${business}/events/delete/${eventId}/`, {
            method: 'POST',  
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to delete event');
        }

        const data = await response.json();
        if (data.success) {
            // Animate the removal
            eventElement.style.transform = 'translateX(100%)';
            eventElement.style.opacity = '0';
            
            // Remove element after animation
            setTimeout(() => {
                eventElement.remove();
                
                // Check if this was the last event
                const eventsList = document.getElementById('events-list');
                if (eventsList && eventsList.children.length === 0) {
                    const noEventsMessage = document.getElementById('no-events-message');
                    if (noEventsMessage) {
                        noEventsMessage.classList.remove('hidden');
                    }
                }
            }, 300);
        } else {
            throw new Error(data.error || 'Failed to delete event');
        }

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

    try {
        // Fetch the pre-populated form from Django
        const response = await fetch(`/${business}/events/get-form/${eventId}/`);
        if (!response.ok) {
            throw new Error('Failed to get edit form');
        }
        const data = await response.json();

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
            editDiv.replaceWith(eventElement);
        });

        // Add form submission handler
        const editForm = editDiv.querySelector(`#editEvent${eventId}`);
        editForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(editForm);

            try {
                const response = await fetch(`/${business}/events/edit/${eventId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: formData
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Failed to update event');
                }

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
