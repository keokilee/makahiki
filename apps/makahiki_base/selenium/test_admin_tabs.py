from selenium import selenium
import unittest, time, re

class test_admin_tab(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_test_admin_tab(self):
        sel = self.selenium
        sel.open("/account/login/")
        sel.type("id_username", "admin")
        sel.type("id_password", "changeme")
        sel.click(u"//input[@type='submit']")
        for i in range(60):
            try:
                if sel.is_text_present("Aloha, Admin"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.failUnless(sel.is_text_present("Admin"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=Logout")
        sel.open("/account/login/")
        sel.type("id_username", "user")
        sel.type("id_password", "changeme")
        sel.click(u"//input[@type='submit']")
        for i in range(60):
            try:
                if sel.is_text_present("Aloha, User"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.failIf(sel.is_text_present("Admin"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=Logout")
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
