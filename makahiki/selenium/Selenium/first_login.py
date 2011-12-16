from selenium import selenium
import unittest, time, re

class first_login(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/activities/")
        self.selenium.start()
    
    def test_first_login(self): 
        sel = self.selenium
        sel.open("/account/login/")
        sel.type("id=id_username", "testbot")
        sel.type("id=id_password", "testbot")
        sel.click("css=input[type=\"submit\"]")
        sel.wait_for_page_to_load("10001")  
        sel.click("id=next")
	time.sleep(2)
        #sel.wait_for_page_to_load("10002")
        sel.click("id=agree")
        time.sleep(2)
        sel.click("id=next")
	time.sleep(2)
        sel.click("id=next")
	time.sleep(2)
        sel.click("id=next")
	time.sleep(2)
        sel.click("id=home")
        
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
