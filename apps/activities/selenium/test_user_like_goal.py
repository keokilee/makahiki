import time, re
from django.test import TestCase
from noseselenium.cases import SeleniumTestCaseMixin

class test_user_goals_like(TestCase, SeleniumTestCaseMixin):
    selenium_test = True
    selenium_fixtures = ["base_data.json", "user_data.json"]
  
    def setUp(self):
        self.verificationErrors = []
    
    def test_test_user_goals_like(self):
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
                if sel.is_element_present("//li[@id='user_tab']/a/span"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//li[@id='user_tab']/a/span")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("link=Goals"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Goals")
        for i in range(60):
            try:
                if sel.is_element_present("//div[@id='available_items']/div[2]/table/tbody/tr[2]/td[1]/div[2]/form/a/span[2]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.failUnless(sel.is_text_present("You are not participating in any goals."))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("//div[@id='available_items']/div[2]/table/tbody/tr[2]/td[1]/div[2]/form/a/span[2]")
        for i in range(60):
            try:
                if sel.is_element_present("link=Unlike"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Unlike")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("//div[@id='available_items']/div[2]/table/tbody/tr[2]/td[1]/div[2]/form/a/span[2]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.failUnless(sel.is_text_present("You are not participating in any goals."))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failIf(sel.is_element_present("link=Unlike"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("//div[@id='login']/a/span")
        sel.wait_for_page_to_load("30000")
    
    def tearDown(self):
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
