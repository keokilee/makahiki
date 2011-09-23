from selenium import selenium
import unittest, time, re

class test_navbar(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000")
        self.selenium.start()
    
    def test_test_navbar(self):
        sel = self.selenium
        sel.open("/account/login/")
        sel.type("id=id_username", "testbot")
        sel.type("id=id_password", "testbot")
        sel.click("css=input[type=\"submit\"]")
        sel.wait_for_page_to_load("30000")
        sel.click("id=home-activities-icon")
        sel.wait_for_page_to_load("30000")
        sel.click("css=a.activities > img")
        sel.wait_for_page_to_load("30000")
        try: self.assertEqual("Kukui Cup :", sel.get_title())
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("css=a.energy > img")
        sel.wait_for_page_to_load("30000")
        try: self.assertEqual("Kukui Cup :", sel.get_title())
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("css=a.news > img")
        sel.wait_for_page_to_load("30000")
        try: self.assertEqual("Kukui Cup :", sel.get_title())
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("css=a.prizes > img")
        sel.wait_for_page_to_load("30000")
        try: self.assertEqual("Kukui Cup :", sel.get_title())
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("css=a.profile > img")
        sel.wait_for_page_to_load("30000")
        try: self.assertEqual("Kukui Cup :", sel.get_title())
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("css=a.help > img")
        sel.wait_for_page_to_load("30000")
        try: self.assertEqual("Kukui Cup :", sel.get_title())
        except AssertionError, e: self.verificationErrors.append(str(e))
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
