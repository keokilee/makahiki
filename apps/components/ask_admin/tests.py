from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core import mail

from components.floors.models import Floor


class AskAdminFunctionalTests(TestCase):
  fixtures = ["base_floors.json"]

  def setUp(self):
    self.user = User.objects.create_user("user", "user@test.com", password="bogus")
    floor = Floor.objects.all()[0]
    profile = self.user.get_profile()
    profile.name = 'test'
    profile.floor = floor
    profile.setup_complete = True
    profile.setup_profile = True
    profile.save()

    self.client.login(username="user", password="bogus")
  
  def testAjaxPost(self):
    """
    Test that an AJAX post to ask an admin sends an email.
    """
    response = self.client.post(reverse('ask_admin_feedback'), {
        'url': 'http://localhost:8000/test/',
        'question': 'question',
    },  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
  
    self.failUnlessEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 1)
    self.assertTrue(mail.outbox[0].subject.find(self.user.get_profile().name) > 0)

