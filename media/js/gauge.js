// Load the Visualization API and the bar chart package.
google.load("visualization", "1", {packages:['gauge']});

// Set a callback to run when the Google Visualization API is loaded.
google.setOnLoadCallback(initializeGauge);

/**
 * Once visualization API is loaded, retrieve data and set callbacks to run once retrieved.
 */
function initializeGauge() {
  // Get all of the dorm data from the spreadsheet.
  var gaugeUrl = 'http://spreadsheets.google.com/tq?key=0Av0U6TKHfzXYdG1vUnduR0RVTktyR1ZtNjAtSE9Qbmc&range=A3:F21&gid=0';
  var gaugeQuery = new google.visualization.Query(gaugeUrl);
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
  var data = response.getDataTable();
  // Format the timestamps in column 3 to a short version. 
  var formatter = new google.visualization.DateFormat({formatType: 'short'});
  formatter.format(data, 3);
  
  // Sets up the display to be centered and such that the gauge and text have the same width.
  var divWidth = 120;
  setChartDivStyle(divWidth);
  
  // Now draw the gauges.
  drawGaugeInfo(data, 17, 'lehua', divWidth);
  drawGaugeInfo(data, 11, 'mokihana', divWidth);
  drawGaugeInfo(data, 5, 'ilima', divWidth);
}

/**
 * Draws the gauge and timestamp for the given dorm. 
 */
function drawGaugeInfo(data, row, dorm, divWidth) {
  // First, blank out the title cell, since we'll display it separately.
  data.setCell(row, 0, '');
  // Now create the data view.  
  var chartView = new google.visualization.DataView(data);
  chartView.setColumns([0,2]);
  chartView.setRows([row]);
  var chart = new google.visualization.Gauge(document.getElementById(dorm + '_chart_div'));
  // 100 is the minimum height for a gauge that still allows the dorm name to be readable.
  chart.draw(chartView, {height: divWidth, max: 5000, greenFrom: 0, greenTo: 2000, yellowFrom: 2001, yellowTo: 4000, redFrom: 4001, redTo: 5000});
  document.getElementById(dorm + '_time_div').innerHTML = data.getFormattedValue(row, 3);
  document.getElementById(dorm + '_title_div').innerHTML = dorm;
  document.getElementById(dorm + '_title_div').style.fontWeight = 'bold';
}

/**
 * Sets the style for the outermost div to be the same width as the width of the gauges.
 */
function setChartDivStyle(width) {
  document.getElementById('gaugediv').style.textAlign = "center";
  document.getElementById('gaugediv').style.width = width;
}
