import time, re
from noseselenium.cases import SeleniumTestCaseMixin
from django.test import TestCase

class test_admin_activity_with_point_range(TestCase, SeleniumTestCaseMixin):
    selenium_test = True
    selenium_fixtures = ["base_data.json", "user_data.json"]
    
    def setUp(self):
        self.verificationErrors = []
    
    def test_test_admin_activity_with_point_range(self):
        sel = self.selenium
        sel.open("/account/login/")
        sel.type("id_username", "admin")
        sel.type("id_password", "changeme")
        sel.click("//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("link=Admin"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Admin")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("link=Activitys"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Activitys")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Add activity")
        sel.wait_for_page_to_load("30000")
        sel.type("id_title", "Variable Point activity")
        sel.type("id_description", "Testing an activity with variable points!")
        sel.type("id_expire_date", "2010-12-31")
        sel.type("id_duration", "20")
        sel.type("id_point_value", "10")
        sel.type("id_point_range_start", "15")
        sel.type("id_point_range_end", "20")
        sel.type("id_textpromptquestion_set-0-question", "Is this a test?")
        sel.type("id_textpromptquestion_set-0-answer", "It is!")
        sel.click("_save")
        for i in range(60):
            try:
                if sel.is_text_present("Please specify either a point_value or a range."): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.type("id_point_value", "")
        sel.type("id_point_range_start", "15")
        sel.type("id_point_range_end", "10")
        sel.click("_save")
        for i in range(60):
            try:
                if sel.is_text_present("The start value must be less than the end value."): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.type("id_point_range_end", "")
        sel.click("_save")
        for i in range(60):
            try:
                if sel.is_text_present("Please specify a end value for the point range."): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.type("id_point_range_start", "")
        sel.click("_save")
        for i in range(60):
            try:
                if sel.is_text_present("Either a point value or a range needs to be specified."): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.type("id_point_range_start", "10")
        sel.type("id_point_range_end", "20")
        sel.click("_save")
        for i in range(60):
            try:
                if sel.is_element_present("link=Variable Point activity"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.failUnless(sel.is_text_present("The activity \"Variable Point activity\" was added successfully."))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=Variable Point activity")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Delete")
        for i in range(60):
            try:
                if sel.is_element_present("//input[@value=\"Yes, I'm sure\"]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//input[@value=\"Yes, I'm sure\"]")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("The activity \"Variable Point activity\" was deleted successfully."))
        except AssertionError, e: self.verificationErrors.append(str(e))
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
