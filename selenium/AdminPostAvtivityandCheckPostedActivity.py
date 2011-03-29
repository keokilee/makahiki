from selenium import selenium
import unittest, time, re

class AdminPostAvtivityandCheckPostedActivity(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_admin_post_avtivityand_check_posted_activity(self):
        sel = self.selenium
        sel.open("/account/login/")
        sel.type("id_username", "gelee")
        sel.type("id_password", "changeme")
        sel.click(u"//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        sel.open("/admin")
        sel.click("//div[@id='content-main']/div[2]/table/tbody/tr[1]/th/a")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Add activity")
        sel.wait_for_page_to_load("30000")
        sel.type("id_name", "TESTING")
        sel.select("id_type", "label=Activity")
        sel.type("id_title", "TESTING")
        sel.type("id_description", "TESTING THIS TEST")
        sel.type("id_duration", "5")
        sel.click("//a[@id='calendarlink1']/img")
        sel.click("//div[@id='calendarin1']/table/tbody/tr[4]/td[4]/a")
        sel.type("id_depends_on", "True")
        sel.type("id_point_value", "5")
        sel.type("id_priority", "2")
        sel.select("id_category", "label=Get Started")
        sel.type("id_textpromptquestion_set-0-question", "testing")
        sel.type("id_textpromptquestion_set-0-answer", "t")
        sel.click("_save")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present(""))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.open("/home")
        sel.click("//div[@id='header-nav-links']/ul/li[3]/a/img")
        sel.wait_for_page_to_load("30000")
        count = sel.get_xpath_count("//table[@id='activities-grid']/tbody/tr[2]/td")
        sel.click("//tr[" + str(count) + "]/td/div/a/div/div/h3")
        sel.wait_for_page_to_load("30000")
        sel.click("link=I Did it, Click here to get points")
        sel.type("id_response", "t")
        sel.click("//input[@value='Submit to get points']")
        sel.wait_for_page_to_load("30000")
        points = sel.get_text("//div[@id='header-user-points']/h3")
        sel.open("/admin")
        sel.click("link=Activity members")
        sel.wait_for_page_to_load("30000")
        sel.click("link=TESTING")
        sel.wait_for_page_to_load("30000")
        sel.click("id_approval_status_2")
        sel.click("_save")
        sel.wait_for_page_to_load("30000")
        sel.open("/home")
        self.failIf(sel.is_text_present("//div[@id='header-user-points']/h3"))
        sel.select_window("null")
        sel.click("link=Logout")
        sel.wait_for_page_to_load("30000")
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
