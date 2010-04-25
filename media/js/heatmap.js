google.load("visualization", "1", {});

systemsbiology.load("visualization", "1.0", {packages:["bioheatmap"]});

// uri given by user to connect to data server.
var host_uri;
// user select type for query.
var dataType;
// user selected source for data.
var source;
// user select dataRange type: 24 hours, 7 or 14 days.
var dateRange;
// used to subtract hour duration based on date range.
var goBack = 24;
// assists in creation of url query by storing string for day.
var day = '';
// assists in creation of url query by storing string for month.
var month = '';
// assists in creation of url query by storing string for year.
var year = '';
// assists in creation of url query by storing string for the starting time.
var startTime = '';
// assists in creation of url query by storing string for the ending time.
var endTime = '';
// defines the interval for query displays, defaults to 2 hours and set to 1440 minutes for 24 hours.
var interval = 120;
// boolean flag to ensure the display of time or date on gadget.
var showTime = true;
// an array for collected tables which will be combined for display.
var table = new Array();
// current date for display.
var newDate;

// Array to hold all the months, used in implementing Date Picker.
var monthArray = new Array('Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec');

// Set default values used to see if user is manually changing time.
var endHour = -1;
var endMin = -1;

google.setOnLoadCallback(initialize);

/* Parses the user preferences and generates the Query to WattDepot and displays the BioHeatMap. */ 
function initialize() {
  var sources = "saunders-floor-2,saunders-floor-3,saunders-floor-4"
  // Store user preferences in corresponding variables.
  host_uri = "http://server.wattdepot.org:8188/gviz";
  source = sources.split(', ');
  dataType = "powerConsumed";
  dateRange = "last7days";
  table = new Array();

  // Depending on the data range selected,
  // changed the sample-interval to WattDepot to compensate for daily or hourly values.
  // Only need to overwrite for last7 and last 14 days since defaults are already set for 24 hours.
  if (dateRange == "last7days") {
    interval = 1440; // How many minutes in a day, for WattDepot query.
    goBack = 144; // 24 hrs * 6 days, go back 6 days from now to get a weeks worth of data.
    showTime = false; // Show the date instead of time on the visualization.
  }
  if (dateRange == "last14days") {
    interval = 1440; // How many minutes in a day, for WattDepot query.
    goBack = 312; // 24 hrs * 13 days, go back 13 days from now to get two weeks worth of data.
    showTime = false; // Show the date instead of time on the visualization.
  }

  // Set the beginning and end dates for the BioHeatMap.
  var endDate = new Date();
  // If newDate has been initialized, then the user has selected a new ending point.
  if (newDate) {
    endDate = newDate; 
  }

  // Get on the hour data starting from last midnight.
  endDate.setMinutes(0);
  endDate.setHours(0);
  // Copy the endDate then subtract the necessary hours.
  // Last two 0's of the constructor sets the seconds and milliseconds to 0.
  var begDate = new Date(endDate.getFullYear(), endDate.getMonth(), 
      endDate.getDate(), endDate.getHours(), endDate.getMinutes(), 0, 0);
  begDate.setHours(0);
  begDate.setHours( begDate.getHours() - goBack );
  begDate.setMinutes(0);

  // Initialize beginning and ending variables to hold the timestamp 
  // in XMLGregorian format that WattDepot requires.
  // Use the appendZero function for hour and minutes to append extra 0 if the value is less than 10.
  // This is used to conform to XMLGregorian format.
  var begHour = appendZero( begDate.getHours() );
  var begMin = appendZero( begDate.getMinutes() );

  // If endHour is at default value -1, then this is the first time
  // the gadget is being run without any on board changes.  Therefore
  // Use endDate parameters, else, parse the newly selected hour by the user.
  if (endHour == -1) {
    endHour = appendZero( endDate.getHours() );
  }
  else {
    begDate.setHours( endHour );
    endHour = appendZero( endHour );
    begHour = appendZero( begDate.getHours() );
  }

  if (endMin == -1) {
    endMin = appendZero( endDate.getMinutes() );
  }
  else {
    begDate.setMinutes( endMin );
    endMin = appendZero( endMin );
    begMin = appendZero( begDate.getMinutes() );
  }

  var endTimestamp = 'T' + endHour + ":" + endMin + ':00.000-10:00';
  var begTimestamp = 'T' + begHour + ":" + begMin + ':00.000-10:00';

  day = appendZero( begDate.getDate() );

  // The month that is retrieved from Date object goes from 0 - 11, need to increment to get standard 1 - 12.
  if (begDate.getMonth() < 10) {
    month = '0' + (begDate.getMonth() +1);  
  }
  else {
    month = (begDate.getMonth() + 1);  
  }

  // Assign years. 
  year = begDate.getFullYear();

  // Puts together the year, month, and day into XMLGregorian timestamp for the beginning time.
  startTime = year + '-' + month + '-' + day + begTimestamp;  
  
  day = appendZero ( endDate.getDate() ); 

  // The month that is retrieved from Date object goes from 0 - 11, need to increment to get standard 1 - 12.
  if (endDate.getMonth() < 10) {
    month = '0' + (endDate.getMonth() +1);  
  }
  else {  
    month = (endDate.getMonth() + 1);  
  }

  // Ass ign years. 
  year = endDate.getFullYear();

  // Put together the year, month, and day into Gregorian timestamp for the ending time.
  endTime = year + '-' + month + '-' + day + endTimestamp;

  // Build the query URL to WattDepot based on user preference.
  // Format:
  // {host}/sources/{source}/calculated?startTime={timestamp}&endTime={timestamp}&samplingInterval={interval}&displaySubsources={boolean}&tq={queryString}
  // More info. at http://code.google.com/p/wattdepot/wiki/UsingGoogleVisualization#Power/Energy/Carbon_URI
  // In order to support multiple sources in a single visualization, need to create an array of queries
  // and store each as an element in the array.
  var query = new Array();
  for (l = 0; l < source.length; l++) {
    var url = host_uri + 'sources/' + source[l].toString() +  '/calculated?startTime=' + 
          startTime + '&endTime=' + endTime + '&samplingInterval=' + interval;
    query[l] = new google.visualization.Query(url);
    query[l].setQuery('select timePoint, ' + dataType);
  }
  query[0].send(function(response) {responseHandler(response, query, source, 0);});

  // Write to the gadget the last time updated.
  var outputNow = new Date();
  document.getElementById("lastchecked").innerHTML = "Last checked: ";
  document.getElementById("lastchecked").innerHTML += outputNow.getDate() + "-" + 
  monthArray[outputNow.getMonth()] + "-" + outputNow.getFullYear();
  document.getElementById("lastchecked").innerHTML += " " + outputNow.toLocaleTimeString();
  setOnboardOptions();

  // Refresh every hour.
  setTimeout("initialize()", 3600000);
}

