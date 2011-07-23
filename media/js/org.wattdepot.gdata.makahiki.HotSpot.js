Namespace("org.wattdepot.gdata.makahiki");

/**  Load the Visualization API and the bar chart package. */
google.load("visualization", "1", {packages:['corechart']});

// Creates a Hot Spot chart with a standard appearance for the Kukui Cup application. 
      
/** Set a callback to run when the Google Visualization API is loaded. */
google.setOnLoadCallback(initializeData);

/** Once visualization API is loaded, retrieve example data and set callback. */
function initializeData() {
  // Get the example data from the spreadsheet.
  var exampleDataURL = 'http://spreadsheets.google.com/tq?&key=0An9ynmXUoikYdEU3bF91ZWIwWlVMcklnb09GSHBZN2c&range=A2:G169&gid=5'
  var exampleDataQuery = new google.visualization.Query(exampleDataURL);
  // Set a callback to run when the dorm data has been retrieved.
  exampleDataQuery.send(displayDormData);
}
      
/** Once dorm data is retrieved, create and display the chart with tooltips. */
function displayDormData(response) {
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
function makeHotSpotImageElement (data) {
  var img = document.createElement('img');
  img.setAttribute('src', getChartUrl(data));
  img.setAttribute('usemap', '#tooltipMap', 0);
  img.setAttribute('usemap', '#tooltipMap', 0);
  // Remove the blue line around the image.
  img.style.border = '0';
  document.getElementById('img').appendChild(img);
  document.getElementById('img').appendChild(createMap(data));
}

/**
 * Returns the URL for generating the chart.
 * Temporarily use the google visualization call to do it to simplify creation of the data parameter.
 * This results in 'flicker' and an extra HTTP call. 
 * We can generate the data param manually later in order to fix this.
 * Note we need to create a view containing just the (x,y,data) columns
 */
function getChartUrl(data) {
  // Create the Chart URL using GViz
//  var view = new google.visualization.DataView(data);
//  view.setColumns([2,3,4]);
//  var chart = new google.visualization.ImageChart(document.getElementById('chart_div'));
//  chart.draw(view, getOptions(data));
  // Remove URL encoding of commas, pipes, and colons, since they take up too many characters and we have a 2K limit
//  var gvizChartUrl = chart.getImageUrl().replace(/%2C/g, ',').replace(/%7C/g, '|').replace(/%3A/g, ':');
//  debug('Gviz URL is: ' + gvizChartUrl);
//  debug('Gviz URL length is : ' + gvizChartUrl.length);

  // Now do it manually.
  var url = 'http://chart.apis.google.com/chart?cht=s' +  
    getChd(data) +
    getChxr(data) +
    getChxl(data) +
    getChs() +
    getChm(data) +
    getChdlp() +
    getChds(data) +
    getChxt();
    
  //debug('My URL is: ' + url);
  // Return the value
  return url;
}

/**
 * Returns the axes to be displayed. 
 */
function getChxt() {
  return '&chxt=x,y';
}

/**
 * Returns the axis range parameter. This simply specifies the number of axis values, which corresponds to the axis labels.
 */
function getChxr(data) {
  return '&chxr=0,-1,' + getNumXCoords(data) + '|1,-1,' + getNumYCoords(data);
}

/**
 * Returns the specification for the X axis and Y axis labels. 
 * Format: 0:||xLabel1|xLabel2|..||1:|yLabel1|yLabel2|...|
 */
function getChxl(data) {
  var xAxisLabelColumn = 0;
  var yAxisLabelColumn = 1;
  var result = ['&chxl=0:||'];
  for (var i = 0; i < getNumXCoords(data); i++) {
    result.push(data.getFormattedValue(i, xAxisLabelColumn), '|');
  }
  result.push('|1:||');
  for (var i = 0; i < getNumYCoords(data); i++) {
    result.push(data.getFormattedValue(i, yAxisLabelColumn), '|');
  }
  return result.join("");
}

/**
 * Returns the size of the chart (width x height) in pixels.
 */
function getChs() {
  var chartWidth = 500;
  var chartHeight = 200;
  return '&chs=' + chartWidth + 'x' + chartHeight;
}

/**
 * Returns the shape marker parameter value.  
 * This parameter consists of a series of marker specifications separated by pipe characters.
 * The first marker specification specifies default marker info. 
 * Default marker info is: o (circle), 459E00 (color), 1 (series index), -1 (all points), 20 (max spot size).
 * After default marker info comes specifications for each of the highlighted spots.  
 * A highlight specification indicates: (o) shape, highlight color, 1 (series index), positional index, and absolute spots size.
 */
function getChm(data) {
  var defaultColor = '459E00';
  var maxSpotSize = 20;
  var defaultSpec = 'o,' + defaultColor + ',1,-1,' + maxSpotSize;
  return '&chm=' + defaultSpec + getHighlightMarkers(data, maxSpotSize);
}

/**
 * Returns the csdlp param, which specifies the legend position. Not sure if this is necessary. 
 */
function getChdlp() {
  return '&chdlp=r';
}

/**
 * Returns the chds param, which specifies scaling. 
 * First two args indicate range of X Axis values. Start with -1 so no dots are at origin.
 * Second two args indicate range of Y Axis values. Start with -1 so no dots are at origin.
 * Final two args are the min and max values, to be used to auto-scale the values. 
 */
function getChds(data) {
  var dataColumn = 4;
  return '&chds=-1,' +  getNumXCoords(data) + ',-1,' + getNumYCoords(data) + ',0,' + getMaxColumnValue(data, dataColumn);
}



/** 
 * Returns the chd parameter to the Chart URL. 
 * This is a string with the format t:{x coords}|{y coords}|{xy vals}
 * For example, given the (x,y,val) tuples (0,0,1), (0,1,2), (1,0,3), (1,1,4), they get encoded as:
 * t:0,1,0,1|0,0,1,1|1,2,3,4
 * One could imagine more intuitive ways to do it.
 */
function getChd(data) {
  var numXCoords = getNumXCoords(data);
  var numYCoords = getNumYCoords(data);
  var dataColumn = 4;
  var result = ['&chd=t:'];
  // First series: print out the X coords Y number of times. 
  for (var y = 0; y < numYCoords; y++) {
    for (var x = 0; x < numXCoords; x++) {
      result.push(x, ',');
    }
  }
  // remove the final trailing ',' and add the pipe
  result.splice(result.lastIndexOf(','), 1);  
  result.push('|');
  // Second series. Print out each Y value X num of times. 
  for (var y = 0; y < numYCoords; y++) {
    for (var x = 0; x < numXCoords; x++) {
      result.push(y, ',');
    }
  }
  // remove the final trailing ',' and add the pipe
  result.splice(result.lastIndexOf(','), 1);  
  result.push('|');
  // Third series. Now put in the data values.
  for (var i = 0; i < data.getNumberOfRows(); i++) {
    result.push(data.getFormattedValue(i, dataColumn), ',');
  }
  // remove the final trailing ','
  result.splice(result.lastIndexOf(','), 1);  
  // return the array as a string.
  return result.join("");
}

function getNumXCoords(data) {
  var xAxisCoordsColumnIndex = 2;
  return data.getDistinctValues(xAxisCoordsColumnIndex).length;
}

function getNumYCoords(data) {
  var yAxisCoordsColumnIndex = 3;
  return data.getDistinctValues(yAxisCoordsColumnIndex).length;
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
  var valueColumn = 4;
  options.chds = '-1,24,-1,7,0,' + getMaxColumnValue(data, valueColumn);
  // Shape marker: o = circle, 333333 = black, 1 = data series, -1 = allpoints, 20 = max size in pts.
  var maxSpotSize = 20;
  var defaultMarker = 'o,459E00,1,-1,' + maxSpotSize;
  options.chm = defaultMarker + getHighlightMarkers(data);
  options.enableEvents = true;
  return options;
}

/** Returns the maximum value found in the given column. */
function getMaxColumnValue(data, column) {
  var max = 0;
  for (var i = 0; i < data.getNumberOfRows(); i++) {
    var currValue = data.getFormattedValue(i, column);
    if ( currValue > max) {
      max = currValue;
    }
  }
  return max;
}

/** Return the marker strings for the hot spots that should be highlighted. */
function getHighlightMarkers(data, maxSpotSize) {
  var highlightColumn = 5;
  var highlightColor = 'FF0000';
  var testString = '|o,FF0000,1,13,5|o,FF0000,1,7,5';
  var xColumn = 2;
  var yColumn = 3
  var valueColumn = 4;
  var returnString = '';
  var maxValue = getMaxColumnValue(data, valueColumn);

  for (var i = 0; i < data.getNumberOfRows(); i++) {
    if (hasData(data, i, highlightColumn)) {
      var value = data.getFormattedValue(i, valueColumn);
      var scaledValue = Math.ceil(((value / maxValue) * 100) / (100 / maxSpotSize));
      returnString = returnString + 
        '|o,' + 
        highlightColor + ',' +
        '1' + ',' +
        i + ',' + 
        scaledValue;
    }
  }
  return returnString;
}

/** Returns true if (row, column) in data has a value. */
function hasData(data, row, column) {
  return (data.getValue(row, column) != null);
}

/** Return the labels for the X Axis. */
function getXAxisLabels(data) {
  return '|12am|1|2|3|4|5|6|7|8|9|10|11|12pm|1|2|3|4|5|6|7|8|9|10|11|';
}

/** Return the labels for the Y Axis. */
function getYAxisLabels(data) {
  return '|Sun|Mon|Tue|Wed|Thr|Fri|Sat|';
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
  var xOffset = 75; //75;    
  var columnWidth = 17.3;
  var rowHeight = 21.5;
  var mapRadius = 8;

  // The numbers corresponding to the columns parts in the data object.
  var xLabelColumn = 0;
  var yLabelColumn = 1;
  var xCoordColumn = 2;
  var yCoordColumn = 3
  var valueColumn = 4;
  var annotationColumn = 6;
  var numXLabels = getNumXCoords(data);
  var numYLabels = getNumYCoords(data);

  // loop through all the data points.
  for (var i = 0; i < data.getNumberOfRows(); i++) {
    // Get the x and y values.
    var x = data.getFormattedValue(i, xCoordColumn);
    var y = data.getFormattedValue(i, yCoordColumn);
    var label = 
      // '(' + (i + 2) + ') ' +
      // data.getFormattedValue(Math.floor(i / numXLabels), yLabelColumn) + ' ' +
      // data.getFormattedValue((i % numXLabels), xLabelColumn) + ': ' +
      data.getFormattedValue(i, valueColumn) + ' watt-hrs';

    if (hasData(data, i, annotationColumn) && 
        data.getFormattedValue(i, annotationColumn).length > 0) {
      label += '<br>' + data.getFormattedValue(i, annotationColumn);
    }

    var area = document.createElement('area');
    area.setAttribute('id', '' + i);
    area.setAttribute('shape', 'circle');
    var xCoord = (xOffset + (columnWidth * x));
    var yCoord = (yOffset - (rowHeight * y));
    area.setAttribute('coords', '' + xCoord + ',' + yCoord +',' + mapRadius);
    area.setAttribute('nohref', 'nohref');
    area.setAttribute('onmouseover', 'showTooltip(\'' + label + '\',' + xCoord + ',' + yCoord + ');');
    area.setAttribute('onmouseout', 'hideTooltip();');
    map.appendChild(area);
  }
  return map;
}

function showTooltip(label, xCoord, yCoord) {
  var tooltip = document.getElementById('tooltip');
  tooltip.style.left = (200+ xCoord + 20) + 'px';
  tooltip.style.top = (320+yCoord + 20) + 'px';
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
  document.getElementById('tooltip').style.visibility='hidden';
}

/**
 * Outputs the message to the Firebug console window (if console is defined).
 */
function debug(msg) {
  if (typeof(console) != 'undefined') {
    console.info(msg);
  }
}


