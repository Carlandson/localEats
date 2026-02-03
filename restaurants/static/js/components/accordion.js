// initializer
export function initializeAccordions() {
    const accordionTriggers = document.querySelectorAll('.accordion-trigger');
    
    accordionTriggers.forEach(trigger => {
        trigger.addEventListener('click', () => {
            const target = document.getElementById(trigger.dataset.target);
            const arrow = trigger.querySelector('svg');
            
            // Toggle panel visibility
            target.classList.toggle('hidden');
            
            // Update trigger styles and arrow rotation
            if (target.classList.contains('hidden')) {
                trigger.classList.remove('bg-gray-100', 'hover:bg-gray-400');
                trigger.classList.add('bg-white', 'hover:bg-gray-50');
                arrow.classList.remove('rotate-90');
            } else {
                trigger.classList.remove('bg-white', 'hover:bg-gray-50');
                trigger.classList.add('bg-gray-100', 'hover:bg-gray-400');
                arrow.classList.add('rotate-90');
            }
        });
    });
}

// template
export function createAccordionHTML(title, contentId, isOpen = false) {
    return `
        <div class="border rounded-lg mb-4">
            <button class="accordion-trigger w-full flex justify-between items-center p-4 ${isOpen ? 'bg-gray-100 hover:bg-gray-400' : 'bg-white hover:bg-gray-50'} rounded-t-lg" 
                    data-target="${contentId}">
                <h2 class="text-lg font-bold">${title}</h2>
                <svg class="w-5 h-5 transition-transform ${isOpen ? 'rotate-90' : ''}" 
                     xmlns="http://www.w3.org/2000/svg" 
                     fill="none" 
                     viewBox="0 0 24 24" 
                     stroke="currentColor">
                    <path stroke-linecap="round" 
                          stroke-linejoin="round" 
                          stroke-width="2" 
                          d="M9 5l7 7-7 7" />
                </svg>
            </button>
            <div id="${contentId}" 
                 class="accordion-content p-4 ${isOpen ? '' : 'hidden'}">
            </div>
        </div>
    `;
}