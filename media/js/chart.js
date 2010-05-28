// Load the Visualization API and the bar chart package.
google.load("visualization", "1", {packages:['corechart']});

// Set a callback to run when the Google Visualization API is loaded.
google.setOnLoadCallback(initializeData);

// Once visualization API is loaded, retrieve data and set callbacks to run once retrieved.
function initializeData() {
  // Get Overall Dorm Data.
  var dormURL = 'http://spreadsheets.google.com/tq?key=0An9ynmXUoikYdG94TnRCYjNqNng5MVZYb01SUEFMQVE&range=C10:D13&gid=0';
  var dormQuery = new google.visualization.Query(dormURL);

  // Set a callback to run when the overall dorm data has been retrieved.
  dormQuery.send(displayDormEnergyData);
}


// Callback that gets the Overall Dorm DataTable and displays it.
function displayDormEnergyData(response) {
// Process errors, if any.
if (response.isError()) {
   alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
   return;
}

// Get the data table, and sort it by energy value.
var data = response.getDataTable();
data.sort([{column: 1}]);
var chart = new google.visualization.BarChart(document.getElementById('dorm_chart_div'));
chart.draw(data, {backgroundColor: '#F5F3E5',
                 colors: ['#459E00'],
                 width: 300,
                 height: 200,
                 legend: 'none',
                 title: 'Dorm Energy Consumption',
                 hAxis: {minValue: '0', title: 'kWh consumed for last 10 days'}
               });
}
