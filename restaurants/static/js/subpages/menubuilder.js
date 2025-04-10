document.addEventListener('DOMContentLoaded', function() {
    const eatery = JSON.parse(document.getElementById('kitchen').textContent);
    const existingCourses = JSON.parse(document.getElementById('existing_courses').textContent);
    const accordionTriggers = document.querySelectorAll('.accordion-trigger');
    
    accordionTriggers.forEach(trigger => {
        trigger.addEventListener('click', () => {
            const target = document.getElementById(trigger.dataset.target);
            const arrow = trigger.querySelector('svg'); // Select the arrow icon
    
            // Toggle panel visibility
            target.classList.toggle('hidden');
    
            // Rotate the arrow based on panel's visibility
            if (target.classList.contains('hidden')) {
                trigger.classList.remove('bg-gray-100', 'hover:bg-gray-400'); 
                trigger.classList.add('bg-white', 'hover:bg-gray-400');
                arrow.classList.remove('rotate-90'); // Reset rotation when hidden
            } else {
                trigger.classList.remove('bg-white', 'hover:bg-gray-50'); // Open state
                trigger.classList.add('bg-gray-100', 'hover:bg-gray-400');
                arrow.classList.add('rotate-90'); // Apply rotation when open
            }
    
            // Optional: Close other panels if needed
            // accordionTriggers.forEach(otherTrigger => {
            //     if (otherTrigger !== trigger) {
            //         const otherTarget = document.getElementById(otherTrigger.dataset.target);
            //         const otherArrow = otherTrigger.querySelector('svg');
            //         otherTarget.classList.add('hidden');
            //         otherArrow.classList.remove('rotate-90');
            //     }
            // });
        });
    });
    document.addEventListener('click', function(e) {
        // Add Course button
        if (e.target.matches('#add')) {
            e.preventDefault();
            const submission = document.querySelector('#addCourse');
            addCourse(submission.value, eatery, existingCourses);
        }

        // Submit Dish button
        if (e.target.matches('.submitDish')) {
            addDish(e.target.id);
        }

        // Edit Dish button
        if (e.target.matches('.editDish')) {
            const itemId = e.target.id.replace('e', '');
            editDish(itemId);
        }

        // Delete Dish button
        if (e.target.matches('.deleteDish')) {
            const dishId = e.target.id.replace('d', '');
            deleteDish(dishId);
        }

        // Delete Course button
        if (e.target.closest('.deleteCourse')) {
            const courseId = e.target.closest('.deleteCourse').getAttribute('data-course-id');
            deleteCourse(courseId);
        }
        if (e.target.matches('.editDescription') || e.target.closest('.editDescription')) {
            const button = e.target.closest('.editDescription') || e.target;
            const courseId = button.dataset.courseId;
            editCourseDescription(courseId);
        }

        // Save Description button
        if (e.target.matches('.saveDescription')) {
            const courseId = e.target.dataset.courseId;
            saveCourseDescription(courseId);
        }
        // Edit Note button
        if (e.target.matches('.editNote') || e.target.closest('.editNote')) {
            const button = e.target.closest('.editNote') || e.target;
            const courseId = button.dataset.courseId;
            editCourseNote(courseId);
        }

        // Save Note button
        if (e.target.matches('.saveNote')) {
            const courseId = e.target.dataset.courseId;
            saveCourseNote(courseId);
        }
        // Add Side Option button
        if (e.target.matches('.addSideOption')) {
            const courseId = e.target.dataset.courseId;
            showSideOptionForm(courseId);
        }

        // Edit Side Option button
        if (e.target.closest('.editSideOption')) {
            const sideId = e.target.closest('.editSideOption').dataset.sideId;
            editSideOption(sideId);
        }

        // Delete Side Option button
        if (e.target.closest('.deleteSideOption')) {
            const sideId = e.target.closest('.deleteSideOption').dataset.sideId;
            deleteSideOption(sideId);
        }
    });
});

