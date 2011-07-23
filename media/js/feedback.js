jQuery(document).ready(function() {
  jQuery("#feedback-dialog").dialog({
    modal: true,
    width: 500,
    position: ["center", 150],
    autoOpen: false,
    open: function() {
      jQuery("#id_url").val(window.location);
      jQuery("#feedback-form textarea").focus();
      jQuery("#feedback-form textarea").val("");
    }
  });
  
  jQuery("#feedback-success").dialog({
    modal: true,
    width: 500,
    position: ["center", 150],
    autoOpen: false
  });
  
  jQuery("#feedback-form textarea").keyup(function() {
    if (this.value.length == 0) {
      jQuery("#feedback-submit").button("option", "disabled", true);
    }
    else {
      jQuery("#feedback-submit").button("option", "disabled", false);
    }
  });
  
  jQuery("#header-feedback").click(function() {
    log_js_action("ask-admin", "form", "show");
    jQuery("#feedback-dialog").dialog("open");
  });
  
  jQuery("#feedback-submit").button({
    disabled: true
  });
  
  jQuery("#feedback-submit").click(function() {
    if(!jQuery(this).button("option", "disabled")) {
      jQuery(this).button("option", "disabled", true);
      // alert(this.form.action);
      jQuery("#feedback-spinner").show();
      $.post(this.form.action, jQuery("#feedback-form").serialize(), function(data) {
        jQuery("#feedback-dialog").dialog("close");
        jQuery("#feedback-success").dialog("open");
        jQuery("#feedback-spinner").hide();
      });
    }
    
    return false;
  });
  
  jQuery("#feedback-success button").click(function() {
    jQuery("#feedback-success").dialog("close");
  })
  jQuery("#header-feedback").removeAttr("disabled");
});