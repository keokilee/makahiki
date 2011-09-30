from selenium import selenium
import unittest, time, re

class test_golow(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_test_golow(self):
        sel = self.selenium
	sel.open("/account/login/")
        sel.type("id=id_username", "testbot")
        sel.type("id=id_password", "testbot")
        sel.click("css=input[type=\"submit\"]")
        sel.wait_for_page_to_load("30000") 
        sel.open("/energy/?ref=nav-button")
        sel.click("css=a.energy > img")
        sel.wait_for_page_to_load("30000")
	time.sleep(5)
        try: self.failUnless(sel.is_element_present("css=img.goog-serverchart-image"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_element_present("//div[@id='EnergyGoalGame-visualization']/table/tbody/tr/td[2]/img"))
        except AssertionError, e: self.verificationErrors.append(str(e))
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
