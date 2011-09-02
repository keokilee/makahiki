/*
 * JavaScript Pretty Date
 * Copyright (c) 2008 John Resig (jquery.com)
 * Licensed under the MIT license.
 * Found at http://ejohn.org/blog/javascript-pretty-date/
 */

// Takes an ISO time and returns a string representing how
// long ago the date represents.
function prettyDate(time){
	var date = new Date((time || "").replace(/-/g,"/").replace(/[TZ]/g," ")),
		diff = (((new Date()).getTime() - date.getTime()) / 1000),
		day_diff = Math.floor(diff / 86400);
			
	if ( isNaN(day_diff) || day_diff < 0 || day_diff >= 31 )
		return;
			
	return day_diff == 0 && (
			diff < 60 && "just now" ||
			diff < 120 && "1 minute ago" ||
			diff < 3600 && Math.floor( diff / 60 ) + " minutes ago" ||
			diff < 7200 && "1 hour ago" ||
			diff < 86400 && Math.floor( diff / 3600 ) + " hours ago") ||
		day_diff == 1 && "yesterday" ||
		day_diff < 7 && day_diff + " days ago" ||
		day_diff < 31 && Math.ceil( day_diff / 7 ) + " weeks ago";
}

// If jQuery is included in the page, adds a jQuery plugin to handle it as well
if ( typeof jQuery != "undefined" )
	jQuery.fn.prettyDate = function(){
		return this.each(function(){
			var date = prettyDate(this.title);
			if ( date )
				jQuery(this).text( date );
		});
	};
	
// Setup the header cycle.
jQuery(document).ready(function($) {
  jQuery("#user-cycle").cycle();
  jQuery("#floor-cycle").cycle();
  
  //Set up the help dialog.
  jQuery("#widget-help-dialog").dialog({
    autoOpen: false,
    width: 550,
    position: ["center", 100],
    modal: true
  });
  
  $("#link-container").hover(function() {
    if ($("#header-canopy-link").hasClass("hidden")) {
      $("#header-canopy-link").removeClass("hidden").css({display: "none"}).fadeIn("slow");
      setCookie("display-canopy", true, 21);
    }
  });
  
  if(getCookie("display-canopy")) {
    // deleteCookie("display-canopy");
    $("#header-canopy-link").removeClass("hidden");
  }
  
  $(".rejection-date").prettyDate();
});

// Function to handle AJAX post requests.
jQuery.ajaxSetup({ 
     beforeSend: function(xhr, settings) {
         function getAjaxCookie(name) {
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
             xhr.setRequestHeader("X-CSRFToken", getAjaxCookie('csrftoken'));
         }
     } 
});

// Make sure to load jQuery before this.
var log_js_action = function(type, object, action) {
  // Send a request to the logging URL.
  jQuery.get("/log/" + type + "/" + object + "/" + action + "/");
}

var toggleHelp = function(category, slug) {
  // log_js_action("ask-admin", "dialog", "open");
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

function onPlayerError(errorCode) {
  var videoSlug = window.location.pathname.split('/'); 
  log_js_action("video_"+videoSlug[videoSlug.length -2], "error", errorCode);
}
      
function onPlayerStateChange(newState) {
  var state = "";
  switch (newState) {
    case -1: state = "unstarted"; break;
    case 0:  state = "end"; break;
    case 1: state = "playing"; break;
    case 2: state = "paused"; break;
    case 3: state = "buffering"; break;
    case 5: state = "cued"; break;
  }
  var videoSlug = window.location.pathname.split('/'); 
  log_js_action("video_"+videoSlug[videoSlug.length -2], "state", state);
}
            
function onYouTubePlayerReady(playerId) {
  ytplayer = document.getElementById("ytPlayer");
  ytplayer.addEventListener("onStateChange", "onPlayerStateChange");
  ytplayer.addEventListener("onError", "onPlayerError");
}