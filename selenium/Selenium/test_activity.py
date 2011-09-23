from selenium import selenium
import unittest, time, re

class test_activity(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_test_activity(self):
        sel = self.selenium
        sel.open("/account/login/")
        sel.type("id=id_username", "testbot")
        sel.type("id=id_password", "testbot")
        sel.click("css=input[type=\"submit\"]")
        sel.wait_for_page_to_load("30000")
        sel.click("id=home-activities-icon")
        sel.wait_for_page_to_load("30000")
        sel.click("css=a[title=\"Intro video\"] > h3")
        sel.wait_for_page_to_load("30000")
        sel.click("css=p > a > button")
        sel.click("id=id_response")
        sel.type("id=id_response", "a")
        sel.click("css=#activity-task-form-content-button > button")
        sel.wait_for_page_to_load("30000")
        sel.open("/admin/")
        sel.click("link=Activity members")
        sel.wait_for_page_to_load("30000")
        sel.click("link=exact:Activity: Watch introduction video")
        sel.wait_for_page_to_load("30000")
        sel.click("id=id_approval_status_1")
        sel.click("name=_save")
        sel.wait_for_page_to_load("30000")
        sel.open("/activities/")
        sel.click("css=#header-user-overall-rank2 > #header-user-points > h3")
        self.assertEqual("25", sel.get_text("css=#header-user-overall-rank2 > #header-user-points > h3"))
        
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
