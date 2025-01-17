function addEvent() {
    const formContainer = document.getElementById('event-form-container');
    const addButton = document.getElementById('add-event');
    
    // Hide the add button and show the form
    addButton.style.display = 'none';
    formContainer.classList.remove('hidden');
    
    // Add the form HTML
    formContainer.innerHTML = getEventFormHTML();
    document.getElementById('createEvent').addEventListener('submit', handleEventSubmission);

    // Add cancel button handler
    formContainer.querySelector('.cancel-add').addEventListener('click', () => {
        formContainer.classList.add('hidden');
        addButton.style.display = 'block';
    });
}

async function handleEventSubmission(event) {
    event.preventDefault();
    
    const formData = new FormData();
    formData.append('name', document.querySelector('#eventName').value);
    formData.append('datetime', document.querySelector('#eventDateTime').value);
    formData.append('description', document.querySelector('#eventDescription').value);

    // Handle image upload if present
    const imageInput = document.querySelector('#eventImage');
    if (imageInput && imageInput.files[0]) {
        formData.append('image', imageInput.files[0]);
    }

    try {
        const response = await fetch(`/${businessSubdirectory}/events/add/`, {
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

        const result = await response.json();
        
        // Add new event to the list
        const eventsList = document.getElementById('events-list');
        const eventArticle = document.createElement('article');
        eventArticle.id = `event${result.event_id}`;
        eventArticle.className = 'border rounded-lg p-4 bg-white shadow-sm';
        eventArticle.innerHTML = createEventHTML(result);
        
        eventsList.insertBefore(eventArticle, eventsList.firstChild);
        
        // Hide form and show add button
        document.getElementById('event-form-container').classList.add('hidden');
        document.getElementById('add-event').style.display = 'block';
        
        // Hide "no events" message if it was showing
        document.getElementById('no-events-message').classList.add('hidden');

        eventArticle.querySelector('.editEvent').addEventListener('click', () => {
            const eventId = result.event_id;
            editEvent(eventId);
        });

        eventArticle.querySelector('.deleteEvent').addEventListener('click', () => {
            const eventId = result.event_id;
            deleteEvent(eventId);
        });
    } catch (error) {
        console.error('Error:', error);
        alert(error.message || 'Error creating event. Please try again.');
    }
}


function editEvent(eventId) {
    const eventElement = document.getElementById(`event${eventId}`);
    if (!eventElement) {
        console.error('Could not find event element');
        return;
    }

    // Get current event data
    const currentValues = {
        name: eventElement.querySelector('h3').textContent,
        datetime: new Date(eventElement.querySelector('p').textContent.replace('Date: ', '')).toISOString().slice(0, 16),
        image: eventElement.querySelector('img')?.src,
        description: eventElement.querySelector('div:nth-child(2) p').textContent
    };

    // Create edit form
    const editDiv = document.createElement('div');
    editDiv.className = 'p-4';
    editDiv.innerHTML = getEventFormHTML(true, eventId, currentValues);

    // Store the original event element
    editDiv.originalEvent = eventElement;

    // Replace event with form
    eventElement.replaceWith(editDiv);

    // Add cancel button functionality
    editDiv.querySelector('.cancel-edit').addEventListener('click', () => {
        editDiv.replaceWith(eventElement);
    });

    // Add form submission handler
    document.querySelector(`#editEvent${eventId}`).addEventListener('submit', async (event) => {
        event.preventDefault();
        
        const formData = {
            name: document.querySelector(`#eventName${eventId}`).value,
            datetime: document.querySelector(`#eventDateTime${eventId}`).value,
            description: document.querySelector(`#eventDescription${eventId}`).value
        };

        // Handle image upload if present
        const imageInput = document.querySelector(`#eventImage${eventId}`);
        if (imageInput && imageInput.files[0]) {
            formData.image = await handleImageUpload(imageInput);
        }

        fetch(`/${business}/events/edit/${eventId}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(formData)
        })
        .then(async response => {
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Network response was not ok');
            }
            return response.json();
        })
        .then(result => {
            const updatedEvent = document.createElement('article');
            updatedEvent.id = `event${eventId}`;
            updatedEvent.className = 'border rounded-lg p-4 bg-white shadow-sm';
            
            updatedEvent.innerHTML = createEventHTML(eventId, formData, result.image_url);

            editDiv.replaceWith(updatedEvent);
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.message || 'Error updating event. Please try again.');
        });
    });
}

function deleteEvent(eventId) {
    if (!confirm('Are you sure you want to delete this event?')) {
        return;
    }

    const eventElement = document.getElementById(`event${eventId}`);
    if (!eventElement) {
        console.error('Could not find event element');
        return;
    }

    // Add loading state
    eventElement.style.opacity = '0.5';
    const buttons = eventElement.querySelectorAll('button');
    buttons.forEach(button => button.disabled = true);

    fetch(`/${business}/events/delete/${eventId}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(() => {
        // Animate the removal
        eventElement.style.transition = 'all 0.3s ease-out';
        eventElement.style.transform = 'translateX(100%)';
        eventElement.style.opacity = '0';
        
        setTimeout(() => {
            eventElement.remove();
            
            // Check if this was the last event
            const eventsList = document.getElementById('events-list');
            if (eventsList.children.length === 0) {
                document.getElementById('no-events-message').classList.remove('hidden');
            }
        }, 300);
    })
    .catch(error => {
        console.error('Error:', error);
        eventElement.style.opacity = '1';
        buttons.forEach(button => button.disabled = false);
        alert('Error deleting event. Please try again.');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    business = JSON.parse(document.getElementById('business').textContent);
    console.log(business);
    
    document.getElementById('add-event').addEventListener('click', addEvent);

    document.addEventListener('click', function(e) {
        // Add Event button
        if (e.target.matches('#addEvent')) {
            e.preventDefault();
            const submission = document.querySelector('#eventName');
            addEvent(submission.value);
        }

        // Submit Event Details button
        if (e.target.matches('.submitEvent')) {
            addEventDetails(e.target.id);
        }

        // Edit Event button
        if (e.target.matches('.editEvent')) {
            const eventId = e.target.id.replace('e', '');
            editEvent(eventId);
        }

        // Delete Event button
        if (e.target.matches('.deleteEvent')) {
            const eventId = e.target.id.replace('d', '');
            deleteEvent(eventId);
        }

        // Edit Description button
        if (e.target.matches('.editDescription') || e.target.closest('.editDescription')) {
            const button = e.target.closest('.editDescription') || e.target;
            const eventId = button.dataset.eventId;
            editEventDescription(eventId);
        }

        // Save Description button
        if (e.target.matches('.saveDescription')) {
            const eventId = e.target.dataset.eventId;
            saveEventDescription(eventId);
        }
    });
});

const getEventFormHTML = (isEdit = false, eventId = '', currentValues = {}) => `
    <form id="${isEdit ? 'editEvent' + eventId : 'createEvent'}" class="p-1" action="post">
        <div class="form-group">
            <input type="text" 
                   class="p-2 m-1 border-double border-4 border-indigo-200" 
                   placeholder="Event Name" 
                   id="${isEdit ? 'eventName' + eventId : 'eventName'}"
                   value="${isEdit ? currentValues.name : ''}" 
                   required>
            <input type="datetime-local" 
                   class="p-2 m-1 border-double border-4 border-indigo-200" 
                   id="${isEdit ? 'eventDateTime' + eventId : 'eventDateTime'}"
                   value="${isEdit ? currentValues.datetime : ''}" 
                   required>
            <div class="image-upload-container">
                <input type="file" 
                       class="p-2 m-1 border-double border-4 border-indigo-200" 
                       accept="image/*"
                       id="${isEdit ? 'eventImage' + eventId : 'eventImage'}">
                ${isEdit && currentValues.image ? `
                    <div class="current-image">
                        <img src="${currentValues.image}" class="h-20 w-20 object-contain" alt="Current image">
                        <p class="text-sm text-gray-500">Current image</p>
                    </div>
                ` : ''}
            </div>
            <textarea class="form-control p-2 m-1" 
                      id="${isEdit ? 'eventDescription' + eventId : 'eventDescription'}" 
                      rows="3" 
                      placeholder="Description">${isEdit ? currentValues.description : ''}</textarea>
        </div>
        <button type="submit" class="bg-blue-500 m-2 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            ${isEdit ? 'Save Changes' : 'Add Event'}
        </button>
        <button type="button" 
                class="${isEdit ? 'cancel-edit' : 'cancel-add'} bg-gray-500 m-2 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">
            Cancel
        </button>
    </form>
`;

function createEventHTML(eventId, formData, imageUrl = null) {
    return `
        <div class="text-center">
            <h3 class="text-xl font-bold mb-2">${formData.name}</h3>
            ${imageUrl ? 
                `<img src="${imageUrl}" class="mx-auto object-contain h-40 w-40" alt="${formData.name}">` :
                `<div class="h-40 w-40 mx-auto flex items-center justify-center bg-gray-100 rounded-lg border-2 border-dashed border-gray-300">
                    <span class="text-gray-400">No Image</span>
                </div>`
            }
            <p class="mt-2 font-semibold">Date: ${new Date(formData.datetime).toLocaleString()}</p>
        </div>
        <div class="text-center">
            <h4 class="font-semibold mb-2">Description:</h4>
            <p>${formData.description}</p>
        </div>
        <div class="md:text-right flex md:justify-end items-center space-x-2">
            <button class="editEvent px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded transition-colors duration-200" 
                    id="e${eventId}">Edit</button>
            <button class="deleteEvent px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded transition-colors duration-200" 
                    id="d${eventId}">Delete</button>
        </div>
    `;
}