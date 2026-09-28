from django.test import TestCase


class SignupPageTests(TestCase):
	def test_signup_page_renders_shared_layout_and_form(self):
		response = self.client.get('/accounts/signup')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Create your account')
		self.assertContains(response, 'signup-email')
		self.assertContains(response, 'Job Board')
