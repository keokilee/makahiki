# Create your views here.
from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.views.decorators.cache import cache_control

from makahiki_base.models import Article

@cache_control(must_revalidate=True, max_age=3600)
def homepage(request):
  """Retrieves articles for the home page."""
  articles = Article.objects.order_by('-pk')
  headlines = _generate_headlines(articles)
  
  return render_to_response("homepage.html", {
    "articles": articles,
    "headlines": headlines,
  }, context_instance = RequestContext(request))
  
def _generate_headlines(items):
  """Private method to generate headlines on demand."""
  for item in items:
    if isinstance(item, Article):
      yield "<p>Latest News: <a href='%s'>%s</a></p>" % (reverse("resources.views.resource", args=(item.id,)), item.title)
  
def article(request, item_id, slug=None):
  """Displays a single article."""
  article = None
  if not slug:
    article = get_object_or_404(Article, pk=item_id)
  else:
    article = get_object_or_404(Article, pk=item_id, slug=slug)

  return render_to_response("makahiki_base/full_article.html", {
    "article": article,
  }, context_instance = RequestContext(request))
  