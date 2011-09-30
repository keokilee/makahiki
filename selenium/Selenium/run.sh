echo ===COPYING FIXTURES...===
cp fixtures/first_login/*.json fixtures 
----------------------------------------------------------------------
echo ===LOADING FIXTURES...===
./scripts/load_data.sh
----------------------------------------------------------------------
echo ===RESETTING TESTBOT...===
python manage.py reset_user_no_prompt testbot
----------------------------------------------------------------------
echo ===RESETTING TESTBOT PASSWORD...===
python selenium/Selenium/reset_testbot.py
echo ----------------------------------------------------------------------
echo ===TESTING FIRST LOGIN PROCESS...===
python selenium/Selenium/first_login.py
echo ----------------------------------------------------------------------
echo ===TESTING ACTIVITY...===
python selenium/Selenium/test_activity.py
echo ----------------------------------------------------------------------
echo ===TESTING COMMITMENT...===
python selenium/Selenium/test_commitment.py 
echo ----------------------------------------------------------------------
echo ===TESTING RAFFLE...===
python selenium/Selenium/add_remove_raffle.py
echo ----------------------------------------------------------------------
