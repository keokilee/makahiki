// Use jQuery via jQuery(...)
jQuery(document).ready(function(){
  jQuery("#canopy-hide-about").click(function() {
    setCookie("hide-about", "true", 21);
    jQuery("#canopy-about").fadeOut();
    return false;
  });
  
  var textarea = jQuery("#wall-post textarea");
  textarea.click(function() {
    if (jQuery("#wall-post-submit").button("option", "disabled")) {
      this.value = "";
    }
  });
  textarea.keyup(function() {
    if (this.value.length == 0) {
      jQuery("#wall-post-submit").button("option", "disabled", true);
    }
    else {
      jQuery("#wall-post-submit").button("option", "disabled", false);
    }
  });
  
  jQuery("#wall-post-submit").button({
    disabled: true
  });
  
  jQuery("#wall-post-submit").click(function() {
    if (!jQuery("#wall-post-submit").button("option", "disabled")) {
      jQuery.post(jQuery("#news-post-form").attr("action"), jQuery("#news-post-form").serialize(), function(data) {
        if (data.message) {
          jQuery("#wall-post-errors").html(data.message);
        }
        else {
          jQuery("#wall-post-errors").html("");
          if (jQuery("#wall-no-posts").is(":visible")) {
            jQuery("#wall-no-posts").hide();
          }
          jQuery(data.contents).hide().prependTo("#wall-posts").fadeIn();
          jQuery("textarea").val("");
          jQuery("#wall-post-submit").button("option", "disabled", true);
        }
      });
    }
    return false;
  });
});