# Create your views here.
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from kukui_cup_base.models import Article, Headline

def homepage(request):
  # Retrieve latest articles and headlines.
  articles = Article.objects.order_by('-pk')
  headlines = Headline.objects.order_by('-pk')[:10]
  
  return render_to_response("homepage.html", {
    "articles": articles,
    "headlines": headlines,
  }, context_instance = RequestContext(request))
  
def article(request, item_id, slug=None):
  article = None
  if not slug:
    article = get_object_or_404(Article, pk=item_id)
  else:
    article = get_object_or_404(Article, pk=item_id, slug=slug)

  return render_to_response("kukui_cup_base/full_article.html", {
    "article": article,
  }, context_instance = RequestContext(request))
  