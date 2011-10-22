$(document).ready(function() {
  // bind 'myForm' and provide a simple callback function 
  $('#profile-form').ajaxForm();
              
  $("#progressbar").progressbar({
    value: 400/7
  });
  
  $("#back").button().click(function() {
    $(this).button("option", "disabled", true);
    $.get("{% url setup_referral %}?from=profile", function(data) {
      $("#ui-dialog-title-setup-dialog").html(data.title);
      $("#setup-dialog").html(data.contents);
    });
  });
  
  $("#next").button().click(function() {
    $(this).button("option", "disabled", true);
    $('#profile-form').ajaxSubmit({
      //beforeSubmit: showRequest,
      dataType: "json",
      success: showResponse,
      error: handleError
    });
    $(this).button("option", "disabled", false);
  });
  
  // Useful for debugging.
  function showRequest(formData, jqForm, options) { 
    // formData is an array; here we use $.param to convert it to a string to display it 
    // but the form plugin does this for you automatically when it submits the data 
    var queryString = $.param(formData); 

    // jqForm is a jQuery object encapsulating the form element.  To access the 
    // DOM element for the form do this: 
    // var formElement = jqForm[0]; 

    alert('About to submit: \n\n' + queryString); 

    // here we could return false to prevent the form from being submitted; 
    // returning anything other than false will allow the form submit to continue 
    return true; 
  }
  
  function handleError(xhr, text, error) {
    alert("Error" + text);
    alert(xhr.status);
    alert(error);
  }
  
  function showResponse(data) {
    $("#ui-dialog-title-setup-dialog").html(data.title);
    $("#setup-dialog").html(data.contents);
  }
  
  FB.init({appId: '{{FACEBOOK_APP_ID}}', status: true, cookie: true, xfbml: true});
});