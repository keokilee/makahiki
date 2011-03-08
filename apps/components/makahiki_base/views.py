# # Create your views here.
# 
# from django.shortcuts import get_object_or_404, render_to_response
# from django.http import HttpResponseRedirect
# from django.core.urlresolvers import reverse
# from django.template import RequestContext
# from django.views.decorators.cache import cache_control
# from minidetector import detect_mobile
# 
# from makahiki_base.models import Article
# 
# @cache_control(must_revalidate=True, max_age=3600)
# def homepage(request):
#   """Retrieves articles for the home page."""
#   articles = Article.objects.order_by('-pk')
#   headlines = _generate_headlines(articles)
#   
#   return render_to_response("homepage.html", {
#     "articles": articles,
#     "headlines": headlines,
#   }, context_instance = RequestContext(request))
#   
# @cache_control(must_revalidate=True, max_age=3600)
# @detect_mobile
# def index(request):
#   """Goes to the base URL.  At this point, we can determine if the user is logged in or on a mobile device."""
#   user = request.user
#   
#   if request.mobile:
#     return HttpResponseRedirect(reverse("mobile_index"))
#   # Check if a user is logged in and a valid participant.
#   elif user.is_authenticated() and user.get_profile().floor:
#     return HttpResponseRedirect(reverse("makahiki_profiles.views.profile", args=(request.user.id,)))
#   else:
#     return homepage(request)
#   
# def _generate_headlines(items):
#   """Private method to generate headlines on demand."""
#   for item in items:
#     if isinstance(item, Article):
#       yield "<p>Latest News: <a href='%s'>%s</a></p>" % (reverse("view_article", args=(item.slug,)), item.title)
#   
# def article(request, slug=None):
#   """Displays a single article."""
#   article = get_object_or_404(Article, slug=slug)
# 
#   return render_to_response("makahiki_base/full_article.html", {
#     "article": article,
#   }, context_instance = RequestContext(request))
#   