/* 
* Handles the response back from WattDepot which returns a Google Visualization dataTable object.
* Uses the returned table from WattDepot and draws the BioHeatMap.
*
* @param response is the response from WattDepot.
* @param query is the array of WattDepot query urls to be retrieved.
* @param source is the current source being handled
* @param number is the current index in the array of queries.
*/
function responseHandler(response, query, source, number) {

  // Disable the loading gif to be replaced by the BioHeatMap.
  var loadingMsgContainer = document.getElementById('loading');
  if (loadingMsgContainer) {
    loadingMsgContainer.style.display = 'none';
  }

  // Container for where the BioHeatMap will be drawn on the gadget.
  var container = document.getElementById('datadiv');

  // If an error occurred with the response, output an error message and stop the gadget.
  if (response.isError()) {
    var errorMessage = response.getMessage();
    document.getElementById('datadiv').innerHTML = "Error: " + errorMessage;
    document.getElementById('datadiv').innerHTML += "<br />" + response.getDetailedMessage();
    gadgets.window.adjustHeight();
    return;
  }

  // Define the heatmap to be displayed in the "container"
  heatmap = new org.systemsbiology.visualization.BioHeatMap(container);
  var responseTable = response.getDataTable();

  // Rename each column to match Source, since a response table from WattDepot does not
  // explicitly display the source it is from.
  responseTable.setColumnLabel(0, source[number].toString());
  //adds the response table to an Array for display in the visualization
  table.push(responseTable);
  //keeps track of the current number of tables checked.
  number++;
  //compares the number of tables returned with the total requested.
  //sents the tables to be combined together if at the end.
  if(number == query.length) {
    combineTable(table);
  }
  else {
    //sends another query with the new number and the next in line.
    query[number].send(function(response) {
      responseHandler(response, query, source, number);});
  }
}

