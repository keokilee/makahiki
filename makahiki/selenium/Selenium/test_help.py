from selenium import selenium
import unittest, time, re

class test_help(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_help(self):
        sel = self.selenium
        sel.open("/account/login/")
        sel.type("id=id_username", "testbot")
        sel.type("id=id_password", "testbot")
        sel.click("css=input[type=\"submit\"]")
        sel.wait_for_page_to_load("30000")
        sel.click("id=home-activities-icon")
        sel.wait_for_page_to_load("30000")
        sel.click("css=a.help > img")
        sel.wait_for_page_to_load("30000")
        sel.click("link=exact:How do you figure out the baseline?")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Back to help page")
        sel.wait_for_page_to_load("30000")
        sel.click("link=exact:What is plug load?")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Back to help page")
        sel.wait_for_page_to_load("30000")
        sel.click("link=exact:Can I collaborate with people on other lounges?")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Back to help page")
        sel.wait_for_page_to_load("30000")
        sel.click("link=exact:How do I contact you with questions?")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Back to help page")
        sel.wait_for_page_to_load("30000")
        sel.click("link=exact:How does the raffle work?")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Back to help page")
        sel.wait_for_page_to_load("30000")
        sel.type("id=help_question", "testbot is testing")
        sel.click("//input[@value='Send']")
        sel.click("css=#feedback-success > button")
        sel.click("css=div.container-bottom")
        sel.click("link=In the Event of Ties")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Back to help page")
        sel.wait_for_page_to_load("30000")
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
