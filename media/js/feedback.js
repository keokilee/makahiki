$(document).ready(function() {
  $("#feedback-dialog").dialog({
    modal: true,
    width: 500,
    position: ["center", 150],
    autoOpen: false,
    open: function() {
      $("#id_url").val(window.location);
      $("#feedback-form textarea").focus();
      $("#feedback-form textarea").val("");
    }
  });
  
  $("#feedback-success").dialog({
    modal: true,
    width: 500,
    position: ["center", 150],
    autoOpen: false
  });
  
  $("#feedback-form textarea").keyup(function() {
    if (this.value.length == 0) {
      $("#feedback-submit").button("option", "disabled", true);
    }
    else {
      $("#feedback-submit").button("option", "disabled", false);
    }
  });
  
  $("#header-feedback").click(function() {
    log_js_action("ask-admin", "form", "show");
    $("#feedback-dialog").dialog("open");
  });
  
  $("#feedback-submit").button({
    disabled: true
  });
  
  $("#feedback-submit").click(function() {
    if(!$(this).button("option", "disabled")) {
      $(this).button("option", "disabled", true);
      // alert(this.form.action);
      $("#feedback-spinner").show();
      $.post(this.form.action, $("#feedback-form").serialize(), function(data) {
        $("#feedback-dialog").dialog("close");
        $("#feedback-success").dialog("open");
        $("#feedback-spinner").hide();
      });
    }
    
    return false;
  });
  
  $("#feedback-success button").click(function() {
    $("#feedback-success").dialog("close");
  })
  $("#header-feedback").removeAttr("disabled");
});