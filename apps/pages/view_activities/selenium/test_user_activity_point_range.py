from django.test import TestCase
from noseselenium.cases import SeleniumTestCaseMixin
import time, re

class test_user_activity_point_range(TestCase, SeleniumTestCaseMixin):
    selenium_test = True
    selenium_fixtures = ["base_data.json", "user_data.json"]
    
    def setUp(self):
        self.verificationErrors = []
    
    def test_test_user_activity_point_range(self):
        sel = self.selenium
        sel.open("/account/login/")
        sel.type("id_username", "admin")
        sel.type("id_password", "changeme")
        sel.click("//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
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
        for i in range(60):
            try:
                if sel.is_element_present("id_title"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.type("id_title", "Variable Point Activity")
        sel.type("id_description", "You get a range of points!")
        sel.type("id_duration", "20")
        sel.type("id_expire_date", "2010-12-31")
        sel.type("id_point_range_start", "10")
        sel.type("id_point_range_end", "20")
        sel.type("id_textpromptquestion_set-0-question", "Is this a variable point activity?")
        sel.type("id_textpromptquestion_set-0-answer", "Yes!")
        sel.click("_save")
        for i in range(60):
            try:
                if sel.is_text_present("The activity \"Variable Point Activity\" was added successfully."): break
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
        sel.open("/account/login/")
        sel.type("id_username", "user")
        sel.type("id_password", "changeme")
        sel.click("//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        sel.click("link=My Cup")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("link=Activities"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Activities")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("10-20"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("//div[@id='available_items']/div[2]/table/tbody/tr[18]/td[3]/a/span[2]")
        sel.wait_for_page_to_load("30000")
        sel.type("id_response", "Yes")
        sel.type("id_comment", "Neato!")
        sel.click("//input[@value='Submit']")
        for i in range(60):
            try:
                if sel.is_text_present("Your request has been submitted!"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.open("/account/login/")
        sel.type("id_username", "admin")
        sel.type("id_password", "changeme")
        sel.click("//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Admin")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("link=Activity members"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Activity members")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Variable Point Activity")
        for i in range(60):
            try:
                if sel.is_element_present("id_points_awarded"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("id_approval_status_2")
        sel.type("id_points_awarded", "15")
        sel.click("_save")
        for i in range(60):
            try:
                if sel.is_text_present("The activity member \"Variable Point Activity : user\" was changed successfully."): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.open("/account/login/")
        sel.type("id_username", "user")
        sel.type("id_password", "changeme")
        sel.click("//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        sel.click("link=My Cup")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_text_present("Points: 15"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.open("/account/login/")
        sel.type("id_username", "admin")
        sel.type("id_password", "changeme")
        sel.click("//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        sel.click("//div[@id='tabhead']/div/ul[2]/li/a/span")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("link=Activity members"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Activity members")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("link=Variable Point Activity"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Variable Point Activity")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("link=Delete"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Delete")
        sel.wait_for_page_to_load("30000")
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
                if sel.is_text_present("The activity member \"Variable Point Activity : user\" was deleted successfully."): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Activities")
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
                if sel.is_element_present("link=Variable Point Activity"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Variable Point Activity")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("link=Delete"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Delete")
        sel.wait_for_page_to_load("30000")
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
                if sel.is_text_present("The activity \"Variable Point Activity\" was deleted successfully."): break
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
