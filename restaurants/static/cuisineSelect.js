document.addEventListener('DOMContentLoaded', function() {
    const cuisineInput = document.getElementById('cuisine-input');
    const cuisineSuggestions = document.getElementById('cuisine-suggestions');
    const selectedCuisines = document.getElementById('selected-cuisines');
    const hiddenInput = document.getElementById('cuisine-hidden');

    const cuisineList = [
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

    let selectedCuisineSet = new Set();

    cuisineInput.addEventListener('input', function() {
        const inputValue = this.value.toLowerCase();
        const filteredCuisines = cuisineList.filter(cuisine => 
            cuisine.toLowerCase().includes(inputValue)
        );

        cuisineSuggestions.innerHTML = '';
        if (filteredCuisines.length > 0 && inputValue.length > 0) {
            filteredCuisines.forEach(cuisine => {
                const div = document.createElement('div');
                div.textContent = cuisine;
                div.addEventListener('click', (event) => addCuisine(cuisine, event));
                cuisineSuggestions.appendChild(div);
            });
            cuisineSuggestions.classList.add('active');
        } else {
            cuisineSuggestions.classList.remove('active');
        }
    });

    function addCuisine(cuisine, event) {
        if (event) {
            event.stopPropagation();
        }
        if (!selectedCuisineSet.has(cuisine)) {
            selectedCuisineSet.add(cuisine);
            updateSelectedCuisines();
            updateHiddenInput();
        }
        cuisineInput.value = '';
        cuisineSuggestions.innerHTML = '';
        cuisineSuggestions.classList.remove('active');
    }

    window.removeCuisine = function(cuisine) {
        selectedCuisineSet.delete(cuisine);
        updateSelectedCuisines();
        updateHiddenInput();
    }

    function updateSelectedCuisines() {
        selectedCuisines.innerHTML = '';
        selectedCuisineSet.forEach(cuisine => {
            const cuisineTag = document.createElement('span');
            cuisineTag.className = 'cuisine-tag';
            cuisineTag.innerHTML = `${cuisine} <button onclick="removeCuisine('${cuisine}')"><span class="remove-cuisine">&times;</span></button>`;
            selectedCuisines.appendChild(cuisineTag);
        });
        cuisineInput.placeholder = selectedCuisineSet.size > 0 ? '' : 'Type to search cuisines...';
    }

    function updateHiddenInput() {
        hiddenInput.value = Array.from(selectedCuisineSet).join(',');
    }

    document.addEventListener('click', function(event) {
        if (cuisineSuggestions.classList.contains('active') && 
            !cuisineInput.contains(event.target) && 
            !cuisineSuggestions.contains(event.target)) {
            cuisineSuggestions.classList.remove('active');
        }
    });

    cuisineInput.addEventListener('focus', function() {
        if (this.value.length > 0) {
            cuisineSuggestions.classList.add('active');
        }
    });
});
