from selenium import selenium
import unittest, time, re

class add_remove_raffle(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_add_remove_raffle(self):
        sel = self.selenium
        sel.open("/account/login/")
        sel.type("id=id_username", "testbot")
        sel.type("id=id_password", "testbot")
        sel.click("css=input[type=\"submit\"]")

        sel.wait_for_page_to_load("30000")
        sel.click("id=home-activities-icon")
        sel.wait_for_page_to_load("30000")
        sel.click("css=a.prizes > img")
        sel.wait_for_page_to_load("30000")
        sel.click("link=+1")
        sel.wait_for_page_to_load("30000")
        self.assertEqual("1", sel.get_text("css=td.number.user-tickets"))
        sel.click("link=-1")
        sel.wait_for_page_to_load("30000")
        self.assertEqual("0", sel.get_text("css=td.number.user-tickets"))
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
