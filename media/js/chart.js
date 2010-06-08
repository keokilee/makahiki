// Load the Visualization API and the bar chart package.
google.load("visualization", "1", {packages:['corechart']});

// Set a callback to run when the Google Visualization API is loaded.
google.setOnLoadCallback(initializeChart);

/**
 * Once visualization API is loaded, retrieve data and set callback to run once retrieved.
 */
function initializeChart() {
  // Get all of the dorm data from the spreadsheet.
  var dormDataURL = 'http://spreadsheets.google.com/tq?key=0Av0U6TKHfzXYdG1vUnduR0RVTktyR1ZtNjAtSE9Qbmc&range=A3:F21&gid=0';
  var dormDataQuery = new google.visualization.Query(dormDataURL);
  // Update the chart once an hour.
  dormDataQuery.setRefreshInterval(3600);
  // Set a callback to run when the dorm data has been retrieved.
  dormDataQuery.send(displayDormData);
}


/**
 * Once data is available, create view to display.
 */
function displayDormData(response) {
  // Process errors, if any.
  if (response.isError()) {
      alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
      return;
  }
  
  // Get the dorm data table.
  var data = response.getDataTable();
  // Format the energy timestamp column. 
  var formatter = new google.visualization.DateFormat({formatType: 'short'});
  formatter.format(data, 5);
  
  // Create the view that is just the total dorm energy data.
  var view = new google.visualization.DataView(data);
  view.setColumns([0,4]);
  view.setRows([5,11,17]);
  var chart = new google.visualization.BarChart(document.getElementById('chart_div'));
  chart.draw(view, {backgroundColor: '#F5F3E5',
                    colors: ['#459E00'],width: 300, 
                    height: 200, 
                    title: 'Energy Usage since 5/25/2010',
                    legend: 'none',
                    hAxis: {minValue: '0', title: 'watt-hours'}
                    });
  // Print out the timestamp for Ilima-dorm wide energy to give a sense for the last update.
  document.getElementById('chart_timestamp_div').innerHTML = 'Updated ' + data.getFormattedValue(5, 5);                          
}