/*
* Contains the function which takes an array of data tables and combines them together into one for visualization.
* 
* @param array is the array of all data tables to be combined.
*/
function combineTable(array) {
  // Combines tables only if there are multiple data tables in the array.
  if(array.length > 1){
    //combined variable hold beginning array which is also becomes the combined array.
    var combined = array[0];

    for (i=1; i < array.length; i++){
      var complete = false;
  
      // Defines an array with the numbers for each column of a table which will be added.
      var dt1 = makeColArray(combined.getNumberOfColumns());
      var dt2 = makeColArray(array[i].getNumberOfColumns());
  
      // Combines the data tables together through google visualization.
      combined = google.visualization.data.join(combined,array[i], 'full',[[0,0]], dt1, dt2);
      if(i == (array.length-1)){
        complete = true;
      }
      // If all the arrays are complete then continue to display function.
      if(complete){
        displayTable(combined);
      }
    }
  }
  // If there is only one array go immediately to the display function.
  else {
    displayTable(array[0]);
  }
}

/**
* Contains the function which creates an array of incrementing integers up to the parameter specified.
* Used to make arrays for the combined values of tables in a google visualization data table.
* 
* @param number is the highest number which should be in an array and the size of the array.
*/
function makeColArray(number){
  var cols = new Array();
  //push numbers onto an array to make a incrementing array.
  for(j = 1; j < number; j++){
    cols.push(j);
  }
  return cols;
}

/** 
* Draws the BioHeatMap on the Gadget.  
* 
* @param dataTable is a table containing the information to be visualized.
*/
function displayTable(dataTable) {  
  // An associative array that configures the BioHeatMap.
  var display = transpose(dataTable);
  // Options found at: http://informatics.systemsbiology.net/visualizations/heatmap/bioheatmap.html#Configuration_Options
  var options = {};
  options['passThroughBlack'] = false;
  options['drawBorder'] = false;
  heatmap.draw(display, options);
  // Automatically resize the gadget.
  gadgets.window.adjustHeight();
}

/* 
* Transposes a response Data Table returned by the WattDepot 
* server used for a Google Visualization.  Response table contains
* two columns, "datetime" and "numbers".  This method is used to 
* conform to a wanted view of rows of sources, and columns of dates. 
*
* @param tempTable is a Google response table to be transposed.
*/
function transpose(tempTable) {

  // Store a copy of the original copy.
  var temp = tempTable;
  
  // Record the amount of rows and columns.
  var rows = temp.getNumberOfRows();
  var cols = temp.getNumberOfColumns();
  
  // Create a new blank DataTable to populate manually.
  var postTable = new google.visualization.DataTable();

  // First column will be of sources, therefore type string will be used.
  postTable.addColumn('string');

  // Add the appropriate amount of columns as there are rows in the original table.
  for (i = 0; i < rows; i++) {
    postTable.addColumn(temp.getColumnType(1), temp.getValue(i,0));
  }

  // Set the column labels (times) that will be displayed on the visualization.
  // 0-th column holds all the names of the sources.
  postTable.setColumnLabel(0, "Sources");
  for (i = 0; i < rows; i++) {
    postTable.setColumnLabel(i + 1, formatDate(temp.getValue(i,0)) );
  }

  // Finally loop through each element in the original table and
  // add the transposed values to their appropriate cell.  Adds values by row.
  for (j = 1; j < cols; j++) {
    // All values for a source is pushed onto this array.
    var addedrow = new Array();
    // Add the source name as a label for the row for viewing.
    addedrow.push(source[j-1]);
    // Each value in traversing column in the original data table gets pushed.
    for (k = 0; k < rows; k++) {
      addedrow.push(temp.getValue(k,j));
    }
    postTable.addRow(addedrow);
  }
  return postTable;
}

