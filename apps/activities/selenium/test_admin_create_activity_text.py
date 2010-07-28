from selenium import selenium
import unittest, time, re
from noseselenium.cases import SeleniumTestCaseMixin

class test_admin_create_activity_text(unittest.TestCase, SeleniumTestCaseMixin):
    selenium_test = True
    selenium_fixtures = ["base_data.json", "user_data.json"]
    
    def test_test_admin_create_activity_text(self):
        sel = self.selenium
        sel.open("/account/login/")
        sel.type("id_username", "admin")
        sel.type("id_password", "changeme")
        sel.click(u"//input[@type='submit']")
        for i in range(60):
            try:
                if sel.is_element_present("//div[@id='tabhead']/div/ul[2]/li[1]/a/span"): break
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
        sel.type("id_title", "Test Activity")
        sel.type("id_description", "A test activity.")
        sel.type("id_point_value", "10")
        sel.type("id_duration", "120")
        sel.type("id_expire_date", "2010-12-31")
        sel.click("_save")
        for i in range(60):
            try:
                if sel.is_text_present("Please correct the error below."): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.failUnless(sel.is_text_present("At least one question is required if the activity's confirmation type is text."))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.type("id_textpromptquestion_set-0-question", "A test question?")
        sel.type("id_textpromptquestion_set-0-answer", "hi")
        sel.click("_save")
        for i in range(60):
            try:
                if sel.is_text_present("The activity \"Test Activity\" was added successfully."): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Test Activity")
        sel.wait_for_page_to_load("30000")
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
        sel.click("link=Log out")
        for i in range(60):
            try:
                if sel.is_text_present("Logged out"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")

if __name__ == "__main__":
    unittest.main()
