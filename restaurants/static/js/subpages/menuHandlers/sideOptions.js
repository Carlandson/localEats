
// For the reformat we need to
// 1.attach listeners to all loaded side options (edit and delete)
// 2.attach listeners to submit changes (add and edit)
// 3.attach listeners to cancel changes
// 4.inject the new side options when added to the liste
// 5.check for duplicate side options when adding new ones
// 6.also update all side options to use django template forms

// this is exposed when the user clicks the edit side option button
async function toggleSideOptionForm(courseId, context, sideOption = null) {
    
}
async function showSideOptionForm(courseId, context, sideOption = null) {
    const formDiv = document.getElementById(`sideOptionsform${courseId}`);
    formDiv.className = "w-full bg-white p-4 rounded-lg border border-gray-200 mt-2 mb-4";  // Adjust the container

    formDiv.innerHTML = `
        <form id="${sideOption ? 'editSideOption' : 'createSideOption'}" class="grid grid-cols-6 gap-4">
            <div class="col-span-6">
                <label class="block text-sm font-medium text-gray-700">Name</label>
                <input type="text" name="name" value="${sideOption?.name || ''}" 
                       class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500" required>
            </div>
            <div class="col-span-6">
                <label class="block text-sm font-medium text-gray-700">Description (optional)</label>
                <textarea name="description" 
                          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 h-16 resize-none"
                >${sideOption?.description || ''}</textarea>
            </div>
            <div class="col-span-3 flex items-center">
                <input type="checkbox" name="is_premium" id="is_premium" 
                       ${sideOption?.is_premium ? 'checked' : ''}
                       class="h-4 w-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500">
                <label for="is_premium" class="ml-2 block text-sm text-gray-900">Premium Option</label>
            </div>
            <div class="col-span-3 premium-price ${sideOption?.is_premium ? '' : 'hidden'}">
                <label class="block text-sm font-medium text-gray-700">Additional Price</label>
                <input type="number" name="price" value="${sideOption?.price || ''}" step="0.01" min="0"
                       class="mt-1 block w-32 rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500">
            </div>
            <div class="col-span-6 flex justify-end space-x-2 mt-2">
                <button type="button" class="cancelSideOption px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded transition-colors duration-200">
                    Cancel
                </button>
                <button type="submit" class="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded transition-colors duration-200">
                    ${sideOption ? 'Save Changes' : 'Add Side Option'}
                </button>
            </div>
        </form>
    `;

    // Add the form before the "Add Side" button
    const buttonContainer = document.getElementById(`addSideButtonContainer${courseId}`);
    if (buttonContainer) {
        buttonContainer.style.display = 'none';
    }

    // Handle premium checkbox toggle
    const premiumCheckbox = formDiv.querySelector('#is_premium');
    const priceDiv = formDiv.querySelector('.premium-price');
    premiumCheckbox.addEventListener('change', () => {
        priceDiv.classList.toggle('hidden', !premiumCheckbox.checked);
    });

    formDiv.querySelector('.cancelSideOption').addEventListener('click', () => {
        // Clear and hide the form
        formDiv.innerHTML = '';
        formDiv.className = 'hidden';

        // Show the add button again
        buttonContainer.style.display = 'block';
    });

    // Handle form submission
    const form = formDiv.querySelector('form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            name: form.querySelector('[name="name"]').value,
            description: form.querySelector('[name="description"]').value,
            is_premium: form.querySelector('[name="is_premium"]').checked,
            price: form.querySelector('[name="price"]').value || 0,
            course_id: courseId
        };

        try {
            await api.menu.addSideOption(context.eatery, formData);
            showToast('Side option added successfully');
            // Update the side options list
            await updateSideOptionsList(courseId, context);
            
            // Remove the form
            formDiv.innerHTML = '';
            formDiv.className = 'hidden';
            if (buttonContainer) {
                buttonContainer.style.display = '';
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error saving side option. Please try again.');
        }
    });
}

// reformat of show edit form
async function showSideOptionEditForm(sideId, context) {
    const sideOptionDisplay = document.getElementById(`sideOption${sideId}`);
    sideOptionDisplay.style.display = 'none';
    const sideOptionForm = document.getElementById(`editSideOptionForm${sideId}`);
    sideOptionForm.style.display = 'block';
}

