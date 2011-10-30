Namespace("org.wattdepot.makahiki");

/**  Load the Visualization API and the bar chart package. */
google.load("visualization", "1", {packages:['corechart', 'imagechart']});

/** Set a callback to run when the Google Visualization API is loaded. */
google.setOnLoadCallback(initialize);

var title = "Energy Consumed";
var host_uri = 'http://server.wattdepot.org:8192/gviz/';

var dataType = "energyConsumed";
var dateRange = "last7days"
var goBack = 168;
var interval = 60;

var table = new Array();
var endDate;
var begDate;
var source;

// Array to hold all the months, used in implementing Date Picker.
var monthArray = new Array('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec');

function initialize() {
    source = document.getElementById("lounge").value;

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

    var url = host_uri + 'sources/' + source + '/calculated?startTime=' +
        startTime + '&endTime=' + endTime + '&samplingInterval=' + interval;
    query = new google.visualization.Query(url);
    //debug(url);
    query.setQuery('select timePoint, ' + dataType);

    query.send(function(response) {
        responseHandler(response, query, source, 0);
    });

    // Write to the gadget the last time updated.
    var outputNow = new Date();
    document.getElementById("lastchecked").innerHTML = "Last checked: " +
        outputNow.getDate() + "-" +
        monthArray[outputNow.getMonth()] + "-" +
        outputNow.getFullYear() + " " +
        outputNow.toLocaleTimeString();

    // Refresh every hour.
    // setTimeout("initialize()", 3600000);
}

/*
 * Sets the on board gadget option of changing the time or day, depending on the date range.
 */
function setOnboardOptions() {
    document.getElementById("onboardoptions").innerHTML = "<a href=\"javascript:showControl()\">Change Lounge</a>";
}

/** Once dorm data is retrieved, create and display the chart with tooltips. */
function responseHandler(response, query, source, number) {
    // Disable the loading gif 
    var loadingMsgContainer = document.getElementById('loading');
    if (loadingMsgContainer) {
        loadingMsgContainer.style.display = 'none';
    }

    // Process errors, if any.
    if (response.isError()) {
        alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
        return;
    }
    // Get the dorm data table.
    var data = response.getDataTable();

    // Make the image element.
    makeHotSpotImageElement(data);
}

/**  Generate an img tag with a chart URL and an accompanying map element for displaying data.  */
function makeHotSpotImageElement(data) {
    var scaleView = new google.visualization.DataTable();
    var view = transpose(data, scaleView);
    var img = document.createElement('img');
    img.setAttribute('src', getChartUrl(scaleView));
    img.setAttribute('usemap', '#tooltipMap', 0);
    img.setAttribute('usemap', '#tooltipMap', 0);
    // Remove the blue line around the image.
    img.style.border = '0';
    document.getElementById('img').appendChild(img);
    document.getElementById('img').appendChild(createMap(view));
}

/*
 * Transposes a response Data Table returned by the WattDepot
 * server used for a Google Visualization.  Response table contains
 * two columns, "datetime" and "numbers".  This method is used to
 * conform to a wanted view of rows of sources, and columns of dates.
 *
 * @param tempTable is a Google response table to be transposed.
 */
function transpose(tempTable, scaleView) {

    // Store a copy of the original copy.
    var temp = tempTable;

    // Record the amount of rows and columns.
    var rows = temp.getNumberOfRows() - 1;
    var cols = temp.getNumberOfColumns();

    // Create a new blank DataTable to populate manually.
    var postTable = new google.visualization.DataTable();

    // columns are X,Y,value, i.e., time, date, value
    postTable.addColumn('number');
    postTable.addColumn('number');
    postTable.addColumn('number');

    scaleView.addColumn('number');
    scaleView.addColumn('number');
    scaleView.addColumn('number');

    for (k = 0; k < rows; k++) {
        x = k % 24;
        y = Number(parseInt(k / 24));
        size = Number(temp.getValue(k, 1).toFixed(0));
        scalesize = Math.round(temp.getValue(k, 1) / 100);

        var addedrow = new Array();
        var addedrow2 = new Array();

        addedrow.push(x);
        addedrow.push(y);
        addedrow.push(size);

        addedrow2.push(x);
        addedrow2.push(y);
        addedrow2.push(scalesize);

        postTable.addRow(addedrow);
        scaleView.addRow(addedrow2);
    }

    // debug(postTable);
    return postTable;
}

/**
 * Returns the URL for generating the chart.
 * Temporarily use the google visualization call to do it to simplify creation of the data parameter.
 * This results in 'flicker' and an extra HTTP call.
 * We can generate the data param manually later in order to fix this.
 * Note we need to create a view containing just the (x,y,data) columns
 */
function getChartUrl(data) {

    var chart = new google.visualization.ImageChart(document.getElementById('chart_div'));
    chart.draw(data, getOptions(data));

    // Get the URL without URL encoding of commas, pipes, and colons, since they take up too many characters and we have a 2K limit
    var gvizChartUrl = chart.getImageUrl().replace(/%2C/g, ',').replace(/%7C/g, '|').replace(/%3A/g, ':');
    //debug('Gviz URL is: ' + gvizChartUrl);

    return gvizChartUrl;
}

