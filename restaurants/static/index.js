document.addEventListener('DOMContentLoaded', () => {
    const x = document.querySelector('#geolocate')
    x.addEventListener('click', () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(search)
        } else {
            x.innerHTML = "Geolocation is not supported by this browser.";
        }
    });
    citySearch.addEventListener('click', filter);
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    mobileMenuButton.addEventListener('click', function() {
        mobileMenu.classList.toggle('hidden');
    });
});

function search(position) {
    restaurantList = document.querySelector("#restaurantSearchList")
    restaurantList.innerHTML = "";
    latitude = position.coords.latitude;
    longitude = position.coords.longitude;
    coordinates = `${latitude}, ${longitude}`
    var selection = document.getElementById("distance")
    var distance = selection.value
    fetch("/search/" + coordinates + "/" + distance)
        .then(response => response.json())
        .then(localKitchen => {
            localKitchen.forEach(kitchen => {
                let eateryDiv = document.createElement('div');
                eateryDiv.innerHTML = `
                <ul class="p-4">
                    <a href="/eatery/${kitchen["name"]}/">
                    <li>
                        <h1 class="text-xl font-bold">${kitchen["name"]}</h1>
                    </li>
                    <li>
                        <span>${kitchen["cuisine"]} cuisine</span>
                    </li>
                    <li>
                        <span> ${kitchen["between"]} miles away</span>
                    </li>
                    </a>
                </ul>
                `;
                restaurantList.appendChild(eateryDiv);
            });
        });
}

function filter() {
    place = document.querySelector('#city').value
    let filterDiv = document.querySelector('#filterQuery');
    filterDiv.innerHTML = "";
    let citySearch = document.createElement('h1');
    citySearch.innerHTML = `<h1 class="text-xl p-2">${place} restaurants</h1>`
    filterDiv.appendChild(citySearch)
    fetch("/filter/" + place, {method:"get"})
        .then(response => response.json())
        .then(localEatery => {
            localEatery.forEach(eatery => {
                let newDiv = document.createElement('div');
                newDiv.innerHTML = `
                <li class="p-4>
                    <ul>
                    <a href="/eatery/${eatery["name"]}/">${eatery["name"]}
                        <li>
                            <i>${eatery["cuisine"]} cuisine</i>
                        </li>
                        <li>
                            <span>${eatery["address"]}</span>
                        </li>
                    </a>
                </ul>
                <br>
                `;
                filterDiv.appendChild(newDiv)
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    mobileMenuButton.addEventListener('click', function() {
        mobileMenu.classList.toggle('hidden');
    });
});