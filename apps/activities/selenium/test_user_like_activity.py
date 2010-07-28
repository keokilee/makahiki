import time, re
from django.test import TestCase
from noseselenium.cases import SeleniumTestCaseMixin

class test_user_like_activity(TestCase, SeleniumTestCaseMixin):
    selenium_test = True
    selenium_fixtures = ["base_data.json", "user_data.json"]
  
    def setUp(self):
        self.verificationErrors = []
    
    def test_test_user_like_activity(self):
        sel = self.selenium
        sel.open("/account/login/")
        for i in range(60):
            try:
                if sel.is_element_present("id_username"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.type("id_username", "user")
        sel.type("id_password", "changeme")
        sel.click("//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("link=My Home"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=My Home")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("link=Activities"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Activities")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("//div[@id='available_items']/div[2]/table/tbody/tr[2]/td[1]/div[2]/form/a/span[2]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//div[@id='available_items']/div[2]/table/tbody/tr[2]/td[1]/div[2]/form/a/span[2]")
        for i in range(60):
            try:
                if sel.is_element_present("link=Unlike"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Unlike")
        for i in range(60):
            try:
                if sel.is_text_present("Available activities:"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        for i in range(60):
            try:
                if not sel.is_element_present("link=Unlike"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
    
    def tearDown(self):
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
