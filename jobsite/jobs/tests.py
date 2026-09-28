from django.test import TestCase


class JobListViewTests(TestCase):
	def test_lists_all_sample_jobs(self):
		response = self.client.get('/jobs/')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Frontend Developer')
		self.assertEqual(response.content.count(b'class="job-card"'), 6)

	def test_filters_jobs_by_keyword(self):
		response = self.client.get('/jobs/', {'q': 'frontend'})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Frontend Developer')
		self.assertNotContains(response, 'Data Analyst')

	def test_filters_jobs_by_location(self):
		response = self.client.get('/jobs/', {'location': 'remote'})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content.count(b'class="job-card"'), 2)

	def test_combines_keyword_and_location_filters(self):
		response = self.client.get('/jobs/', {
			'q': 'developer',
			'location': 'remote',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Frontend Developer')
		self.assertEqual(response.content.count(b'class="job-card"'), 1)

	def test_shows_empty_state_when_no_jobs_match(self):
		response = self.client.get('/jobs/', {'q': 'no matching role'})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'No jobs found.')
