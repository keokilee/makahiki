from selenium import selenium
import unittest, time, re

class test_canopy_post(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_test_canopy_post(self):
        sel = self.selenium
	sel.open("/account/login/")
        sel.type("id=id_username", "testbot")
        sel.type("id=id_password", "testbot")
        sel.click("css=input[type=\"submit\"]")
        sel.wait_for_page_to_load("30000") 
        sel.open("/canopy/")
        sel.click("id=id_post")
	sel.key_down("id=id_post", "a")
        sel.key_press("id=id_post", "a")
        sel.key_up("id=id_post", "a")
        sel.type("id=id_post", "testbot1")
        sel.click("id=wall-post-submit")
        sel.click("css=div.news-text > p")
        try: self.failUnless(sel.is_text_present("testbot1"))
        except AssertionError, e: self.verificationErrors.append(str(e))
	time.sleep(3)
        sel.click("id=id_post")
	sel.key_down("id=id_post", "a")
        sel.key_press("id=id_post", "a")
        sel.key_up("id=id_post", "a")
        sel.type("id=id_post", "testbot2")
        sel.click("id=wall-post-submit")
        sel.click("css=div.news-text > p")
        try: self.failUnless(sel.is_text_present("testbot2"))
        except AssertionError, e: self.verificationErrors.append(str(e))
	
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
