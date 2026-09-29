from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class SignupTests(TestCase):
    url = reverse('home:signup')

    def test_signup_page_loads(self):
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_valid_signup_creates_user_and_logs_in(self):
        resp = self.client.post(self.url, {
            'username': 'alice',
            'password1': 'Tr0ub4dor&3',
            'password2': 'Tr0ub4dor&3',
        })
        self.assertRedirects(resp, '/')
        self.assertTrue(User.objects.filter(username='alice').exists())
        # user is logged in after signup
        resp2 = self.client.get('/')
        self.assertEqual(resp2.context['user'].username, 'alice')

    def test_already_logged_in_redirects(self):
        User.objects.create_user('bob', password='Tr0ub4dor&3')
        self.client.login(username='bob', password='Tr0ub4dor&3')
        resp = self.client.get(self.url)
        self.assertRedirects(resp, '/')

    def test_rejects_too_short_password(self):
        resp = self.client.post(self.url, {
            'username': 'carol',
            'password1': 'abc1',
            'password2': 'abc1',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username='carol').exists())
        self.assertContains(resp, 'too short')

    def test_rejects_common_password(self):
        resp = self.client.post(self.url, {
            'username': 'dave',
            'password1': 'password',
            'password2': 'password',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username='dave').exists())
        self.assertContains(resp, 'too common')

    def test_rejects_entirely_numeric_password(self):
        resp = self.client.post(self.url, {
            'username': 'eve',
            'password1': '12345678',
            'password2': '12345678',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username='eve').exists())
        self.assertContains(resp, 'entirely numeric')

    def test_rejects_mismatched_passwords(self):
        resp = self.client.post(self.url, {
            'username': 'frank',
            'password1': 'Tr0ub4dor&3',
            'password2': 'Tr0ub4dor&4',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username='frank').exists())

    def test_rejects_password_similar_to_username(self):
        resp = self.client.post(self.url, {
            'username': 'myusername',
            'password1': 'myusername1',
            'password2': 'myusername1',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username='myusername').exists())
        self.assertContains(resp, 'too similar')


class LoginTests(TestCase):
    url = reverse('login')

    def setUp(self):
        self.user = User.objects.create_user('alice', password='Tr0ub4dor&3')

    def test_login_page_loads(self):
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_valid_login_redirects_home(self):
        resp = self.client.post(self.url, {
            'username': 'alice',
            'password': 'Tr0ub4dor&3',
        })
        self.assertRedirects(resp, '/')

    def test_wrong_password_rejected(self):
        resp = self.client.post(self.url, {
            'username': 'alice',
            'password': 'wrongpassword',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.wsgi_request.user.is_authenticated)

    def test_nonexistent_user_rejected(self):
        resp = self.client.post(self.url, {
            'username': 'nobody',
            'password': 'Tr0ub4dor&3',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.wsgi_request.user.is_authenticated)

    def test_protected_pages_redirect_to_login(self):
        for url in ['/profile/', '/cart/', '/cart/applications/', '/jobs/recommendations/']:
            with self.subTest(url=url):
                resp = self.client.get(url)
                self.assertEqual(resp.status_code, 302)
                self.assertIn('/accounts/login/', resp['Location'])