/* 
* Takes in a Date object and returns either a formatted date or time.
* Times are formatted using AM/PM, dates are returned as Month/Day. 
*
* @param date is a date object to be formatted.
*/
function formatDate ( date ) {
  // Depending on the date range, either show the time or date as the column label.
  if ( showTime ) {
    // Hours in a Date object are stored 0-23, used % 12 to convert to AM/PM.
    // Append any 0's in front to align the labels on display.
    var columnHour = appendZero(date.getHours() % 12);
    var columnMin = appendZero(date.getMinutes());
    var amPM;
    if ( date.getHours() >= 12 ) {
      amPM = "PM";
    }
    else {
      amPM = "AM";
    }
    if(columnHour == '00') {
      columnHour = 12; 
    }
    return columnHour + ":" + columnMin + " " + amPM;
  }
  else {
    // Format the date as Month/Day, year is optional, but seems too long for gadget use.
    var columnMonth = date.getMonth() + 1;
    var columnDay = appendZero(date.getDate());
    var ColumnYear = date.getFullYear();
    return columnMonth + "-" + columnDay;
  }
}

/* 
* Appends a 0 at the beginning of a variable if it is less than 10.
* Convenience method to convert to XML Gregorian standards. 
*
* @param number is the number to append '0' if less than 10.
*/
function appendZero ( number ) {
  if (number < 10) {
    return '0' + number;
  }
  return number;
}

/*
* Sets the on board gadget option of changing the time or day, depending on the date range.
*/
function setOnboardOptions() {
  // If a option that displays time is chosen, have the option to set the time.
  // Otherwise display the option to change day.
  if ( showTime ) {
    document.getElementById("onboardoptions").innerHTML = "<a href=\"javascript:showTimeOptions()\">Change End Time</a>";
  }
  else {
    document.getElementById("onboardoptions").innerHTML = "<a href=\"javascript:showDateOptions()\">Change End Day</a>";
  }
}

/*
* Creates and populates a date picker and time drop-down menus via HTML to change the end Date of the Google Gadget. 
*/
function showDateOptions() {
  // Dropdown menus will be displayed in the div tag onboarduidiv.
  var onboarduidiv = document.getElementById("onboarduidiv");
  // Reset the display to show all drop-down menus
  onboarduidiv.style.display = '';
  // Call the corresponding options that return the HTML markup to populate the options for each drop-down.
  var monthDropdown = createMonthDropDown();
  var dayDropdown = createDayDropDown();
  var yearDropdown = createYearDropDown();

  onboarduidiv.innerHTML = "<select id=\"changeDay\">" + dayDropdown + "</select> - ";
  onboarduidiv.innerHTML += "<select id=\"changeMonth\" onchange=\"changeMonth(this.value);\">" + monthDropdown + "</select> - ";
  onboarduidiv.innerHTML += "<select id=\"changeYear\">" + yearDropdown + "</select>";

  // createDropDown menu returns HTML code that contains the options for the specific drop-downs.
  // Create 2 drop-downs for the hour (1 through 12) and minute (0 through 59)
  var hourDropdown = createDropDown(1, 12, "hour");
  var minDropdown = createDropDown(0, 59, "min");

  // Add the outer select tags that will hold the Hour, Minute, and AM/PM drop-down menus.
  onboarduidiv.innerHTML = onboarduidiv.innerHTML + "<br /><select id=\"changeHour\">" + hourDropdown + "</select>";
  onboarduidiv.innerHTML = onboarduidiv.innerHTML + " : " + "<select id=\"changeMin\">" + minDropdown + "</select>";
  if (endHour >= 12) {
    onboarduidiv.innerHTML = onboarduidiv.innerHTML + " " + 
    "<select id=\"amPM\"><option value=\"am\">AM</option><option selected value=\"pm\">PM</option></select>";
  }
  else {
    onboarduidiv.innerHTML = onboarduidiv.innerHTML + " " + 
    "<select id=\"amPM\"><option selected value=\"am\">AM</option><option value=\"pm\">PM</option></select>";
  }

  // Adds the button to save the new setting, once the button is clicked, refreshes the gadget with the new settings.
  onboarduidiv.innerHTML = onboarduidiv.innerHTML + " <input type=\"button\" value=\"Save\" onclick=\"updateDate();\" />";
  onboarduidiv.innerHTML = onboarduidiv.innerHTML + " <input type=\"button\" value=\"Cancel\" onclick=\"clearUIDIV();\" />";

  // Adjust the height of the gadget to accomodate the populated drop-down menues.
  gadgets.window.adjustHeight();
}

