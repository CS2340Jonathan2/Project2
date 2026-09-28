from django.shortcuts import redirect, render

from jobs.views import jobs as available_jobs


sample_cart_jobs = [
    {
        'id': '1',
        'title': 'Software Engineer Intern',
        'company': 'Tech Company',
        'location': 'Atlanta, GA',
        'salary': '$40 - $50 / hr',
        'salaryNum': 45,
        'workType': 'On-site',
        'skills': ['Python', 'React', 'Git', 'Data Structures'],
        'desc': 'Collaborate with engineers to build user-facing features, resolve bugs, and learn clean code practices.',
        'addedDate': 3,
    },
    {
        'id': '2',
        'title': 'Product Operations Co-op',
        'company': 'Harbor Health',
        'location': 'Hybrid',
        'salary': '$35 - $42 / hr',
        'salaryNum': 38.5,
        'workType': 'Hybrid',
        'skills': ['SQL', 'Tableau', 'Agile', 'Jira'],
        'desc': 'Support product teams by analyzing platform data, improving workflows, and organizing user feedback.',
        'addedDate': 2,
    },
    {
        'id': '3',
        'title': 'Data Analyst Intern',
        'company': 'CivicWorks',
        'location': 'Atlanta, GA',
        'salary': '$30 - $38 / hr',
        'salaryNum': 34,
        'workType': 'On-site',
        'skills': ['Excel', 'SQL', 'Python', 'PowerBI'],
        'desc': 'Transform raw data into useful dashboards and share key insights with product leads.',
        'addedDate': 1,
    },
]


def index(request):
    cart_items = request.session.get('cart_jobs')
    if cart_items is None:
        cart_items = sample_cart_jobs

    return render(request, 'cart/index.html', {
        'cart_jobs': cart_items,
    })


def confirm(request):
    applications = [
        {
            'id': 1,
            'job': {'title': 'Frontend Developer', 'company_name': 'Northstar Digital'},
            'tailored_message': 'I am excited to bring my experience building accessible web interfaces to your team.',
            'status': 'Pending',
            'status_url': '#application-status-1',
        },
        {
            'id': 2,
            'job': {'title': 'Data Analyst', 'company_name': 'Brightline Health'},
            'tailored_message': 'My background in data analysis and communicating insights makes this role a strong fit.',
            'status': 'Pending',
            'status_url': '#application-status-2',
        },
    ]
    return render(request, 'cart/confirm.html', {
        'applications': applications,
        'applications_url': '#all-applications',
    })


def add(request, id):
    job = next((item for item in available_jobs if item['id'] == id), None)
    if job is not None:
        cart_items = request.session.get('cart_jobs', [])
        existing_ids = {str(item['id']) for item in cart_items}
        job_id = str(job['id'])
        if job_id not in existing_ids:
            cart_items.append({
                'id': job_id,
                'title': job['title'],
                'company': job['company'],
                'location': job['location'],
                'salary': job['salary'],
                'salaryNum': 0,
                'workType': job['type'],
                'skills': [],
                'desc': job['description'],
                'addedDate': 0,
            })
            request.session['cart_jobs'] = cart_items
    return redirect('cart.index')
