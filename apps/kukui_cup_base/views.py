# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext

from news.models import Article

def homepage(request):
  articles = Article.objects.all()[:5]
  return render_to_response("homepage.html", {
    "articles": articles,
  }, context_instance = RequestContext(request))
  