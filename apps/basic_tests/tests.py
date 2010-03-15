import os

# Attempt to bootstrap the Windmill tests.
try:
  from windmill.authoring import djangotest 
  
  class TestProjectWindmillTest(djangotest.WindmillDjangoUnitTest): 
      test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'windmilltests')
      browser = 'firefox'
      
except ImportError:
  print "Skipping Windmill tests because it is not installed."
  
