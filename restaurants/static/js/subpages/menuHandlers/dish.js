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