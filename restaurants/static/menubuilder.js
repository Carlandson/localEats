document.addEventListener('DOMContentLoaded', function() {
    const btn = document.querySelector('#add');
    const submission = document.querySelector('#addCourse');
    btn.onclick = (event)  => {
        event.preventDefault();
        addCourse(submission.value);
    }
    const tagids = []
    const dishBtn = document.getElementsByClassName('submitDish');
    for(const courseBtn of dishBtn) {
        const tagid = courseBtn.id
        tagids.push(tagid)
    };
    tagids.forEach (course => {
        document.querySelector("#"+course).addEventListener('click', () => addDish(course));
    });
    const editBtn = document.getElementsByClassName('editDish');
    const btnTag = []
    for(const eachBtn of editBtn) {
        const btnId = eachBtn.id;
        let item = btnId.replace('e', '')
        btnTag.push(item)
    };
    btnTag.forEach(i => {
        document.querySelector("#e"+i).addEventListener('click', () => editDish(i));
    });
    const btnDelete = document.getElementsByClassName('deleteDish');
    const deleteBtns = []
    for(const deleteBtn of btnDelete) {
        const del = deleteBtn.id;
        let dishDelete = del.replace('d', '')
        deleteBtns.push(dishDelete)
    };
    deleteBtns.forEach(j => {
        document.querySelector("#d"+j).addEventListener('click', () => deleteDish(j));
    });
    const deleteCourseBtns = document.getElementsByClassName('deleteCourse');
    const deleteCourseList = []
    for(const deleteCourseBtn of deleteCourseBtns) {
        const delCourse = deleteCourseBtn.id;
        let courseDelete = delCourse.replace('delete', '')
        deleteCourseList.push(courseDelete)
    };
    deleteCourseList.forEach(k => {
        document.querySelector("#delete"+k).addEventListener('click', () => deleteCourse(k));
    });

    const courseList = [
        "Appetizers",
        "Lunch",
        "Entrees",
        "Salads",
        "Desserts",
        "Drinks",
        "Specials"  
    ]
});

function addCourse(dishData){
    let currentKitchen = JSON.parse(document.getElementById('kitchen').textContent)
    console.log(currentKitchen);
    fetch(currentKitchen + "/add_course/" + dishData, {method: "POST"})
        .then(response => response.json())
        .then(result => {
            location.reload();
        })
};

//click to open a form to fill out form for a dish
function addDish(course){
    let currentCourse = course.replace('submit', "")
    const eatery = JSON.parse(document.getElementById('kitchen').textContent);
    let addDiv = document.getElementById(course);
    let swapDiv = document.createElement('div');
        swapDiv.innerHTML = `
        <form id="createDish" class="p-1" action="post">
            <div class="form-group">
                <input type="text" class="p-2 m-1 border-double border-4 border-indigo-200" placeholder="Name of Dish" id="dishName">
                <input type="number" class="p-2 m-1 border-double border-4 border-indigo-200" placeholder="Price" step="any" id="dishPrice">
                <input type="url" class="p-2 m-1 border-double border-4 border-indigo-200" placeholder="Image" id="dishPicture">
                <textarea class="form-control" class="p-2 m-1" id="dishDescription" rows="3" placeholder="Description"></textarea>
            </div>
            <button type="submit" class="bg-blue-500 m-2 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Add Dish</button>
        </form>
        `;
    addDiv.replaceWith(swapDiv);
    document.querySelector('#createDish').addEventListener('submit', (event) => {
        event.preventDefault()
        fetch('/add_dish/' + eatery, {
            method: 'POST',
            body: JSON.stringify({
                name: document.querySelector("#dishName").value,
                price: document.querySelector("#dishPrice").value,
                image_url: document.querySelector("#dishPicture").value,
                description: document.querySelector("#dishDescription").value,
                recipe_owner: eatery,
                course: currentCourse
            })
        })
        .then(response => response.json())
        .then(result => {location.reload()})
    });
};
//click to open a form with prefilled information for editing
function editDish(dishid) {
    fetch("/edit_dish/" + dishid, {method: "GET"})
        .then(response => response.json())
        .then(item => {
            var itemName = item['name'];
            var itemPrice = item['price'];
            var itemDescription = item['description'];
            var itemImage = item['image_url'];
            var editName = document.createElement('div');
                editName.innerHTML = `
                <form id="editDish" class="p-1">
                    <div class="form-group">
                        <input type="text" class="p-2 m-1 border-double border-4 border-indigo-200" value="${itemName}"id="dishName">
                        <input type="number" class="p-2 m-1 border-double border-4 border-indigo-200" value="${itemPrice}" step="any" id="dishPrice">
                        <input type="url" class="p-2 m-1 border-double border-4 border-indigo-200" value="${itemImage}" id="dishImage">
                        <textarea class="form-control" class="p-2 m-1" id="dishDescription" rows="3">${itemDescription}</textarea>
                    </div>
                    <button type="click" id="submitChanges" class="bg-blue-500 m-2 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Submit Changes</button>
                </form>
            `
            var divMod = document.getElementById("o"+dishid);
            let editSubmit = document.querySelector('#submitChanges');
            divMod.replaceWith(editName);
            document.querySelector('#submitChanges').addEventListener('click', () => submitChanges(dishid));
        });
};

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
    fetch('/delete_dish/' + dishId, {method: "GET"})
    .then(result => {
        location.reload()
    });
};

function deleteCourse(course) {
    const eatery = JSON.parse(document.getElementById('kitchen').textContent);
    fetch('/delete_course/' + eatery + "/" + course, {method: "GET"})
    .then(result => {
        location.reload()
    });
};