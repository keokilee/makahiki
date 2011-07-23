
Namespace("org.wattdepot.makahiki");

  /**loads the visualization for both annotated timelines and for table. */
  google.load('visualization','1',{'packages':['annotatedtimeline', 'table']}); 

/**connects the Time dropdown menu to the google visualization system. */
// google.setOnLoadCallback(addTime); 
 /**connects the init function (which runs a query) to the google visualization. */
 google.setOnLoadCallback(init); 
  

     var host_uri = 'http://server.wattdepot.org:8192/gviz/'; 
      var begTimestamp = 'T00:00:00.000-10:00'; 
      var endTimestamp = 'T23:59:00.000-10:00'; 
      var begDate = ''; 
      var endDate = ''; 
      var powerSource = new Array();      
      var dataType = ''; 
      var isError = false; 
      var interval= 15;
      var table = new Array();
      var lastFlag = false;
      var sourceNo = 0;
      
 /**intializes the variables used in the visualization page. */
 var begTimestamp = 'T00:00:00.000-10:00'; 
 var endTimestamp = 'T23:59:00.000-10:00'; 
 var begDate = ''; 
 var endDate = ''; 
 var powerSource = new Array();      
 var dataType = ''; 
 var isError = false; 
 //presets the interval for a query to 15 minutes.
 var interval= 15;
 var table = new Array();
 var lastFlag = false;
 var sourceNo = 0;
       
 /**
 * Contains the function which cancels an processing query by stopping the browser.
 * 
 * @author Edward Meyer, Kendyll Doi, Bao Huy Ung
 */
 function cancelquery(){ 
     /**particularly checks for Internet Explorer since it uses a different command to stop the page from loading. */
     if(navigator.appName == "Microsoft Internet Explorer") {  
         window.document.execCommand('Stop'); 
     } 
     /**stops the page to other browsers specifications. */
     else { 
         window.stop(); 
     } 
     /**removes the now working notification */
     document.getElementById('working').style.display="none"; 
 }      
  
  /**
 * Contains the function which calls the queries based on input from the html.
 * 
 * @author Edward Meyer, Kendyll Doi, Bao Huy Ung
 */
 function init(){ 
     /**Sets necessary variables to the input from the html page. */
     interval = 15; 
     begDate = new Date("07/14/2011"); 
     endDate = new Date("07/21/2011"); 
    /** Clears the values from any previously entered queries which are stored in the variables.*/
     dataType = 'powerConsumed';
     table = [];
     sourceNo = 0;
     lastFlag = false;
     /**sensorFlag and calcFlag to differentiate between calculated data and sensor data.  */
     var sensorFlag = false; 
     var calcFlag = false; 
       
     powerSource = ["Lehua-A"];    
       
      /**time conversion code courtesy of Carbonomter http://code.google.com/p/ekolugical-carbonometer/ 
      modified to function by Kendyll Doi, Edward Meyer, and Bao Huy Ung */
       
      /**Resets the variables to retrieve information from webpage.*/
      var day = ''; 
      var month = ''; 
      var year = ''; 
      var startTime = ''; 
      var endTime = '';      
      /**Obtains values from dropdown menus in webpage.*/
      var begHour = "12"; 
      var begMin = "00"; 
      var endHour = "11"; 
      var endMin = "59"; 
      var begm = "AM"; 
      var endm = "PM"; 
  
      /**modify time picker numbers into military time. */
      if (begm == 'PM' && begHour < 12){ 
           begHour = parseInt(begHour)+12; 
      } 
      else if (begm == 'AM' && begHour == '12'){ 
           begHour = '00'; 
      } 
       
      if (endm == 'PM' && endHour < 12){ 
           endHour = parseInt(endHour)+12; 
      } 
      else if (endm == 'PM' && endHour == '12'){ 
           endHour = '00'; 
      } 
      
      /**Converts the time stamp into gregorian timestamp format.*/
      var begTimestamp = 'T' + begHour + ":" + begMin + ':00.000-10:00'; 
      var endTimestamp = 'T' + endHour + ":" + endMin + ':00.000-10:00'; 
  
      /**Concerts dates and month to conform with gregorian timestamp format.*/
      if (begDate.getDate() < 10) { 
            day = '0' + begDate.getDate();
      } 
      else { 
            day = begDate.getDate(); 
      } 
      if (begDate.getMonth() < 10) { 
            month = '0' + (begDate.getMonth() +1); 
      } 
      else { 
            month = (begDate.getMonth() + 1); 
      } 
      /**Assigns years from the selected year on the webpage.*/
      year = begDate.getFullYear(); 
      /**Puts together the year, month, and day into Gregorian timestamp form for the beginning time.*/ 
      startTime = year + '-' + month + '-' + day + begTimestamp; 
    
      /**Converts dates and month to conform with gregorian timestamp format.*/
      if (endDate.getDate() < 10) { 
           day = '0' + endDate.getDate(); 
      } 
      else { 
           day = endDate.getDate(); 
      } 
      if (endDate.getMonth() < 10) { 
            month = '0' + (endDate.getMonth() +1); 
      } 
      else { 
            month = (endDate.getMonth() + 1); 
      } 
      /**Assigns years from the selected year on the webpage.*/
      year = endDate.getFullYear(); 
      /**Converts dates and month to conform with gregorian timestamp format.*/
      endTime = year + '-' + month + '-' + day + endTimestamp;      
            
      calcFlag = true; 
      
      /**sensor data and calculated data have different query a uri.  */
      var query = new Array();
      for (i=0; i<powerSource.length; i++){
        var url = host_uri + 'sources/' + powerSource[i] +  '/calculated?startTime=' + startTime + '&endTime=' + endTime + '&samplingInterval='+interval; 
         //var url = host_uri + 'sources/' + powerSource[i] + '/sensordata?startTime=' + startTime + '&endTime=' + endTime; 
        //debug(url) ;
        
        query[i] = new google.visualization.Query(url); 
        query[i].setQuery('select timePoint, ' + dataType);
      }
       
      /**get a total difference in time (in minutes) between the beginning and end dates. */
      var dateDiff = (endDate.getDate() - begDate.getDate())*60*24; 
      var monthDiff = (endDate.getMonth() - begDate.getMonth())*60*24*30; 
      var yearDiff = (endDate.getFullYear() - begDate.getFullYear())*60*24*365; 
      var hourDiff = (endHour - begHour)*60; 
      var minDiff = endMin - begMin; 
      var totalDiff = dateDiff + monthDiff + yearDiff + hourDiff + minDiff; 
       
       
      /**displays "now working" dialogue with cancel button.*/
      document.getElementById('working').style.display="block"; 
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
     
     
     var chart = new google.visualization.AnnotatedTimeLine(document.getElementById('chart_div')); 
     chart.draw(data, {displayAnnotations: false, wmode: "opaque", legendPosition: "newRow"}); 

     //var table = new google.visualization.Table(document.getElementById('chart_div')); 
     //table.draw(data, {showRowNumber: true});  

    /**Removes the "now working" notification from the webpage.*/
    document.getElementById('working').style.display="none"; 
    
 } 

