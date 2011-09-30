from selenium import selenium
import unittest, time, re

class test_quest(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_test_quest(self):
        sel = self.selenium
	sel.open("/account/login/")
        sel.type("id=id_username", "testbot")
        sel.type("id=id_password", "testbot")
        sel.click("css=input[type=\"submit\"]")
        sel.wait_for_page_to_load("30000") 
        sel.open("/activities/?ref=nav-button")
        sel.click("id=learn-about-energy")
        sel.click("css=#quest-contents > div.quest-options > form > button[type=\"submit\"]")
        sel.wait_for_page_to_load("30000")
        sel.click("css=a[title=\"Power & Energy\"] > h3")
        sel.wait_for_page_to_load("30000")
        sel.click("css=p > a > button")
        sel.click("id=id_response")
        sel.type("id=id_response", "testbot")
        sel.click("css=#activity-task-form-content-button > button")
        sel.wait_for_page_to_load("30000")
        sel.click("css=a.activities > img")
        sel.wait_for_page_to_load("30000")
        sel.click("css=a[title=\"Energy Intuition\"] > h3")
        sel.wait_for_page_to_load("30000")
        sel.click("css=p > a > button")
        sel.click("id=id_response")
        sel.type("id=id_response", "testbot")
        sel.click("css=#activity-task-form-content-button > button")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("Congratulations! You completed the 'Learn about energy' quest."))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("css=center > button")
        sel.click("id=notification-item-1")
        try: self.failUnless(sel.is_element_present("id=notification-item-1"))
        except AssertionError, e: self.verificationErrors.append(str(e))
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
