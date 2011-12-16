Namespace("org.wattdepot.makahiki");

// Store user preferences in corresponding variables.
var title = "Energy Consumed";
var host_uri = 'http://server.wattdepot.org:8192/gviz/';
var dataType = "energyConsumed";

// an array for collected tables which will be combined for display.
var table;

var options = {};
options['passThroughBlack'] = false;
options['drawBorder'] = false;
//   options['mapWidth'] = 450;
//   options['mapHeight'] = 300;
options['cellWidth'] = 18;
options['cellHeight'] = 18;

// Array to hold all the months, used in implementing Date Picker.
var monthArray = new Array('Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec');

google.setOnLoadCallback(initialize);

/* Parses the user preferences and generates the Query to WattDepot and displays the BioHeatMap. */
function initialize() {

    var dorms = document.getElementsByName("heatmap-dorm");
    var dorm;
    for (i = 0; i < dorms.length; i++)
        if (dorms[i].checked)
            dorm = dorms[i].value;

    var lounges = document.getElementsByName("heatmap-lounge-" + dorm);

    source = [];
    for (i = 0; i < lounges.length; i++) {

        source.push(lounges[i].id);
    }
    //debug(source);

    table = new Array();

    var periods = document.getElementsByName("period");
    for (i = 0; i < periods.length; i++)
        if (periods[i].checked)
            dateRange = periods[i].value;

    // Depending on the data range selected,
    // changed the sample-interval to WattDepot to compensate for daily or hourly values.
    // Only need to overwrite for last7 and last 14 days since defaults are already set for 24 hours.
    if (dateRange == "last14days") {
        interval = 1440; // How many minutes in a day, for WattDepot query.
        goBack = 312; // 24 hrs * 13 days, go back 6 days from now to get a weeks worth of data.
        showTime = false; // Show the date instead of time on the visualization.
    }
    if (dateRange == "last24hours") {
        interval = 60; // How many minutes in a day, for WattDepot query.
        goBack = 24; // 24 hrs * 13 days, go back 13 days from now to get two weeks worth of data.
        showTime = true; // Show the date instead of time on the visualization.
    }

    // Set the beginning and end dates
    endDate = new Date();
    // Get on the hour data starting from last midnight.
    endDate.setMinutes(0);
    endDate.setHours(0);

    // Copy the endDate then subtract the necessary hours.
    // Last two 0's of the constructor sets the seconds and milliseconds to 0.
    begDate = new Date(endDate.getFullYear(), endDate.getMonth(),
        endDate.getDate(), endDate.getHours(), endDate.getMinutes(), 0, 0);
    begDate.setHours(0);
    begDate.setHours(begDate.getHours() - goBack);
    begDate.setMinutes(0);

    // Initialize beginning and ending variables to hold the timestamp
    // in XMLGregorian format that WattDepot requires.
    // Use the appendZero function for hour and minutes to append extra 0 if the value is less than 10.
    // This is used to conform to XMLGregorian format.
    var begHour = appendZero(begDate.getHours());
    var begMin = appendZero(begDate.getMinutes());
    var endHour = appendZero(endDate.getHours());
    var endMin = appendZero(endDate.getMinutes());

    var endTimestamp = 'T' + endHour + ":" + endMin + ':00.000-10:00';
    var begTimestamp = 'T' + begHour + ":" + begMin + ':00.000-10:00';

    // Put together the year, month, and day into Gregorian timestamp
    var startTime = begDate.getFullYear() + '-' + appendZero(begDate.getMonth() + 1) + '-'
        + appendZero(begDate.getDate()) + begTimestamp;

    var endTime = endDate.getFullYear() + '-' + appendZero(endDate.getMonth() + 1) + '-'
        + appendZero(endDate.getDate()) + endTimestamp;

    // Build the query URL to WattDepot based on user preference.
    // Format:
    // {host}/sources/{source}/calculated?startTime={timestamp}&endTime={timestamp}&samplingInterval={interval}&displaySubsources={boolean}&tq={queryString}
    // More info. at http://code.google.com/p/wattdepot/wiki/UsingGoogleVisualization#Power/Energy/Carbon_URI
    // In order to support multiple sources in a single visualization, need to create an array of queries
    // and store each as an element in the array.
    var query = new Array();
    for (l = 0; l < source.length; l++) {
        var url = host_uri + 'sources/' + source[l].toString() + '/calculated?startTime=' +
            startTime + '&endTime=' + endTime + '&samplingInterval=' + interval;
        //debug(url);
        query[l] = new google.visualization.Query(url);
        query[l].setQuery('select timePoint, ' + dataType);
    }
    query[0].send(function(response) {
        responseHandler(response, query, source, 0);
    });

    // Write to the gadget the last time updated.
    var outputNow = new Date();
    document.getElementById("lastchecked").innerHTML = "Last checked: ";
    document.getElementById("lastchecked").innerHTML += outputNow.getDate() + "-" +
        monthArray[outputNow.getMonth()] + "-" + outputNow.getFullYear();
    document.getElementById("lastchecked").innerHTML += " " + outputNow.toLocaleTimeString();

    // Refresh every hour.
    //setTimeout("initialize()", 3600000);
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
    // Container for where the BioHeatMap will be drawn on the gadget.

    // If an error occurred with the response, output an error message and stop the gadget.
    if (response.isError()) {
        var errorMessage = response.getMessage();
        document.getElementById('datadiv').innerHTML = "Error: " + errorMessage;
        document.getElementById('datadiv').innerHTML += "<br />" + response.getDetailedMessage();
        return;
    }

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
    if (number == query.length) {
        combineTable(table);
    }
    else {
        //sends another query with the new number and the next in line.
        query[number].send(function(response) {
            responseHandler(response, query, source, number);
        });
    }

}

