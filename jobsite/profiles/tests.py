from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Profile

User = get_user_model()


class ProfileCreateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('alice', 'alice@example.com', 'pw-12345!')
        self.client.login(username='alice', password='pw-12345!')

    def test_create_profile(self):
        resp = self.client.post(reverse('profiles:edit'), {
            'headline': 'CS student', 'skills': 'Python, SQL', 'commute_radius': 15,
            'show_experience': 'on', 'is_visible_to_recruiters': 'on',
        })
        self.assertRedirects(resp, reverse('profiles:detail', args=['alice']))
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.skill_list(), ['python', 'sql'])
        self.assertEqual(profile.commute_radius, 15)

    def test_edit_updates_same_profile(self):
        Profile.objects.create(user=self.user, headline='Old')
        self.client.post(reverse('profiles:edit'), {'headline': 'New', 'commute_radius': 10})
        self.assertEqual(Profile.objects.filter(user=self.user).count(), 1)
        self.assertEqual(Profile.objects.get(user=self.user).headline, 'New')

    def test_rejects_non_http_links(self):
        resp = self.client.post(reverse('profiles:edit'), {
            'headline': 'x', 'commute_radius': 10, 'links': 'javascript:alert(1)',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Profile.objects.exists())

    def test_requires_login(self):
        self.client.logout()
        resp = self.client.get(reverse('profiles:edit'))
        self.assertEqual(resp.status_code, 302)


class ProfilePrivacyTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('bob', 'bob@example.com', 'pw-12345!')
        self.viewer = User.objects.create_user('carol', 'carol@example.com', 'pw-12345!')
        self.profile = Profile.objects.create(
            user=self.owner, headline='Dev', experience='Secret Corp',
            show_email=False, show_experience=False, is_visible_to_recruiters=True,
        )
        self.url = reverse('profiles:detail', args=['bob'])

    def test_hidden_fields_not_shown_to_others(self):
        self.client.login(username='carol', password='pw-12345!')
        resp = self.client.get(self.url)
        self.assertNotContains(resp, 'bob@example.com')
        self.assertNotContains(resp, 'Secret Corp')

    def test_owner_sees_everything(self):
        self.client.login(username='bob', password='pw-12345!')
        resp = self.client.get(self.url)
        self.assertContains(resp, 'bob@example.com')
        self.assertContains(resp, 'Secret Corp')

    def test_shown_fields_visible_to_others(self):
        self.profile.show_email = True
        self.profile.show_experience = True
        self.profile.save()
        self.client.login(username='carol', password='pw-12345!')
        resp = self.client.get(self.url)
        self.assertContains(resp, 'bob@example.com')
        self.assertContains(resp, 'Secret Corp')

    def test_invisible_profile_is_404_for_others(self):
        self.profile.is_visible_to_recruiters = False
        self.profile.save()
        self.client.login(username='carol', password='pw-12345!')
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.client.login(username='bob', password='pw-12345!')
        self.assertEqual(self.client.get(self.url).status_code, 200)
