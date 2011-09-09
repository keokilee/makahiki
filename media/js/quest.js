jQuery(document).ready(function() {
  // Hide the details until someone clicks on it.
  // jQuery("#quest-details").hide();
  
  // Handler for clicking a quest title.
  jQuery(".quest-title").click(function() {
    //Set the title as selected if it is not already selected
    if (!jQuery(this).parent().hasClass("selected")) {
      jQuery(this).parent().siblings("li").removeClass("selected");
      jQuery(this).parent().addClass("selected");
      
      //Insert the contents of the quest-description into the details.
      jQuery("#quest-contents").html(jQuery(this).next(".quest-description").html());
      
      // Set cookie that identifies this quest as open.
      setCookie("visible-quest", "#" + jQuery(this).attr('id'));

      //Toggle quest-details if it is hidden.
      if (!jQuery("#quest-details").is(":visible")) {
        if(jQuery(this).parent().hasClass('canopy-mission')) {
          log_js_action("canopy-mission", jQuery(this).attr('id'), 'show');
        }
        else {
          log_js_action("quest", jQuery(this).attr('id'), 'show'); 
        }
        // console.log(jQuery(this).attr('id'));
        jQuery("#quest-details").slideDown("slow", function() {
          //Animation complete
        });
      }
    }
    
    else {
      //Hide quest details and remove selected.
      jQuery(this).parent().removeClass("selected");
      
      // Remove cookie.
      deleteCookie("visible-quest");
      
      if(jQuery(this).parent().hasClass('canopy-quest')) {
        log_js_action("canopy-quest", jQuery(this).attr('id'), 'hide');
      }
      else {
        log_js_action("quest", jQuery(this).attr('id'), 'hide');
      }
      jQuery("#quest-details").slideUp("slow", function() {
        //Animation complete
      });
    }
  });
  
  // Handler for clicking on the hide link.
  jQuery("#quest-hide").click(function() {
    jQuery("#quest-box li").removeClass("selected");
    deleteCookie("visible-quest");
    if(jQuery(this).parent().hasClass('canopy-quest')) {
      log_js_action("canopy-quest", jQuery(this).attr('id'), 'hide');
    }
    else {
      log_js_action("quest", jQuery(this).attr('id'), 'hide');
    }
    jQuery("#quest-details").slideUp("slow", function() {
      //Animation complete
    });
  });
  
  // If the cookie is set, display the quest.
  var value = getCookie("visible-quest");
  if (value && (jQuery(value).attr('id') != null)) {
    jQuery(value).parent().addClass("selected");
    jQuery("#quest-contents").html(jQuery(value).next(".quest-description").html());

    if(jQuery(value).parent().hasClass('canopy-quest')) {
      log_js_action("canopy-quest", jQuery(value).attr('id'), 'show');
    }
    else {
      log_js_action("quest", jQuery(value).attr('id'), 'show'); 
    }
    // console.log(jQuery(this).attr('id'));
    jQuery("#quest-details").show();
  }
  else if (value) {
    // alert("delete");
    // Could not find this quest item, so let's delete the cookie.
    deleteCookie("visible-quest");
  }
});
