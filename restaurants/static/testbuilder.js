document.addEventListener('DOMContentLoaded', () => {
    const currentKitchen = JSON.parse(document.getElementById('kitchen').textContent);

    // Add course
    const addCourseBtn = document.querySelector('#add');
    const courseInput = document.querySelector('#addCourse');
    addCourseBtn.addEventListener('click', (event) => {
        event.preventDefault();
        addCourse(courseInput.value, currentKitchen);
    });

    // Add dish buttons
    document.querySelectorAll('.submitDish').forEach(btn => {
        btn.addEventListener('click', () => addDish(btn.id, currentKitchen));
    });

    // Edit dish buttons
    document.querySelectorAll('.editDish').forEach(btn => {
        const dishId = btn.id.replace('e', '');
        btn.addEventListener('click', () => editDish(dishId));
    });

    // Delete dish buttons
    document.querySelectorAll('.deleteDish').forEach(btn => {
        const dishId = btn.id.replace('d', '');
        btn.addEventListener('click', () => deleteDish(dishId));
    });

    // Delete course buttons
    document.querySelectorAll('.deleteCourse').forEach(btn => {
        const courseId = btn.id.replace('delete', '');
        btn.addEventListener('click', () => deleteCourse(courseId, currentKitchen));
    });
});

async function addCourse(dishData, currentKitchen) {
    try {
        const response = await fetch(`/add_course/${dishData}/${currentKitchen}`, {method: "POST"});
        const result = await response.json();
        location.reload();
    } catch (error) {
        console.error('Error:', error);
    }
}

function addDish(course, eatery) {
    const currentCourse = course.replace('submit', "");
    const addDiv = document.getElementById(course);
    const swapDiv = document.createElement('div');
    swapDiv.innerHTML = `
        <form id="createDish" class="p-1">
            <div class="form-group">
                <input type="text" class="p-2 m-1 border-double border-4 border-indigo-200" placeholder="Name of Dish" id="dishName">
                <input type="number" class="p-2 m-1 border-double border-4 border-indigo-200" placeholder="Price" step="any" id="dishPrice">
                <input type="url" class="p-2 m-1 border-double border-4 border-indigo-200" placeholder="Image" id="dishPicture">
                <textarea class="form-control p-2 m-1" id="dishDescription" rows="3" placeholder="Description"></textarea>
            </div>
            <button type="submit" class="bg-blue-500 m-2 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Add Dish</button>
        </form>
    `;
    addDiv.replaceWith(swapDiv);

    document.querySelector('#createDish').addEventListener('submit', async (event) => {
        event.preventDefault();
        try {
            const response = await fetch(`/add_dish/${eatery}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: document.querySelector("#dishName").value,
                    price: document.querySelector("#dishPrice").value,
                    image_url: document.querySelector("#dishPicture").value,
                    description: document.querySelector("#dishDescription").value,
                    recipe_owner: eatery,
                    course: currentCourse
                })
            });
            const result = await response.json();
            location.reload();
        } catch (error) {
            console.error('Error:', error);
        }
    });
}

async function editDish(dishid) {
    try {
        const response = await fetch(`/edit_dish/${dishid}`, {method: "GET"});
        const item = await response.json();
        const editName = document.createElement('div');
        editName.innerHTML = `
            <form id="editDish" class="p-1">
                <div class="form-group">
                    <input type="text" class="p-2 m-1 border-double border-4 border-indigo-200" value="${item.name}" id="dishName">
                    <input type="number" class="p-2 m-1 border-double border-4 border-indigo-200" value="${item.price}" step="any" id="dishPrice">
                    <input type="url" class="p-2 m-1 border-double border-4 border-indigo-200" value="${item.image_url}" id="dishImage">
                    <textarea class="form-control p-2 m-1" id="dishDescription" rows="3">${item.description}</textarea>
                </div>
                <button type="button" id="submitChanges" class="bg-blue-500 m-2 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Submit Changes</button>
            </form>
        `;
        const divMod = document.getElementById(`o${dishid}`);
        divMod.replaceWith(editName);
        document.querySelector('#submitChanges').addEventListener('click', () => submitChanges(dishid));
    } catch (error) {
        console.error('Error:', error);
    }
}

async function submitChanges(dishid) {
    try {
        const response = await fetch(`/edit_dish/${dishid}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                description: document.querySelector('#dishDescription').value,
                name: document.querySelector('#dishName').value,
                price: document.querySelector('#dishPrice').value,
                image: document.querySelector('#dishImage').value,
            })
        });
        const result = await response.json();
        location.reload();
    } catch (error) {
        console.error('Error:', error);
    }
}

async function deleteDish(dishId) {
    try {
        await fetch(`/delete_dish/${dishId}`, {method: "GET"});
        location.reload();
    } catch (error) {
        console.error('Error:', error);
    }
}

async function deleteCourse(course, eatery) {
    try {
        await fetch(`/delete_course/${eatery}/${course}`, {method: "GET"});
        location.reload();
    } catch (error) {
        console.error('Error:', error);
    }
}