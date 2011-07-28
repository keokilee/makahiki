
Namespace("org.wattdepot.makahiki");

  /**loads the visualization for both annotated timelines and for table. */
  google.load('visualization','1',{'packages':['annotatedtimeline', 'table']}); 

 google.setOnLoadCallback(initialize); 
  
 var host_uri = 'http://server.wattdepot.org:8192/gviz/'; 
      
 var powerSource;      
 var table;
 var sourceNo;       
  
  /**
 * Contains the function which calls the queries based on input from the html.
 * 
 * @author Edward Meyer, Kendyll Doi, Bao Huy Ung
 */
 function initialize(){ 
   powerSource = [];
   table = [];
   sourceNo = 0;       
   
          /**Sets necessary variables to the input from the html page. */
          var periods = document.getElementsByName("period");
          for (i = 0; i<periods.length; i++)
            if (periods[i].checked) 
              dateRange = periods[i].value;

          var datatypes = document.getElementsByName("datatype");
          for (i = 0; i<datatypes.length; i++)
            if (datatypes[i].checked) 
              dataType = datatypes[i].value;
 
          
          var lounges = document.getElementsByName("lounge");
          for (i = 0; i<lounges.length; i++)
            if (lounges[i].checked) 
              powerSource.push(lounges[i].value);
          
          // Depending on the data range selected,
          // changed the sample-interval to WattDepot to compensate for daily or hourly values.
          // Only need to overwrite for last7 and last 14 days since defaults are already set for 24 hours.
          if (dateRange == "last21days") {
            interval = 60; // How many minutes in a day, for WattDepot query.
            goBack = 480; // 24 hrs * 20 days, go back 6 days from now to get a weeks worth of data.
          }
          if (dateRange == "last7days") {
            interval = 60; // How many minutes in a day, for WattDepot query.
            goBack = 144; // 24 hrs * 6 days, go back 6 days from now to get a weeks worth of data.
          }
          if (dateRange == "last24hours") {
            interval = 15; // How many minutes in a day, for WattDepot query.
            goBack = 24; // 24 hrs 
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
          begDate.setHours( begDate.getHours() - goBack );
          begDate.setMinutes(0);

          // Initialize beginning and ending variables to hold the timestamp 
          // in XMLGregorian format that WattDepot requires.
          // Use the appendZero function for hour and minutes to append extra 0 if the value is less than 10.
          // This is used to conform to XMLGregorian format.
          var begHour = appendZero( begDate.getHours() );
          var begMin = appendZero( begDate.getMinutes() );
          var endHour = appendZero( endDate.getHours() );
          var endMin = appendZero( endDate.getMinutes() );

          var endTimestamp = 'T' + endHour + ":" + endMin + ':00.000-10:00';
          var begTimestamp = 'T' + begHour + ":" + begMin + ':00.000-10:00';

          // Put together the year, month, and day into Gregorian timestamp
          var startTime = begDate.getFullYear() + '-' + appendZero( begDate.getMonth() + 1 ) + '-' 
                       + appendZero ( begDate.getDate() ) + begTimestamp;
          
          var endTime = endDate.getFullYear() + '-' + appendZero( endDate.getMonth() + 1 ) + '-' 
                       + appendZero ( endDate.getDate() ) + endTimestamp;
       
      /**sensor data and calculated data have different query a uri.  */
      var query = new Array();
      for (i=0; i<powerSource.length; i++){
        var url = host_uri + 'sources/' + powerSource[i] +  '/calculated?startTime=' + startTime + '&endTime=' + endTime + '&samplingInterval='+interval; 
         //var url = host_uri + 'sources/' + powerSource[i] + '/sensordata?startTime=' + startTime + '&endTime=' + endTime; 
        //debug(url) ;
        
        query[i] = new google.visualization.Query(url); 
        query[i].setQuery('select timePoint, ' + dataType);
      }
              
      /**begin processing query with first entry in array. passing the query response, the whole query, and the current index.*/
      query[0].send(function(response) { handleQueryResponse(response, query, 0)});  
 } 

function debug(msg) {
  if (typeof(console) != 'undefined') {
    console.info(msg);
  }
}

/**
 * Contains the function which takes the response from a query and modifies it with labels, then forwards it to be displayed.
 * Recursively calls itself to handle each query individually allowing each one to be labeled with a proper power source.
 * 
 * @author Edward Meyer, Kendyll Doi, Bao Huy Ung
 * @param response is the returned data table from a query.
 *        query is the array containing all the queries.
 *        number is the current source and position.
 */
  function handleQueryResponse(response, query, number) { 
    if (response.isError()) {
      alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
      /**Removes the "now working" notification from the webpage.*/
      document.getElementById('working').style.display="none";
      return;
    }
    
    var data = response.getDataTable(); 
    
    /**appends the columns in the datatable with the source which it came from.*/
    for(k = 1; k < data.getNumberOfColumns(); k++){
       data.setColumnLabel(k, powerSource[number] + " " + data.getColumnLabel(k));
    }
    
    /**increments source number for next query and power source.*/
    sourceNo++;
    /**pushes table on to arrway for processing*/
    table.push(data);
    /**If all queries are completed then process the data into one table.*/
    if(sourceNo == query.length){
        combineTable(table);
    }
    /**Recursively recalls the handleQueryResponse function to process next query.*/
    else {
        query[sourceNo].send(function(response) { handleQueryResponse(response, query, sourceNo)}); 
    }
  }
  
/**
 * Contains the function which takes an array of data tables and combines them together into one for visualization.
 * 
 * @author Edward Meyer, Kendyll Doi, Bao Huy Ung
 * @param array is the array of all data tables to be combined.
 */
  function combineTable(array){
    /**Combines tables only if there are multiple data tables in the array.*/
     if(array.length>1){
        var combined = array[0];
        for (i=1; i<array.length; i++){
          var complete = false;
          /**defines an array with the numbers for each column of a table which will be added.*/
          var dt1 = makeColArray(combined.getNumberOfColumns());
          var dt2 = makeColArray(array[i].getNumberOfColumns());
          /**combines the data tables together through google visualization.*/
          combined = google.visualization.data.join(combined,array[i], 'full',[[0,0]], dt1, dt2);
          if(i == (array.length-1)){
                complete = true;
          }
          /**If all the arrays are complete then continue to display function.*/
          if(complete){
              processData(combined);
          }
        }
     }
     /**If there is only one array go immediately to the display function.*/
     else {
         processData(array[0]);
     }
  }
  
/**
 * Contains the function which creates an array of incrementing integers up to the parameter specified.
 * Used to make arrays for the combined values of tables in a google visualization data table.
 * 
 * @author Edward Meyer, Kendyll Doi, Bao Huy Ung
 * @param number is the highest number which should be in an array and the size of the array.
 */
  function makeColArray(number){
//    alert(number);
     var cols = new Array();
     for(j = 1; j < number; j++){
        cols.push(j);
     }
//     alert(cols);
     return cols;
  }
  
 /**
  * Contains the function which takes the data table to be displayed and produces the googlevisualization onto the id on the webpage.
  * 
  * @author Edward Meyer, Kendyll Doi, Bao Huy Ung
  * @param data is the data table returned from a query.
  */
  function processData(data){
     document.getElementById('loading').style.display = 'none';
     
     var chart = new google.visualization.AnnotatedTimeLine(document.getElementById('chart_div')); 
     chart.draw(data, {displayAnnotations: false, wmode: "opaque", legendPosition: "newRow"}); 

     //var table = new google.visualization.Table(document.getElementById('chart_div')); 
     //table.draw(data, {showRowNumber: true});  
    
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


  function update() {
            // Clear the contents of the drop-down menus, and re-display the loading sign.
            document.getElementById("chart_div").innerHTML = "";
            document.getElementById("loading").style.display = '';
            initialize();
  }