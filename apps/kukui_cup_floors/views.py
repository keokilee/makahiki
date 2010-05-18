# Create your views here.

def dorm(dorm_slug):
  dorm = get_object_or_404(Dorm, slug=dorm_slug)
  
def floor(dorm_slug, floor):
  dorm = get_object_or_404(Dorm, slug=dorm_slug)
  floor = get_object_or_404(Floor, dorm=dorm, floor_number=floor)