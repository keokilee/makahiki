#!/bin/bash

var='fixtures/'

if [ "$#" -eq 1 ]
  then
    var="$1"
fi

python manage.py dumpdata --indent=2 floors.dorm floors.floor > $var/base_floors.json

python manage.py dumpdata --indent=2 activities > $var/base_activities.json

python manage.py dumpdata --indent=2 quests > $var/base_quests.json

python manage.py dumpdata --indent=2 help_topics > $var/base_help.json

python manage.py dumpdata --indent=2 auth.user makahiki_profiles makahiki_avatar > $var/test_users.json

python manage.py dumpdata --indent=2 floors.post > $var/test_posts.json

python manage.py dumpdata --indent=2 energy_goals > $var/test_energy_goals.json

python manage.py dumpdata --indent=2 prizes.prize prizes.raffledeadline prizes.raffleprize > $var/test_prizes.json

# python manage.py dumpdata --indent=2 brabeion.badgeaward > $var/test_badges.json

