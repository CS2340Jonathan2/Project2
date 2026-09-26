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
