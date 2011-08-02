// Setup the header cycle.

jQuery(document).ready(function($) {
  jQuery("#user-cycle").cycle();
  jQuery("#floor-cycle").cycle();
  
  //Set up the help dialog.
  jQuery("#widget-help-dialog").dialog({
    autoOpen: false,
    width: 550,
    modal: true
  });
  
  $("#link-container").hover(function() {
    if ($("#header-canopy-link").hasClass("hidden")) {
      $("#header-canopy-link").removeClass("hidden").css({display: "none"}).fadeIn("slow");
      setCookie("display-canopy", true, 0);
    }
  });
  
  if(getCookie("display-canopy")) {
    // deleteCookie("display-canopy");
    $("#header-canopy-link").removeClass("hidden");
  }
});

// Function to handle AJAX post requests.
jQuery.ajaxSetup({ 
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
  jQuery.get("/log/" + type + "/" + object + "/" + action + "/");
}

var toggleHelp = function(category, slug) {
  jQuery("#widget-help-dialog").dialog("open");
  jQuery("#ui-dialog-title-widget-help-dialog").html("");
  jQuery("#widget-help-dialog").html("");
  jQuery.ajax({
    url: "/help/" + category + "/" + slug + "/", 
    success: function(data) {
      jQuery("#ui-dialog-title-widget-help-dialog").html(data.title);
      jQuery("#widget-help-dialog").html(data.contents);
    },
    error: function(XMLHttpRequest, textStatus, errorThrown) {
      jQuery("#ui-dialog-title-widget-help-dialog").html("(empty)");
      jQuery("#widget-help-dialog").html("There is no help content for this widget. " +
          "If you are an admin, please create a new topic in category '" + category + 
          "' and slug '" + slug + "'.");
    }
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