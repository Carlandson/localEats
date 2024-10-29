document.addEventListener('DOMContentLoaded', function() {
    const accordionTriggers = document.querySelectorAll('.accordion-trigger');
    
    accordionTriggers.forEach(trigger => {
        trigger.addEventListener('click', () => {
            const target = document.getElementById(trigger.dataset.target);
            const arrow = trigger.querySelector('svg');
            
            // Toggle current panel
            target.classList.toggle('hidden');
            arrow.classList.toggle('rotate-180');
            
            // Optional: Close other panels
            // accordionTriggers.forEach(otherTrigger => {
            //     if (otherTrigger !== trigger) {
            //         const otherTarget = document.getElementById(otherTrigger.dataset.target);
            //         const otherArrow = otherTrigger.querySelector('svg');
            //         otherTarget.classList.add('hidden');
            //         otherArrow.classList.remove('rotate-180');
            //     }
            // });
        });
    });
    document.addEventListener('click', function(e) {
        // Add Course button
        if (e.target.matches('#add')) {
            e.preventDefault();
            const submission = document.querySelector('#addCourse');
            addCourse(submission.value);
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

function addCourse(dishData){
    let currentKitchen = JSON.parse(document.getElementById('kitchen').textContent);
    // Fix the URL construction - remove the duplicate restaurant name
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
};

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
    const eatery = JSON.parse(document.getElementById('kitchen').textContent);
    let addButton = document.getElementById(course);
    
    // Find the correct panel by traversing up and then finding the container
    let parentPanel = addButton.closest('.accordion-collapse') || addButton.closest('[id^="panel"]');
    
    if (!parentPanel) {
        console.error('Could not find parent panel');
        return;
    }

    // Store the original button's parent
    const buttonContainer = addButton.parentNode;

    let formDiv = document.createElement('div');
    formDiv.innerHTML = getFormHTML(false);

    // Replace the button with the form
    addButton.replaceWith(formDiv);

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

            // Restore the button
            buttonContainer.appendChild(addButton);
            formDiv.remove();

            // Add event listeners to new buttons
            const newEditBtn = newDishArticle.querySelector('.editDish');
            const newDeleteBtn = newDishArticle.querySelector('.deleteDish');
            newEditBtn.addEventListener('click', () => editDish(result.dish_id));
            newDeleteBtn.addEventListener('click', () => deleteDish(result.dish_id));
        })
        .catch(error => {
            console.error('Error:', error);
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

function restoreAddButton(course, currentCourse) {
    const swapDiv = document.querySelector('#createDish').parentElement;
    const addButton = document.createElement('button');
    addButton.id = course;
    addButton.className = 'submitDish text-center w-60 rounded m-2 bg-emerald-300 md:w-96';
    addButton.textContent = `Add a dish to ${currentCourse}`;
    addButton.addEventListener('click', () => addDish(course));
    swapDiv.replaceWith(addButton);
}

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
        const eatery = JSON.parse(document.getElementById('kitchen').textContent);

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

            // Add event listeners to new buttons
            const newEditBtn = updatedDish.querySelector('.editDish');
            const newDeleteBtn = updatedDish.querySelector('.deleteDish');
            newEditBtn.addEventListener('click', () => editDish(dishId));
            newDeleteBtn.addEventListener('click', () => deleteDish(dishId));
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

// Add this if you haven't already
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

    const eatery = JSON.parse(document.getElementById('kitchen').textContent);
    const courseElement = document.getElementById(`delete${courseId}`).closest('.mb-4');
    
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
        courseElement.style.transition = 'all 0.3s ease-out';
        courseElement.style.transform = 'translateX(100%)';
        courseElement.style.opacity = '0';
        
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