/*
* Generates the option HTML markup to populate the Month dropdown menu. 
*/
function createMonthDropDown() {
  // Get the current month to set the default option.
  var currentMonth = new Date().getMonth();

  var monthOptions = '';

  // Generate the HTML markup for the month dropdowns and set the default option to the current month.
  for (var i = 0; i < monthArray.length; i++) {
    if (currentMonth == i) {
      monthOptions = monthOptions + "<option selected value=" + i + ">" + monthArray[i].toString() + "</option>";
    }
    else {
      monthOptions = monthOptions + "<option value=" + i + ">" + monthArray[i].toString() + "</option>";
    }
  }
  return monthOptions;
}

/*
* Generates the option HTML markup to populate the Day dropdown menu.
*/
function createDayDropDown() {
  // Get the curernt day to set the default option.
  var currentDay = new Date().getDate();

  var dayOptions = '';

  // Generate the HTML markup for the amount of days.  Assumes a default 1 through 31.
  for (var i = 1; i <= 31; i++) {
    if (currentDay == i) {
      dayOptions = dayOptions + "<option selected value=" + i + ">" + i + "</option>";
    }
    else {
      dayOptions = dayOptions + "<option value=" + i + ">" + i + "</option>";
    }
  }
  return dayOptions;

}

/* 
* Generates the option HTML markup to populate the Year dropdown menu.
* Populates from current year, down to 10 years. 
*/
function createYearDropDown() {
  // Get the current year to set the default option.
  var currentYear = new Date().getFullYear();

  var yearOptions = "<option selected value=" + currentYear + ">" + currentYear + "</option>";

  // Generate the HTML markup for the number of years.  Goes back 10 years from current. */
  for (var i = (currentYear - 1); i >= (currentYear - 10); i--) {
    yearOptions += "<option value=" + i + ">" + i + "</option>";
  }
  return yearOptions;
}

/* Creates and populates the drop-down menus via HTML to change the end time of the Google Gadget. */
function showTimeOptions() {
  // Dropdown menus will be displayed in the div tag onboarduidiv.
  var onboarduidiv = document.getElementById("onboarduidiv");
  // Reset the display to show all drop-down menus
  onboarduidiv.style.display = '';

  // createDropDown menu returns HTML code that contains the options for the specific drop-downs.
  // Create 2 drop-downs for the hour (1 through 12) and minute (0 through 59)
  var hourDropdown = createDropDown(1, 12, "hour");
  var minDropdown = createDropDown(0, 59, "min");

  // Add the outer select tags that will hold the Hour, Minute, and AM/PM drop-down menus.
  onboarduidiv.innerHTML = "<select id=\"changeHour\">" + hourDropdown + "</select>";
  onboarduidiv.innerHTML = onboarduidiv.innerHTML + " : " + "<select id=\"changeMin\">" + minDropdown + "</select>";
  if (endHour >= 12) {
    onboarduidiv.innerHTML = onboarduidiv.innerHTML + " " + 
      "<select id=\"amPM\"><option value=\"am\">AM</option><option selected value=\"pm\">PM</option></select>";
  }
  else {
    onboarduidiv.innerHTML = onboarduidiv.innerHTML + " " + 
      "<select id=\"amPM\"><option selected value=\"am\">AM</option><option value=\"pm\">PM</option></select>";
  }

  // Adds the button to save the new setting, once the button is clicked, refreshes the gadget with the new settings.
  onboarduidiv.innerHTML = onboarduidiv.innerHTML + " <input type=\"button\" value=\"Save\" onclick=\"updateTime();\" />";
  onboarduidiv.innerHTML = onboarduidiv.innerHTML + " <input type=\"button\" value=\"Cancel\" onclick=\"clearUIDIV();\" />";

  // Adjust the height of the gadget to accomodate the populated drop-down menues.
  gadgets.window.adjustHeight();
}

