import { GoogleMapsLoader } from '../utils/googleMapsLoader.js';
import { 
    BUSINESS_CATEGORIES, 
    BUSINESS_TYPES, 
    businessTypeHelpers 
} from '../constants/businessTypes.js';



class AddressAutocomplete {
    constructor() {
        this.addressInput = document.getElementById('id_address');
        this.cityInput = document.getElementById('id_city');
        this.stateInput = document.getElementById('id_state');
        this.zipInput = document.getElementById('id_zip_code');
    }

    initialize(maps) {
        if (!this.addressInput) return;

        this.autocomplete = new maps.places.Autocomplete(this.addressInput, {
            types: ['address'],
            componentRestrictions: { country: 'us' }
        });

        this.autocomplete.addListener('place_changed', () => this.fillInAddress());
    }

    fillInAddress() {
        const place = this.autocomplete.getPlace();
        
        // Clear existing values
        this.addressInput.value = '';
        this.cityInput.value = '';
        this.stateInput.value = '';
        this.zipInput.value = '';

        // Fill in the address fields
        for (const component of place.address_components) {
            const componentType = component.types[0];

            switch (componentType) {
                case 'street_number':
                    this.addressInput.value = `${component.long_name} `;
                    break;
                case 'route':
                    this.addressInput.value += component.long_name;
                    break;
                case 'locality':
                    this.cityInput.value = component.long_name;
                    break;
                case 'administrative_area_level_1':
                    this.stateInput.value = component.short_name;
                    break;
                case 'postal_code':
                    this.zipInput.value = component.long_name;
                    break;
            }
        }
    }
}

export class BusinessForm {
    constructor() {
        this.initializeElements();
        this.initializeData();
        this.initializeEventListeners();
    }

    initializeElements() {
        // Existing elements
        this.cuisineInput = document.getElementById('cuisine-input');
        this.cuisineSuggestions = document.getElementById('cuisine-suggestions');
        this.selectedCuisines = document.getElementById('selected-cuisines');
        this.hiddenInput = document.getElementById('cuisine-hidden');
        this.businessHiddenInput = document.getElementById('business-hidden');
        this.cuisineSection = document.querySelector('#cuisine-section');

        // New elements for category selection
        this.categorySelect = document.getElementById('business-category');
        this.businessTypeSelect = document.getElementById('business-type');
        this.customBusinessInput = document.getElementById('custom-business-type');
    }

    initializeData() {
        // Replace the simple business list with our structured data
        this.businessCategories = BUSINESS_CATEGORIES;
        this.businessTypes = BUSINESS_TYPES;
        this.selectedCategory = null;
        this.selectedBusinessType = null;

        this.cuisineList = [
            'Afghan', 'Algerian', 'American', 'Armenian', 'Argentinian', 'Australian', 
            'Bangladeshi', 'BBQ', 'Belgian', 'Brazilian', 'Cajun', 'Cambodian', 
            'Caribbean', 'Chilean', 'Chinese', 'Colombian', 'Creole', 'Cuban', 
            'Dutch', 'Egyptian', 'Emirati', 'Ethiopian', 'Filipino', 'French', 
            'Georgian', 'German', 'Greek', 'Hawaiian', 'Hawaiian', 
            'Hungarian', 'Indian', 'Indonesian', 'Israeli', 'Italian', 'Jamaican', 
            'Japanese', 'Kazakh', 'Korean', 'Lebanese', 'Malaysian', 'Midwestern', 
            'Mexican', 'Mongolian', 'Moroccan', 'Nepalese', 'New England', 
            'New Zealand', 'Pacific Northwest', 'Pakistani', 'Peruvian', 'Persian', 
            'Polish', 'Portuguese', 'Russian', 'Saudi', 'Singaporean', 'Somali', 
            'Soul Food', 'Southern', 'Spanish', 'Sri Lankan', 'Sudanese', 
            'Swedish', 'Swiss', 'Syrian', 'Tex-Mex', 'Thai', 'Tibetan', 
            'Turkish', 'Tunisian', 'Ukrainian', 'Uzbek', 'Vietnamese'
        ];    

        this.selectedCuisineSet = new Set();
    }

    initializeEventListeners() {
        // Add category selection handler
        if (this.categorySelect) {
            this.populateCategories();
            this.categorySelect.addEventListener('change', (e) => {
                this.handleCategoryChange(e.target.value);
            });
        }

        // Add business type selection handler
        if (this.businessTypeSelect) {
            this.businessTypeSelect.addEventListener('change', (e) => {
                this.handleBusinessTypeChange(e.target.value);
            });
        }

        // Existing event listeners
        if (this.cuisineInput) {
            this.cuisineInput.addEventListener('input', this.handleCuisineInput.bind(this));
            this.cuisineInput.addEventListener('focus', this.handleCuisineFocus.bind(this));
        }

        document.addEventListener('click', this.handleDocumentClick.bind(this));
    }


