async function initializeMenuBuilder() {
    try {
        // Get required elements
        const kitchenConfig = JSON.parse(document.getElementById('kitchen').textContent);
        
        if (!kitchenConfig) {
            throw new Error('Required kitchen configuration not found');
        }

        // Create context object
        const context = {
            eatery: kitchenConfig,
            accordionTriggers: document.querySelectorAll('.accordion-trigger')
        };

        // Initialize all handlers
        try {
            initializeAccordions(context);
            initializeEventListeners(context);
        } catch (handlerError) {
            console.error('Error initializing menu builder handlers:', handlerError);
            throw handlerError;
        }

        return context;
    } catch (error) {
        console.error('Error in menu builder initialization:', error);
        throw error;
    }
}

function initializeAccordions(context) {
    context.accordionTriggers.forEach(trigger => {
        trigger.addEventListener('click', () => {
            const target = document.getElementById(trigger.dataset.target);
            const arrow = trigger.querySelector('svg');
            
            // Toggle panel visibility
            target.classList.toggle('hidden');
            
            // Update styles based on visibility
            if (target.classList.contains('hidden')) {
                trigger.classList.remove('bg-gray-100', 'hover:bg-gray-400');
                trigger.classList.add('bg-white', 'hover:bg-gray-400');
                arrow.classList.remove('rotate-90');
            } else {
                trigger.classList.remove('bg-white', 'hover:bg-gray-50');
                trigger.classList.add('bg-gray-100', 'hover:bg-gray-400');
                arrow.classList.add('rotate-90');
            }
        });
    });
}

function initializeEventListeners(context) {
    document.addEventListener('click', (e) => handleClicks(e, context));
}

function handleClicks(e, context) {
    // Add Course button
    if (e.target.matches('#add')) {
        e.preventDefault();
        const submission = document.querySelector('#addCourse');
        addCourse(submission.value, context);
    }

    // Submit Dish button
    if (e.target.matches('.submitDish')) {
        addDish(e.target.id, context);
    }

    // Edit Dish button
    if (e.target.matches('.editDish')) {
        const itemId = e.target.id.replace('e', '');
        editDish(itemId, context);
    }

    // Delete Dish button
    if (e.target.matches('.deleteDish')) {
        const dishId = e.target.id.replace('d', '');
        deleteDish(dishId, context);
    }

    // Delete Course button
    if (e.target.closest('.deleteCourse')) {
        const courseId = e.target.closest('.deleteCourse').getAttribute('data-course-id');
        deleteCourse(courseId, context);
    }

    // Edit Description button
    if (e.target.matches('.editDescription') || e.target.closest('.editDescription')) {
        const button = e.target.closest('.editDescription') || e.target;
        const courseId = button.dataset.courseId;
        editCourseDescription(courseId, context);
    }

    // Save Description button
    if (e.target.matches('.saveDescription')) {
        const courseId = e.target.dataset.courseId;
        saveCourseDescription(courseId, context);
    }

    // Edit Note button
    if (e.target.matches('.editNote') || e.target.closest('.editNote')) {
        const button = e.target.closest('.editNote') || e.target;
        const courseId = button.dataset.courseId;
        editCourseNote(courseId, context);
    }

    // Save Note button
    if (e.target.matches('.saveNote')) {
        const courseId = e.target.dataset.courseId;
        saveCourseNote(courseId, context);
    }

    // Add Side Option button
    if (e.target.matches('.addSideOption')) {
        const courseId = e.target.dataset.courseId;
        showSideOptionForm(courseId, context);
    }

    // Edit Side Option button
    if (e.target.closest('.editSideOption')) {
        const sideId = e.target.closest('.editSideOption').dataset.sideId;
        editSideOption(sideId, context);
    }

    // Delete Side Option button
    if (e.target.closest('.deleteSideOption')) {
        const sideId = e.target.closest('.deleteSideOption').dataset.sideId;
        deleteSideOption(sideId, context);
    }
}

