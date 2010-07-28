from selenium import selenium
import unittest, time, re
from noseselenium.cases import SeleniumTestCaseMixin

class test_admin_create_event(unittest.TestCase, SeleniumTestCaseMixin):
    selenium_test = True
    selenium_fixtures = ["base_data.json", "user_data.json"]
    
    def setUp(self):
        self.verificationErrors = []
        
    def test_test_admin_create_event(self):
        sel = self.selenium
        sel.open("/account/login/")
        for i in range(60):
            try:
                if sel.is_element_present("id_username"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.type("id_username", "admin")
        sel.type("id_password", "changeme")
        sel.click(u"//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_text_present("Admin"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//div[@id='tabhead']/div/ul[2]/li[1]/a/span")
        for i in range(60):
            try:
                if sel.is_element_present("link=Activitys"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Activitys")
        for i in range(60):
            try:
                if sel.is_element_present("link=Add activity"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Add activity")
        for i in range(60):
            try:
                if sel.is_element_present("id_title"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.type("id_title", "Test Activity With Confirmation Codes")
        sel.type("id_description", "A test activity")
        sel.type("id_point_value", "10")
        sel.type("id_duration", "120")
        sel.type("id_expire_date", "2010-12-31")
        sel.click("id_is_event")
        sel.select("id_confirm_type", "label=Confirmation Code")
        sel.click("_save")
        for i in range(60):
            try:
                if sel.is_text_present("Events require an event date."): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//form[@id='activity_form']/div[3]/fieldset[2]/div[2]/div/p[1]/span[1]/a[1]")
        sel.click("link=Now")
        try: self.failUnless(sel.is_text_present("The number of codes is required for this confirmation type."))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.type("id_num_codes", "100")
        try: self.failUnless(sel.is_text_present("This confirmation type requires a confirmation prompt."))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.type("id_confirm_prompt", "Enter the confirmation code from this event.")
        sel.click("_save")
        for i in range(60):
            try:
                if sel.is_element_present("link=Test Activity With Confirmation Codes"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.failUnless(sel.is_text_present("The activity \"Test Activity With Confirmation Codes\" was added successfully."))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=Test Activity With Confirmation Codes")
        for i in range(60):
            try:
                if sel.is_element_present("link=View codes"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        for i in range(60):
            try:
                if sel.is_text_present("Test Activity With Confirmation Codes"): break
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
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("link=Log out"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Log out")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_text_present("Logged out"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        
    def tearDown(self):
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
