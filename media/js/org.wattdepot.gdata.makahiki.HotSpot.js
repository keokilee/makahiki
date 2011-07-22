Namespace("org.wattdepot.gdata.makahiki");
  
// Creates a Hot Spot chart with a standard appearance for the Kukui Cup application. 
org.wattdepot.gdata.makahiki.HotSpot = function() {

  // The standard size for Hot Spot Charts is 500 x 200.
  var chartWidth = 500;
  var chartHeight = 200;
  var spotColor = "459E00";
  var highlightColor = "FF0000";
  var maxSpotSize = 20;

  var xAxisLabelColumn = 0;
  var yAxisLabelColumn = 1;
  var xAxisCoordsColumn = 2;
  var yAxisCoordsColumn = 3;
  var dataColumn = 4;
  var highlightColumn = 5;
  var annotationColumn = 6;

  var backgroundColor = "#fff";
  var textColor = "#0000FF";

  // These are essentially 'magic' values that must be custom set for each different style of HotSpot map.
  // The following default values work for the Example HotSpot data. 
  // (xOffSet, yOffset) must be the position of the bottom left dot.
  // Use Firebug > HTML > div id="img" > map  and then move mouse over first area tag to see the location.
  var mapXOffset = 75;    
  var mapYOffset = 158;   
  var mapColumnWidth = 17.3;
  var mapRowHeight = 21.5;
  var mapRadius = 8;

  // Draw the chart.
  function draw(datatable, id) {
    var element = document.getElementById(id);
    var img = document.createElement('img');
    img.setAttribute('src', getChartUrl(datatable));
    img.setAttribute('usemap', '#tooltipMap', 0);
    img.setAttribute('usemap', '#tooltipMap', 0);
    // Remove the blue line around the image.
    img.style.border = '0';
    element.appendChild(img);
    element.appendChild(createMap(datatable));
    //debug('html is: ' + document.getElementById(id).innerHTML);
  }

  // Return the URL for generating the chart.
  function getChartUrl(data) {
    var url = 'http://chart.apis.google.com/chart?cht=s' +  
      getChd(data) + getChxr(data) + getChxl(data) + getChs() + 
      getChm(data) + getChdlp() + getChds(data) + getChxt() + getChf() + getChxs();
    return url;
  }

  // Return the chart background color
  function getChf () {
    return '&chf=bg,s,' + backgroundColor;
  }


  // Return the axes to be displayed. 
  function getChxt() {
    return '&chxt=x,y';
  }

  // Return the formatting for the axis labels
  function getChxs() {
    return '&chxs=0,' + textColor + '|1,' + textColor;
  }


  // Return the axis range parameter. This simply specifies the number of axis values, which corresponds to the axis labels.
  function getChxr(data) {
    return '&chxr=0,-1,' + getNumXCoords(data) + '|1,-1,' + getNumYCoords(data);
  }

  // Return the specification for the X axis and Y axis labels. 
  // Format: 0:||xLabel1|xLabel2|..||1:|yLabel1|yLabel2|...|
  function getChxl(data) {
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

  // Return the size of the chart (width x height) in pixels.
  function getChs() {
    return '&chs=' + chartWidth + 'x' + chartHeight;
  }

  // Return the shape marker parameter value.  
  // This parameter consists of a series of marker specifications separated by pipe characters.
  // The first marker specification specifies default marker info. 
  // Default marker info is: o (circle), 459E00 (color), 1 (series index), -1 (all points), 20 (max spot size).
  // After default marker info comes specifications for each of the highlighted spots.  
  // A highlight specification indicates: (o) shape, highlight color, 1 (series index), positional index, and absolute spots size.
  function getChm(data) {
    var defaultSpec = 'o,' + spotColor + ',1,-1,' + maxSpotSize;
    return '&chm=' + defaultSpec + getHighlightMarkers(data, maxSpotSize);
  }

  // Return the csdlp param, which specifies the legend position. Not sure if this is necessary. 
  function getChdlp() {
    return '&chdlp=r';
  }

  // Return the chds param, which specifies scaling. 
  // First two args indicate range of X Axis values. Start with -1 so no dots are at origin.
  // Second two args indicate range of Y Axis values. Start with -1 so no dots are at origin.
  // Final two args are the min and max values, to be used to auto-scale the values. 
  function getChds(data) {
    return '&chds=-1,' +  getNumXCoords(data) + ',-1,' + getNumYCoords(data) + ',0,' + getMaxColumnValue(data, dataColumn);
  }

  // Return the chd parameter to the Chart URL. 
  // This is a string with the format t:{x coords}|{y coords}|{xy vals}
  // For example, given the (x,y,val) tuples (0,0,1), (0,1,2), (1,0,3), (1,1,4), they get encoded as:
  // t:0,1,0,1|0,0,1,1|1,2,3,4
  // One could imagine more intuitive ways to do it.
  function getChd(data) {
    var numXCoords = getNumXCoords(data);
    var numYCoords = getNumYCoords(data);
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

  // Return the number of distinct X coordinate values.
  function getNumXCoords(data) {
    return data.getDistinctValues(xAxisCoordsColumn).length;
  }

  // Return the number of distinct Y coordinate values.
  function getNumYCoords(data) {
    return data.getDistinctValues(yAxisCoordsColumn).length;
  }

  // Return the maximum value found in the given column.
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

  // Return the marker strings for the hot spots that should be highlighted. 
  function getHighlightMarkers(data, maxSpotSize) {
    var returnString = '';
    var maxValue = getMaxColumnValue(data, dataColumn);

    for (var i = 0; i < data.getNumberOfRows(); i++) {
      if (hasData(data, i, highlightColumn)) {
        var value = data.getFormattedValue(i, dataColumn);
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

  // Return true if (row, column) in data has a value.
  function hasData(data, row, column) {
    return (data.getValue(row, column) != null);
  }

  // Create and return the image map element. 
  function createMap(data) {
    var map = document.createElement('map');
    map.setAttribute('id', 'tooltipMap');
    map.setAttribute('name', 'tooltipMap');

    var numXLabels = getNumXCoords(data);
    var numYLabels = getNumYCoords(data);

    // loop through all the data points.
    for (var i = 0; i < data.getNumberOfRows(); i++) {
      // Get the x and y values.
      var x = data.getFormattedValue(i, xAxisCoordsColumn);
      var y = data.getFormattedValue(i, yAxisCoordsColumn);
      var label = 
        // '(' + (i + 2) + ') ' +
        // data.getFormattedValue(Math.floor(i / numXLabels), yAxisLabelColumn) + ' ' +
        // data.getFormattedValue((i % numXLabels), xAxisLabelColumn) + ': ' +
        data.getFormattedValue(i, dataColumn) + ' watt-hrs';

      if (hasData(data, i, annotationColumn) && 
          data.getFormattedValue(i, annotationColumn).length > 0) {
        label += '<br>' + data.getFormattedValue(i, annotationColumn);
      }

      var area = document.createElement('area');
      area.setAttribute('id', '' + i);
      area.setAttribute('shape', 'circle');
      var xCoord = (mapXOffset + (mapColumnWidth * x));
      var yCoord = (mapYOffset - (mapRowHeight * y));
      area.setAttribute('coords', '' + xCoord + ',' + yCoord +',' + mapRadius);
      area.setAttribute('nohref', 'nohref');
      area.setAttribute('onmouseover', 'showHotSpotTooltip(\'' + label + '\',' + xCoord + ',' + yCoord + ');');
      area.setAttribute('onmouseout', 'hideHotSpotTooltip();');
      map.appendChild(area);
    }
    return map;
  }

  // The public function (for the page) that shows a HotSpot tooltip.
  function showHotSpotTooltip(label, xCoord, yCoord) {
    var tooltip = document.getElementById('tooltip');
    tooltip.style.left = (xCoord + 20) + 'px';
    tooltip.style.top = (yCoord + 20) + 'px';
    tooltip.style.width = 'auto'; 
    tooltip.style.height = 'auto'; 
    tooltip.style.position = 'absolute';
    tooltip.style.background = '#fff';
    tooltip.innerHTML = label;
    tooltip.style.borderStyle = 'solid';
    tooltip.style.borderWidth = 'thin';
    tooltip.style.color = '#459E00';
    tooltip.style.visibility = 'visible';
  }

  // The public function (for the page) that hides the hotspot tooltip.
  function hideHotSpotTooltip() {
    document.getElementById('tooltip').style.visibility='hidden';
  }

  function setMapXOffset(newOffset) {
    mapXOffset = newOffset;
  }

  function setMapYOffset(newOffset) {
    mapYOffset = newOffset;
  }

  function setMapColumnWidth(newWidth) {
    mapColumnWidth = newWidth;
  }

  function setMapRowHeight(newHeight) {
    mapRowHeight = newHeight;
  }

/**
 * Outputs the message to the Firebug console window (if console is defined).
 */
function debug(msg) {
  if (typeof(console) != 'undefined') {
    console.info(msg);
  }
}

  return {
    // Public interface to this function. 
    draw : draw,
    showHotSpotTooltip : showHotSpotTooltip,
    hideHotSpotTooltip : hideHotSpotTooltip,
    setMapXOffset : setMapXOffset,
    setMapYOffset : setMapYOffset,
    setMapColumnWidth : setMapColumnWidth,
    setMapRowHeight : setMapRowHeight
  };
}
