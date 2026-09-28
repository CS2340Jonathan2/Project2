from django.test import TestCase
from django.urls import reverse


class CartViewTests(TestCase):
    def test_cart_page_renders_sample_jobs_and_controls(self):
        response = self.client.get(reverse('cart.index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Software Engineer Intern')
        self.assertContains(response, 'compareBarBtn')
        self.assertContains(response, 'Add a job to your cart')

    def test_confirmation_preview_shows_sample_pending_applications(self):
        response = self.client.get(reverse('cart.confirm'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Frontend Developer')
        self.assertContains(response, 'Brightline Health')
        self.assertContains(response, '2 submitted')
        self.assertContains(response, 'View all your applications')

    def test_add_route_saves_job_to_session(self):
        response = self.client.get(reverse('cart.add', kwargs={'id': 1}))

        self.assertRedirects(response, reverse('cart.index'))
        self.assertEqual(self.client.session['cart_jobs'][0]['title'], 'Frontend Developer')

    def test_unknown_job_does_not_create_cart_entry(self):
        response = self.client.get(reverse('cart.add', kwargs={'id': 999}))

        self.assertRedirects(response, reverse('cart.index'))
        self.assertNotIn('cart_jobs', self.client.session)