/* 
* Implements the cancel actions for onboard options by clearing the onboarduidiv tag,
* and resizing the gadget. 
*/
function clearUIDIV() {
  document.getElementById('onboarduidiv').innerHTML = '';
  document.getElementById('onboarduidiv').style.display = 'none';
  gadgets.window.adjustHeight();
}

/* 
* Used to create the drop-down menus for hour and minutes.
* Takes in the start number, the number to end, and the type (hour or min),
* and generates the HTML necessary to create the corresponding drop-down menus. 
*
* @param startNumber is where starting number of the drop-down
* @param endNumber is the ending number of the drop-down.
* @param dropType can by "hour" or "min"
*/
function createDropDown ( startNumber, endNumber, dropType ) {
  // Used to hold all the "option" HTML coding.
  var dropDown = '';

  // Generate the HTML for each option, and sets the default selection to the
  // last displayed end date.
  for (var i = startNumber; i <= endNumber; i++) {
    var displayValue = i;

    // WattDepot uses Gregorian Timestamps which take in double-digits, therefore
    // need to append an extra 0 to numbers less than 10.
    if (i < 10) {
      displayValue = '0' + i;
    }
    // Need to handle hours since Gregorian uses 0 through 23, while the drop-down menu
    // will display standard scale of (1 through 12).
    if (dropType == "hour") {
      if ((endHour == i) || ((endHour % 12) == i) || (endHour == 0 && i == 12)) {
        dropDown = dropDown + "<option selected value=" + i + ">" + displayValue + "</option>";
      }
      else {
        dropDown = dropDown + "<option value=" + i + ">" + displayValue + "</option>";
      }
    }
    if (dropType == "min") {
      if ((endMin == i)) {
        dropDown = dropDown + "<option selected value=" + i + ">" + displayValue + "</option>";
      }
      else {
        dropDown = dropDown + "<option value=" + i + ">" + displayValue + "</option>";
      }
    }
  }
  return dropDown;
}

/*
* When the user selects a month, the day drop-down should be changed to 1-29 for February
* and 1-30 for April, June, September, or November. 
* If the user changes month back to a longer month like January, then the appropriate days
* should be added back to the day select.
*
* @param month is the number of the selected month (0-11)
*/
function changeMonth(month) {
  month++; // Increment from 0-11 to 1-12 scale.
  var selectDay = document.getElementById("changeDay");
  switch (month) {
    case 2:
      if (selectDay.length > 30) {
        selectDay.remove(30);
      }
      if (selectDay.length > 29) {
        selectDay.remove(29);
      }
      break;
    case 4:
    case 6:
    case 9:
    case 11:
      if (selectDay.length > 29) {
        selectDay.remove(30);
      }
      break;
    default: // case 1, 3, 5, 7, 8, 10, or 12
    if (selectDay.length < 30) {
      try {
        var elOptNew = document.createElement('option');
        elOptNew.text = elOptNew.value = '30';
        selectDay.add(elOptNew, null); // standards compliant; doesn't work in IE
      }
      catch(ex) {
        selectDay.add(elOptNew); // IE only
      }
    }
    if (selectDay.length < 31) {
      try {
        var elOptNew = document.createElement('option');
        elOptNew.text = elOptNew.value = '31';
        selectDay.add(elOptNew, null); // standards compliant; doesn't work in IE
      }
      catch(ex) {
        selectDay.add(elOptNew); // IE only
      }
    }
    break;
  }
}

