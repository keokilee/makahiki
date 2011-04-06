import time, re
from noseselenium.cases import SeleniumTestCaseMixin
from django.test import TestCase

class test_setup_wizard(TestCase, SeleniumTestCaseMixin):
  selenium_fixtures = ["fixtures/base_floors.json", "fixtures/test_users.json"]
  def setUp(self):
    self.verificationErrors = []
      
  def test_test_setup_wizard(self):
    sel = self.selenium
    sel.open("/account/login/")
    sel.type("id_username", "user")
    sel.type("id_password", "changeme")
    sel.click("//input[@type='submit']")
    sel.wait_for_page_to_load("30000")
    for i in range(60):
        try:
            if sel.is_element_present("next"): break
        except: pass
        time.sleep(1)
    else: self.fail("time out")
    try: self.failUnless(sel.is_text_present("According to our records, your name is Maile Tanaka and you live in Ilima: Lounge A."))
    except AssertionError, e: self.verificationErrors.append(str(e))
    sel.click("next")
    for i in range(60):
        try:
            if sel.is_element_present("//button[@id='agree' and @role=\"button\"]"): break
        except: pass
        time.sleep(1)
    else: self.fail("time out")
    try: self.failUnless(sel.is_text_present("Terms and Conditions"))
    except AssertionError, e: self.verificationErrors.append(str(e))
    sel.click("//button[@id='agree' and @role='button']")
    for i in range(60):
        try:
            if sel.is_element_present("skip"): break
        except: pass
        time.sleep(1)
    else: self.fail("time out")
    sel.click("//div[@id='setup-dialog']/h2")
    try: self.failUnless(sel.is_text_present("Connect Kukui Cup to Facebook"))
    except AssertionError, e: self.verificationErrors.append(str(e))
    sel.click("skip")
    for i in range(60):
        try:
            if sel.is_element_present("next"): break
        except: pass
        time.sleep(1)
    else: self.fail("time out")
    try: self.failUnless(sel.is_text_present("Customize your Kukui Cup profile"))
    except AssertionError, e: self.verificationErrors.append(str(e))
    sel.type("id_display_name", "")
    sel.click("next")
    for i in range(60):
        try:
            if sel.is_text_present("This field is required."): break
        except: pass
        time.sleep(1)
    else: self.fail("time out")
    sel.type("id_display_name", "Maile Tanaka")
    for i in range(60):
        try:
            if sel.is_element_present("//button[@id='next' and @role=\"button\"]"): break
        except: pass
        time.sleep(1)
    else: self.fail("time out")
    sel.click("next")
    for i in range(60):
        try:
            if sel.is_text_present("Next ->\nget your points!"): break
        except: pass
        time.sleep(1)
    else: self.fail("time out")
    try: self.failUnless(sel.is_text_present("Introduction Video"))
    except AssertionError, e: self.verificationErrors.append(str(e))
    sel.click("next")
    for i in range(60):
        try:
            if sel.is_text_present("Submit My Answer ->\nalmost done"): break
        except: pass
        time.sleep(1)
    else: self.fail("time out")
    try: self.failUnless(sel.is_text_present("Verification Question"))
    except AssertionError, e: self.verificationErrors.append(str(e))
    sel.click("activity-select")
    sel.select("activity-select", "label=Sophomores")
    sel.click("//option[@value='sophomores']")
    for i in range(60):
        try:
            if sel.is_text_present("Incorrect!"): break
        except: pass
        time.sleep(1)
    else: self.fail("time out")
    sel.select("activity-select", "label=First-year students")
    sel.click("//option[@value='first-years']")
    for i in range(60):
        try:
            if sel.is_text_present("Correct!"): break
        except: pass
        time.sleep(1)
    else: self.fail("time out")
    sel.click("next")
    for i in range(60):
        try:
            if sel.is_text_present("Go home"): break
        except: pass
        time.sleep(1)
    else: self.fail("time out")
    try: self.failUnless(sel.is_text_present("Introduction Complete"))
    except AssertionError, e: self.verificationErrors.append(str(e))
    sel.click("home")
    sel.wait_for_page_to_load("30000")
    for i in range(60):
        try:
            if sel.is_element_present("link=Logout"): break
        except: pass
        time.sleep(1)
    else: self.fail("time out")
    sel.click("link=Logout")
    sel.wait_for_page_to_load("30000")

  def tearDown(self):
    self.assertEqual([], self.verificationErrors)

