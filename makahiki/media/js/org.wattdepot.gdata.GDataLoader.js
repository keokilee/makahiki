Namespace("org.wattdepot.gdata");

// Summary: Loads all visualization packages of interest, retrieves datatables for all passed URLs, and passes them to the callback.

// API:
// GDataLoader is a variable argument function that enables clients to retrieve 0 - 3 datatables. These are the valid invocations:
// GDataLoader(callback) -> loads Google visualization API, then calls callback, but does not retrieve any datatables.
// GDataLoader(callback, url1, refresh1) -> callback(datatable1)
// GDataLoader(callback, url1, refresh1, url2, refresh2) -> callback(datatable1, datatable2)
// GDataLoader(callback, url1, refresh1, url2, refresh2, url2, refresh3) -> callback(datatable1, datatable2, datatable3)

// Declared parameters document the complete invocation approach, though not all parameters are required.
org.wattdepot.gdata.GDataLoader = function(callback, url1, refresh1, url2, refresh2, url3, refresh3) {

  // the datatables that will store the results.
  var datatable1, datatable2, datatable3;

  // find out how many args we have, which determines how many callbacks we use.
  var numArgs = arguments.length;
  
  // Load the Visualization API and all packages of interest to the system.
  // Actually, loading *everything* might be expensive, so let's cut down on that for now.
  // Might need to pass a parameter to GDataLoader to say what packages to load for each visualization for efficiency purposes. 
  //google.load("visualization", "1", {packages:['gauge','corechart','imagesparkline','annotatedtimeline']});

  google.load("visualization", "1", {});
      
  // Set a callback to run when the Google Visualization API is loaded.
  google.setOnLoadCallback(query1);

  /**
   * Once visualization API is loaded, retrieve first datatable.
   */
  function query1() {
    if (numArgs === 1) {
      callback();
    }
    else {
      // Get all of the dorm data from the spreadsheet.
      var query1 = new google.visualization.Query(url1);
      // Set the refresh interval. 
      query1.setRefreshInterval(refresh1);
      // Set a callback to run when the dorm data has been retrieved.
      query1.send(getDataTable1);
    }
  }

  // Runs when the spreadsheet data is available. 
  function getDataTable1(response) {
    // Process errors, if any.
    if (response.isError()) {
      // Comment out this alert, since it appears when waking up a laptop.
      //alert('Error in query (url1): ' + response.getMessage() + ' ' + response.getDetailedMessage());
      return;
    }
    // Get the DataTable representing the first spreadsheetURL.
    datatable1 = response.getDataTable();
    // Invoke the passed callback with the DataTable.
    if (numArgs === 3) {
      callback(datatable1);
    }
    else {
      var query2 = new google.visualization.Query(url2);
      query2.setRefreshInterval(refresh2);
      query2.send(getDataTable2);
      
    }
  }

  // Runs when the second spreadsheet data is available. 
  function getDataTable2(response) {
    // Process errors, if any.
    if (response.isError()) {
      // Comment out this alert, since it appears when waking up a laptop.
      // alert('Error in query (url2): ' + response.getMessage() + ' ' + response.getDetailedMessage());
      return;
    }
    // Get the DataTable representing the second url.
    datatable2 = response.getDataTable();
    // Invoke the passed callback with the DataTable.
    if (numArgs === 5) {
      callback(datatable1, datatable2);
    }
    else {
      var query3 = new google.visualization.Query(url3);
      query3.setRefreshInterval(refresh3);
      query3.send(getDataTable3);
    }
  }

  // Runs when the third spreadsheet data is available. 
  function getDataTable3(response) {
    // Process errors, if any.
    if (response.isError()) {
      // Comment out this alert, since it appears when waking up a laptop.
      // alert('Error in query (url3): ' + response.getMessage() + ' ' + response.getDetailedMessage());
      return;
    }
    // Get the DataTable representing the third url.
    datatable3 = response.getDataTable();
    // Invoke the passed callback with all the datatables.
    callback(datatable1, datatable2, datatable3);
  }
}


