from django.shortcuts import render

jobs = [
	{
		'id': 1,
		'title': 'Frontend Developer',
		'company': 'Northstar Digital',
		'location': 'Remote',
		'type': 'Full-time',
		'salary': '$85,000-$105,000',
		'description': 'Build accessible, responsive interfaces for products used by thousands of customers.',
	},
	{
		'id': 2,
		'title': 'Data Analyst',
		'company': 'Brightline Health',
		'location': 'Boston, MA',
		'type': 'Full-time',
		'salary': '$72,000-$90,000',
		'description': 'Turn healthcare data into clear insights that help teams make better decisions.',
	},
	{
		'id': 3,
		'title': 'Marketing Coordinator',
		'company': 'Fieldwork Studio',
		'location': 'New York, NY',
		'type': 'Hybrid',
		'salary': '$55,000-$68,000',
		'description': 'Coordinate campaigns, content, and events for a growing creative team.',
	},
	{
		'id': 4,
		'title': 'Customer Support Specialist',
		'company': 'Cloudwell',
		'location': 'Remote',
		'type': 'Full-time',
		'salary': '$48,000-$60,000',
		'description': 'Help customers get the most from a friendly, fast-growing software platform.',
	},
	{
		'id': 5,
		'title': 'Project Manager',
		'company': 'Civic Works Group',
		'location': 'Chicago, IL',
		'type': 'Full-time',
		'salary': '$78,000-$98,000',
		'description': 'Keep cross-functional projects on track from planning through delivery.',
	},
	{
		'id': 6,
		'title': 'Junior UX Designer',
		'company': 'Pine & Pixel',
		'location': 'Austin, TX',
		'type': 'Hybrid',
		'salary': '$62,000-$76,000',
		'description': 'Create thoughtful user flows and visual designs alongside an experienced product team.',
	},
]


def index(request):
	query = request.GET.get('q', '').strip()
	location = request.GET.get('location', '').strip()
	filtered_jobs = jobs

	if query:
		query_match = query.casefold()
		filtered_jobs = [
			job for job in filtered_jobs
			if query_match in ' '.join(map(str, job.values())).casefold()
		]

	if location:
		location_match = location.casefold()
		filtered_jobs = [
			job for job in filtered_jobs
			if location_match in job['location'].casefold()
		]

	template_data = {
		'title': 'Jobs',
		'jobs': filtered_jobs,
		'query': query,
		'location': location,
	}
	return render(request, 'jobs/index.html', {
		'template_data': template_data,
	})
