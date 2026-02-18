
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