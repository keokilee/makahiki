from selenium import selenium
import unittest, time, re

class test_user_activity_question(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://change-this-to-the-site-you-are-testing/")
        self.selenium.start()
    
    def test_test_user_activity_question(self):
        sel = self.selenium
        sel.open("/account/login/")
        sel.type("id_username", "user")
        sel.type("id_password", "changeme")
        sel.click(u"//input[@value='Log in »']")
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
                if sel.is_element_present("link=Activities"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Activities")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("//div[@id='available_items']/div[2]/table/tbody/tr[3]/td[3]/a/span[2]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//div[@id='available_items']/div[2]/table/tbody/tr[3]/td[3]/a/span[2]")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("id_response"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.type("id_response", "watt")
        sel.type("id_comment", "Hello.")
        sel.click("//input[@value='Submit']")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_text_present("Your request has been submitted!"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//div[@id='login']/a/span[2]")
        sel.wait_for_page_to_load("30000")
        sel.open("/account/login/")
        for i in range(60):
            try:
                if sel.is_element_present("id_username"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.type("id_username", "admin")
        sel.type("id_password", "changeme")
        sel.click(u"//input[@value='Log in »']")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("//div[@id='tabhead']/div/ul[2]/li[1]/a/span"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Admin")
        for i in range(60):
            try:
                if sel.is_element_present("link=Activity members"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Activity members")
        for i in range(60):
            try:
                if sel.is_element_present("link=Pending approval"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Pending approval")
        for i in range(60):
            try:
                if sel.is_element_present("link=Watch \"Be Energy Akamai!, Episode 1\""): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Watch \"Be Energy Akamai!, Episode 1\"")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("id_approval_status_2"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("id_approval_status_2")
        sel.click("_save")
        for i in range(60):
            try:
                if sel.is_element_present("link=Log out"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Log out")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("link=Log in again"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.open("/account/login/")
        for i in range(60):
            try:
                if sel.is_element_present("id_username"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.type("id_username", "user")
        sel.type("id_password", "changeme")
        sel.click(u"//input[@value='Log in »']")
        for i in range(60):
            try:
                if sel.is_element_present("//li[@id='user_tab']/a/span"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//li[@id='user_tab']/a/span")
        for i in range(60):
            try:
                if sel.is_element_present("link=Activities"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Activities")
        for i in range(60):
            try:
                if sel.is_element_present("//div[@id='completed_items']/div[2]/ul/li/div[1]/a/div[2]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=My Floor")
        for i in range(60):
            try:
                if sel.is_text_present("has been awarded 10 points for completing \"Watch \"Be Energy Akamai!, Episode 1\"\"."): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//div[@id='login']/a/span[2]")
        sel.open("/account/login/")
        for i in range(60):
            try:
                if sel.is_element_present("id_username"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.type("id_username", "admin")
        sel.type("id_password", "changeme")
        sel.click(u"//input[@value='Log in »']")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("//div[@id='tabhead']/div/ul[2]/li[1]/a/span"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Admin")
        for i in range(60):
            try:
                if sel.is_element_present("link=Activity members"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Activity members")
        for i in range(60):
            try:
                if sel.is_element_present("link=Watch \"Be Energy Akamai!, Episode 1\""): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Watch \"Be Energy Akamai!, Episode 1\"")
        for i in range(60):
            try:
                if sel.is_element_present("link=Delete"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Delete")
        for i in range(60):
            try:
                if sel.is_element_present("//input[@value=\"Yes, I'm sure\"]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//input[@value=\"Yes, I'm sure\"]")
        for i in range(60):
            try:
                if sel.is_text_present("The activity member \"Watch \"Be Energy Akamai!, Episode 1\" : user\" was deleted successfully."): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Log out")
        for i in range(60):
            try:
                if sel.is_element_present("link=Log in again"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
