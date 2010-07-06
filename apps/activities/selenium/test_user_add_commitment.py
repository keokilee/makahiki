from selenium import selenium
import unittest, time, re

class test_add_commitment(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_test_add_commitment(self):
        sel = self.selenium
        sel.open("/account/login/")
        sel.type("id_username", "user")
        sel.type("id_password", "changeme")
        sel.click(u"//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("//li[@id='user_tab']/a/span"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//li[@id='user_tab']/a/span")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("link=Commitments"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Commitments")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("//div[@id='available_items']/div[2]/table/tbody/tr[2]/td[3]/form/a/span[2]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//div[@id='available_items']/div[2]/table/tbody/tr[2]/td[3]/form/a/span[2]")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_text_present("I will turn off my laptop/computer every night before going to sleep"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.failUnless(sel.is_text_present("You are now committed to \"I will turn off my laptop/computer every night before going to sleep\""))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_element_present("//div[@id='commitments']/div[2]/table/tbody/tr[2]/td[3]/form/a/span[2]"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=My Floor")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_text_present("I will turn off my laptop/computer every night before going to sleep"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.failUnless(sel.is_text_present("is participating in the commitment \"I will turn off my laptop/computer every night before going to sleep\"."))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=Commitments")
        for i in range(60):
            try:
                if sel.is_element_present("//div[@id='user_items']/div[2]/table/tbody/tr[2]/td[3]/form/a/span[2]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//div[@id='user_items']/div[2]/table/tbody/tr[2]/td[3]/form/a/span[2]")
        self.failUnless(re.search(r"^Are you sure you wish to remove this commitment[\s\S]$", sel.get_confirmation()))
        for i in range(60):
            try:
                if sel.is_text_present("You are not participating in any commitments."): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.failUnless(sel.is_text_present("Commitment \"I will turn off my laptop/computer every night before going to sleep\" has been removed."))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=My Floor")
        for i in range(60):
            try:
                if sel.is_text_present("I will turn off my laptop/computer every night before going to sleep"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.failUnless(sel.is_text_present("is no longer participating in \"I will turn off my laptop/computer every night before going to sleep\"."))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=Logout")
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([''], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
