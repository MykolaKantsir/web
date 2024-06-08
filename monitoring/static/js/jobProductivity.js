document.addEventListener('DOMContentLoaded', function() {
    const productivityElement = document.getElementById('job-productivity');
    const productivityUrl = productivityElement.getAttribute('data-productivity-url');
    window.productivityPieChart = null;

    // Make sure we have the URL before making the request
    if (productivityUrl) {
      fetch(productivityUrl, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        // Process your data and update the DOM accordingly
        // For example, you might have a function to update the productivity details:
        updateProductivityDetails(data);
      })
      .catch(error => {
        console.error('There has been a problem with your fetch operation:', error);
      });
    } else {
      console.error('Productivity URL is not specified.');
    }
  });
  
  function updateProductivityDetails(data) {
    // Define colors as variables
    var colors = {
        green: 'rgba(0, 128, 0)',
        yellow: 'rgba(255, 255, 0)',
        orange: 'rgba(255, 128, 0)'
    };

    var ctx = document.getElementById('productivityPieChart').getContext('2d');
    var chartData = [
        convertTimeToMinutes(data.machining_time),
        convertTimeToMinutes(data.changing_parts_time),
        convertTimeToMinutes(data.setup_time)
    ];

    // Destroy previous chart instance if exists
    if (window.productivityPieChart) {
        window.productivityPieChart.destroy();
    }

    // Create a new chart instance
    window.productivityPieChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Machining Time', 'Changing Parts Time', 'Setup Time'],
            datasets: [{
                label: 'Cycle Time Breakdown',
                data: chartData,
                backgroundColor: [colors.green, colors.yellow, colors.orange],
                borderColor: '#fff', // Set border color here (white for separation)
                borderWidth: 2
            }]
        },
        options: {
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            },
            responsive: false,
            maintainAspectRatio: false, // Maintain aspect ratio if desired
        }
    });
    
    // Calculate total outside of the .map() function
    var total = chartData.reduce(function(a, b) { return a + b; }, 0);

    // Update color explanation and percentages
    var colorInfoContainer = document.getElementById('color-info');
    if (colorInfoContainer) {
        var labels = ['Machining Time', 'Changing Parts Time', 'Setup Time'];
        var backgroundColors = [colors.green, colors.yellow, colors.orange];
        colorInfoContainer.innerHTML = labels.map(function(label, index) {
            // Use the 'total' variable calculated earlier
            var percentage = Math.floor((chartData[index] / total) * 100 + 0.5);
            return '<div class="color-legend">' +
                       '<span class="color-box" style="background-color: ' + backgroundColors[index] + ';"></span> ' +
                       label + ': ' + percentage + '%' +
                   '</div>';
        }).join('');
    }
}

// Helper function to convert HH:MM:SS time format to minutes
function convertTimeToMinutes(time) {
    var parts = time.split(':');
    return parseInt(parts[0], 10) * 60 + parseInt(parts[1], 10);
}
