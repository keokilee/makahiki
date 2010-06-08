// Load the Visualization API and the bar chart package.
google.load("visualization", "1", {packages:['gauge']});

// Set a callback to run when the Google Visualization API is loaded.
google.setOnLoadCallback(initializeGauge);

/**
 * Once visualization API is loaded, retrieve data and set callbacks to run once retrieved.
 */
function initializeGauge() {
  // Get all of the dorm data from the spreadsheet.
  var gaugeURL = 'http://spreadsheets.google.com/tq?key=0Av0U6TKHfzXYdG1vUnduR0RVTktyR1ZtNjAtSE9Qbmc&range=A3:F21&gid=0';
  var gaugeQuery = new google.visualization.Query(gaugeURL);
  // Update the gauges every 5 seconds
  gaugeQuery.setRefreshInterval(5);

  // Set a callback to run when the dorm data has been retrieved.
  gaugeQuery.send(displayGaugeData);
}


/**
 * Once dorm data is retrieved, create DataViews and display gauges.
 */
function displayGaugeData(response) {
  // Process errors, if any.
  if (response.isError()) {
      alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
      return;
  }
  
  // Get the dorm data table.
  var gaugeData = response.getDataTable();
  // Format the timestamps in column 3 to a short version. 
  var gaugeFormatter = new google.visualization.DateFormat({formatType: 'short'});
  gaugeFormatter.format(gaugeData, 3);
  
  // Now draw the gauges.
  drawGaugeInfo(gaugeData, 17, 'lehua');
  drawGaugeInfo(gaugeData, 11, 'mokihana');
  drawGaugeInfo(gaugeData, 5, 'ilima');
}

/**
 * Draws the gauge and timestamp for the given dorm. 
 */
function drawGaugeInfo(data, row, dorm) {
  var gaugeView = new google.visualization.DataView(data);
  gaugeView.setColumns([0,2]);
  gaugeView.setRows([row]);
  var gauge = new google.visualization.Gauge(document.getElementById(dorm + '_chart_div'));
  // 90 is the minimum height for a gauge that still allows the dorm name to be readable.
  gauge.draw(gaugeView, {height: 90, max: 5000, greenFrom: 0, greenTo: 2000, yellowFrom:2001, yellowTo: 4000, redFrom: 4001, redTo: 5000});
  document.getElementById(dorm + '_time_div').innerHTML = data.getFormattedValue(row, 3);
}

