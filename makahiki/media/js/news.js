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
  
  $("#wall-post-submit").click(function() {
    if (!$("#wall-post-submit").button("option", "disabled")) {
      $.post(this.form.action, $("#news-post-form").serialize(), function(data) {
        if (data.message) {
          $("#wall-post-errors").html(data.message);
        }
        else {
          $("#wall-post-errors").html("");
          if ($("#wall-no-posts").is(":visible")) {
            $("#wall-no-posts").hide();
          }
          $(data.contents).hide().prependTo("#wall-posts").fadeIn();
          $("textarea").val("");
          $("#wall-post-submit").button("option", "disabled", true);
        }
      });
    }
    return false;
  });
});