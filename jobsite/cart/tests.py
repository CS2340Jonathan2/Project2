from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from jobs.models import Job
from .models import Application, JobCartItem

User = get_user_model()


class CartTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='lola',
            password='testpass123'
        )

        self.job = Job.objects.create(
            title='Product Intern',
            description='Internship role',
            skills='Python Communication',
            preferred_education='College student',
            company_name='Example Company',
            location='Atlanta',
            salary_min=20,
            salary_max=30,
            is_remote=True,
            visa_sponsorship=True,
            latitude=33.7490,
            longitude=-84.3880,
        )

        self.client.login(
            username='lola',
            password='testpass123'
        )

    def test_add_job_to_cart(self):
        response = self.client.post(
            reverse('cart:add_to_cart', args=[self.job.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            JobCartItem.objects.filter(
                user=self.user,
                job=self.job
            ).exists()
        )

    def test_cart_list(self):
        JobCartItem.objects.create(
            user=self.user,
            job=self.job
        )

        response = self.client.get(
            reverse('cart:cart_list')
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(
            response.json()['jobs'][0]['title'],
            'Product Intern'
        )

    def test_remove_job_from_cart(self):
        JobCartItem.objects.create(
            user=self.user,
            job=self.job
        )

        response = self.client.post(
            reverse('cart:remove_from_cart', args=[self.job.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            JobCartItem.objects.filter(
                user=self.user,
                job=self.job
            ).exists()
        )

    def test_apply_to_job(self):
        response = self.client.post(
            reverse('cart:apply_to_job', args=[self.job.id]),
            {'tailored_note': 'I am interested in this role.'}
        )

        self.assertEqual(response.status_code, 201)

        application = Application.objects.get(
            user=self.user,
            job=self.job
        )

        self.assertEqual(application.status, 'applied')
        self.assertEqual(
            application.tailored_note,
            'I am interested in this role.'
        )

    def test_duplicate_application_rejected(self):
        Application.objects.create(
            user=self.user,
            job=self.job
        )

        response = self.client.post(
            reverse('cart:apply_to_job', args=[self.job.id])
        )

        self.assertEqual(response.status_code, 400)

    def test_application_list(self):
        Application.objects.create(
            user=self.user,
            job=self.job,
            status='interview'
        )

        response = self.client.get(
            reverse('cart:application_list')
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(
            response.json()['applications'][0]['status'],
            'interview'
        )