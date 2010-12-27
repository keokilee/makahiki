from selenium import selenium
import time, re
from noseselenium.cases import SeleniumTestCaseMixin
from django.test import TestCase

class test_admin_activity_image(TestCase, SeleniumTestCaseMixin):
    selenium_test = True
    selenium_fixtures = ["base_data.json", "user_data.json"]
    
    def setUp(self):
        self.verificationErrors = []
        
    def test_test_admin_activity_image(self):
        sel = self.selenium
        sel.open("/account/login/")
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
                if sel.is_element_present("link=Activitys"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Activitys")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("link=Add activity"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Add activity")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("id_title"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.type("id_title", "Test Activity With Image Upload")
        sel.type("id_description", "A test activity")
        sel.type("id_point_value", "10")
        sel.type("id_duration", "5")
        sel.type("id_expire_date", "2010-12-31")
        sel.select("id_confirm_type", "label=Image Upload")
        sel.click("_save")
        for i in range(60):
            try:
                if sel.is_text_present("This confirmation type requires a confirmation prompt."): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.type("id_confirm_prompt", "Upload an image. Any image!")
        sel.click("_save")
        for i in range(60):
            try:
                if sel.is_element_present("link=Test Activity With Image Upload"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Test Activity With Image Upload")
        for i in range(60):
            try:
                if sel.is_element_present("link=Delete"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Delete")
        for i in range(60):
            try:
                if sel.is_element_present("//input[@value=\"Yes, I'm sure\"]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//input[@value=\"Yes, I'm sure\"]")
        for i in range(60):
            try:
                if sel.is_element_present("link=Log out"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Log out")
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
