from selenium import selenium
import unittest, time, re

class test_goals(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://change-this-to-the-site-you-are-testing/")
        self.selenium.start()
    
    def test_test_goals(self):
        sel = self.selenium
        sel.open("/account/login/")
        for i in range(60):
            try:
                if sel.is_element_present(u"//input[@value='Log in »']"): break
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
        sel.click("//div[@id='tabhead']/div/ul[2]/li[1]/a/span")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("link=Goals"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Goals")
        for i in range(60):
            try:
                if sel.is_element_present("link=Add goal"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Add goal")
        for i in range(60):
            try:
                if sel.is_element_present("id_title"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.type("id_title", "A test goal")
        sel.type("id_description", "Go testing!")
        sel.type("id_point_value", "10")
        sel.click("_save")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_text_present("The goal \"A test goal\" was added successfully."): break
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
                if sel.is_element_present("link=Goals"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Goals")
        try: self.failUnless(sel.is_element_present("//div[@id='available_items']/div[2]/table/tbody/tr[5]/td[1]/div[1]/a/div[2]"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("//div[@id='available_items']/div[2]/table/tbody/tr[5]/td[3]/form/a/span[2]")
        for i in range(60):
            try:
                if sel.is_text_present("Your floor is now participating in the goal \"A test goal\""): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//div[@id='goals']/div[2]/table/tbody/tr[2]/td[3]/form/a/span[2]")
        self.failUnless(re.search(r"^Are you sure you wish to remove this goal[\s\S]$", sel.get_confirmation()))
        for i in range(60):
            try:
                if sel.is_text_present("Your floor's participation in \"A test goal\" has been removed"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Goals")
        for i in range(60):
            try:
                if sel.is_element_present("//div[@id='available_items']/div[2]/table/tbody/tr[5]/td[3]/form/a"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//div[@id='available_items']/div[2]/table/tbody/tr[5]/td[3]/form/a")
        for i in range(60):
            try:
                if sel.is_element_present("//div[@id='goals']/div[2]/table/tbody/tr[2]/td[3]/a/span[2]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//div[@id='goals']/div[2]/table/tbody/tr[2]/td[3]/a/span[2]")
        for i in range(60):
            try:
                if sel.is_element_present("id_comment"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.type("id_comment", "Hi admins!")
        sel.click("//input[@value='Submit']")
        for i in range(60):
            try:
                if sel.is_text_present("Your request has been submitted!"): break
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
        sel.type("id_username", "admin")
        sel.type("id_password", "changeme")
        sel.click(u"//input[@value='Log in »']")
        for i in range(60):
            try:
                if sel.is_element_present("//div[@id='tabhead']/div/ul[2]/li[1]/a/span"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Admin")
        for i in range(60):
            try:
                if sel.is_element_present("link=Goal members"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Goal members")
        for i in range(60):
            try:
                if sel.is_element_present("link=A test goal"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=A test goal")
        for i in range(60):
            try:
                if sel.is_element_present("id_admin_comment"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("id_approval_status_2")
        sel.click("_save")
        for i in range(60):
            try:
                if sel.is_text_present("The goal member \"A test goal : Hale Wainani Floor 3-4\" was changed successfully."): break
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
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("//li[@id='user_tab']/a/span"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("//li[@id='user_tab']/a/span")
        for i in range(60):
            try:
                if sel.is_text_present("Your floor is not participating in any goals."): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Goals")
        sel.wait_for_page_to_load("30000")
        for i in range(60):
            try:
                if sel.is_element_present("//div[@id='completed_items']/div[2]/ul/li/div[1]/a/div[2]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=My Floor")
        for i in range(60):
            try:
                if sel.is_text_present("user 's goal \"A test goal\" has been completed! Everyone on the floor received 10 points."): break
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
        sel.type("id_username", "admin")
        sel.type("id_password", "changeme")
        sel.click(u"//input[@value='Log in »']")
        for i in range(60):
            try:
                if sel.is_element_present("link=Admin"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Admin")
        for i in range(60):
            try:
                if sel.is_element_present("link=Goal members"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Goal members")
        for i in range(60):
            try:
                if sel.is_element_present("link=A test goal"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=A test goal")
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
                if sel.is_text_present("The goal member \"A test goal : Hale Wainani Floor 3-4\" was deleted successfully."): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=Log out")
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
