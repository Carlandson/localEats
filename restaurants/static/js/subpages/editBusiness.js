import { showToast } from '../components/toast.js';
import { api } from '../utils/subpagesAPI.js';

document.addEventListener('DOMContentLoaded', function() {
    const business = JSON.parse(document.getElementById('business').textContent);
    let map = null;
    let marker = null;

    // Handle edit buttons
    document.querySelectorAll('.edit-button').forEach(button => {
        button.addEventListener('click', function() {
            const fieldContainer = this.closest('[data-field]');
            const fieldName = fieldContainer.dataset.field;
            const displayWrapper = fieldContainer.closest('.field-display-wrapper');
            const editWrapper = displayWrapper.nextElementSibling;
            
            displayWrapper.classList.add('hidden');
            editWrapper.classList.remove('hidden');

            // Initialize map when editing address
            if (fieldName === 'address') {
                initializeMap();
            }
        });
    });

    // Special handling for address field with Google Places Autocomplete
    const addressField = document.querySelector('.address-autocomplete');
    if (addressField && window.google) {
        const autocomplete = new google.maps.places.Autocomplete(addressField, {
            types: ['address']
        });

        autocomplete.addListener('place_changed', async function() {
            const place = autocomplete.getPlace();
            if (!place.formatted_address) return;

            // Update map marker if map is initialized
            if (map && marker && place.geometry) {
                map.setCenter(place.geometry.location);
                marker.setPosition(place.geometry.location);
            }

            try {
                const response = await api.editBusiness.updateField(business, 'address', place.formatted_address);
                
                if (response.status === 'success') {
                    showToast('Address updated successfully!');
                    const displayValue = document.querySelector('[data-field="address"] .text-gray-900');
                    displayValue.textContent = response.address;
                    
                    // Hide edit wrapper and show display wrapper
                    const editWrapper = addressField.closest('.field-edit-wrapper');
                    const displayWrapper = editWrapper.previousElementSibling;
                    editWrapper.classList.add('hidden');
                    displayWrapper.classList.remove('hidden');

                    // Clean up map
                    map = null;
                    marker = null;
                } else {
                    throw new Error(response.errors?.[0] || 'Update failed');
                }
            } catch (error) {
                console.error('Update failed:', error);
                showToast(error.message || 'Failed to update address. Please try again.', 'error');
            }
        });
    }

    // Function to initialize Google Map
    function initializeMap() {
        const mapElement = document.getElementById('map');
        const addressInput = document.querySelector('.address-autocomplete');
        const currentAddress = addressInput.value;

        if (!mapElement || !window.google || map) return;

        // Default to a central location if no address
        const defaultLocation = { lat: 40.7128, lng: -74.0060 }; // New York City

        // Initialize the map
        map = new google.maps.Map(mapElement, {
            zoom: 15,
            center: defaultLocation,
            mapTypeControl: false,
        });

        marker = new google.maps.Marker({
            map: map,
            draggable: false,
            position: defaultLocation,
        });

        // If we have a current address, geocode it and center the map
        if (currentAddress) {
            const geocoder = new google.maps.Geocoder();
            geocoder.geocode({ address: currentAddress }, (results, status) => {
                if (status === 'OK' && results[0]) {
                    const location = results[0].geometry.location;
                    map.setCenter(location);
                    marker.setPosition(location);
                }
            });
        }
    }

    // Handle save buttons for other fields
    document.querySelectorAll('.save-button').forEach(button => {
        button.addEventListener('click', async function() {
            const editWrapper = this.closest('.field-edit-wrapper');
            const displayWrapper = editWrapper.previousElementSibling;
            const fieldContainer = displayWrapper.querySelector('[data-field]');
            const fieldName = fieldContainer.dataset.field;
            const input = editWrapper.querySelector(`[name="${fieldName}"]`);
            const value = input.value;
            const displayValue = fieldContainer.querySelector('.text-gray-900');

            try {
                const response = await api.editBusiness.updateField(business, fieldName, value);
                
                if (response.status === 'success') {
                    showToast('Changes saved successfully!');
                    displayValue.textContent = response[fieldName];
                    editWrapper.classList.add('hidden');
                    displayWrapper.classList.remove('hidden');
                } else {
                    throw new Error(response.errors?.[0] || 'Update failed');
                }
            } catch (error) {
                console.error('Update failed:', error);
                showToast(error.message || 'Failed to update. Please try again.', 'error');
            }
        });
    });

    // Handle cancel buttons
    document.querySelectorAll('.cancel-button').forEach(button => {
        button.addEventListener('click', function() {
            const editWrapper = this.closest('.field-edit-wrapper');
            const displayWrapper = editWrapper.previousElementSibling;
            
            editWrapper.classList.add('hidden');
            displayWrapper.classList.remove('hidden');
        });
    });
});