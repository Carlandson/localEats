document.addEventListener('DOMContentLoaded', function() {
    const addressInput = document.getElementById('id_address');
    const cityInput = document.getElementById('id_city');
    const stateInput = document.getElementById('id_state');
    const zipInput = document.getElementById('id_zip_code');

    // Initialize Google Places Autocomplete
    const autocomplete = new google.maps.places.Autocomplete(addressInput, {
        types: ['address'],
        componentRestrictions: { country: 'us' } // Restrict to US addresses
    });

    // Listen for place selection
    autocomplete.addListener('place_changed', fillInAddress);

    function fillInAddress() {
        const place = autocomplete.getPlace();
        
        // Clear existing values
        addressInput.value = '';
        cityInput.value = '';
        stateInput.value = '';
        zipInput.value = '';

        // Fill in the address fields
        for (const component of place.address_components) {
            const componentType = component.types[0];

            switch (componentType) {
                case 'street_number':
                    addressInput.value = `${component.long_name} `;
                    break;
                case 'route':
                    addressInput.value += component.long_name;
                    break;
                case 'locality':
                    cityInput.value = component.long_name;
                    break;
                case 'administrative_area_level_1':
                    stateInput.value = component.short_name;
                    break;
                case 'postal_code':
                    zipInput.value = component.long_name;
                    break;
            }
        }
    }
});