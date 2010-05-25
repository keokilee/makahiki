// Load the Visualization API and the bar chart package.
google.load("visualization", "1", {packages:['corechart']});

// Set a callback to run when the Google Visualization API is loaded.
google.setOnLoadCallback(initializeData);

// Once visualization API is loaded, retrieve data and set callbacks to run once retrieved.
function initializeData() {
  // Get Ilima Dorm Data
  var ilimaURL = 'http://spreadsheets.google.com/tq?key=0An9ynmXUoikYdEZwd1l6NWNyN3lsQ2dWTndLb19GVGc&range=C14:D19&gid=0&headers=-1';
  var ilimaQuery = new google.visualization.Query(ilimaURL);

  // Set a callback to run when the Ilima floor-level data has been retrieved.
  ilimaQuery.send(displayIlimaEnergyData);

  // Get Overall Dorm Data.
  var dormURL = 'http://spreadsheets.google.com/tq?key=0An9ynmXUoikYdEZwd1l6NWNyN3lsQ2dWTndLb19GVGc&range=C35:D38&gid=0&headers=-1';
  var dormQuery = new google.visualization.Query(dormURL);

  // Set a callback to run when the overall dorm data has been retrieved.
  dormQuery.send(displayDormEnergyData);

  // Get Combined Floor-level data.
  var combinedURL = 'http://spreadsheets.google.com/tq?key=0An9ynmXUoikYdEZwd1l6NWNyN3lsQ2dWTndLb19GVGc&range=A42:D47&gid=0&headers=-1';
  var combinedQuery = new google.visualization.Query(combinedURL);

  // Set a callback to run when the overall dorm data has been retrieved.
  combinedQuery.send(displayCombinedEnergyData);
}


// Callback that gets the Ilima DataTable and displays it.
function displayIlimaEnergyData(response) {
  // Process errors, if any.
  if (response.isError()) {
      alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
      return;
  }
  
  // Get the data table, and sort it by energy value.
  var data = response.getDataTable();
  data.sort([{column: 1}]);
  var chart = new google.visualization.BarChart(document.getElementById('ilima_chart_div'));
  chart.draw(data, {width: 300,
                    height: 200,
                    legend: 'none',
                    title: 'Hale Ilima Energy Per Floor',
                    hAxis: {minValue: '0', title: 'kWh consumed from 5/19/2010 to now'}
                  });
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
  chart.draw(data, {width: 300,
                    height: 200,
                    legend: 'none',
                    title: 'Overall Dorm Energy',
                    hAxis: {minValue: '0', title: 'kWh consumed from 5/19/2010 to now'}
                  });
}

// Callback that gets the Combined floor-level DataTable and displays it.
function displayCombinedEnergyData(response) {
  // Process errors, if any.
  if (response.isError()) {
      alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
      return;
  }
  
  // Get the data table, and sort it by energy value.
  var data = response.getDataTable();
  var chart = new google.visualization.BarChart(document.getElementById('combined_chart_div'));
  chart.draw(data, {width: 300,
                    height: 200,
                    title: 'Dorm Energy Per Floor',
                    hAxis: {minValue: '0', title: 'kWh consumed from 5/19/2010 to now'}
                  });
}