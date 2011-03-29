from selenium import selenium
import unittest, time, re

class NewsPostToWall(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_news_post_to_wall(self):
        sel = self.selenium
        sel.open("/account/login/")
        sel.type("id_username", "gelee")
        sel.type("id_password", "changeme")
        sel.click(u"//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        sel.click("home-news-icon")
        sel.wait_for_page_to_load("30000")
        sel.type("id_post", "TESTING")
        sel.click("//a[@id='wall-post-submit']/span")
        try: self.failUnless(sel.is_text_present(""))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=Logout")
        sel.wait_for_page_to_load("30000")
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
