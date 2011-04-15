from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from pages.view_help.forms import AskAdminForm

@login_required
def index(request):
  form = None
  if request.method == "POST":
    form = AskAdminForm(request.POST)
    if form.is_valid():
      user = request.user
      email = user.get_profile().contact_email or user.email
      form.success = "Your question has been sent to the Kukui Cup administrators. We will email a response to " + email
      
  if not form:
    form = AskAdminForm()
    
  return render_to_response("help/index.html", {
      "form": form,
  }, context_instance=RequestContext(request))
  
def defineKukuiCup(request):
  return render_to_response("help/theKukuiCup.html", {}, context_instance=RequestContext(request))
  
def termsConditions(request):
  return render_to_response("help/termsConditions.html", {}, context_instance=RequestContext(request))
  
def figureBaseline(request):
  return render_to_response("help/figureOutBaseline.html", {}, context_instance=RequestContext(request))
  
def plugLoad(request):
  return render_to_response("help/plugLoad.html", {}, context_instance=RequestContext(request))
  
def collaborate(request):
  return render_to_response("help/collaborate.html", {}, context_instance=RequestContext(request))
  
def contact(request):
  return render_to_response("help/contactInfo.html", {}, context_instance=RequestContext(request))
  
def timeline(request):
  return render_to_response("help/timeline.html", {}, context_instance=RequestContext(request))
  
def competitions(request):
  return render_to_response("help/competitions.html", {}, context_instance=RequestContext(request))
  
def conservation(request):
  return render_to_response("help/loungeEnergyConservations.html", {}, context_instance=RequestContext(request))
  
def kukuinutpoints(request):
  return render_to_response("help/individualKukuiNutPoints.html", {}, context_instance=RequestContext(request))
  
def activities(request):
  return render_to_response("help/performingactivities.html", {}, context_instance=RequestContext(request))
  
def committments(request):
  return render_to_response("help/makingcommittments.html", {}, context_instance=RequestContext(request))
  
def conservationgoal(request):
  return render_to_response("help/settingconservationgoal.html", {}, context_instance=RequestContext(request))
  
def awardprizes(request):
  return render_to_response("help/awardprizes.html", {}, context_instance=RequestContext(request))
  
def eventoftie(request):
  return render_to_response("help/eventoftie.html", {}, context_instance=RequestContext(request))
  
def raffle(request):
  return render_to_response("help/raffle.html", {}, context_instance=RequestContext(request))