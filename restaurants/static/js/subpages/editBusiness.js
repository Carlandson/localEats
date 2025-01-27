document.addEventListener('DOMContentLoaded', function() {
    const business = JSON.parse(document.getElementById('business').textContent);
    console.log(business)
    document.querySelectorAll('.edit-button').forEach(button => {
        button.addEventListener('click', function() {
            const displayWrapper = this.closest('.field-display-wrapper');
            const editWrapper = displayWrapper.nextElementSibling;
            
            displayWrapper.classList.add('hidden');
            editWrapper.classList.remove('hidden');
        });
    });

    // Add click handlers for all save buttons
    document.querySelectorAll('.save-button').forEach(button => {
        button.addEventListener('click', async function() {
            const editWrapper = this.closest('.field-edit-wrapper');
            const displayWrapper = editWrapper.previousElementSibling;
            const field = displayWrapper.querySelector('[data-field]').getAttribute('data-field');
            
            await saveField(field, business);
        });
    });

    // Add click handlers for all cancel buttons
    document.querySelectorAll('.cancel-button').forEach(button => {
        button.addEventListener('click', function() {
            const editWrapper = this.closest('.field-edit-wrapper');
            const displayWrapper = editWrapper.previousElementSibling;
            
            editWrapper.classList.add('hidden');
            displayWrapper.classList.remove('hidden');
        });
    });
    const addressEditButton = document.querySelector('[data-field="address"] .edit-button');
    if (addressEditButton) {
        addressEditButton.addEventListener('click', function() {
            setTimeout(initializeAddressField, 100); // Short delay to ensure DOM is ready
        });
    }
});

async function saveField(fieldName) {
    const form = document.querySelector('form');
    const formData = new FormData();
    const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;
    formData.append('csrfmiddlewaretoken', csrfToken);
  
    // Only send the specific field data
    formData.append('field_name', fieldName);
    formData.append(fieldName, form.querySelector(`[name="${fieldName}"]`).value);
    
    try {
        const response = await fetch('update/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            }
        });

        const data = await response.json();
        
        if (response.ok) {
            // Update the display value
            const displayWrapper = document.querySelector(`[data-field="${fieldName}"]`);
            const valueDisplay = displayWrapper.querySelector('.text-gray-900');
            valueDisplay.textContent = data[fieldName] || 'Not set';
            
            // Toggle back to display mode
            const editWrapper = displayWrapper.closest('.field-display-wrapper').nextElementSibling;
            displayWrapper.closest('.field-display-wrapper').classList.remove('hidden');
            editWrapper.classList.add('hidden');
            
            showMessage('Changes saved successfully!', 'success');
        } else {
            throw new Error(data.errors ? data.errors : 'Failed to save changes');
        }
    } catch (error) {
        showMessage(`Failed to save changes: ${error.message}`, 'error');
        console.error('Save error:', error);
    }
}
function showMessage(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `fixed top-4 right-4 p-4 rounded-md shadow-lg z-50 ${
        type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
    } transition-opacity duration-500`;
    messageDiv.textContent = message;
    
    // Remove existing messages
    document.querySelectorAll('.message-alert').forEach(el => el.remove());
    
    document.body.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.style.opacity = '0';
        setTimeout(() => messageDiv.remove(), 500);
    }, 3000);
}

function initializeAddressField() {
    const addressInput = document.querySelector('#address-input');
    const geolocationInput = document.querySelector('#id_geolocation');
    const mapDiv = document.querySelector('#map');
    
    if (!addressInput || !mapDiv) return;

    const map = new google.maps.Map(mapDiv, {
        zoom: 15,
        center: { lat: -34.397, lng: 150.644 } // Default center
    });

    const marker = new google.maps.Marker({
        map: map,
        draggable: true
    });

    // Initialize the autocomplete
    const autocomplete = new google.maps.places.Autocomplete(addressInput);
    autocomplete.bindTo('bounds', map);

    // Handle place selection
    autocomplete.addListener('place_changed', function() {
        const place = autocomplete.getPlace();
        if (!place.geometry) return;

        // Update map
        map.setCenter(place.geometry.location);
        marker.setPosition(place.geometry.location);

        // Update form fields
        geolocationInput.value = `${place.geometry.location.lat()},${place.geometry.location.lng()}`;
        
        // Update address components
        for (const component of place.address_components) {
            const type = component.types[0];
            if (type === 'postal_code') {
                document.querySelector('#id_zip_code').value = component.long_name;
            } else if (type === 'locality') {
                document.querySelector('#id_city').value = component.long_name;
            } else if (type === 'administrative_area_level_1') {
                document.querySelector('#id_state').value = component.short_name;
            }
        }
    });
}