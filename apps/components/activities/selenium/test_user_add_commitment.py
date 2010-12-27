from django.test import TestCase
from noseselenium.cases import SeleniumTestCaseMixin
import re, time

class test_user_add_commitment(TestCase, SeleniumTestCaseMixin):
    selenium_test = True
    selenium_fixtures = ["base_data.json", "user_data.json"]
    
    def setUp(self):
        self.verificationErrors = []
    
    def test_user_add_commitment(self):
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
                if sel.is_element_present("link=Commitments"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Commitments")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("//div[@id='available_items']/div[2]/table/tbody/tr[2]/td[3]/form/a/span[1]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//div[@id='available_items']/div[2]/table/tbody/tr[2]/td[3]/form/a/span[2]")
        for i in range(60):
            try:
                if sel.is_element_present("//div[@id='commitments']/div[2]/table/tbody/tr[2]/td[3]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.failUnless(sel.is_element_present("message_1"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_element_present("//div[@id='commitments']/div[2]/table/tbody/tr[2]/td[3]/form/a/span[2]"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("//div[@id='commitments']/div[2]/table/tbody/tr[2]/td[3]/form/a/span[1]")
        self.failUnless(re.search(r"^Are you sure you wish to remove this commitment[\s\S]$", sel.get_confirmation()))
        for i in range(60):
            try:
                if sel.is_text_present("You are not participating in any commitments."): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//div[@id='login']/a/span")
    
    def tearDown(self):
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
