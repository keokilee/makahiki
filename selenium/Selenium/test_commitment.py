from selenium import selenium
import unittest, time, re

class test_commitment(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_test_commitment(self):
        sel = self.selenium
	sel.open("/account/login/")
        sel.type("id=id_username", "testbot")
        sel.type("id=id_password", "testbot")
        sel.click("css=input[type=\"submit\"]")
        sel.wait_for_page_to_load("30000")
        sel.click("id=home-activities-icon")
        sel.wait_for_page_to_load("30000")
        sel.click("css=a[title=\"Turn off vampires\"] > h3")
        sel.wait_for_page_to_load("30000")
        sel.click("//div[@id='activity-task-details-content']/center[3]/a/button")
        sel.wait_for_page_to_load("30000")
        sel.click("id=round-energy-value")
        self.assertEqual("27", sel.get_text("css=#header-user-overall-rank4 > #header-user-points > h3"))
        sel.open("/admin/")
        sel.click("link=Commitment members")
        sel.wait_for_page_to_load("30000")
        sel.click("link=I will turn off vampire loads using a power strip : testbot")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Today")
        sel.click("name=_save")
        sel.wait_for_page_to_load("30000")
        sel.open("/home/")
        sel.click("id=home-activities-icon")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Turn off vampires")
        sel.wait_for_page_to_load("30000")
        sel.click("css=p > a > button")
        sel.click("css=#activity-task-form-content-button > button")
        sel.wait_for_page_to_load("30000")
        self.assertEqual("32", sel.get_text("css=#header-user-overall-rank4 > #header-user-points > h3"))
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
