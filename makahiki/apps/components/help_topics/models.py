from django.db import models

MARKDOWN_LINK = "http://daringfireball.net/projects/markdown/syntax"
MARKDOWN_TEXT = "Uses <a href=\"" + MARKDOWN_LINK + "\" target=\"_blank\">Markdown</a> formatting."
HELP_CATEGORIES = (
    ("faq", "Frequently Asked Questions"),
    ("rules", "Rules of the competition"),
    ("widget", "Widget Help"),
)

class HelpTopic(models.Model):
  """
  Represents a help topic in the system.
  """
  title = models.CharField(max_length=255, help_text="The title of the topic.")
  slug = models.SlugField(help_text="Automatically generated if left blank.")
  category = models.CharField(max_length=50, choices=HELP_CATEGORIES)
  contents = models.TextField(help_text="The content of the help topic. %s" % MARKDOWN_TEXT)
  parent_topic = models.ForeignKey("HelpTopic", 
      null=True, 
      blank=True, 
      help_text="Optional parent topic of this topic.",
      related_name="sub_topics",
  )
  
  @models.permalink
  def get_absolute_url(self):
      return ('help_topic', [self.category, self.slug])
  
  def __unicode__(self):
    return "%s: %s" % (self.category.capitalize(), self.title)
    
  
