import time, re
from noseselenium.cases import SeleniumTestCaseMixin
from django.test import TestCase

from components.makahiki_profiles.models import Profile

class test_news_post(TestCase, SeleniumTestCaseMixin):
    selenium_fixtures = ["fixtures/base_floors.json", "fixtures/test_users.json"]
  
    def setUp(self):
        self.verificationErrors = []
    
    def test_test_news_post(self):
        profile = Profile.objects.get(user__username="user")
        profile.setup_complete = True
        profile.setup_profile = True
        profile.save()
      
        sel = self.selenium
        sel.open("/account/login/")
        sel.type("id_username", "user")
        sel.type("id_password", "changeme")
        sel.click("//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        sel.click("home-news-icon")
        sel.wait_for_page_to_load("30000")
        sel.type("id_post", "Hello world")
        sel.click("//a[@id='wall-post-submit']/span")
        for i in range(60):
            try:
                if sel.is_text_present("Maile Tanaka Hello world"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
    
    def tearDown(self):
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