/*
 * Contains the function which takes an array of data tables and combines them together into one for visualization.
 *
 * @param array is the array of all data tables to be combined.
 */
function combineTable(array) {
    // Combines tables only if there are multiple data tables in the array.
    if (array.length > 1) {
        //combined variable hold beginning array which is also becomes the combined array.
        var combined = array[0];

        for (i = 1; i < array.length; i++) {
            var complete = false;

            // Defines an array with the numbers for each column of a table which will be added.
            var dt1 = makeColArray(combined.getNumberOfColumns());
            var dt2 = makeColArray(array[i].getNumberOfColumns());

            // Combines the data tables together through google visualization.
            combined = google.visualization.data.join(combined, array[i], 'full', [
                [0,0]
            ], dt1, dt2);
            if (i == (array.length - 1)) {
                complete = true;
            }
            // If all the arrays are complete then continue to display function.
            if (complete) {
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
function makeColArray(number) {
    var cols = new Array();
    //push numbers onto an array to make a incrementing array.
    for (j = 1; j < number; j++) {
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

    // Disable the loading gif to be replaced by the BioHeatMap.
    var loadingMsgContainer = document.getElementById('loading');
    if (loadingMsgContainer) {
        loadingMsgContainer.style.display = 'none';
    }

    //debug(display);

    var container = document.getElementById('datadiv');

    // Define the heatmap to be displayed in the "container"
    var heatmap = new org.systemsbiology.visualization.BioHeatMap(container);

    heatmap.draw(display, options);
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
        postTable.addColumn(temp.getColumnType(1), temp.getValue(i, 0));
    }

    // Set the column labels (times) that will be displayed on the visualization.
    // 0-th column holds all the names of the sources.
    postTable.setColumnLabel(0, "Sources");
    for (i = 0; i < rows; i++) {
        postTable.setColumnLabel(i + 1, formatDate(temp.getValue(i, 0)));
    }

    // Finally loop through each element in the original table and
    // add the transposed values to their appropriate cell.  Adds values by row.
    for (j = 1; j < cols; j++) {
        // All values for a source is pushed onto this array.
        var addedrow = new Array();
        // Add the source name as a label for the row for viewing.
        addedrow.push(source[j - 1]);
        // Each value in traversing column in the original data table gets pushed.
        for (k = 0; k < rows; k++) {
            addedrow.push(Number(temp.getValue(k, j).toFixed(0)));
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
function formatDate(date) {
    // Depending on the date range, either show the time or date as the column label.
    if (showTime) {
        // Hours in a Date object are stored 0-23, used % 12 to convert to AM/PM.
        // Append any 0's in front to align the labels on display.
        var columnHour = appendZero(date.getHours() % 12);
        var columnMin = appendZero(date.getMinutes());
        var amPM;
        if (date.getHours() >= 12) {
            amPM = "PM";
        }
        else {
            amPM = "AM";
        }
        if (columnHour == '00') {
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
function appendZero(number) {
    if (number < 10) {
        return '0' + number;
    }
    return number;
}

function updatePeriod() {

    // Clear the contents of the drop-down menus, and re-display the loading sign.
    document.getElementById("datadiv").innerHTML = "";
    document.getElementById("loading").style.display = '';
    initialize();
}

/**
 * Outputs the message to the Firebug console window (if console is defined).
 */
function debug(msg) {
    if (typeof(console) != 'undefined') {
        console.info(msg);
    }
}