import os

# Attempt to bootstrap the Windmill tests.
try:
  from windmill.authoring import djangotest 
  
  wmtests = os.path.join(os.path.dirname(os.path.abspath(__file__)),"windmilltests")
  for nm in os.listdir(wmtests):
    if nm.startswith("test") and nm.endswith(".py"):
      testnm = nm[:-3]
      class WindmillTest(djangotest.WindmillDjangoUnitTest):
        test_dir = os.path.join(wmtests,nm)
        browser = "firefox" 
      WindmillTest.__name__ = testnm
      globals()[testnm] = WindmillTest
      del WindmillTest
      
except ImportError:
  print "Skipping Windmill tests because it is not installed."
  