/* Called when the user clicks "Save" when the Date Range is 7 or 14 Days.
* Refreshes the gadget with the values from the drop-down menus.  Will only refresh
* the gadget if the configured time occurs before the current time. 
*/
function updateDate() {
  // To make it easier to compare times, create 2 Date objects, 1 with the current date,
  // and another configured with the user selected options.
  var now = new Date();

  // Grab the new date from the drop-down menu's.
  var newDay = document.getElementById('changeDay').value;
  var newMonth = document.getElementById('changeMonth').value;
  var newYear = document.getElementById('changeYear').value;

  // Grab the new time from the drop-down menu's.
  var newMinute = document.getElementById('changeMin').value;
  var newHour = document.getElementById('changeHour').value;
  // If PM, add 12 to the hour, the value is subtracted by 0 to implicitly convert to integer.
  if (document.getElementById("amPM").value == "pm") {
    if (newHour != 12) {
      newHour = newHour - 0 + 12;
    }
    else {
      if (newHour == 12) {
        newHour = 0;
      }
    }
  }

  // Create a new date object with the user selected date and time.
  // 0's assume 0 seconds and milliseconds.
  var changeDate = new Date(newYear, newMonth, newDay, newHour, newMinute, 0, 0);

  // Compare if the new time is in the future.
  // If it is, output an error message on the gadget.
  if (changeDate > now) {
    document.getElementById("datadiv").innerHTML = "Error: New end date is a date in the future. <br />";
    document.getElementById("datadiv").innerHTML = document.getElementById("datadiv").innerHTML + "Please select another date.";
  }
  else {
    // Else, the date is not in the future. Reset the ending time variables and refresh the gadget.
    endMin = newMinute;
    endHour = newHour;
  
    // Initialize global variable newDate with the new end date to query data.
    newDate = changeDate;
    // Clear the contents of the drop-down menus, and re-display the loading sign.
    document.getElementById("onboarduidiv").innerHTML = "";
    document.getElementById('onboarduidiv').style.display = 'none';
    document.getElementById("datadiv").innerHTML = "";
    document.getElementById("loading").style.display = '';
    initialize();
  }

}

/* 
* Called when the user clicks on "Save" after updating to a new end time.
* Ensures the changed time is not in the future then refreshes the gadget
* with the updated end time. 
*/
function updateTime() {
  // To make it easier to compare times, configure Date variables to appropriate times.
  var now = new Date();
  var changeDate = new Date();
  var tempEndHour = document.getElementById("changeHour").value;

  // If PM, add 12 to the hour, the value is subtracted by 0 to implicitly convert to integer.
  if (document.getElementById("amPM").value == "pm") {
    if (tempEndHour != 12) {
      tempEndHour = tempEndHour - 0 + 12;
    }
  } 
  else {
    if (tempEndHour == 12) {
      tempEndHour = 0;
    }
  }
  changeDate.setHours( tempEndHour );
  changeDate.setMinutes( document.getElementById("changeMin").value );

  // Compare if the new time is in the future.
  // If it is, output an error message on the gadget.
  if (changeDate > now) {
    document.getElementById("datadiv").innerHTML = "Error: New end time is a time in the future. <br />";
    document.getElementById("datadiv").innerHTML = document.getElementById("datadiv").innerHTML + "Please select another time.";
  }
  else {
    // Else, the time is not in the future and reset the ending time variables and refresh the gadget.
    endMin = document.getElementById("changeMin").value;
    endHour = tempEndHour;

    // Clear the contents of the drop-down menus, and re-display the loading sign.
    document.getElementById("onboarduidiv").innerHTML = "";
    document.getElementById('onboarduidiv').style.display = 'none';
    document.getElementById("datadiv").innerHTML = "";
    document.getElementById("loading").style.display = '';
    initialize();
  }
}