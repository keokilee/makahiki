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

      //Toggle quest-details if it is hidden.
      if (!$("#quest-details").is(":visible")) {
        log_js_action("quest", $(this).attr('id'), 'show');
        // console.log($(this).attr('id'));
        $("#quest-details").slideDown("slow", function() {
          //Animation complete
        });
      }
    }
    
    else {
      //Hide quest details and remove selected.
      $(this).parent().removeClass("selected");
      log_js_action("quest", $(this).attr('id'), 'hide');
      $("#quest-details").slideUp("slow", function() {
        //Animation complete
      });
    }
  });
  
  // Handler for clicking on the hide link.
  $("#quest-hide").click(function() {
    $("#quest-box li").removeClass("selected");
    log_js_action("quest", $(this).attr('id'), 'hide');
    $("#quest-details").slideUp("slow", function() {
      //Animation complete
    });
  });
})
