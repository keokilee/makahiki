import time, re
from django.test import TestCase
from noseselenium.cases import SeleniumTestCaseMixin

class test_goals(TestCase, SeleniumTestCaseMixin):
    selenium_test = True
    selenium_fixtures = ["base_data.json", "user_data.json"]
    
    def setUp(self):
        self.verificationErrors = []
        
    def test_test_goals(self):
        sel = self.selenium
        sel.open("/account/login/")
        for i in range(60):
            try:
                if sel.is_element_present(u"//input[@type='submit']"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.type("id_username", "admin")
        sel.type("id_password", "changeme")
        sel.click(u"//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("//div[@id='tabhead']/div/ul[2]/li[1]/a/span"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//div[@id='tabhead']/div/ul[2]/li[1]/a/span")
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
                if sel.is_element_present("link=Add goal"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Add goal")
        for i in range(60):
            try:
                if sel.is_element_present("id_title"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.type("id_title", "A test goal")
        sel.type("id_description", "Go testing!")
        sel.type("id_point_value", "10")
        sel.click("_save")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_text_present("The goal \"A test goal\" was added successfully."): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=A test goal")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Delete")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("//div[@id='content']/ul/li/a"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//input[@value=\"Yes, I'm sure\"]")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("//div[@id='container']/ul/li"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Log out")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("link=Log in again"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")

    def tearDown(self):
        self.assertEqual([], self.verificationErrors)
if __name__ == "__main__":
    unittest.main()