const getFormHTML = (isEdit = false, dishId = '', currentValues = {}) => `
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

function handleImageUpload(fileInput) {
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

function addCourse(dishData, currentKitchen, existingCourses){
    if (existingCourses.map(course => course.toLowerCase()).includes(dishData.toLowerCase())) {
        alert('A course with this name already exists. Please choose a different name.');
        return;
    }

    fetch(`/${currentKitchen}/menu/add_course/`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            course_name: dishData
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(result => {
        location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Add this function to get CSRF token
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

function addDish(course) {
    let currentCourse = course.replace('submit', "");
    let addButton = document.getElementById(course);
    
    // Find the correct panel by traversing up and then finding the container
    let parentPanel = addButton.closest('.accordion-collapse') || addButton.closest('[id^="panel"]');
    
    if (!parentPanel) {
        console.error('Could not find parent panel');
        return;
    }

    // Store the original button's parent
    // const buttonContainer = addButton.parentNode;

    const buttonContainer = addButton.closest('.text-center');
    const deleteButton = buttonContainer.querySelector('.deleteCourse');
    buttonContainer.style.display = 'none';

    let formDiv = document.createElement('div');
    formDiv.innerHTML = getFormHTML(false);
    buttonContainer.parentNode.insertBefore(formDiv, buttonContainer);
    // Replace the button with the form
    // addButton.replaceWith(formDiv);

    // Add cancel button functionality
    formDiv.querySelector('.cancel-add').addEventListener('click', () => {
        // Restore the button to its original container
        buttonContainer.appendChild(addButton);
        formDiv.remove();
    });

    document.querySelector('#createDish').addEventListener('submit', async (event) => {
        event.preventDefault();
        
        const formData = {
            name: document.querySelector("#dishName").value,
            price: document.querySelector("#dishPrice").value,
            description: document.querySelector("#dishDescription").value,
            course: currentCourse
        };

        // Get the image data if it exists
        const imageInput = document.querySelector('#dishImage');
        if (imageInput && imageInput.files[0]) {
            const imageData = await handleImageUpload(imageInput);
            formData.image = imageData;
        }

        fetch(`/${eatery}/menu/add_dish/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(formData)
        })
        .then(async response => {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error);
            }
            return data;
        })
        .then(result => {
            const newDishArticle = document.createElement('article');
            newDishArticle.id = `o${result.dish_id}`;
            newDishArticle.className = 'border rounded-lg p-4 mb-4 grid md:grid-cols-3 gap-4';
            
            newDishArticle.innerHTML = createDishHTML(result.dish_id, formData, result.image_url);

            // Insert the new dish before the button container
            buttonContainer.insertAdjacentElement('beforebegin', newDishArticle);
            
            // Show the original button container
            buttonContainer.style.display = '';
            formDiv.remove();
        })
        .catch(error => {
            console.error('Error:', error);
            // Show the original button container on error
            buttonContainer.style.display = '';
            formDiv.remove();
            alert(error.message || 'Error adding dish. Please try again.');
        });
    });
}

function restoreAddButton(course, currentCourse, formDiv) {
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'text-center space-y-2 mt-4';
    buttonContainer.innerHTML = `
        <button id="${course}" 
                class="submitDish w-full md:w-96 px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded transition-colors duration-200">
            Add a dish to ${currentCourse}
        </button>
    `;
    
    // Add the click event listener to the new button
    buttonContainer.querySelector('.submitDish').addEventListener('click', () => addDish(course));
    
    // Replace the form with the button
    formDiv.replaceWith(buttonContainer);
}

// function restoreAddButton(course, currentCourse) {
//     const swapDiv = document.querySelector('#createDish').parentElement;
//     const addButton = document.createElement('button');
//     addButton.id = course;
//     addButton.className = 'submitDish text-center w-60 rounded m-2 bg-emerald-300 md:w-96';
//     addButton.textContent = `Add a dish to ${currentCourse}`;
//     addButton.addEventListener('click', () => addDish(course));
//     swapDiv.replaceWith(addButton);
// }

