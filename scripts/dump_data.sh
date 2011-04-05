python manage.py dumpdata --indent=2 floors.dorm floors.floor > fixtures/base_floors.json

python manage.py dumpdata --indent=2 activities > fixtures/base_activities.json

python manage.py dumpdata --indent=2 quests.Quest > fixtures/base_quests.json

python manage.py dumpdata --indent=2 account auth.user makahiki_profiles.profile > fixtures/test_users.json

python manage.py dumpdata --indent=2 floors.post > fixtures/test_posts.json

python manage.py dumpdata --indent=2 energy_goals > fixtures/test_energy_goals.json

python manage.py dumpdata --indent=2 prizes > fixtures/test_prizes.json

