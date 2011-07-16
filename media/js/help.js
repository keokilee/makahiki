$(document).ready(function() {
  $("#help-ask-form textarea").keyup(function() {
    if (this.value.length == 0) {
      $("#help-ask-submit input").button("option", "disabled", true);
    }
    else {
      $("#help-ask-submit input").button("option", "disabled", false);
    }
  });
  
  $("#help-ask-submit input").button({
    disabled: true
  });
  
  $("#help-ask-submit input").click(function() {
    if(!$(this).button("option", "disabled")) {
      $(this).button("option", "disabled", true);
      $("#field_url").val(window.location);
      $("#help-ask-spinner").show();
      $.post(this.form.action, $("#help-ask-form").serialize(), function(data) {
        $("#feedback-success").dialog("open");
        $("#help-ask-spinner").hide();
        $("#help-ask-form textarea").val("");
      });

      return false;
    }
  });
});