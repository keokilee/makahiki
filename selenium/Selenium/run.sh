echo ===COPYING FIXTURES...===
cp fixtures/first_login/*.json fixtures 
echo ----------------------------------------------------------------------
echo ===LOADING FIXTURES...===
./scripts/load_data.sh
echo ----------------------------------------------------------------------
echo ===RESETTING TESTBOT...===
python manage.py reset_user_no_prompt testbot
echo ----------------------------------------------------------------------

echo ===RESETTING TESTBOT PASSWORD...===
python selenium/Selenium/reset_testbot.py 

echo ===TESTING FIRST LOGIN PROCESS...===
python selenium/Selenium/first_login.py  

echo ===TESTING GOLOW PAGE...===
python selenium/Selenium/test_golow.py 

echo ===TESTING NAVBAR...===
python selenium/Selenium/test_navbar.py 

echo ===TESTING ACTIVITY...===
python selenium/Selenium/test_activity.py 

echo ===TESTING COMMITMENT...===
python selenium/Selenium/test_commitment.py  

echo ===TESTING EVENT...===
python selenium/Selenium/test_event.py

echo ===TESTING NEWS...===
python selenium/Selenium/test_news.py

echo ===TESTING PROFILE...===
python selenium/Selenium/test_profile.py

echo ===TESTING QUESTS...===
python selenium/Selenium/test_quest.py

echo ===TESTING RAFFLE...===
python selenium/Selenium/add_remove_raffle.py

echo ===TESTING CANOPY VISUALIZATIONS...===
echo IF THIS TEST FAILS, ITS PROBABLY DUE TO A SLOW INTERNET CONNECTION 
python selenium/Selenium/test_canopy_graph.py 

echo ===TESTING CANOPY POST...===
python selenium/Selenium/test_canopy_post.py 

echo ===TESTING HELP...===
python selenium/Selenium/test_help.py


