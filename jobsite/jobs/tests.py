from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from profiles.models import Profile

from .geo import haversine_miles
from .models import Job

User = get_user_model()

GT = (33.7756, -84.3963)  # Georgia Tech


class HaversineTests(TestCase):
    def test_same_point_is_zero(self):
        self.assertAlmostEqual(haversine_miles(*GT, *GT), 0)

    def test_atlanta_to_athens(self):
        # Roughly 60 miles as the crow flies
        d = haversine_miles(33.7490, -84.3880, 33.9519, -83.3576)
        self.assertTrue(55 < d < 65, d)


class MapDataTests(TestCase):
    def setUp(self):
        self.near = Job.objects.create(title='Near', description='-', location='Midtown',
                                       latitude=33.7816, longitude=-84.3831)
        self.far = Job.objects.create(title='Far', description='-', location='Athens',
                                      latitude=33.9519, longitude=-83.3576)
        self.url = reverse('jobs:map_data')

    def titles(self, resp):
        return [j['title'] for j in resp.json()['jobs']]

    def test_all_jobs_without_location(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertCountEqual(self.titles(resp), ['Near', 'Far'])

    def test_radius_filter(self):
        resp = self.client.get(self.url, {'lat': GT[0], 'lng': GT[1], 'radius': 10})
        self.assertEqual(self.titles(resp), ['Near'])

    def test_sorted_by_distance(self):
        resp = self.client.get(self.url, {'lat': GT[0], 'lng': GT[1], 'radius': 100})
        self.assertEqual(self.titles(resp), ['Near', 'Far'])

    def test_uses_commute_radius_by_default(self):
        user = User.objects.create_user('dan', password='pw-12345!')
        Profile.objects.create(user=user, headline='x', commute_radius=5)
        self.client.login(username='dan', password='pw-12345!')
        resp = self.client.get(self.url, {'lat': GT[0], 'lng': GT[1]})
        self.assertEqual(resp.json()['radius_miles'], 5)
        self.assertEqual(self.titles(resp), ['Near'])

    def test_bad_input(self):
        self.assertEqual(self.client.get(self.url, {'lat': 'abc', 'lng': 1}).status_code, 400)
        self.assertEqual(self.client.get(self.url, {'lat': 33}).status_code, 400)
        self.assertEqual(self.client.get(self.url, {'lat': 33, 'lng': -84, 'radius': -1}).status_code, 400)

class JobFilterTests(TestCase):
    def setUp(self):
        Job.objects.create(
            title='Software Engineer',
            description='Backend role',
            skills='Python Django',
            location='Atlanta',
            salary_min=90000,
            salary_max=120000,
            is_remote=True,
            visa_sponsorship=True,
            latitude=33.7490,
            longitude=-84.3880,
        )

        Job.objects.create(
            title='Data Analyst',
            description='Analytics role',
            skills='SQL Excel',
            location='New York',
            salary_min=70000,
            salary_max=90000,
            is_remote=False,
            visa_sponsorship=False,
            latitude=40.7128,
            longitude=-74.0060,
        )

        self.url = reverse('jobs:job_list')

    def titles(self, response):
        return [job['title'] for job in response.json()['jobs']]

    def test_filter_by_title(self):
        response = self.client.get(self.url, {'title': 'software'})
        self.assertEqual(self.titles(response), ['Software Engineer'])

    def test_filter_by_skills(self):
        response = self.client.get(self.url, {'skills': 'Python'})
        self.assertEqual(self.titles(response), ['Software Engineer'])

    def test_filter_by_location(self):
        response = self.client.get(self.url, {'location': 'Atlanta'})
        self.assertEqual(self.titles(response), ['Software Engineer'])

    def test_filter_by_salary(self):
        response = self.client.get(
            self.url,
            {'salary_min': 80000, 'salary_max': 130000}
        )
        self.assertEqual(self.titles(response), ['Software Engineer'])

    def test_filter_by_remote(self):
        response = self.client.get(self.url, {'remote': 'true'})
        self.assertEqual(self.titles(response), ['Software Engineer'])

    def test_filter_by_visa_sponsorship(self):
        response = self.client.get(
            self.url,
            {'visa_sponsorship': 'true'}
        )
        self.assertEqual(self.titles(response), ['Software Engineer'])

class RecommendationsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('alice', 'alice@example.com', 'pw-12345!')
        self.client.login(username='alice', password='pw-12345!')
        self.url = reverse('jobs:recommendations')
        self.job_defaults = dict(description='desc', location='Atlanta', latitude=33.749, longitude=-84.388)

    def test_requires_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_no_profile_shows_prompt(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Create one')

    def test_no_skills_shows_prompt(self):
        Profile.objects.create(user=self.user, headline='Dev', skills='')
        resp = self.client.get(self.url)
        self.assertContains(resp, 'Add skills')

    def test_matching_jobs_returned(self):
        Profile.objects.create(user=self.user, headline='Dev', skills='Python, SQL')
        Job.objects.create(title='Backend Dev', skills='Python, Django', **self.job_defaults)
        Job.objects.create(title='DB Admin', skills='SQL, Postgres', **self.job_defaults)
        Job.objects.create(title='Designer', skills='Figma, CSS', **self.job_defaults)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Backend Dev')
        self.assertContains(resp, 'DB Admin')
        self.assertNotContains(resp, 'Designer')

    def test_ranked_by_match_count(self):
        Profile.objects.create(user=self.user, headline='Dev', skills='Python, SQL, Django')
        Job.objects.create(title='One Match', skills='Python', **self.job_defaults)
        Job.objects.create(title='Two Matches', skills='Python, SQL', **self.job_defaults)
        resp = self.client.get(self.url)
        content = resp.content.decode()
        self.assertLess(content.index('Two Matches'), content.index('One Match'))

    def test_no_matching_jobs_shows_message(self):
        Profile.objects.create(user=self.user, headline='Dev', skills='COBOL')
        Job.objects.create(title='Python Dev', skills='Python', **self.job_defaults)
        resp = self.client.get(self.url)
        self.assertContains(resp, 'No jobs matched')
