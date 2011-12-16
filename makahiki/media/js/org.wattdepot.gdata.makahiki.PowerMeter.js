Namespace("org.wattdepot.gdata.makahiki");

// http://code.google.com/apis/visualization/documentation/gallery/genericimagechart.html
google.load("visualization", "1", {packages:['corechart', 'imagechart']});

// Creates a table showing current power data.
org.wattdepot.gdata.makahiki.PowerMeter = function() {
 

  // Generates a datatable for this specific source from the multi-source datatable.
  // The datatable is used to generate a table containing just two entries: the timestamp and the power.
  // Column 0 contains the timestamp.
  // Column 1 contains the power value associated with that timestamp.
  function makeDataTable(rollingSecondsDatatable, source) {
    // Create the data table of power values to return.
    var powerTable = new google.visualization.DataTable();
    var numPowerTableRows = 1;
    powerTable.addColumn('date'); // the time of day.
    powerTable.addColumn('number'); // the power in Wh.
    powerTable.addColumn('number'); // the baseline power in Wh.
    powerTable.addRows(numPowerTableRows);
    // Determine the row in the rollingDays table that contains this source's data.
    var rollingPowerSourceRow = findRow(rollingSecondsDatatable, source);
    var timestampVal = rollingSecondsDatatable.getValue(rollingPowerSourceRow, 1);
    var powerVal = rollingSecondsDatatable.getValue(rollingPowerSourceRow, 2);
    var baselineVal = rollingSecondsDatatable.getValue(rollingPowerSourceRow, 3);
    powerTable.setCell(0, 0, timestampVal);
    powerTable.setCell(0, 1, powerVal);
    powerTable.setCell(0, 2, baselineVal);
    var dateFormatter = new google.visualization.DateFormat({pattern: 'MM/dd/yy h:mm:ss a'});
    dateFormatter.format(powerTable, 0);
    return powerTable;
  }
  
  // Returns the row in which source's data is located, or -1 if not found.
  function findRow(datatable, source) {
    for (var i = 0; i < datatable.getNumberOfRows(); i++) {
      if (datatable.getValue(i, 0) == source) {
        return i;
      }
    }
    return -1;
  }

  // Draws the three components (title, table, caption) of the energy visualization.
  function draw(id, source, spreadsheetDatatable, options) {
    // Define look and feel parameters using options object to override defaults. 
    var width = options.width || 300;
    var backgroundColor = options.backgroundColor || "F5F3E5";
    var globalStyle = options.globalStyle || {};
    var titleStyle = options.titleStyle || {};
    var captionStyle = options.captionStyle || {};
    var powerRange = options.powerRange || 6000;
    var title = options.title || source;
    var height = 200;
    var greenColor = '459E00';
    var redColor = 'FF0000';
    // Create a datatable with this source's data. 
    var datatable = makeDataTable(spreadsheetDatatable, source);
    // Get the top-level div where this visualization should go.
    element = document.getElementById(id);
    // Now add the elements.
    addGlobalStyle(element, backgroundColor, width, globalStyle);
    addTitleDiv(element, id, title, titleStyle);
    addMeterDiv(element, id, datatable, backgroundColor, width, powerRange);
    addCaptionDiv(element, id, captionStyle, datatable);
  }

  // Adds 'global' CSS styling to the top-level div passed into this instance.
  function addGlobalStyle(element, backgroundColor, width, globalStyle) {
    element.style.backgroundColor = backgroundColor;
    element.style.margin = '0 auto';
    element.style.width = width + 'px';
    addStyleProperties(element, globalStyle);
  }

  function addTitleDiv(element, id, title, titleStyle, width) {
    var divId = id + '__Title';
    var div = getElementByIdOrCreate(divId, 'div');
    element.appendChild(div);
    div.style.textAlign = 'center';
    addStyleProperties(div, titleStyle);
    div.style.width = width + 'px';
    div.innerHTML = title;
  }

  // Updates the divElement style attribute with all properties in styleObject.
  function addStyleProperties(divElement, styleObject) {
    for (key in styleObject) {
      if (styleObject.hasOwnProperty(key)) {
        divElement.style[key] = styleObject[key]; 
      }
    }
  }

  function addMeterDiv(element, id, datatable, backgroundColor, width, powerRange) {
    var divId = id + '__PowerMeter';
    var div = getElementByIdOrCreate(divId, 'div');
    element.appendChild(div);
    div.style.backgroundColor = backgroundColor;
    var powerVal = datatable.getValue(0,1);
    var baselineVal = datatable.getValue(0,2);
    var minVal = baselineVal - (powerRange / 2);
    var maxVal = baselineVal + (powerRange / 2);
    // Ensure that min value is less than power value by at least 100 W.
    if (powerVal < minVal) {
      minVal = powerVal - 100;
    }
    // Disallow min values less than zero.
    if (minVal < 0) {
      minVal = 0;
    };
    // Make sure that maxVal is greater than powerVal.
    if (powerVal > maxVal) {
      maxVal = powerVal + 300;
    }
 
    var view = new google.visualization.DataView(datatable);
    view.setColumns([1]);
    var chart = new google.visualization.ImageChart(div);
    chart.draw(view, {cht: 'gom',
                      chs:  width + 'x108',
                      chf: 'bg,s,' + backgroundColor,
                      chxl: '0:|' + powerVal + ' W|1:|' + minVal + ' W|' + maxVal + ' W',
                      chxt: 'x,y',
                      chco: '3CB371,FFFF00,FF0000',
                      chds: minVal + ',' + maxVal,
                      chls: '4|12'
             });
  }

  function addCaptionDiv(element, id, captionStyle, datatable) {
    var divId = id + '__Caption';
    var div = getElementByIdOrCreate(divId, 'div');
    div.style.textAlign = 'center';
    element.appendChild(div);
    addStyleProperties(div, captionStyle);
    var lastUpdate = datatable.getFormattedValue(0,0);
    div.innerHTML = 'As of: ' + lastUpdate;
  }

  // Returns the pre-existing element with id 'id', or else creates and returns
  // a new element with type elementType and that id.
  function getElementByIdOrCreate(id, elementType) {
    var element = document.getElementById(id);
    if (element) {
      return element;
    }
    else {
      element = document.createElement(elementType);
      element.setAttribute("id", id);
      return element;
    }
  }

  return {
    // Public interface to this function.
    draw : draw
  };
};

