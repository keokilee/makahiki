var dataContainer = null;
var dataSourceUrl = null;
var dataSourceUrlPart1 = "/sources/";
var dataSourceUrlPart2 = "/sensordata/latest?tq=select%20timePoint%2C%20";
var host = null;
var refreshInterval = null;
var unit = null;
var source = null;

google.load("visualization", "1");
//google.setOnLoadCallback(sendQuery);

/**
 * testing data source name: "monitor-test", "monitor-test2", and "monitor-test3"
 * testing host: http://server.wattdepot.org:8184/gviz
 * datasource Url structure: {host}/sources/{source}/sensordata/latest?tq={queryString}   
 */
function sendQuery(host, source) {
  refreshInterval = 15000;
  var powerLastCheck = document.getElementById('powerlastcheck');
  var energyLastCheck = document.getElementById('energylastcheck');

  powerUrl = host + dataSourceUrlPart1 + source + dataSourceUrlPart2 + "powerConsumed";
  energyUrl = host + dataSourceUrlPart1 + source + dataSourceUrlPart2 + "energyConsumedToDate";
  powerLastCheck.innerHTML = generateCheckDate();
  energyLastCheck.innerHTML = generateCheckDate();

  var powerQuery = new google.visualization.Query(powerUrl);
  var energyQuery = new google.visualization.Query(energyUrl);
  powerQuery.send(handlePowerQuery);
  energyQuery.send(handleEnergyQuery);

  setTimeout(function() {
    sendQuery(host, source);
  },refreshInterval);
}

/**
 * Query response handler function.
 * Called by the Google Visualization API once the response is received.
 * Takes the query response and formats it as a table.
 */
function handlePowerQuery(response) {
  var dataDiv = document.getElementById('powerdata');
  dataContainer = new monitor.visualization(dataDiv);
  var data = response.getDataTable();

  dataContainer.draw(data, "Watts");
}

/**
 * Query response handler function.
 * Called by the Google Visualization API once the response is received.
 * Takes the query response and formats it as a table.
 */
function handleEnergyQuery(response) {
  var dataDiv = document.getElementById('energydata');
  dataContainer = new monitor.visualization(dataDiv);
  var data = response.getDataTable();

  dataContainer.draw(data, "Watt Hours");
}

// function generateTitle(source, dataDisplayed) {
//   var html = [];
//   html.push(source);
//   html.push("<br />");
//   if (dataDisplayed == "energyGeneratedToDate") {
//     html.push("Current Energy Generated");
//     unit = "Watt Hours";
//   }
//   else if (dataDisplayed == "energyConsumedToDate") {
//     html.push("Current Energy Consumed");
//     unit = "Watt Hours";
//   }
//   else if (dataDisplayed == "powerGenerated") {
//     html.push("Current Power Generated");
//     unit = "Watts";
//   }
//   else if (dataDisplayed == "powerConsumed") {
//     html.push("Current Power Consumed");
//     unit = "Watts";
//   }
//   else {
//     html.push(dataDisplayed);
//   }
//   return html.join('');
// }

function generateCheckDate() {
  var html = [];
  var checkDate = new Date();
  var months = new Array('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec');
  html.push("<font style = \"font-size:0.8em; font-style: italic\">Last check was at: ");
  html.push(months[checkDate.getMonth()]);
  html.push(" " + checkDate.getDate() + ", " + checkDate.getFullYear() + " ");
  html.push(checkDate.toLocaleTimeString());
  html.push("</font>");
  return html.join('');
}
  





