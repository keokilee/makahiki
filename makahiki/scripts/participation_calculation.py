from django.db.models import Q

for floor in Floor.objects.order_by('dorm__name', 'number'):
  r1_participation = floor.profile_set.filter(scoreboardentry__round_name='Round 1', scoreboardentry__points__gte=50).distinct().count()
  r2_participation = floor.profile_set.filter(Q(scoreboardentry__round_name='Round 2', scoreboardentry__points__gte=50) | Q(scoreboardentry__round_name='Round 1', scoreboardentry__points__gte=50)).distinct().count()
  overall = floor.profile_set.filter(points__gte=50).count()
  print "%s,%d,%d,%d,%d" % (floor, r1_participation, r2_participation, overall,floor.profile_set.count())