    populateCategories() {
        this.categorySelect.innerHTML = '<option value="">Select a Category</option>';
        Object.entries(this.businessCategories).forEach(([key, label]) => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = label;
            this.categorySelect.appendChild(option);
        });
    }

    handleCategoryChange(category) {
        this.selectedCategory = category;
        this.businessTypeSelect.style.display = 'block';
        this.populateBusinessTypes(category);
        
        // Reset business type selection
        this.businessTypeSelect.value = '';
        this.customBusinessInput.style.display = 'none';
        this.customBusinessInput.value = '';
        this.cuisineSection.style.display = 'none';
    }

    populateBusinessTypes(category) {
        console.log('Category received:', category);
        console.log('Business Types object:', this.businessTypes);
        console.log('Business Categories object:', this.businessCategories);
        console.log('Available keys in Business Types:', Object.keys(this.businessTypes));
        console.log('Trying to access:', this.businessTypes[category]);
        this.businessTypeSelect.innerHTML = '<option value="">Select a Business Type</option>';
        const types = this.businessTypes[this.businessCategories[category]];
        console.log('Found types:', types);
        if (types) {
            types.forEach(type => {
                const option = document.createElement('option');
                option.value = type.id;
                option.textContent = type.label;
                this.businessTypeSelect.appendChild(option);
            });
        }
    }

    handleBusinessTypeChange(businessTypeId) {
        this.selectedBusinessType = businessTypeId;
        
        // Handle custom business type
        if (businessTypeId === 'custom') {
            this.customBusinessInput.style.display = 'block';
        } else {
            this.customBusinessInput.style.display = 'none';
        }

        // Show/hide cuisine section based on business type
        if (businessTypeHelpers.requiresCuisine(businessTypeId)) {
            this.cuisineSection.style.display = 'block';
        } else {
            this.cuisineSection.style.display = 'none';
            this.selectedCuisineSet.clear();
            this.updateSelectedCuisines();
            this.updateHiddenInput();
        }

        // Update hidden input with selected business type
        this.businessHiddenInput.value = businessTypeId;
    }

    handleCuisineInput() {
        try {
            const inputValue = this.cuisineInput.value.toLowerCase();
            const filteredCuisines = this.cuisineList.filter(cuisine =>
                cuisine.toLowerCase().includes(inputValue)
            );

            this.cuisineSuggestions.innerHTML = '';
            if (filteredCuisines.length > 0 && inputValue.length > 0) {
                filteredCuisines.forEach(cuisine => {
                    const div = document.createElement('div');
                    div.textContent = cuisine;
                    div.addEventListener('click', (event) => this.addCuisine(cuisine, event));
                    this.cuisineSuggestions.appendChild(div);
                });
                this.cuisineSuggestions.classList.add('active');
            } else {
                this.cuisineSuggestions.classList.remove('active');
            }
        } catch (error) {
            console.error('Error handling cuisine input:', error);
        }
    }

    addCuisine(cuisine, event) {
        try {
            if (event) {
                event.stopPropagation();
            }
            if (!this.selectedCuisineSet.has(cuisine)) {
                this.selectedCuisineSet.add(cuisine);
                this.updateSelectedCuisines();
                this.updateHiddenInput();
            }
            this.cuisineInput.value = '';
            this.cuisineSuggestions.innerHTML = '';
            this.cuisineSuggestions.classList.remove('active');
        } catch (error) {
            console.error('Error adding cuisine:', error);
        }
    }

    removeCuisine(cuisine) {
        try {
            this.selectedCuisineSet.delete(cuisine);
            this.updateSelectedCuisines();
            this.updateHiddenInput();
        } catch (error) {
            console.error('Error removing cuisine:', error);
        }
    }

    updateSelectedCuisines() {
        try {
            this.selectedCuisines.innerHTML = '';
            this.selectedCuisineSet.forEach(cuisine => {
                const cuisineTag = document.createElement('span');
                cuisineTag.className = 'cuisine-tag';
                cuisineTag.innerHTML = `${cuisine} <button onclick="window.businessForm.removeCuisine('${cuisine}')"><span class="remove-cuisine">&times;</span></button>`;
                this.selectedCuisines.appendChild(cuisineTag);
            });
            this.cuisineInput.placeholder = this.selectedCuisineSet.size > 0 ? '' : 'Type to search cuisines...';
        } catch (error) {
            console.error('Error updating selected cuisines:', error);
        }
    }

    updateHiddenInput() {
        try {
            this.hiddenInput.value = Array.from(this.selectedCuisineSet).join(',');
        } catch (error) {
            console.error('Error updating hidden input:', error);
        }
    }

    handleDocumentClick(event) {
        try {
            if (this.businessSuggestions?.classList.contains('active') &&
                !this.businessInput?.contains(event.target) &&
                !this.businessSuggestions?.contains(event.target)) {
                this.businessSuggestions.classList.remove('active');
            }

            if (this.cuisineSuggestions?.classList.contains('active') &&
                !this.cuisineInput?.contains(event.target) &&
                !this.cuisineSuggestions?.contains(event.target)) {
                this.cuisineSuggestions.classList.remove('active');
            }
        } catch (error) {
            console.error('Error handling document click:', error);
        }
    }

    handleCuisineFocus() {
        try {
            if (this.cuisineInput.value.length > 0) {
                this.cuisineSuggestions.classList.add('active');
            }
        } catch (error) {
            console.error('Error handling cuisine focus:', error);
        }
    }
}

let businessFormInstance = null;

window.removeCuisine = function(cuisine) {
    if (!businessFormInstance) {
        businessFormInstance = new BusinessForm();
    }
    businessFormInstance.removeCuisine(cuisine);
};
// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Initialize address autocomplete
        const apiKey = window.__GOOGLE_MAPS_API_KEY__;
        if (apiKey) {
            const maps = await GoogleMapsLoader.loadAPI(apiKey);
            const addressAutocomplete = new AddressAutocomplete();
            addressAutocomplete.initialize(maps);
            delete window.__GOOGLE_MAPS_API_KEY__;
        }

        // Initialize business form and store the instance
        businessFormInstance = new BusinessForm();
    } catch (error) {
        console.error('Initialization error:', error);
    }
});
