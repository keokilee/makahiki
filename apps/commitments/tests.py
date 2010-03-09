import unittest

class CommitmentsTestCase(unittest.TestCase):
  def testBasic(self):
    foo = "Python"
    self.assertEquals(foo, "Python")
