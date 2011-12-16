from selenium import selenium
import unittest, time, re

class main_buttons(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_main_buttons(self):
        sel = self.selenium
        sel.open("/account/login/")
        sel.type("id_username", "gelee")
        sel.type("id_password", "changeme")
        sel.click(u"//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        sel.click("home-energy-icon")
        sel.wait_for_page_to_load("30000")
        sel.click("//div[@id='header-nav-links']/ul/li[1]/a/img")
        sel.wait_for_page_to_load("30000")
        sel.click("home-activities-icon")
        sel.wait_for_page_to_load("30000")
        sel.click("//div[@id='header-nav-links']/ul/li[1]/a/img")
        sel.wait_for_page_to_load("30000")
        sel.click("home-news-icon")
        sel.wait_for_page_to_load("30000")
        sel.click("//div[@id='header-nav-links']/ul/li[1]/a/img")
        sel.wait_for_page_to_load("30000")
        sel.click("home-prizes-icon")
        sel.wait_for_page_to_load("30000")
        sel.click("//div[@id='header-nav-links']/ul/li[1]/a/img")
        sel.wait_for_page_to_load("30000")
        sel.click("home-help-icon")
        sel.wait_for_page_to_load("30000")
        sel.click("//div[@id='header-nav-links']/ul/li[1]/a/img")
        sel.wait_for_page_to_load("30000")
        sel.click("//div[@id='home-profile']/a/img")
        sel.wait_for_page_to_load("30000")
        sel.click("//div[@id='header-nav-links']/ul/li[1]/a/img")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Logout")
        sel.wait_for_page_to_load("30000")
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
