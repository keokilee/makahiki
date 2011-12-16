# User social bonuses
data = {}
for user in User.objects.filter(profile__points__gt=0):
    bonuses = user.pointstransaction_set.filter(message__endswith='Social Bonus)').count()
    if bonuses == 0:
        data['0'] = data.get('0', 0) + 1
    elif bonuses <= 10:
        data['1-10'] = data.get('1-10', 0) + 1
    elif bonuses <= 20:
        data['11-20'] = data.get('11-20', 0) + 1
    elif bonuses <= 30:
        data['21-30'] = data.get('21-30', 0) + 1
    else:
        data['31+'] = data.get('31+', 0) + 1

for key, value in data.iteritems():
    print '%s,%d' % (key, value)
    
# lounge goals and points   
for floor in Floor.objects.order_by('dorm__name', 'number'):
    goals = floor.floorenergygoal_set.count()
    print '%s,%d,%d' % (floor, goals, floor.points())
    
# raffle information
# 25-100: 13.24% (27/204)
# 100-500: 51.32% (78/152)
# 500-1000: 88.88% (32/36)
# 1000+: 100% (9/9)
query = User.objects.filter(profile__points__gt=500, profile__points__lte=1000)
user_count = query.count()
total = 0
for user in query:
    if user.raffleticket_set.count() > 0:
        total += 1
        
print total