echo ===RESETTING TESTBOT...===
python manage.py reset_user_no_prompt testbot
echo ----------------------------------------------------------------------
echo ===RESETTING TESTBOT PASSWORD...===
python selenium/Selenium/reset_testbot.py
echo ---------------------------------------------------------------------- 
echo ===COPYING FIXTURES...===
cp fixtures/pre_event/*.json fixtures 
echo ----------------------------------------------------------------------
echo ===LOADING FIXTURES...===
./scripts/load_data.sh
echo ----------------------------------------------------------------------


