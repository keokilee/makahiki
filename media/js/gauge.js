var gauge = null;
var options = null;
var host = null;
var dataSourceUrl = null;
var source = null;
var dataSourceUrlPart1 = "/sources/";
var dataSourceUrlPart2 = "/sensordata/latest?tq=select%20timePoint%2C%20";
var dataDisplayed = null;
var yellowThreshold = null;
var redThreshold = null;
var maxThreshold = null;
var refreshInterval = null;
var queryDataValue = null;
var sourcediv = document.getElementById("sourcediv");
var data_displayed_div = document.getElementById("data_displayed_div");
var lastcheckdiv = document.getElementById("lastcheckdiv");

var loadingMsgContainer = document.getElementById('loading');
if (loadingMsgContainer){
  loadingMsgContainer.style.display='none';
}

google.load('visualization', '1', {packages:['gauge']});
google.setOnLoadCallback(sendQuery);

/**
 * Sets up the data source to be queried.
 */
function sendQuery() {
  host = checkTrailingSlash("http://server.wattdepot.org:8188/gviz");
  source = "kailua-house";
  dataDisplayed = "powerConsumed";
  yellowThreshold = "150";
  redThreshold = "250";
  maxThreshold = "300";
  refreshInterval = 15000;

  dataSourceUrl = host + dataSourceUrlPart1 + source + dataSourceUrlPart2 + dataDisplayed;
  
  sourcediv.innerHTML = '<p align=\"center\" style=\"font-weight:bold;font-size:large;\">' + source + '</p>'
  data_displayed_div.innerHTML= '<p align=\"center\" style=\"font-weight:bold;font-size:large;\">' + generateDataDisplayed(dataDisplayed) + '</p>';
  
  gauge = new google.visualization.Gauge(document.getElementById('chartdiv'));
  
  setGaugeOptions(yellowThreshold, redThreshold, maxThreshold);

  moveTicker();
}

/**
 * Query response handler function.
 * Called by the Google Visualization API once the response is received.
 * Takes the query response and formats it as a table.
 */
function handleDataValueQueryResponse(responseDataValue) {
  var data = responseDataValue.getDataTable();
  data.setColumnLabel(1, "Watts");
  //generateGaugeUnits(data);
  gauge.draw(data, options);
}

/**
 * Moves the gadget ticker whenever the gauge refreshes
 * instead of refreshing the whole gauge image.
 */
function moveTicker() {
  queryDataValue = new google.visualization.Query(dataSourceUrl);
  queryDataValue.send(handleDataValueQueryResponse);
  lastcheckdiv.innerHTML = generateCheckDate();
  setTimeout("moveTicker()", refreshInterval);
}

/**
 * Checks if there is a trailing slash in the url to parse to accepted program url.
 * Then returns the string without the trailing slash.
 * Ex. http://server.wattdepot.org:8188/gviz/ returns http://server.wattdepot.org:8188/gviz
 */
function checkTrailingSlash(url) {
  var str = url;
  var char = str.charAt(str.length-1);
  if (char.match("/") == null){
    return str;
  } else {
    return str.substr(0,str.length-1);
  }
}

function generateDataDisplayed(dataDisplayed){
  var data = dataDisplayed;
  if (data.match("powerConsumed")) {
    return "Power Consumed";
  } else {
    return "Power Generated";
  }
}

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

function setGaugeOptions(yellowThreshold, redThreshold, maxGaugeValue){
  var yellowValue = yellowThreshold;
  var redValue = redThreshold;
  var maxValue = maxGaugeValue;

  if(yellowValue == 0){
    yellowValue = null;
  }

  if(redValue == 0){
    redValue = null;
  }

  options = {width: 400, height: 120, redFrom: redValue, redTo: maxValue, yellowFrom:yellowValue, yellowTo: redValue, minorTicks: 5, max: maxValue};
}

/**
 * Since the power generated or consumed is always in watts, this function converts watts to MW, or kW. 
 */
function generateGaugeUnits(dataTable){
  var table = dataTable;
  var watts = table.getValue(0,1);
  var unit = null;
  
  if(watts >= 10000000){
    unit = "MW";
    watts = watts/1000000;
  } else if(watts >= 10000){
    unit = "kW";
    watts = watts/1000
  } else {
    unit = "Watts";
  }

  //debugdiv.innerHTML = '<p align=\"center\" style=\"font-weight:bold;font-size:large;\">Cell (0,1):' +watts + '</p>';

  table.setColumnLabel(1, unit);
  table.setValue(0,1,watts);
  updateGaugeOptions(unit);
}

function updateGaugeOptions(unit){
  var yellowValue = yellowThreshold;
  var redValue = redThreshold;
  var maxValue = maxThreshold;

  if(unit.match("MW")){
    yellowValue = yellowValue/1000000;
    redValue = redValue/1000000;
    maxValue = maxValue/1000000;
  }

  if(unit.match("kW")){
    yellowValue = yellowValue/1000;
    redValue = redValue/1000;
    maxValue = maxValue/1000;
  }

  options = {width: 400, height: 120, redFrom: redValue, redTo: maxValue, yellowFrom:yellowValue, yellowTo: redValue, minorTicks: 5, max: maxValue};
}



