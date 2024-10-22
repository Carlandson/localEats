document.addEventListener('DOMContentLoaded', function() {
    const cuisineInput = document.getElementById('cuisine-input');
    const cuisineSuggestions = document.getElementById('cuisine-suggestions');
    const selectedCuisines = document.getElementById('selected-cuisines');
    const hiddenInput = document.getElementById('cuisine-hidden');

    const cuisineList = [
        'Italian', 'Chinese', 'Japanese', 'Mexican', 'Indian', 'French', 'Thai', 
        'Spanish', 'Greek', 'Lebanese', 'Turkish', 'Vietnamese', 'Korean', 
        'American', 'Brazilian', 'Peruvian', 'Moroccan', 'Ethiopian', 'Russian',
        // Add more cuisines as needed
    ];

    let selectedCuisineSet = new Set();

    cuisineInput.addEventListener('input', function() {
        const inputValue = this.value.toLowerCase();
        const filteredCuisines = cuisineList.filter(cuisine => 
            cuisine.toLowerCase().includes(inputValue)
        );

        cuisineSuggestions.innerHTML = '';
        filteredCuisines.forEach(cuisine => {
            const div = document.createElement('div');
            div.textContent = cuisine;
            div.addEventListener('click', () => addCuisine(cuisine));
            cuisineSuggestions.appendChild(div);
        });
    });

    function addCuisine(cuisine) {
        if (!selectedCuisineSet.has(cuisine)) {
            selectedCuisineSet.add(cuisine);
            updateSelectedCuisines();
            updateHiddenInput();
        }
        cuisineInput.value = '';
        cuisineSuggestions.innerHTML = '';
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
            cuisineTag.innerHTML = `${cuisine} <button onclick="removeCuisine('${cuisine}')">&times;</button>`;
            selectedCuisines.appendChild(cuisineTag);
        });
        cuisineInput.placeholder = selectedCuisineSet.size > 0 ? '' : 'Type to search cuisines...';
    }

    function updateHiddenInput() {
        hiddenInput.value = Array.from(selectedCuisineSet).join(',');
    }
});