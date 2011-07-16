$(document).ready(function() {
  var textarea = $("#wall-post textarea");
  textarea.click(function() {
    if ($("#wall-post-submit").button("option", "disabled")) {
      this.value = "";
    }
  });
  textarea.keyup(function() {
    if (this.value.length == 0) {
      $("#wall-post-submit").button("option", "disabled", true);
    }
    else {
      $("#wall-post-submit").button("option", "disabled", false);
    }
  });
  
  var post_button = $("#wall-post-submit");
  $("#wall-post-submit").button({
    disabled: true
  });
});