async function editSideOption(sideId, context) {
    try {
        const data = await api.menu.editSideOption(context.eatery, sideId);
        // Hide the side option element temporarily
        const sideElement = document.getElementById(`sideOption${sideId}`);
        if (sideElement) {
            sideElement.style.display = 'none';
        }
        // Show the edit form
        showSideOptionForm(data.course_id, context, {
            id: sideId,
            name: data.name,
            description: data.description,
            is_premium: data.is_premium,
            price: data.price
        });
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error loading side option data. Please try again.');
    }
}

async function deleteSideOption(sideId, context) {
    // Find the button first, then traverse up to the parent container
    const deleteButton = document.querySelector(`button.deleteSideOption[data-side-id="${sideId}"]`);
    if (!deleteButton) {
        console.error('Could not find delete button');
        return;
    }

    // Find the side option div directly by ID
    const sideElement = document.getElementById(`sideOption${sideId}`);
    if (!sideElement) {
        console.error('Could not find side option element');
        return;
    }

    // Add loading state
    sideElement.style.opacity = '0.5';
    const buttons = sideElement.querySelectorAll('button');
    buttons.forEach(button => button.disabled = true);

    try {
        const result = await api.menu.deleteSideOption(context.eatery, sideId);
        showToast('Side option deleted successfully');
        
        // Animate removal
        sideElement.style.transition = 'all 0.3s ease-out';
        sideElement.style.transform = 'translateX(100%)';
        sideElement.style.opacity = '0';
        
        setTimeout(() => {
            sideElement.remove();
            
            // Check if this was the last side option
            const listContainer = document.getElementById(`sideOptionsList${result.course_id}`);
            const remainingSides = listContainer.querySelectorAll('div[data-side-id]').length;
            
            if (remainingSides === 0) {
                updateSideOptionsList(result.course_id, context);
            }
        }, 300);
    } catch (error) {
        console.error('Error:', error);
        sideElement.style.opacity = '1';
        buttons.forEach(button => button.disabled = false);
        alert('Error deleting side option. Please try again.');
    }
}

async function updateSideOptionsList(courseId, context) {
    try {
        const response = await fetch(`/${context.eatery}/menu/side_options/${courseId}/`)
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        console.log('Received side options:', data); // Debug log
        
        // Ensure sideOptions is an array
        const sideOptions = Array.isArray(data) ? data : [];

        // Find the main list container
        const listContainer = document.getElementById(`sideOptionsList${courseId}`);
        if (!listContainer) {
            console.error('Could not find list container:', `sideOptionsList${courseId}`);
            return;
        }

        // Clear the entire list container first
        listContainer.innerHTML = '';

        // Create a container for side options
        const sideOptionsContainer = document.createElement('div');
        sideOptionsContainer.className = 'side-options-container';
        listContainer.appendChild(sideOptionsContainer);
        
        // Add side options in order
        if (sideOptions.length > 0) {
            sideOptions.forEach(side => {
                if (!side || !side.id) {
                    console.error('Invalid side option:', side);
                    return;
                }
                
                const sideDiv = document.createElement('div');
                sideDiv.id = `sideOption${side.id}`;
                sideDiv.setAttribute('data-side-id', side.id);
                sideDiv.className = 'flex justify-between items-center p-2 ' + 
                                   (side.is_premium ? 'bg-amber-50' : 'bg-gray-50') + 
                                   ' rounded mb-2';
                
                sideDiv.innerHTML = `
                    <div>
                        <div class="flex items-center gap-2">
                            <p class="font-medium">${side.name || ''}</p>
                            ${side.is_premium ? `<span class="text-sm text-amber-600 font-medium">+$${side.price || '0.00'}</span>` : ''}
                        </div>
                        ${side.description ? `<p class="text-sm text-gray-600">${side.description}</p>` : ''}
                    </div>
                    <div class="flex gap-2">
                        <button class="editSideOption text-blue-500 hover:text-blue-700"
                                data-side-id="${side.id}">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                            </svg>
                        </button>
                        <button class="deleteSideOption text-red-500 hover:text-red-700"
                                data-side-id="${side.id}">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                            </svg>
                        </button>
                    </div>
                `;
                
                sideOptionsContainer.appendChild(sideDiv);
            });
        } else {
            // Add "No side options" message if needed
            const noOptionsMessage = document.createElement('p');
            noOptionsMessage.className = 'text-gray-500 text-center';
            noOptionsMessage.textContent = 'No side options available';
            sideOptionsContainer.appendChild(noOptionsMessage);
        }

    } catch (error) {
        console.error('Error:', error);
        alert('Error updating side options list. Please try again.');
    }
}