function cancelAdd(course) {
    const currentCourse = course.replace('submit', "");
    restoreAddButton(course, currentCourse);
}
//click to open a form with prefilled information for editing
function editDish(dishId) {
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
        description: dishElement.querySelector('div:nth-child(2) p')?.textContent || '',
    };

    // Create edit form
    const editDiv = document.createElement('div');
    editDiv.className = 'p-4';
    editDiv.innerHTML = getFormHTML(true, dishId, currentValues);

    // Store the original dish element
    editDiv.originalDish = dishElement;

    // Replace dish with form
    dishElement.replaceWith(editDiv);

    // Add cancel button functionality
    editDiv.querySelector('.cancel-edit').addEventListener('click', () => {
        editDiv.replaceWith(dishElement);
    });

    // Add form submission handler
    document.querySelector(`#editDish${dishId}`).addEventListener('submit', async (event) => {
        event.preventDefault();
        const imageInput = document.querySelector(`#dishImage${dishId}`);
        const imageData = await handleImageUpload(imageInput);
        // const eatery = JSON.parse(document.getElementById('kitchen').textContent);

        const formData = {
            name: document.querySelector(`#dishName${dishId}`).value,
            price: document.querySelector(`#dishPrice${dishId}`).value,
            image: imageData,
            description: document.querySelector(`#dishDescription${dishId}`).value
        };

        fetch(`/${eatery}/menu/edit_dish/${dishId}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(formData)
        })
        .then(async response => {
            if (!response.ok) {
                // Get the error message from the response
                const errorData = await response.json();
                throw new Error(errorData.error || 'Network response was not ok');
            }
            return response.json();
        })
        .then(result => {
            // Update the dish element with new data
            const updatedDish = document.createElement('article');
            updatedDish.id = `o${dishId}`;
            updatedDish.className = 'border rounded-lg p-4 mb-4 grid md:grid-cols-3 gap-4';
            
            updatedDish.innerHTML = createDishHTML(dishId, formData, result.image_url);

            // Replace form with updated dish
            editDiv.replaceWith(updatedDish);
        })
        .catch(error => {
            console.error('Error:', error);
            if (error.message) {
                // If we already have an error message (from our throw new Error(data.error))
                alert(error.message);
            } else {
                alert('Error updating dish. Please try again.');
            }
        });
    });
}

function submitChanges(dishid) {
    fetch("/edit_dish/" + dishid, {
        method: 'POST',
        body: JSON.stringify({
            description: document.querySelector('#dishDescription').value,
            name: document.querySelector('#dishName').value,
            price: document.querySelector('#dishPrice').value,
            image: document.querySelector('#dishImage').value,
        })
    })
    .then(result => {
        location.reload()
    })
};

function deleteDish(dishId) {
    if (!confirm('Are you sure you want to delete this dish?')) {
        return;
    }

    const dishElement = document.getElementById(`o${dishId}`);
    if (!dishElement) {
        console.error('Could not find dish element');
        return;
    }

    // Add loading state
    dishElement.style.opacity = '0.5';
    const buttons = dishElement.querySelectorAll('button');
    buttons.forEach(button => button.disabled = true);

    fetch(`/delete_dish/${dishId}`, {
        method: "DELETE",
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
    .then(result => {
        // Animate the removal
        dishElement.style.transition = 'all 0.3s ease-out';
        dishElement.style.transform = 'translateX(100%)';
        dishElement.style.opacity = '0';
        
        setTimeout(() => {
            dishElement.remove();
            
            // Check if this was the last dish in the course
            const parentPanel = dishElement.closest('.accordion-body');
            const remainingDishes = parentPanel.querySelectorAll('article').length;
            
            if (remainingDishes === 0) {
                // Add "No dishes" message
                const emptyMessage = document.createElement('p');
                emptyMessage.className = 'text-gray-500 text-center py-4';
                emptyMessage.textContent = 'No dishes available for this course.';
                
                // Insert before the "Add dish" button
                const addButton = parentPanel.querySelector('.text-center');
                parentPanel.insertBefore(emptyMessage, addButton);
            }
        }, 300); // Match this with the CSS transition time
    })
    .catch(error => {
        console.error('Error:', error);
        // Restore the dish element state
        dishElement.style.opacity = '1';
        buttons.forEach(button => button.disabled = false);
        alert('Error deleting dish. Please try again.');
    });
}

// function deleteCourse(course) {
//     const eatery = JSON.parse(document.getElementById('kitchen').textContent);
//     fetch('/delete_course/' + eatery + "/" + course, {method: "GET"})
//     .then(result => {
//         location.reload()
//     });
// };

function deleteCourse(courseId) {
    if (!confirm('Are you sure you want to delete this course? This will delete all dishes in this course.')) {
        return;
    }

    const courseElement = document.getElementById(`delete${courseId}`).closest('.mb-4');
    const courseName = courseElement.querySelector('.accordion-trigger h2').textContent.trim();
    
    // Add loading state
    courseElement.style.opacity = '0.5';
    const buttons = courseElement.querySelectorAll('button');
    buttons.forEach(button => button.disabled = true);

    fetch(`/${eatery}/menu/delete_course/${courseId}/`, {
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
    .then(result => {
        // Animate the course removal
        courseElement.style.transition = 'all 0.3s ease-out';
        courseElement.style.transform = 'translateX(100%)';
        courseElement.style.opacity = '0';
        
        // Remove the course from existingCourses array
        const courseIndex = existingCourses.findIndex(course => 
            course.toLowerCase() === courseName.toLowerCase()
        );
        if (courseIndex > -1) {
            existingCourses.splice(courseIndex, 1);
        }

        // Add the course back to the dropdown
        const dropdown = document.getElementById('addCourse');
        const option = document.createElement('option');
        option.value = courseName;
        option.textContent = courseName;
        
        // Insert the option in alphabetical order
        const options = Array.from(dropdown.options);
        const insertIndex = options.findIndex(opt => 
            opt.text.toLowerCase() > courseName.toLowerCase()
        );
        
        if (insertIndex === -1) {
            dropdown.appendChild(option); // Add to end if it should go last
        } else {
            dropdown.insertBefore(option, dropdown.options[insertIndex]); // Insert at correct position
        }

        setTimeout(() => {
            courseElement.remove();
        }, 300);
    })
    .catch(error => {
        console.error('Error:', error);
        courseElement.style.opacity = '1';
        buttons.forEach(button => button.disabled = false);
        alert('Error deleting course. Please try again.');
    });
}

function editCourseDescription(courseId) {
    const displayDiv = document.getElementById(`descriptionDisplay${courseId}`);
    const formDiv = document.getElementById(`descriptionForm${courseId}`);
    
    // Show form, hide display
    displayDiv.classList.add('hidden');
    formDiv.classList.remove('hidden');
    
    // Set textarea value to current description
    const currentDescription = displayDiv.querySelector('p').textContent;
    document.getElementById(`courseDescription${courseId}`).value = currentDescription;
}

function saveCourseDescription(courseId) {
    // const eatery = JSON.parse(document.getElementById('kitchen').textContent);
    
    fetch(`/${eatery}/menu/update_course_description/${courseId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            description: document.querySelector(`#courseDescription${courseId}`).value
        })
    })
    .then(response => response.json())
    .then(result => {
        const description = document.querySelector(`#courseDescription${courseId}`).value;
        
        // Find the parent container - try both possible parent elements
        let parentContainer = document.getElementById(`descriptionForm${courseId}`);
        if (!parentContainer) {
            console.error('Could not find description form');
            return;
        }
        parentContainer = parentContainer.parentElement;
        
        // Create new container
        const containerDiv = document.createElement('div');
        containerDiv.className = 'mb-4';
        
        // Create display div
        const displayDiv = document.createElement('div');
        displayDiv.id = `descriptionDisplay${courseId}`;
        displayDiv.classList.remove('hidden');
        displayDiv.innerHTML = `
            <div class="flex justify-between items-start gap-4">
                <p class="text-gray-600">${description || 'No description added yet.'}</p>
                <button class="editDescription text-blue-500 hover:text-blue-700 flex-shrink-0"
                        data-course-id="${courseId}">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                    </svg>
                </button>
            </div>
        `;

        // Create form div (hidden)
        const formDiv = document.createElement('div');
        formDiv.id = `descriptionForm${courseId}`;
        formDiv.className = 'mt-2 hidden';
        formDiv.innerHTML = `
            <textarea id="courseDescription${courseId}" 
                    class="w-full p-2 border rounded"
                    rows="3"
                    placeholder="Add a description for this course">${description}</textarea>
            <button class="saveDescription mt-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded transition-colors duration-200"
                    data-course-id="${courseId}">
                Save Description
            </button>
        `;

        // Add both divs to container
        containerDiv.appendChild(displayDiv);
        containerDiv.appendChild(formDiv);

        // Replace the entire parent container
        parentContainer.replaceWith(containerDiv);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating description. Please try again.');
    });
}

