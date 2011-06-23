from django.shortcuts import render_to_response
from django.template import RequestContext

def index(request):
  return render_to_response("mobile/index.html", {}, context_instance=RequestContext(request))

def smartgrid(request):
  return render_to_response("mobile/smartgrid/index.html", {}, context_instance=RequestContext(request))

def landing(request):
  return render_to_response("mobile/landing.html", {}, context_instance=RequestContext(request))

def sevent(request):
  return render_to_response("mobile/events/sevent/index.html", {}, context_instance=RequestContext(request))

def events(request):
  return render_to_response("mobile/events/index.html", {}, context_instance=RequestContext(request))
