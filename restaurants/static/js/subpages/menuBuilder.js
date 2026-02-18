import { api } from '../utils/subpagesAPI.js';
import { showToast } from '../components/toast.js';
import { debounce, throttle } from '../utils/debounce.js';
// import { showSideOptionForm, editSideOption, deleteSideOption, updateSideOptionsList } from './menuHandlers/sideOptions.js';

// initializer
async function initializeMenuBuilder() {
    try {
        // Get required elements
        const kitchenConfig = JSON.parse(document.getElementById('business').textContent);
        const existingCourses = JSON.parse(document.getElementById('existing_courses').textContent);

        if (!kitchenConfig) {
            throw new Error('Required kitchen configuration not found');
        }

        // Create context object
        const context = {
            eatery: kitchenConfig,
            accordionTriggers: document.querySelectorAll('.accordion-trigger'),
            existingCourses: existingCourses,
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

// initializer
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
    // Throttle click handler to prevent rapid-fire clicks
    document.addEventListener('click', throttle((e) => handleClicks(e, context), 500));
}

function handleClicks(e, context) {
    // Add Course button
    if (e.target.matches('#add')) {
        e.preventDefault();
        const submission = document.querySelector('#addCourse');
        addCourse(submission.value, context, context.existingCourses);
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
        <form id="${isEdit ? 'editDish' + dishId : 'createDish'}" class="border-4 border-rose-300 shadow-lg rounded-lg p-4 mb-4 grid md:grid-cols-3 gap-4">
            <div class="text-center">
                <input type="text" 
                    class="border-4 border-rose-300 shadow-lg text-xl font-bold mb-2 w-fit mx-auto text-center bg-transparent rounded-lg focus:border-rose-500 focus:outline-none"
                    placeholder="Name of Dish" 
                    id="${isEdit ? 'dishName' + dishId : 'dishName'}"
                    value="${isEdit ? currentValues.name : ''}" 
                    required>
                
                <div class="relative h-40 w-40 mx-auto border-4 border-rose-300 shadow-lg rounded-lg w-fit h-auto">
                    ${isEdit && currentValues.image ? `
                        <img src="${currentValues.image}" class="mx-auto object-contain h-40 w-40" alt="Current image" id="previewImage${dishId}">
                    ` : `
                        <div class="h-40 w-40 mx-auto flex items-center justify-center bg-gray-100 rounded-lg border-2 border-dashed border-gray-300" id="previewImage${dishId}">
                            <span class="text-gray-400">No Image</span>
                        </div>
                    `}
                    <input type="file" 
                        class="absolute inset-0 opacity-0 cursor-pointer w-40"
                        accept="image/*"
                        id="${isEdit ? 'dishImage' + dishId : 'dishImage'}">
                </div>
                
                <div class="mt-2 font-semibold flex items-center justify-center gap-1">
                    <span>Price: $</span>
                    <input type="number" 
                        class="border-4 border-rose-300 shadow-lg w-20 text-center bg-transparent focus:border-rose-500 focus:outline-none"
                        placeholder="0.00" 
                        step="any" 
                        id="${isEdit ? 'dishPrice' + dishId : 'dishPrice'}"
                        value="${isEdit ? currentValues.price : ''}" 
                        required>
                </div>
            </div>

            <div class="text-center">
                <h4 class="font-semibold mb-2">Description:</h4>
                <textarea class="border-4 border-rose-300 shadow-lg w-full bg-transparent border-gray-300 rounded-md focus:border-emerald-500 focus:border-rose-500 focus:outline-none min-h-[100px]" 
                        id="${isEdit ? 'dishDescription' + dishId : 'dishDescription'}" 
                        placeholder="Description">${isEdit ? currentValues.description : ''}</textarea>
            </div>

            <div class="md:text-right flex md:justify-end items-center space-x-2">
                <button type="submit" 
                        class="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded transition-colors duration-200">
                    ${isEdit ? 'Save Changes' : 'Add Dish'}
                </button>
                <button type="button" 
                        class="${isEdit ? 'cancel-edit' : 'cancel-add'} px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded transition-colors duration-200">
                    Cancel
                </button>
            </div>
        </form>
    `;
}

function previewImage(input, previewId) {
    const preview = document.getElementById(previewId);
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            if (preview.tagName === 'IMG') {
                preview.src = e.target.result;
            } else {
                // Replace the no-image div with an img
                const img = document.createElement('img');
                img.src = e.target.result;
                img.className = 'mx-auto object-contain h-40 w-40';
                img.id = previewId;
                preview.parentNode.replaceChild(img, preview);
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
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
                    id="e${dishId}">
                Edit
            </button>
            <button class="deleteDish px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded transition-colors duration-200" 
                    id="d${dishId}">
                Delete
            </button>
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

async function addCourse(dishData, context, existingCourses) {
    if (existingCourses.map(course => course.toLowerCase()).includes(dishData.toLowerCase())) {
        alert('A course with this name already exists. Please choose a different name.');
        return;
    }
    try {
        await api.menu.addCourse(context.eatery, { course_name: dishData });
        window.location.href = window.location.pathname + '?t=' + Date.now();
    } catch (error) {
        console.error('Error:');
        showToast('Error adding course. Please try again.');
    }
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
    const imageInput = formDiv.querySelector('#dishImage');
    const previewId = 'previewImage';
    imageInput.addEventListener('change', function() {
        previewImage(this, previewId);
    });
    formDiv.querySelector('.cancel-add').addEventListener('click', () => {
        buttonContainer.style.display = '';
        formDiv.remove();
    });

    const submitHandler = throttle(async (event) => {
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
            const data = await api.menu.addDish(context.eatery, formData);
            // const response = await fetch(`/${context.eatery}/menu/add_dish/`, {
            //     method: 'POST',
            //     headers: {
            //         'Content-Type': 'application/json',
            //         'X-CSRFToken': context.csrfToken
            //     },
            //     body: JSON.stringify(formData)
            // });

            // const data = await response.json();
            // if (!response.ok) {
            //     throw new Error(data.error);
            // }

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
    }, 2000); // Prevent submissions within 2 seconds of each other

    formDiv.querySelector('#createDish').addEventListener('submit', submitHandler);
}

async function editDish(dishId, context) {
    try {
        const dishElement = document.getElementById(`o${dishId}`);
        if (!dishElement) {
            console.error('Could not find dish element');
            return;
        }
    
        // Get current dish data
        const currentValues = {
            name: dishElement.querySelector('h3')?.textContent || '',
            price: dishElement.querySelector('.font-semibold')?.textContent.replace('Price: $', '') || '',
            image: dishElement.querySelector('img')?.src || '',
            description: dishElement.querySelector('[data-dish-description]')?.textContent?.trim() || 
                        dishElement.querySelector('p')?.textContent?.trim() || '',
        };
        // Create edit form
        const editDiv = document.createElement('div');
        editDiv.innerHTML = getFormHTML(true, dishId, currentValues);

        // Store the original dish element
        editDiv.originalDish = dishElement;

        // Replace dish with form
        dishElement.replaceWith(editDiv);


        const imageInput = editDiv.querySelector(`#dishImage${dishId}`);
        const previewId = `previewImage${dishId}`;
        imageInput.addEventListener('change', function() {
            previewImage(this, previewId);
        });    
        // Add cancel button functionality
        editDiv.querySelector('.cancel-edit').addEventListener('click', () => {
            editDiv.replaceWith(dishElement);
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
                const data = await api.menu.editDish(context.eatery, dishId, formData);
                // const response = await fetch(`/${context.eatery}/menu/edit_dish/${dishId}/`, {
                //     method: 'POST',
                //     headers: {
                //         'Content-Type': 'application/json',
                //         'X-CSRFToken': context.csrfToken
                //     },
                //     body: JSON.stringify(formData)
                // });

                // const data = await response.json();
                editDiv.className = 'border rounded-lg p-4 mb-4 grid md:grid-cols-3 gap-4';
                editDiv.innerHTML = createDishHTML(dishId, formData, data.image_url);
                showToast('Dish updated successfully');
            } catch (error) {
                console.error('Error:', error);
                alert(error.message || 'Error updating dish. Please try again.');
                }
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
        await api.menu.deleteDish(context.eatery, dishId);
        showToast('Dish deleted successfully');
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
        await api.menu.deleteCourse(context.eatery, courseId);
        showToast('Course deleted successfully');
        // Find and remove the course section
        const courseSection = document.querySelector(`[data-course-id="${courseId}"]`).closest('.course-container');
        const courseName = courseSection.querySelector('h2')?.textContent?.trim();
        if (courseName) {
            // Remove from in-memory list so "add course" duplicate check allows adding it again
            if (Array.isArray(context.existingCourses)) {
                context.existingCourses = context.existingCourses.filter(
                    c => (typeof c === 'string' ? c : c.name || '').toLowerCase() !== courseName.toLowerCase()
                );
            }
            // Add deleted course back to the "Add a Course" dropdown
            const addSelect = document.getElementById('addCourse');
            if (addSelect && !Array.from(addSelect.options).some(o => o.value.toLowerCase() === courseName.toLowerCase())) {
                const option = document.createElement('option');
                option.value = courseName;
                option.textContent = courseName;
                addSelect.appendChild(option);
            }
        }  
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

async function editCourseDescription(courseId) {
    const displayDiv = document.getElementById(`descriptionDisplay${courseId}`);
    const formDiv = document.getElementById(`descriptionForm${courseId}`);
    
    if (!displayDiv || !formDiv) {
        console.error('Required elements not found');
        return;
    }
    
    // Show form, hide display
    displayDiv.classList.add('hidden');
    formDiv.classList.remove('hidden');
    
    // Set textarea value to current description
    const currentDescription = displayDiv.querySelector('p')?.textContent?.trim() || '';
    const textarea = document.getElementById(`courseDescription${courseId}`);
    if (textarea) {
        textarea.value = currentDescription;
        textarea.focus(); // Automatically focus the textarea for better UX
    }
}


async function saveCourseDescription(courseId, context) {
    const formDiv = document.getElementById(`descriptionForm${courseId}`);
    const displayDiv = document.getElementById(`descriptionDisplay${courseId}`);
    const textarea = document.getElementById(`courseDescription${courseId}`);
    if (!formDiv || !textarea) {
        console.error('Could not find description form or textarea');
        return;
    }
    const newDescription = textarea.value;
    try {
        await api.menu.updateCourseDescription(context.eatery, courseId, { description: newDescription });
        showToast('Course description updated successfully');
        // Update display content in place (like home.js welcome)
        const displayContent = displayDiv.querySelector('.flex.justify-between') || displayDiv;
        const p = displayDiv.querySelector('p');
        if (p) {
            p.textContent = newDescription || 'No description added yet.';
        } else {
            displayDiv.innerHTML = `
                <div class="flex justify-between items-start gap-4">
                    <p class="text-gray-600">${newDescription || 'No description added yet.'}</p>
                    <button class="editDescription text-blue-500 hover:text-blue-700 flex-shrink-0" data-course-id="${courseId}">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">...</svg>
                    </button>
                </div>
            `;
            displayDiv.querySelector('.editDescription').addEventListener('click', () => editCourseDescription(courseId, context));
        }
        displayDiv.classList.remove('hidden');
        formDiv.classList.add('hidden');
    } catch (error) {
        console.error('Error:', error);
        showToast('Error saving description. Please try again.');
    }
}

function editCourseNote(courseId) {
    const displayDiv = document.getElementById(`noteDisplay${courseId}`);
    const formDiv = document.getElementById(`noteForm${courseId}`);

    if (!displayDiv || !formDiv) {
        console.error('Required elements not found');
        return;
    }
    // Show form, hide display
    displayDiv.classList.add('hidden');
    formDiv.classList.remove('hidden');
    
    // Set textarea value to current note
    const currentNote = displayDiv.querySelector('p')?.textContent?.trim() || '';
    const textarea = document.getElementById(`courseNote${courseId}`);
    if (textarea) {
        textarea.value = currentNote;
        textarea.focus();
    }
}

async function saveCourseNote(courseId, context) {
    const formDiv = document.getElementById(`noteForm${courseId}`);
    const displayDiv = document.getElementById(`noteDisplay${courseId}`);
    const textarea = document.getElementById(`courseNote${courseId}`);
    if (!formDiv || !textarea) {
        console.error('Could not find note form or textarea');
        return;
    }
    const newNote = textarea.value;
    try {
        await api.menu.updateCourseNote(context.eatery, courseId, { note: newNote });
        showToast('Course note updated successfully');
        // Update display content in place (same pattern as welcome / course description)
        let targetDisplay = displayDiv;
        if (!displayDiv) {
            targetDisplay = document.createElement('div');
            targetDisplay.id = `noteDisplay${courseId}`;
            targetDisplay.className = 'mt-2';
            formDiv.parentElement.insertBefore(targetDisplay, formDiv);
        }
        const p = targetDisplay.querySelector('p');
        if (p) {
            p.textContent = newNote || 'No note added yet.';
        } else {
            targetDisplay.innerHTML = `
                <div class="flex justify-between items-start gap-4">
                    <p class="text-gray-600">${newNote || 'No note added yet.'}</p>
                    <button class="editNote text-blue-500 hover:text-blue-700 flex-shrink-0" data-course-id="${courseId}">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                        </svg>
                    </button>
                </div>
            `;
            targetDisplay.querySelector('.editNote').addEventListener('click', () => editCourseNote(courseId, context));
        }
        targetDisplay.classList.remove('hidden');
        formDiv.classList.add('hidden');
    } catch (error) {
        console.error('Error:', error);
        alert('Error saving note. Please try again.');
    }
}

function showSideOptionForm(courseId, context, sideOption = null) {
    console.log(courseId, context, sideOption);
    const formDiv = document.getElementById(`sideOptionsForm${courseId}`);
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


document.addEventListener('DOMContentLoaded', async () => {
    try {
        await initializeMenuBuilder();
    } catch (error) {
        console.error('Failed to initialize menu builder:', error);
        alert('Error initializing menu builder. Please refresh the page.');
    }
});