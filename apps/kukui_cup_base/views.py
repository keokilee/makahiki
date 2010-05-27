# Create your views here.
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from kukui_cup_base.models import Article

def homepage(request):
  articles = Article.objects.order_by('-pk')
  return render_to_response("homepage.html", {
    "articles": articles,
  }, context_instance = RequestContext(request))
  
def article(request, item_id, slug=None):
  article = None
  if not slug:
    article = get_object_or_404(Article, pk=item_id)
  else:
    article = get_object_or_404(Article, pk=item_id, slug=slug)

  return render_to_response("news/full_article.html", {
    "article": article,
  }, context_instance = RequestContext(request))
  