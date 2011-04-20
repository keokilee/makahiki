$(document).ready(function() {
  // Hide the details until someone clicks on it.
  // $("#quest-details").hide();
  
  // Handler for clicking a quest title.
  $(".quest-title").click(function() {
    //Set the title as selected if it is not already selected
    if (!$(this).parent().hasClass("selected")) {
      $(this).parent().siblings("li").removeClass("selected");
      $(this).parent().addClass("selected");
    }
    
    //Insert the contents of the quest-description into the details.
    $("#quest-contents").html($(this).next(".quest-description").html());
    
    //Toggle quest-details if it is hidden.
    if (!$("#quest-details").is(":visible")) {
      $("#quest-details").slideDown("slow", function() {
        //Animation complete
      });
    }
  });
  
  // Handler for clicking on the hide link.
  $("#quest-hide").click(function() {
    $("#quest-box li").removeClass("selected");
    $("#quest-details").slideUp("slow", function() {
      //Animation complete
    });
  });
  
  // If we have a quest dialog, display it.
  if ($("#quest-complete-dialog") != null) {
    $("#quest-complete-dialog").dialog({
      modal: true, 
      width: "520px"
      //       buttons: {
      //   "OK": function() {
      //          $( this ).dialog( "close" );
      //  }
      // }
    });
  }
})
