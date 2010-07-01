Namespace("org.wattdepot.gdata.kukuicup");

// Creates the status summary pane for the Kukui Cup application. 
org.wattdepot.gdata.kukuicup.EnergyStatusSummary = function() {

  // Width of this visualization.
  var width = 150; 
  var green = '#459E00';
  var yellow = '#FFCC00';
  var red = '#FF0000';

  function draw(datatable, element) {
    addTopLevelStyle(element);
    addTitleDiv(element, datatable);
    addHeaderDiv(element, 'Overall Status');
    addSmileyDiv(element, datatable);
    addHeaderDiv(element, 'Current Power');
    addCurrentPowerDiv(element, datatable);
    addHeaderDiv(element, 'Recent Trends');
    addSparkDiv(element, datatable, [2], 0, 5, red);
    addSparkDiv(element, datatable, [3], 0, 23, yellow);
    addSparkDiv(element, datatable, [4], 0, 6, green);
    addHeaderDiv(element, 'Use vs. Baseline');
    addBaselineDiv(element, datatable);
    addLastUpdateDiv(element, datatable);
  }

  // Adds 'global' CSS styling to the top-level div passed into this instance.
  function addTopLevelStyle(element) {
    element.style.fontFamily = 'Verdana,sansSerif';
  }

  // Adds standard div CSS styling (which cannot be applied to the spark lines).
  function addDivStyle(element) {
    element.style.width = width + 'px';
    element.style.textAlign = 'center';
  }

  // Adds special header CSS styling.
  function addHeaderStyle(element) {
    element.style.margin = '6px 0px 3px 0px';
    element.style.width = width + 'px';
    element.style.textAlign = 'center';
    element.style.backgroundColor = '#cccccc';
    element.style.fontVariant = 'small-caps';
    element.style.fontWeight = 'normal';
    element.style.fontSize = '0.8em';
  }

  // The baseline chart has a 30px white space at top.  use this to reduce the gap between it and the section above it.
  function addBaselineFixStyle (element) {
    //element.style.position = 'relative';
    element.style.marginTop = '-20px';
    //element.style.zIndex = '0';
  }

  function addInfoStyle(element) {
    element.style.fontSize = '0.7em';
    element.style.fontWeight = 'normal';
    element.style.width = width + 'px';
    element.style.textAlign = 'center';
  }

  function addTitleDiv(element, datatable) {
    var div = document.createElement('div');
    addDivStyle(div);
    // Special CSS just for the title.
    div.style.fontSize = '1.0em';
    div.style.fontWeight = 'bold';
    div.innerHTML = 'Ilima 3-4'; // should use datatable.
    element.appendChild(div);
  }

  function addHeaderDiv(element, headerString) {
    var div = document.createElement('div');
    addHeaderStyle(div);
    div.innerHTML = headerString;
    div.style.zIndex = '1';
    div.style.position = 'relative';
    element.appendChild(div);
  }

  function addSmileyDiv(element, datatable) {
    var div = document.createElement('div');
    addDivStyle(div);
    element.appendChild(div);
    var img = document.createElement('img');
    img.setAttribute('src', "http://wattdepot-gdata.googlecode.com/svn/trunk/javascript/dev/smiley.happy.green.orig.png");  // should be computed from datatable.
    div.appendChild(img);
  }

  function addCurrentPowerDiv(element, datatable) {
    var div = document.createElement('div');
    addDivStyle(div);
    // Add custom styling.
    div.style.color = yellow;
    div.style.fontSize = '1.5em';
    div.style.fontWeight = 'bold';
    div.innerHTML = '1587 kW';
    element.appendChild(div);
    var info = document.createElement('div');
    addInfoStyle(info);
    info.innerHTML = '(5% over baseline)';
    element.appendChild(info);
  }

  function addSparkDiv(element, datatable, columns, startRow, endRow, colorName) {
    var div = document.createElement('div');
    div.style.zIndex = '1';
    element.appendChild(div);
    var view = new google.visualization.DataView(datatable);
    view.setColumns(columns);
    view.setRows(startRow, endRow);
    var chart = new google.visualization.ImageSparkLine(div);
    chart.draw(view, {color: colorName, width: width, height: 10, showAxisLines: false,  showValueLabels: false, labelPosition: 'left'});
  }

  function addBaselineDiv(element, datatable) {
    var div = document.createElement('div');
    addBaselineFixStyle(div);
    element.appendChild(div);
    var cumColumnIndex = datatable.addColumn('number','Cumulative Energy');
    var cumTotal = 0;
    var i;
    for (i =0; i < 7; i++) {
      cumTotal += datatable.getValue(i, 4);
      datatable.setValue(i, cumColumnIndex, cumTotal);
    }
    var view = new google.visualization.DataView(datatable);
    view.setColumns([7,8,9,cumColumnIndex]);
    view.setRows(0,6);
    var chart = new google.visualization.AreaChart(div);
    chart.draw(view, {
      width: width, 
      height: width, 
      colors: [red, green, 'white'],
      legend: 'none',
      pointSize: 0,
    });
  }

  function addLastUpdateDiv(element, datatable) {
    var div = document.createElement('div');
    addInfoStyle(div);
    div.innerHTML = 'Updated: 7/1/10 9:43am';
    element.appendChild(div);
  }

  return {
    // Public interface to this function. 
    draw : draw
  };
}