function getFormHTML(isEdit = false, dishId = '', currentValues = {}) {
    return `
        <form id="${isEdit ? 'editDish' + dishId : 'createDish'}" class="p-1" action="post">
            <div class="form-group">
                <input type="text" 
                       class="p-2 m-1 border-double border-4 border-indigo-200" 
                       placeholder="Name of Dish" 
                       id="${isEdit ? 'dishName' + dishId : 'dishName'}"
                       value="${isEdit ? currentValues.name : ''}" 
                       required>
                <input type="number" 
                       class="p-2 m-1 border-double border-4 border-indigo-200" 
                       placeholder="Price" 
                       step="any" 
                       id="${isEdit ? 'dishPrice' + dishId : 'dishPrice'}"
                       value="${isEdit ? currentValues.price : ''}" 
                       required>
                <div class="image-upload-container">
                    <input type="file" 
                           class="p-2 m-1 border-double border-4 border-indigo-200" 
                           accept="image/*"
                           id="${isEdit ? 'dishImage' + dishId : 'dishImage'}">
                    ${isEdit && currentValues.image ? `
                        <div class="current-image">
                            <img src="${currentValues.image}" class="h-20 w-20 object-contain" alt="Current image">
                            <p class="text-sm text-gray-500">Current image</p>
                        </div>
                    ` : ''}
                </div>
                <textarea class="form-control p-2 m-1" 
                          id="${isEdit ? 'dishDescription' + dishId : 'dishDescription'}" 
                          rows="3" 
                          placeholder="Description">${isEdit ? currentValues.description : ''}</textarea>
            </div>
            <button type="submit" class="bg-blue-500 m-2 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                ${isEdit ? 'Save Changes' : 'Add Dish'}
            </button>
            <button type="button" 
                    class="${isEdit ? 'cancel-edit' : 'cancel-add'} bg-gray-500 m-2 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">
                Cancel
            </button>
        </form>
    `;
}

function createDishHTML(dishId, formData, imageUrl = null) {
    return `
        <div class="text-center">
            <h3 class="text-xl font-bold mb-2">${formData.name}</h3>
            ${imageUrl ? 
                `<img src="${imageUrl}" class="mx-auto object-contain h-40 w-40" alt="${formData.name}">` :
                `<div class="h-40 w-40 mx-auto flex items-center justify-center bg-gray-100 rounded-lg border-2 border-dashed border-gray-300">
                    <span class="text-gray-400">No Image</span>
                </div>`
            }
            <p class="mt-2 font-semibold">Price: $${formData.price}</p>
        </div>
        <div class="text-center">
            <h4 class="font-semibold mb-2">Description:</h4>
            <p>${formData.description}</p>
        </div>
        <div class="md:text-right flex md:justify-end items-center space-x-2">
            <button class="editDish px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded transition-colors duration-200" 
                    id="e${dishId}">Edit</button>
            <button class="deleteDish px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded transition-colors duration-200" 
                    id="d${dishId}">Delete</button>
        </div>
    `;
}

async function handleImageUpload(fileInput) {
    return new Promise((resolve, reject) => {
        if (!fileInput.files || !fileInput.files[0]) {
            resolve(null);
            return;
        }

        const file = fileInput.files[0];
        const reader = new FileReader();

        reader.onload = (e) => {
            resolve(e.target.result);
        };
        reader.onerror = (e) => {
            reject(e);
        };

        reader.readAsDataURL(file);
    });
}

