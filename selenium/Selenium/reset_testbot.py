from selenium import selenium
import unittest, time, re

class reset_testbot(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_reset_testbot(self):
        sel = self.selenium
        sel.open("/account/login/")
        sel.type("id=id_username", "admin")
        sel.type("id=id_password", "admin")
        sel.click("css=input[type=\"submit\"]")
        sel.wait_for_page_to_load("30000")
        sel.open("/admin/")
        sel.click("link=Users")
        sel.wait_for_page_to_load("30000")
        sel.click("link=testbot")
        sel.wait_for_page_to_load("30000")
        sel.click("link=change password form")
        sel.wait_for_page_to_load("30000")
        sel.type("id=id_password1", "testbot")
	sel.type("id=id_password2", "testbot")
        sel.click("css=input.default")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Log out")
        sel.wait_for_page_to_load("30000")
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
