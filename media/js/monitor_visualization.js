// Declare a unique namespace.
var monitor = {};

// Class constructor. Parameter container is a DOM elementon the client 
// that will contain the visualization.
monitor.visualization = function(container) {
  this.containerElement = container;
}

// Main drawing logic.
// Parameters:
//   data is data to display, type google.visualization.DataTable.
//   options is a name/value map of options. Our example takes one option.


monitor.visualization.prototype.draw = function(data, unit) { 
  var html = [];
  var date = this.escapeHtml(data.getFormattedValue(0,0));
  var value = this.escapeHtml(data.getFormattedValue(0,1));
  value = parseFloat(value);
  value = Math.floor(value + 0.5);
  html.push('<font style=\"font-size:1.2em; font-weight:bold; font-family:arial,sans-serif\">');
  html.push(value);
  html.push('</font>');
  html.push(' ');
  html.push(unit);
  html.push('<br /><font style=\"font-size:0.8em; font-style: italic\">Data Updated at: '); 
  html.push(date);
  html.push('</font>');

  this.containerElement.innerHTML = html.join('');
}


// Utility function to escape HTML special characters
monitor.visualization.prototype.escapeHtml = function(text) {
  if (text == null)
    return '';
  return text.replace(/&/g, '&').replace(/</g, '<')
      .replace(/>/g, '>').replace(/"/g, '"');
}