/** Build and return the options array for the chart. */
function getOptions(data) {
    // Set up the options
    var options = {};
    // Scatter chart
    options.cht = 's';
    // Image size
    options.chs = '500x200';
    // X-axis (0) and Y-axis (1) labels
    options.chxl = '0:|' + getXAxisLabels(data) + '|1:|' + getYAxisLabels(data);
    // Adjust the X & Y axis with -1 so that dots line up correctly.
    // The last two numbers indicate the scaling range.
    // Supply the lowest and highest value in the dataset to get automatic dot scaling.
    var valueColumn = 2;
    var maxValue = getMaxColumnValue(data, 2)

    options.chds = '-1,24,-1,7,0,' + maxValue;

    // Shape marker: o = circle, 333333 = black, 1 = data series, -1 = allpoints, 20 = max size in pts.
    var maxSpotSize = 20;
    var defaultMarker = 'o,459E00,1,-1,' + maxSpotSize;

    options.chm = defaultMarker + getHighlightMarkers(data, maxValue, maxSpotSize);
    options.enableEvents = true;

    return options;
}

function getNumXCoords(data) {
    return 24;
}

function getNumYCoords(data) {
    return 7;
}

/** Returns the maximum value found in the given column. */
function getMaxColumnValue(data, column) {
    var max = 0;

    for (var i = 0; i < data.getNumberOfRows(); i++) {
        var currValue = data.getValue(i, column);
        if (currValue > max) {
            max = currValue;
        }
    }

    return max;
}

/** Return the marker strings for the hot spots that should be highlighted. */
function getHighlightMarkers(data, maxValue, maxSpotSize) {
    var highlightColor = 'FF0000';
    var valueColumn = 2;
    var returnString = '';

    var rowInds = data.getSortedRows([
        {column: valueColumn, desc: true}
    ]);
    for (var i = 0; i < 5; i++) {
        var v = data.getValue(rowInds[i], valueColumn);
        var scaledValue = Math.ceil(((v / maxValue) * 100) / (100 / maxSpotSize));
        returnString = returnString +
            '|o,' +
            highlightColor + ',' +
            '1' + ',' +
            rowInds[i] + ',' +
            scaledValue;

    }

    return returnString;
}

/** Return the labels for the X Axis. */
function getXAxisLabels(data) {
    return '|12am|1|2|3|4|5|6|7|8|9|10|11|12pm|1|2|3|4|5|6|7|8|9|10|11|';
}

/** Return the labels for the Y Axis. */
function getYAxisLabels(data) {

    var yLabel = '|';
    var mon = appendZero(begDate.getMonth() + 1);
    for (i = begDate.getDate(); i < endDate.getDate(); i++)
        yLabel += mon + '-' + appendZero(i) + '|';
    return yLabel;
}


/** Create and return the image map element.  */
function createMap(data) {
    var map = document.createElement('map');
    map.setAttribute('id', 'tooltipMap');
    map.setAttribute('name', 'tooltipMap');

    // Initial offset into the chart to get the map aligned with the (x,y) values.
    // (xOffSet, yOffset) must be the position of the bottom left dot.
    // Note that these need to be custom set for each chart, I don't know any way to compute them!
    // Use Firebug > HTML > div id="img" > map  and then move mouse over first area tag to see the location.
    var yOffset = 158; //158;
    var xOffset = 55; //75;
    var columnWidth = 18; // 17.3;
    var rowHeight = 21.5;
    var mapRadius = 8;

    // loop through all the data points.
    for (var i = 0; i < data.getNumberOfRows(); i++) {
        // Get the x and y values.
        var x = data.getValue(i, 0);
        var y = data.getValue(i, 1);
        var label = data.getValue(i, 2).toFixed(0) + ' Wh';

        var area = document.createElement('area');
        area.setAttribute('id', '' + i);
        area.setAttribute('shape', 'circle');
        var xCoord = (xOffset + (columnWidth * x)).toFixed(0);
        var yCoord = (yOffset - (rowHeight * y)).toFixed(0);
        area.setAttribute('coords', '' + xCoord + ',' + yCoord + ',' + mapRadius);
        area.setAttribute('nohref', 'nohref');
        area.setAttribute('onmouseover', 'showTooltip(\'' + label + '\',' + xCoord + ',' + yCoord + ');');
        area.setAttribute('onmouseout', 'hideTooltip();');
        map.appendChild(area);
    }
    return map;
}
/**
 * Outputs the message to the Firebug console window (if console is defined).
 */
function debug(msg) {
    if (typeof(console) != 'undefined') {
        console.info(msg);
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


function showTooltip(label, xCoord, yCoord) {
    var tooltip = document.getElementById('tooltip');
    tooltip.style.left = (30 + xCoord + 20) + 'px';
    tooltip.style.top = (320 + yCoord + 20) + 'px';
    tooltip.style.width = 'auto';
    tooltip.style.height = 'auto';
    tooltip.style.position = 'absolute';
    tooltip.style.background = '#fff';
    tooltip.innerHTML = label;
    tooltip.style.borderStyle = 'solid';
    tooltip.style.borderWidth = 'thin';
    tooltip.style.color = '459E00';
    tooltip.style.visibility = 'visible';
}

function hideTooltip() {
    document.getElementById('tooltip').style.visibility = 'hidden';
}

function updateLounge() {

    source = document.getElementById("lounge").value;

    // Clear the contents of the drop-down menus, and re-display the loading sign.
    document.getElementById("img").innerHTML = "";
    document.getElementById("loading").style.display = '';
    initialize();
}
