from selenium import selenium
import unittest, time, re

class test_news(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_test_news(self):
        sel = self.selenium
	sel.open("/account/login/")
        sel.type("id=id_username", "testbot")
        sel.type("id=id_password", "testbot")
        sel.click("css=input[type=\"submit\"]")
        sel.wait_for_page_to_load("30000") 
        sel.click("css=a.news > img")
        sel.wait_for_page_to_load("30000") 
	time.sleep(4)
	sel.click("id=id_post") 
        sel.key_down("id=id_post", "a")
        sel.key_press("id=id_post", "a")
        sel.key_up("id=id_post", "a")
        sel.type("id=id_post", "testpost") 
        sel.click("id=wall-post-submit") 
	time.sleep(4)
        try: self.failUnless(sel.is_text_present("testpost"))
        except AssertionError, e: 
	  self.verificationErrors.append(str(e)) 
        sel.key_down("id=id_post", "a")
        sel.key_press("id=id_post", "a")
        sel.key_up("id=id_post", "a")
        sel.type("id=id_post", "testpost2")
        sel.click("id=wall-post-submit") 
	time.sleep(4)
        try: self.failUnless(sel.is_text_present("testpost2"))
        except AssertionError, e: 
          self.verificationErrors.append(str(e))
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
