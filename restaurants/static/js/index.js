document.addEventListener('DOMContentLoaded', () => {
    // Mobile button
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    mobileMenuButton.addEventListener('click', function() {
        mobileMenu.classList.toggle('hidden');
    });
    document?.querySelector('.prev')?.addEventListener('click', () => plusSlides(-1));
    document?.querySelector('.next')?.addEventListener('click', () => plusSlides(1));
    // slider
    let slideIndex = 0;
    let slideInterval;


    function showSlides(n) {
        let slides = document?.getElementsByClassName("mySlides");
        let dots = document?.getElementsByClassName("dot");
    

        if (n !== undefined) {
            slideIndex = n;
        } else {
            slideIndex++;
        }
    
        if (slideIndex > slides.length) {slideIndex = 1}
        if (slideIndex < 1) {slideIndex = slides.length}
    
        for (let i = 0; i < slides.length; i++) {
            slides[i].style.display = "none";
        }
        for (let i = 0; i < dots.length; i++) {
            dots[i].className = dots[i].className.replace(" active", "");
        }
    
        slides[slideIndex-1].style.display = "block";
        if (dots.length > 0) {
            dots[slideIndex-1].className += " active";
        }
    
        // Reset the timer
        clearTimeout(slideInterval);
        slideInterval = setTimeout(() => showSlides(), 6000); // Change image every 2 seconds
    }
    // Next/previous controls
    function plusSlides(n) {
        showSlides(slideIndex + n);
    }

    // Thumbnail image controls
    function currentSlide(n) {
        showSlides(n);
    }

    // Start the slideshow
    showSlides();
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
                // Test remove eatery
                eateryDiv.innerHTML = `
                <ul class="p-4">
                    <a href="/${kitchen["name"]}/">
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
                    <a href="/${eatery["name"]}/">${eatery["name"]}
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