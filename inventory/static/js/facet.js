function initializeFacetInteractions() {
    // Get all facet buttons
    const facetButtons = document.querySelectorAll('.facet');

    facetButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Close other dropdowns
            facetButtons.forEach(innerButton => {
                if (innerButton !== button) {
                    const innerTargetId = innerButton.getAttribute('data-target');
                    const innerTargetElement = document.querySelector(innerTargetId);
                    const innerContainer = innerButton.closest('.facet-container');
                    if (!innerTargetElement.classList.contains('d-none')) {
                        innerTargetElement.classList.add('d-none');
                        innerContainer.classList.remove('expanded');
                    }
                }
            });

            // Get the target element from the data-target attribute
            const targetId = button.getAttribute('data-target');
            const targetElement = document.querySelector(targetId);
            const container = button.closest('.facet-container');

            // Toggle the visibility
            if (targetElement.classList.contains('d-none')) {
                targetElement.classList.remove('d-none');
                container.classList.add('expanded');
            } else {
                targetElement.classList.add('d-none');
                container.classList.remove('expanded');
            }

            // Align dropdown based on position in grid
            const buttonRect = button.getBoundingClientRect();
            const containerRect = document.getElementById('facetsBlock').getBoundingClientRect();
            const buttonCenter = buttonRect.left + (buttonRect.width / 2);

            // Check if the button's center is closer to the right edge of the container
            if (Math.abs(buttonCenter - containerRect.right) < Math.abs(buttonCenter - containerRect.left)) {
                targetElement.style.left = 'auto';
                targetElement.style.right = '0';
            } else {
                targetElement.style.left = '0';
                targetElement.style.right = 'auto';
            }
        });
    });
    
    
    const searchInputs = document.querySelectorAll('.facet-search');

    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = input.value.toLowerCase();
            const facetContents = input.closest('.facet-contents');
            if (!facetContents) return;  // Safeguard

            const facetContainer = facetContents.querySelector('.scrollable-content'); // Adjusted class
            if (!facetContainer) return;  // Safeguard

            const checkboxContainers = facetContainer.querySelectorAll('div > input[type="checkbox"]');

            checkboxContainers.forEach(checkbox => {
                const div = checkbox.parentElement;
                if (div.textContent.toLowerCase().includes(searchTerm)) {
                    div.style.display = '';
                } else {
                    div.style.display = 'none';
                }
            });
        });
    });
  
    const minSliders = document.querySelectorAll(".minSlider");
    const maxSliders = document.querySelectorAll(".maxSlider");
    
    minSliders.forEach(minSlider => {
        const stepSize = (parseFloat(minSlider.getAttribute('max')) - parseFloat(minSlider.getAttribute('min'))) < 2 ? 0.1 : 1;
        minSlider.setAttribute('step', stepSize);
        minSlider.setAttribute('min', Math.floor(parseFloat(minSlider.getAttribute('min'))));
        minSlider.addEventListener("input", function() {
            const container = minSlider.closest(".facet-contents");
            const minValueSpanLocal = container.querySelector("span[id^='min']");
            const maxSlider = container.querySelector(".maxSlider");
            const min = parseFloat(minSlider.value);
            const max = parseFloat(maxSlider.value);
            if (min >= max) {
                minSlider.value = (max - stepSize).toFixed(1);
            }
            minValueSpanLocal.textContent = minSlider.value;
        });
    });
    
    maxSliders.forEach(maxSlider => {
        const stepSize = (parseFloat(maxSlider.getAttribute('max')) - parseFloat(maxSlider.getAttribute('min'))) < 2 ? 0.1 : 1;
        maxSlider.setAttribute('step', stepSize);
        maxSlider.setAttribute('max', Math.ceil(parseFloat(maxSlider.getAttribute('max'))));
        maxSlider.addEventListener("input", function() {
            const container = maxSlider.closest(".facet-contents");
            const maxValueSpanLocal = container.querySelector("span[id^='max']");
            const minSlider = container.querySelector(".minSlider");
            const min = parseFloat(minSlider.value);
            const max = parseFloat(maxSlider.value);
            if (max <= min) {
                maxSlider.value = (min + stepSize).toFixed(1);
            }
            maxValueSpanLocal.textContent = maxSlider.value;
        });
    });
}

// Case if the facets are present in the beginning, when the page loads
document.addEventListener("DOMContentLoaded", initializeFacetInteractions);