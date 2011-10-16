Namespace("org.wattdepot.gdata.makahiki");

// http://code.google.com/apis/visualization/documentation/gallery/genericimagechart.html

// Creates an Energy Data visualization for the last 24 hours.
org.wattdepot.gdata.makahiki.EnergyRank = function() {
  
  // Reads the data table and returns a new one sorted by energy usage over the interval.
  // startDays is the start of the interval and endDays is the end of the interval.
  // For example, to look at the energy usage between 5 days ago and today, 
  // startDays should be 5 and endDays should be 0.
  // Any negative numbers in endDays will be converted to 0.
  function processDataTable(energyDataTable, startDays, endDays) {
    if (startDays < endDays) {
      console.error("Start must be greater than or equal to end.");
      return null;
    }
    
    // Construct the data table to be returned.  It should have 2 columns, source and energy usage.
    var returnTable = new google.visualization.DataTable({
      cols: [
        {id: "source", label: "Source", type: "string"},
        {id: "usage", label: "Energy Usage", type: "number"}
      ]
    });
    
    // Operate on a clone of the data table.
    var dataTable = energyDataTable.clone();
    
    // Remove dorm rows.
    // console.log("Removing source row " + dataTable.getValue(19, 0));
    dataTable.removeRow(19);
    // console.log("Removing source row " + dataTable.getValue(13, 0));
    dataTable.removeRow(13);
    // console.log("Removing source row " + dataTable.getValue(7, 0));
    dataTable.removeRow(7);
    // console.log("Removing source row " + dataTable.getValue(1, 0));
    dataTable.removeRow(1);
    // console.log("Removing source row " + dataTable.getValue(0, 0));
    dataTable.removeRow(0);
    
    // Note that first two columns are source and timestamp.
    var start = startDays + 2; 
    var end = endDays + 2;
    
    // If the start or end are less than 2, set them to 2.
    // We also check if either exceed 32 since there are 30 days of data.
    if (start < 2) {
      start = 2;
    }
    else if (start > 32) {
      start = 32;
    }
    if (end < 2) {
      end = 2;
    }
    else if (end > 32) {
      end = 32;
    }
    // console.log('start: ' + start + ', end: ' + end);
    // Iterate over the rows and insert them into the returned table.
    // Note that first row is source information.
    // console.log("Table now has " + dataTable.getNumberOfRows() + " rows");
    for (i = 0; i < dataTable.getNumberOfRows(); i++) {
      var source = dataTable.getValue(i, 0);
      // console.log("Have source " + source);
      var usage = 0;
      for (j = end; j <= start; j++) {
        usage = usage + dataTable.getValue(i, j);
      }
      
      // Bogus value to make sure lounges without metered energy is huge.
      // if (usage == 0) {
      //         usage = 10000000;
      //       }
      returnTable.addRow([source, usage]);
    }
    
    // Now sort and return.
    returnTable.sort({column: 1});
    return returnTable;
  }
  
  // Returns the leader of the competition and their current energy use.
  function calculateLeader(usageTable) {
    // This is simply the top row.
    return {
      source: usageTable.getValue(0, 0),
      usage: usageTable.getValue(0, 1)
    }
  }
  
  // Calculates the rank and current energy of the source.
  function calculateRankInfo(usageTable, source) {
    if (source) {
        // Get the index of the source.
        var rows = usageTable.getFilteredRows([{column: 0, value: source}]);
        if (rows.length == 0) {
          console.error("Could not find source " + source);
          return null;
        }

        var index = rows[0];
        return {
          rank: index + 1,
          usage: usageTable.getValue(index, 1),
        }
    }
  }

  // Insert the rank and energy into the specified elements.
  function draw(rankId, energyId, sourceInfo) {
    if (sourceInfo) {
        // Get the rank element.
        var element = document.getElementById(rankId);
        element.innerHTML = "#" + sourceInfo.rank;

        // Get the energy element.
        element = document.getElementById(energyId);
        element.innerHTML = "" + Math.floor(sourceInfo.usage / 1000);
    }
  }
  
  // Insert the leader into the specified element.
  function insertLeader(elementId, leaderInfo) {
    var element = document.getElementById(elementId);
    if (element !== null) {
      element.innerHTML = leaderInfo.source;
    }
  }
  
  // Creates a table containing the complete standings.
  function drawCompleteStandings(tableId, sourceName, usageTable, showNoData) {
    // Create the header of the table.
    var htmlString = "<tr><th>Rank</th><th style='text-align: left'>Lounge</th>";
    htmlString += "<th style='text-align: right; padding-right: 20px'>kWh used</th></tr>";
    
    var value = 0
    // Iterate over the rows of the table and create the html.
    for (i = 0; i < usageTable.getNumberOfRows(); i++) {
      if (!showNoData || usageTable.getValue(i, 1) !== 10000000) {
        if (sourceName && (sourceName == usageTable.getValue(i, 0))) {
          htmlString += "<tr style='font-weight: bold'>";
        }
        else {
          htmlString += "<tr style='margin: 0 5px'>";
        }
        htmlString += "<td class='energy-rank-rank'>" + (i + 1) + "</td>";
        htmlString += "<td class='energy-rank-lounge' style='text-align: left'>" + usageTable.getValue(i, 0) + "</td>"
        htmlString += "<td class='energy-rank-value' style='text-align: right; padding-right: 20px'>" + Math.floor(usageTable.getValue(i, 1) / 1000) + "</td></tr>";
      }
    }
    
    // Insert the HTML string.
    var element = document.getElementById(tableId);
    element.innerHTML = htmlString;
  }

  return {
    // Public interface to this function.
    draw : draw,
    insertLeader : insertLeader,
    calculateRankInfo : calculateRankInfo,
    calculateLeader: calculateLeader,
    processDataTable: processDataTable,
    drawCompleteStandings: drawCompleteStandings
  };
}