async function addCourse(dishData, context) {
    try {
        const response = await fetch(`/${context.eatery}/menu/add_course/`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                course_name: dishData
            })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        await response.json();
        location.reload();
    } catch (error) {
        console.error('Error:', error);
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

async function addDish(course, context) {
    let currentCourse = course.replace('submit', "");
    let addButton = document.getElementById(course);
    let parentPanel = addButton.closest('.accordion-collapse') || addButton.closest('[id^="panel"]');
    
    if (!parentPanel) {
        console.error('Could not find parent panel');
        return;
    }

    const buttonContainer = addButton.closest('.text-center');
    const deleteButton = buttonContainer.querySelector('.deleteCourse');
    buttonContainer.style.display = 'none';

    let formDiv = document.createElement('div');
    formDiv.innerHTML = getFormHTML(false);
    buttonContainer.parentNode.insertBefore(formDiv, buttonContainer);

    formDiv.querySelector('.cancel-add').addEventListener('click', () => {
        buttonContainer.style.display = '';
        formDiv.remove();
    });

    formDiv.querySelector('#createDish').addEventListener('submit', async (event) => {
        event.preventDefault();
        
        const formData = {
            name: document.querySelector("#dishName").value,
            price: document.querySelector("#dishPrice").value,
            description: document.querySelector("#dishDescription").value,
            course: currentCourse
        };

        const imageInput = document.querySelector('#dishImage');
        if (imageInput && imageInput.files[0]) {
            formData.image = await handleImageUpload(imageInput);
        }

        try {
            const response = await fetch(`/${context.eatery}/menu/add_dish/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error);
            }

            const newDishArticle = document.createElement('article');
            newDishArticle.id = `o${data.dish_id}`;
            newDishArticle.className = 'border rounded-lg p-4 mb-4 grid md:grid-cols-3 gap-4';
            newDishArticle.innerHTML = createDishHTML(data.dish_id, formData, data.image_url);

            buttonContainer.insertAdjacentElement('beforebegin', newDishArticle);
            buttonContainer.style.display = '';
            formDiv.remove();
        } catch (error) {
            console.error('Error:', error);
            buttonContainer.style.display = '';
            formDiv.remove();
            alert(error.message || 'Error adding dish. Please try again.');
        }
    });
}

async function editDish(dishId, context) {
    try {
        const response = await fetch(`/${context.eatery}/menu/edit_dish/${dishId}/`);
        if (!response.ok) throw new Error('Network response was not ok');
        const dishData = await response.json();

        const dishArticle = document.getElementById(`o${dishId}`);
        if (!dishArticle) throw new Error('Dish article not found');

        const originalContent = dishArticle.innerHTML;
        dishArticle.innerHTML = getFormHTML(true, dishId, {
            name: dishData.name,
            price: dishData.price,
            description: dishData.description,
            image: dishData.image
        });

        const form = document.getElementById(`editDish${dishId}`);
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            const formData = {
                name: document.querySelector(`#dishName${dishId}`).value,
                price: document.querySelector(`#dishPrice${dishId}`).value,
                description: document.querySelector(`#dishDescription${dishId}`).value
            };

            const imageInput = document.querySelector(`#dishImage${dishId}`);
            if (imageInput && imageInput.files[0]) {
                formData.image = await handleImageUpload(imageInput);
            }

            try {
                const response = await fetch(`/${context.eatery}/menu/edit_dish/${dishId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();
                if (!response.ok) throw new Error(data.error);

                dishArticle.innerHTML = createDishHTML(dishId, formData, data.image_url);
            } catch (error) {
                console.error('Error:', error);
                alert(error.message || 'Error updating dish. Please try again.');
                dishArticle.innerHTML = originalContent;
            }
        });

        form.querySelector('.cancel-edit').addEventListener('click', () => {
            dishArticle.innerHTML = originalContent;
        });
    } catch (error) {
        console.error('Error:', error);
        alert('Error loading dish data. Please try again.');
    }
}

async function deleteDish(dishId, context) {
    if (!confirm('Are you sure you want to delete this dish?')) {
        return;
    }

    const dishArticle = document.getElementById(`o${dishId}`);
    if (!dishArticle) {
        console.error('Could not find dish article');
        return;
    }

    try {
        const response = await fetch(`/${context.eatery}/menu/delete_dish/${dishId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (!response.ok) throw new Error('Network response was not ok');

        dishArticle.style.transition = 'all 0.3s ease-out';
        dishArticle.style.transform = 'translateX(100%)';
        dishArticle.style.opacity = '0';
        
        setTimeout(() => {
            dishArticle.remove();
        }, 300);
    } catch (error) {
        console.error('Error:', error);
        alert('Error deleting dish. Please try again.');
    }
}

async function deleteCourse(courseId, context) {
    if (!confirm('Are you sure you want to delete this course and all its dishes?')) {
        return;
    }

    try {
        const response = await fetch(`/${context.eatery}/menu/delete_course/${courseId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (!response.ok) throw new Error('Network response was not ok');

        // Find and remove the course section
        const courseSection = document.querySelector(`[data-course-id="${courseId}"]`).closest('section');
        if (courseSection) {
            courseSection.style.transition = 'all 0.3s ease-out';
            courseSection.style.transform = 'translateX(100%)';
            courseSection.style.opacity = '0';
            
            setTimeout(() => {
                courseSection.remove();
            }, 300);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error deleting course. Please try again.');
    }
}

async function editCourseDescription(courseId, context) {
    const descriptionDiv = document.querySelector(`#courseDescription${courseId}`);
    const currentDescription = descriptionDiv.textContent.trim();
    const editButton = document.querySelector(`.editDescription[data-course-id="${courseId}"]`);

    // Create and show textarea
    const textarea = document.createElement('textarea');
    textarea.value = currentDescription;
    textarea.className = 'w-full p-2 border rounded';
    textarea.rows = 3;

    // Create save button
    const saveButton = document.createElement('button');
    saveButton.textContent = 'Save';
    saveButton.className = 'saveDescription px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded transition-colors duration-200 mt-2';
    saveButton.dataset.courseId = courseId;

    // Replace content and hide edit button
    descriptionDiv.textContent = '';
    descriptionDiv.appendChild(textarea);
    descriptionDiv.appendChild(saveButton);
    editButton.style.display = 'none';
}

async function saveCourseDescription(courseId, context) {
    const descriptionDiv = document.querySelector(`#courseDescription${courseId}`);
    const textarea = descriptionDiv.querySelector('textarea');
    const editButton = document.querySelector(`.editDescription[data-course-id="${courseId}"]`);
    const newDescription = textarea.value;

    try {
        const response = await fetch(`/${context.eatery}/menu/update_course/${courseId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                description: newDescription
            })
        });

        if (!response.ok) throw new Error('Network response was not ok');

        // Update UI
        descriptionDiv.textContent = newDescription;
        editButton.style.display = '';
    } catch (error) {
        console.error('Error:', error);
        alert('Error saving description. Please try again.');
    }
}

async function editCourseNote(courseId, context) {
    const noteDiv = document.querySelector(`#courseNote${courseId}`);
    const currentNote = noteDiv.textContent.trim();
    const editButton = document.querySelector(`.editNote[data-course-id="${courseId}"]`);

    // Create and show textarea
    const textarea = document.createElement('textarea');
    textarea.value = currentNote;
    textarea.className = 'w-full p-2 border rounded';
    textarea.rows = 3;

    // Create save button
    const saveButton = document.createElement('button');
    saveButton.textContent = 'Save';
    saveButton.className = 'saveNote px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded transition-colors duration-200 mt-2';
    saveButton.dataset.courseId = courseId;

    // Replace content and hide edit button
    noteDiv.textContent = '';
    noteDiv.appendChild(textarea);
    noteDiv.appendChild(saveButton);
    editButton.style.display = 'none';
}

async function saveCourseNote(courseId, context) {
    const noteDiv = document.querySelector(`#courseNote${courseId}`);
    const textarea = noteDiv.querySelector('textarea');
    const editButton = document.querySelector(`.editNote[data-course-id="${courseId}"]`);
    const newNote = textarea.value;

    try {
        const response = await fetch(`/${context.eatery}/menu/update_course/${courseId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                note: newNote
            })
        });

        if (!response.ok) throw new Error('Network response was not ok');

        // Update UI
        noteDiv.textContent = newNote;
        editButton.style.display = '';
    } catch (error) {
        console.error('Error:', error);
        alert('Error saving note. Please try again.');
    }
}

function showSideOptionForm(courseId, context, sideOption = null) {
    const listContainer = document.getElementById(`sideOptionsList${courseId}`);
    if (!listContainer) return;

    const formDiv = document.createElement('div');
    formDiv.className = 'bg-white p-4 rounded-lg shadow mb-4';
    formDiv.innerHTML = `
        <form id="${sideOption ? 'editSideOption' : 'createSideOption'}" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700">Name</label>
                <input type="text" name="name" value="${sideOption?.name || ''}" 
                       class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500" required>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Description (optional)</label>
                <textarea name="description" rows="2" 
                          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500"
                >${sideOption?.description || ''}</textarea>
            </div>
            <div class="flex items-center space-x-4">
                <div class="flex items-center">
                    <input type="checkbox" name="is_premium" id="is_premium" 
                           ${sideOption?.is_premium ? 'checked' : ''}
                           class="h-4 w-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500">
                    <label for="is_premium" class="ml-2 block text-sm text-gray-900">Premium Option</label>
                </div>
                <div class="premium-price ${sideOption?.is_premium ? '' : 'hidden'}">
                    <label class="block text-sm font-medium text-gray-700">Additional Price</label>
                    <input type="number" name="price" value="${sideOption?.price || ''}" step="0.01" min="0"
                           class="mt-1 block w-24 rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500">
                </div>
            </div>
            <div class="flex justify-end space-x-2">
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
    listContainer.appendChild(formDiv);

    // Handle premium checkbox toggle
    const premiumCheckbox = formDiv.querySelector('#is_premium');
    const priceDiv = formDiv.querySelector('.premium-price');
    premiumCheckbox.addEventListener('change', () => {
        priceDiv.classList.toggle('hidden', !premiumCheckbox.checked);
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
            const url = sideOption ? 
                `/${context.eatery}/menu/side_options/${sideOption.id}/` :
                `/${context.eatery}/menu/side_options/create/`;
                
            const response = await fetch(url, {
                method: sideOption ? 'PUT' : 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) throw new Error('Network response was not ok');
            
            // Update the side options list
            await updateSideOptionsList(courseId, context);
            
            // Remove the form
            formDiv.remove();
            if (buttonContainer) {
                buttonContainer.style.display = '';
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error saving side option. Please try again.');
        }
    });
}

async function editSideOption(sideId, context) {
    try {
        const response = await fetch(`/${context.eatery}/menu/side_options/${sideId}/`);
        if (!response.ok) throw new Error('Network response was not ok');
        
        const sideOption = await response.json();
        const courseId = sideOption.course_id;
        
        // Hide the side option element temporarily
        const sideElement = document.getElementById(`sideOption${sideId}`);
        if (sideElement) {
            sideElement.style.display = 'none';
        }
        
        // Show the edit form
        showSideOptionForm(courseId, context, {
            id: sideId,
            name: sideOption.name,
            description: sideOption.description,
            is_premium: sideOption.is_premium,
            price: sideOption.price
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
        const response = await fetch(`/${context.eatery}/menu/side_options/${sideId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const result = await response.json();
        
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
        const response = await fetch(`/${context.eatery}/menu/side_options/${courseId}/`);
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

        // Add the button container
        const buttonContainer = document.createElement('div');
        buttonContainer.id = `addSideButtonContainer${courseId}`;
        buttonContainer.className = 'flex justify-end mt-2';
        buttonContainer.innerHTML = `
            <button class="addSideOption text-sm px-3 py-1 bg-green-500 hover:bg-green-600 text-white rounded"
                    data-course-id="${courseId}">
                Add Side
            </button>
        `;
        const parentContainer = listContainer.parentElement;
        parentContainer.appendChild(buttonContainer);

    } catch (error) {
        console.error('Error:', error);
        alert('Error updating side options list. Please try again.');
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    try {
        await initializeMenuBuilder();
    } catch (error) {
        console.error('Failed to initialize menu builder:', error);
        alert('Error initializing menu builder. Please refresh the page.');
    }
});