from selenium import selenium
import unittest, time, re

class GoLowPostToWall(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_go_low_post_to_wall(self):
        sel = self.selenium
        sel.open("/account/login/")
        sel.type("id_username", "gelee")
        sel.type("id_password", "changeme")
        sel.click(u"//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        sel.click("home-energy-icon")
        sel.wait_for_page_to_load("30000")
        sel.type("energy-status-posts-button", "What up bro!!!")
        sel.click("//button[@type='button']")
        try: self.failUnless(sel.is_text_present("energy-status-posts-table-list"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=Logout")
        sel.wait_for_page_to_load("30000")
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