// Add these new functions
function editCourseNote(courseId) {
    const displayDiv = document.getElementById(`noteDisplay${courseId}`);
    const formDiv = document.getElementById(`noteForm${courseId}`);
    
    // Show form, hide display
    displayDiv.classList.add('hidden');
    formDiv.classList.remove('hidden');
    
    // Set textarea value to current note
    const currentNote = displayDiv.querySelector('p').textContent;
    document.getElementById(`courseNote${courseId}`).value = currentNote;
}

function saveCourseNote(courseId) {
    // const eatery = JSON.parse(document.getElementById('kitchen').textContent);
    
    fetch(`/${eatery}/menu/update_course_note/${courseId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            note: document.querySelector(`#courseNote${courseId}`).value
        })
    })
    .then(response => response.json())
    .then(result => {
        const note = document.querySelector(`#courseNote${courseId}`).value;
        
        // Find the parent container
        const parentContainer = document.getElementById(`noteForm${courseId}`).parentElement;
        
        // Create new container
        const containerDiv = document.createElement('div');
        containerDiv.className = 'mb-4';
        
        // Create display div
        const displayDiv = document.createElement('div');
        displayDiv.id = `noteDisplay${courseId}`;
        displayDiv.classList.remove('hidden');
        displayDiv.innerHTML = `
            <div class="flex justify-between items-start gap-4">
                <p class="text-gray-600">${note || 'No note added yet.'}</p>
                <button class="editNote text-blue-500 hover:text-blue-700 flex-shrink-0"
                        data-course-id="${courseId}">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                    </svg>
                </button>
            </div>
        `;

        // Create form div (hidden)
        const formDiv = document.createElement('div');
        formDiv.id = `noteForm${courseId}`;
        formDiv.className = 'mt-2 hidden';
        formDiv.innerHTML = `
            <textarea id="courseNote${courseId}" 
                    class="w-full p-2 border rounded"
                    rows="3"
                    placeholder="Add a note for this course">${note}</textarea>
            <button class="saveNote mt-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded transition-colors duration-200"
                    data-course-id="${courseId}">
                Save Note
            </button>
        `;

        // Add both divs to container
        containerDiv.appendChild(displayDiv);
        containerDiv.appendChild(formDiv);

        // Replace the entire parent container
        parentContainer.replaceWith(containerDiv);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating note. Please try again.');
    });
}

