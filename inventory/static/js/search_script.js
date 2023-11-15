$(document).ready(function(){
    $("#searchButton").click(function(){
        const searchTerm = $("#searchInput").val().trim(); // Trim whitespace

        // Check if searchTerm is empty or less than 4 characters
        if (searchTerm.length < 3) {
            // Optionally, you can alert the user or handle this case as needed
            alert("Please enter at least 3 characters for the search.");
            return; // Exit the function, no AJAX call
        }

        // Proceed with AJAX call if searchTerm is valid
        $.ajax({
            url: "/inventory/search_product/",
            data: { 'search_term': searchTerm },
            type: 'GET',
            dataType: 'html',
            success: function(data){
                $("#searchResults").html(data);
            },
            error: function(error){
                console.log(error);
            }
        });
    });
});