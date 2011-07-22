import time, re
from noseselenium.cases import SeleniumTestCaseMixin
from django.test import TestCase

class test_news_post(TestCase, SeleniumTestCaseMixin):
    selenium_fixtures = ["fixtures/base_floors.json", "fixtures/test_users.json"]
    def setUp(self):
        self.verificationErrors = []
    
    def test_test_news_post(self):
        sel = self.selenium
        sel.open("/account/login/")
        sel.type("id_username", "returning_user")
        sel.type("id_password", "changeme")
        sel.click("//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        sel.click("home-news-icon")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("There are no posts yet!"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.type("id_post", "Hello world")
        sel.key_up("id_post", "!")
        for i in range(60):
            try:
                if sel.is_element_present("//a[@id='wall-post-submit']/span"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//a[@id='wall-post-submit']/span")
        for i in range(60):
            try:
                if sel.is_text_present("Maile T. Hello world"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.failIf(sel.is_text_present("There are no posts yet!"))
        sel.click("id_post")
        sel.type("id_post", "Another post")
        sel.key_up("id_post", "!")
        sel.click("//a[@id='wall-post-submit']/span")
        for i in range(60):
            try:
                if sel.is_text_present("Maile T. Another post"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.failUnless(sel.is_text_present("Maile T. Hello world"))
        sel.click("link=Logout")
        sel.wait_for_page_to_load("30000")
    
    def tearDown(self):
        self.assertEqual([], self.verificationErrors)

