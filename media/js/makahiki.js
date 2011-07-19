// Setup the header cycle.
$(document).ready(function() {
  $("#user-cycle").cycle();
  $("#floor-cycle").cycle();
  
  //Set up the help dialog.
  $("#widget-help-dialog").dialog({
    autoOpen: false,
    modal: true
  });
});

// Function to handle AJAX post requests.
$.ajaxSetup({ 
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                 if (cookie.substring(0, name.length + 1) == (name + '=')) {
                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                     break;
                 }
             }
         }
         return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     } 
});

// Make sure to load jQuery before this.
var log_js_action = function(type, object, action) {
  // Send a request to the logging URL.
  $.get("/log/" + type + "/" + object + "/" + action + "/");
}

var toggleHelp = function(category, slug) {
  $("#widget-help-dialog").dialog("open");
  $.get("/help/" + category + "/" + slug + "/", function(data) {
    $("#ui-dialog-title-widget-help-dialog").html(data.title);
    $("#widget-help-dialog").html(data.contents);
  });
}

// Utility functions for get/set/delete cookies
function setCookie(name,value,days) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime()+(days*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
    }
    else var expires = "";
    document.cookie = name+"="+value+expires+"; path=/";
}

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

function deleteCookie(name) {
    setCookie(name,"",-1);
}