function showSideOptionForm(courseId, sideOption = null) {
    const buttonContainer = document.getElementById(`addSideButtonContainer${courseId}`);
    // Create a new div for the form instead of replacing existing content
    const formDiv = document.createElement('div');
    formDiv.id = `addSideButtonContainer${courseId}`; // Keep the same ID
    formDiv.className = 'bg-white p-4 rounded-lg border mt-2';
    
    formDiv.innerHTML = `
        <h3 class="text-lg font-semibold mb-4">${sideOption ? 'Edit' : 'Add'} Side Option</h3>
        <form id="sideOptionForm" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700">Name</label>
                <input type="text" id="sideName" 
                       class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                       value="${sideOption ? sideOption.name : ''}" required>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Description</label>
                <textarea id="sideDescription" 
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        rows="2">${sideOption ? sideOption.description || '' : ''}</textarea>
            </div>
            <div class="flex items-center gap-4">
                <div class="flex items-center">
                    <input type="checkbox" id="isPremium" 
                           class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                           ${sideOption && sideOption.is_premium ? 'checked' : ''}>
                    <label class="ml-2 text-sm text-gray-700">Premium Side</label>
                </div>
                <div class="flex-1" id="priceField" ${sideOption && sideOption.is_premium ? '' : 'hidden'}>
                    <label class="block text-sm font-medium text-gray-700">Price</label>
                    <input type="number" id="sidePrice" 
                           class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                           step="0.01" min="0"
                           value="${sideOption ? sideOption.price || '0.00' : '0.00'}">
                </div>
            </div>
            <div class="flex justify-end gap-2 mt-4">
                <button type="button" class="cancelSideOption px-4 py-2 text-gray-700 hover:text-gray-900">
                    Cancel
                </button>
                <button type="submit" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                    ${sideOption ? 'Save Changes' : 'Add Side'}
                </button>
            </div>
        </form>
    `;

    // Add the form to the container
    buttonContainer.replaceWith(formDiv);
    // const container = document.getElementById(`sideOptionsList${courseId}`);
    // container.appendChild(formDiv);
    formDiv.querySelector('.cancelSideOption').addEventListener('click', () => {
        const newButtonContainer = document.createElement('div');
        newButtonContainer.id = `addSideButtonContainer${courseId}`;
        newButtonContainer.className = 'flex justify-end mt-2';
        newButtonContainer.innerHTML = `
            <button class="addSideOption text-sm px-3 py-1 bg-green-500 hover:bg-green-600 text-white rounded"
                    data-course-id="${courseId}">
                Add Side
            </button>
        `;
        formDiv.replaceWith(newButtonContainer);
    });
    // Toggle price field visibility based on premium checkbox
    const isPremiumCheckbox = formDiv.querySelector('#isPremium');
    const priceField = formDiv.querySelector('#priceField');
    isPremiumCheckbox.addEventListener('change', () => {
        priceField.hidden = !isPremiumCheckbox.checked;
    });

    // Handle form submission
    const form = formDiv.querySelector('#sideOptionForm');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = {
            name: formDiv.querySelector('#sideName').value,
            description: formDiv.querySelector('#sideDescription').value,
            is_premium: formDiv.querySelector('#isPremium').checked,
            price: formDiv.querySelector('#sidePrice').value || 0,
            course_id: courseId
        };

        try {
            const endpoint = sideOption 
                ? `/${eatery}/menu/side_options/${sideOption.id}/`
                : `/${eatery}/menu/side_options/${courseId}/`;
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) throw new Error('Network response was not ok');
            const result = await response.json();

            // Remove the form
            const newButtonContainer = document.createElement('div');
            newButtonContainer.id = `addSideButtonContainer${courseId}`;
            newButtonContainer.className = 'flex justify-end mt-2';
            newButtonContainer.innerHTML = `
                <button class="addSideOption text-sm px-3 py-1 bg-green-500 hover:bg-green-600 text-white rounded"
                        data-course-id="${courseId}">
                    Add Side
                </button>
            `;
            formDiv.remove();
            
            // Update the side options list
            await updateSideOptionsList(courseId);

        } catch (error) {
            console.error('Error:', error);
            alert('Error saving side option. Please try again.');
        }
    });

    // Handle cancel button
    formDiv.querySelector('.cancelSideOption').addEventListener('click', () => {
        formDiv.remove();
    });
}
async function editSideOption(sideId) {
    try {
        const response = await fetch(`/${eatery}/menu/side_options/${sideId}/`);
        if (!response.ok) throw new Error('Network response was not ok');
        const sideOption = await response.json();
        showSideOptionForm(sideOption.course_id, sideOption);
    } catch (error) {
        console.error('Error:', error);
        alert('Error loading side option. Please try again.');
    }
}

function deleteSideOption(sideId) {
    if (!confirm('Are you sure you want to delete this side option?')) {
        return;
    }

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

    fetch(`/${eatery}/menu/side_options/${sideId}/`, {
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
    .then(result => {
        sideElement.style.transition = 'all 0.3s ease-out';
        sideElement.style.transform = 'translateX(100%)';
        sideElement.style.opacity = '0';
        
        setTimeout(() => {
            sideElement.remove();
            
            // Check if this was the last side option
            const listContainer = document.getElementById(`sideOptionsList${result.course_id}`);
            const remainingSides = listContainer.querySelectorAll('div[data-side-id]').length;
            
            if (remainingSides === 0) {
                updateSideOptionsList(result.course_id);
            }
        }, 300);
    })
    .catch(error => {
        console.error('Error:', error);
        sideElement.style.opacity = '1';
        buttons.forEach(button => button.disabled = false);
        alert('Error deleting side option. Please try again.');
    });
}

async function updateSideOptionsList(courseId) {
    try {
        const response = await fetch(`/${eatery}/menu/side_options/${courseId}/`);
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