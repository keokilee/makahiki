$(document).ready(function() {
  // Hide the details until someone clicks on it.
  // $("#quest-details").hide();
  
  // Handler for clicking a quest title.
  $(".quest-title").click(function() {
    //Set the title as selected if it is not already selected
    if (!$(this).parent().hasClass("selected")) {
      $(this).parent().siblings("li").removeClass("selected");
      $(this).parent().addClass("selected");
      
      //Insert the contents of the quest-description into the details.
      $("#quest-contents").html($(this).next(".quest-description").html());
      
      // Set cookie that identifies this quest as open.
      setCookie("visible-quest", "#" + $(this).attr('id'));

      //Toggle quest-details if it is hidden.
      if (!$("#quest-details").is(":visible")) {
        if($(this).parent().hasClass('canopy-quest')) {
          log_js_action("canopy-quest", $(this).attr('id'), 'show');
        }
        else {
          log_js_action("quest", $(this).attr('id'), 'show'); 
        }
        // console.log($(this).attr('id'));
        $("#quest-details").slideDown("slow", function() {
          //Animation complete
        });
      }
    }
    
    else {
      //Hide quest details and remove selected.
      $(this).parent().removeClass("selected");
      
      // Remove cookie.
      deleteCookie("visible-quest");
      
      if($(this).parent().hasClass('canopy-quest')) {
        log_js_action("canopy-quest", $(this).attr('id'), 'hide');
      }
      else {
        log_js_action("quest", $(this).attr('id'), 'hide');
      }
      $("#quest-details").slideUp("slow", function() {
        //Animation complete
      });
    }
  });
  
  // Handler for clicking on the hide link.
  $("#quest-hide").click(function() {
    $("#quest-box li").removeClass("selected");
    deleteCookie("visible-quest");
    if($(this).parent().hasClass('canopy-quest')) {
      log_js_action("canopy-quest", $(this).attr('id'), 'hide');
    }
    else {
      log_js_action("quest", $(this).attr('id'), 'hide');
    }
    $("#quest-details").slideUp("slow", function() {
      //Animation complete
    });
  });
  
  $("#quest-help-dialog").dialog({
    modal: true,
    width: 450,
    autoOpen: false
  });
  
  $("#quest-help-icon").click(function() {
    $('#quest-help-dialog').dialog('open');
  });
  
  // If the cookie is set, display the quest.
  var value = getCookie("visible-quest");
  if (value) {
    $(value).parent().addClass("selected");
    $("#quest-contents").html($(value).next(".quest-description").html());

    if($(value).parent().hasClass('canopy-quest')) {
      log_js_action("canopy-quest", $(value).attr('id'), 'show');
    }
    else {
      log_js_action("quest", $(value).attr('id'), 'show'); 
    }
    // console.log($(this).attr('id'));
    $("#quest-details").show();
  }
});
