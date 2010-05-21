// Load the Visualization API and the piechart package.
google.load("visualization", "1", {packages:['corechart']});

// Set a callback to run when the Google Visualization API is loaded.
google.setOnLoadCallback(initializeData);

// Gets the Dorm energy usage data from the following URL.
function initializeData() {
  var query = new google.visualization.Query('http://spreadsheets.google.com/tq?key=0An9ynmXUoikYdFZmZE5leDdGUjBLc0htTGhlbnlDN2c&range=D5:H6&gid=0');

  // Send the query with a callback function.
  query.send(handleQueryResponse);
}


// Callback that gets the DataTable and displays it.
function handleQueryResponse(response) {
  if (response.isError()) {
     alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
     return;
  }

  var data = response.getDataTable();
  var chart = new google.visualization.BarChart(document.getElementById('standings_div'));
  chart.draw(data, {width: 400,
                   height: 200,
                   fontSize: 10,
                   legendFontSize: 10,
                   title: 'Hale Ilima Energy Consumed Per Floor',
                   hAxis: {minValue: '0', title: 'kWh consumed from 5/2/10 to 5/4/10'}
  });
}