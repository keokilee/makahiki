from selenium import selenium
import unittest, time, re

class Login_Logout(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_login__logout(self):
        sel = self.selenium
#
        sel.open("/account/login/")
        sel.type("id_username", "testbot")
        sel.type("id_password", "tesbot")
        sel.click(u"//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
#
        sel.click("link=Logout")
        sel.wait_for_page_to_load("30000")
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
