from selenium import selenium
import unittest, time, re

class test_profile(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_test_profile(self):
        sel = self.selenium
        sel.open("/account/login/")
        sel.type("id=id_username", "testbot")
        sel.type("id=id_password", "testbot")
        sel.click("css=input[type=\"submit\"]")
        sel.wait_for_page_to_load("30000")
        sel.click("css=a.profile > img")
        sel.wait_for_page_to_load("30000")
        sel.type("id=id_display_name", "testbot2")
        sel.click("id=profile-form-submit-button")
        sel.wait_for_page_to_load("30000")
        try: self.assertEqual("testbot2", sel.get_text("id=header-user-username"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("id=id_contact_email")
        sel.type("id=id_contact_email", "testbot@testbot.com@@")
        sel.click("id=profile-form-submit-button")
        sel.wait_for_page_to_load("30000")
        sel.click("css=ul.errorlist > li")
        try: self.failUnless(sel.is_text_present("Enter a valid e-mail address"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("id=id_contact_email")
        sel.click("id=profile-form-contact-email-fields")
        sel.type("id=id_contact_email", "testbot@testbot.com")
        sel.click("id=id_contact_text")
        sel.type("id=id_contact_text", "111-111-111144")
        sel.click("id=profile-form-submit-button")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("Phone numbers must be in XXX-XXX-XXXX format"))
        except AssertionError, e: self.verificationErrors.append(str(e))
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
