
document.addEventListener("DOMContentLoaded", function() {

    // Event listener for buttons with data-toggle="filter"
    $("[data-toggle='filter']").click(function(){
        const target = $(this).data('target'); 
        $(target).toggleClass('d-none');
    });

    // Get all filter buttons based on their class
    let filterButtons = document.querySelectorAll('.btn.btn-outline-secondary.mb-2.w-100');
    let currentCategory = "";

    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            currentCategory = this.getAttribute('data-search'); // Get data-search attribute
            fetchFilteredProducts(); // Fetch products based on the category
        });
    });

    let appliedFilters = {};

    // Function to fetch filtered products based on category and facet selections
    function fetchFilteredProducts(facetSelections = {}) {
        let requestData = {
            'category': currentCategory
        };

        let consolidatedFacetSelections = {};
        
        // Flatten the facetSelections for the GET request
        for (let [facetName, selection] of Object.entries(facetSelections)) {
            if (Array.isArray(selection)) {
                // Categorical facets are arrays
                consolidatedFacetSelections[facetName] = selection;
            } else if (typeof selection === "object" && selection !== null) {
                // Numerical facets have min and max properties
                if (!consolidatedFacetSelections[facetName]) {
                    consolidatedFacetSelections[facetName] = {};
                }
                consolidatedFacetSelections[facetName]['min'] = selection.min;
                consolidatedFacetSelections[facetName]['max'] = selection.max;
            } else {
                // Boolean facets and other types
                consolidatedFacetSelections[facetName] = selection;
            }
        }

        // Convert consolidated facet selections to JSON string and add to requestData
        requestData['facets'] = JSON.stringify(consolidatedFacetSelections);
        
        $.ajax({
            url: '/inventory/search_category/',
            data: requestData,
            dataType: 'json',
            success: function (data) {
                $('#searchResults').html(data.products);
                $('#facets').html(data.facets);

                // Handle the applied filters from the JSON response
                let appliedFiltersBlock = document.getElementById('appliedFiltersBlock');
                if (appliedFiltersBlock) {
                    appliedFiltersBlock.innerHTML = '';  // Clear existing content

                    for (let [name, value] of Object.entries(data.applied_filters)) {
                        let template;
                        let node;

                        if (Array.isArray(value)) { // Categorical
                            template = document.getElementById('categoricalFilterTemplate');
                            node = document.importNode(template.content, true);
                            node.querySelector('.filter-name').textContent = `${name}: ${value}`;
                            node.querySelector('.remove-filter').setAttribute('data-filter-name', name);
                            node.querySelector('.remove-filter').setAttribute('data-filter-value', value);

                        } else if (typeof value === 'object' && value.min && value.max) { // Numerical
                            template = document.getElementById('numericalFilterTemplate');
                            node = document.importNode(template.content, true);
                            node.querySelector('.filter-name').textContent = `${name}: ${value.min} - ${value.max}`;
                            node.querySelector('.remove-filter').setAttribute('data-filter-name', name);
                            node.querySelector('.remove-filter').setAttribute('data-filter-min', value.min);
                            node.querySelector('.remove-filter').setAttribute('data-filter-max', value.max);

                        } else { // Boolean or others
                            template = document.getElementById('booleanFilterTemplate');
                            node = document.importNode(template.content, true);
                            node.querySelector('.filter-name').textContent = `${name}: ${value}`;
                            node.querySelector('.remove-filter').setAttribute('data-filter-name', name);
                        }

                        appliedFiltersBlock.appendChild(node);
                    }
                }
                // Update applied filters
                appliedFilters = data.applied_filters || {};
                // Initialize facet interactions
                initializeFacetInteractions();
                // Attach event listeners to facet "Submit" buttons
                attachSubmitButtonListeners();
            }
        });
    }

    // Capture facet selections and send them along with the current category
    function handleFacetSubmit(facetContainer) {
        let facetSelections = {};

        // Capture categorical facet selections
        let checkboxes = facetContainer.querySelectorAll('input[type="checkbox"]:checked');
        checkboxes.forEach(checkbox => {
            let facetName = checkbox.name;
            let facetValue = checkbox.value;
            if (!facetSelections[facetName]) {
                facetSelections[facetName] = [];
            }
            facetSelections[facetName].push(facetValue);
        });

        // Capture numerical facet selections
        let minSlider = facetContainer.querySelector('.minSlider');
        let maxSlider = facetContainer.querySelector('.maxSlider');
        if (minSlider && maxSlider) {
            let facetName = minSlider.id.replace('minSlider_', '');
            facetSelections[facetName] = {
                'min': minSlider.value,
                'max': maxSlider.value
            };
        }

        // Capture boolean facet selections
        let radioSelected = facetContainer.querySelector('input[type="radio"]:checked');
        if (radioSelected) {
            let booleanFacetName = radioSelected.name;
            let dataBoolValue = radioSelected.getAttribute('data-bool-value');
            let boolValue = dataBoolValue === 'true';

            facetSelections[booleanFacetName] = boolValue;
        }

        // Combine new and applied filters
        facetSelections = {...appliedFilters, ...facetSelections};

        fetchFilteredProducts(facetSelections); // Fetch products based on the category and facet selections
    }

    // Function to attach event listeners to facet "Submit" buttons
    function attachSubmitButtonListeners() {
        let facetSubmitButtons = document.querySelectorAll('.submit-btn');
        facetSubmitButtons.forEach(button => {
            button.addEventListener('click', function() {
                handleFacetSubmit(button.closest('.facet-container'));
            });
        });
    }

    // Event delegation for individual filter removal
    document.addEventListener('click', function(event) {
        if (event.target.matches('.remove-filter')) {
            const filterName = event.target.getAttribute('data-filter-name');
            delete appliedFilters[filterName];  // Remove the specific filter
            fetchFilteredProducts(appliedFilters);  // Fetch products with updated filters
        }
    });

});
