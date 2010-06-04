// Load the Visualization API and the bar chart package.
google.load("visualization", "1", {packages:['gauge']});

// Set a callback to run when the Google Visualization API is loaded.
google.setOnLoadCallback(initializeGauge);

// Once visualization API is loaded, retrieve data and set callbacks to run once retrieved.
function initializeGauge() {
  // Get all of the dorm data from the spreadsheet.
  var gaugeURL = 'http://spreadsheets.google.com/tq?key=0Av0U6TKHfzXYdG1vUnduR0RVTktyR1ZtNjAtSE9Qbmc&range=A3:F21&gid=0';
  var gaugeQuery = new google.visualization.Query(gaugeURL);
  // Update the gauges every 30 seconds
  gaugeQuery.setRefreshInterval(30);

  // Set a callback to run when the dorm data has been retrieved.
  gaugeQuery.send(displayGaugeData);
}


// Callback that gets the dorm data and creates DataViews to display each table individually.
function displayGaugeData(response) {
  // Process errors, if any.
  if (response.isError()) {
      alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
      return;
  }
  
  // Get the dorm data table.
  var data = response.getDataTable();
  
  // Create the view that is just ilima floors.
  var view = new google.visualization.DataView(data);
  view.setColumns([0,2]);
  view.setRows([5, 11, 17]);
  var chart = new google.visualization.Gauge(document.getElementById('gauge_div'));
  chart.draw(view, {height: 100, max: 5000, greenFrom: 0, greenTo: 2000, yellowFrom:2001, yellowTo: 4000, redFrom: 4001, redTo: 5000});
}
