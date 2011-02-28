$(document).ready(function() {
  var textarea = $("textarea");
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
  post_button.button({
    disabled: true
  });
  
  post_button.click(function() {
    if (!$(this).button("option", "disabled")) {
      $.post("{% url news_post %}", $("#news-post-form").serialize(), function(data) {
        if (data.message) {
          $("#wall-post-errors").html(data.message);
        }
        else {
          $("#wall-post-errors").html("");
          $(data.contents).hide().prependTo("#wall-posts").fadeIn();
          textarea.val("");
          $("#wall-post-submit").button("option", "disabled", true);
        }
      });
    }
    return false;
  });
  
});