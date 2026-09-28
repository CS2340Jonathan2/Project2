from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from profiles.models import Profile

from .geo import haversine_miles
from .models import Job

def job_list(request):
    jobs = Job.objects.all()

    title = request.GET.get('title')
    skills = request.GET.get('skills')
    location = request.GET.get('location')
    salary_min = request.GET.get('salary_min')
    salary_max = request.GET.get('salary_max')
    remote = request.GET.get('remote')
    visa = request.GET.get('visa_sponsorship')

    if title:
        jobs = jobs.filter(title__icontains=title)

    if skills:
        jobs = jobs.filter(skills__icontains=skills)

    if location:
        jobs = jobs.filter(location__icontains=location)

    if salary_min:
        jobs = jobs.filter(salary_min__gte=salary_min)

    if salary_max:
        jobs = jobs.filter(salary_max__lte=salary_max)

    if remote in ['true', 'false']:
        jobs = jobs.filter(is_remote=(remote == 'true'))

    if visa in ['true', 'false']:
        jobs = jobs.filter(visa_sponsorship=(visa == 'true'))

    results = [
        {
            'id': job.id,
            'title': job.title,
            'skills': job.skills,
            'location': job.location,
            'salary_min': job.salary_min,
            'salary_max': job.salary_max,
            'is_remote': job.is_remote,
            'visa_sponsorship': job.visa_sponsorship,
        }
        for job in jobs
    ]

    return JsonResponse({
        'count': len(results),
        'jobs': results,
    })

def job_search(request):
    jobs = Job.objects.all()

    title    = request.GET.get('title', '')
    skills   = request.GET.get('skills', '')
    location = request.GET.get('location', '')
    salary_min = request.GET.get('salary_min', '')
    salary_max = request.GET.get('salary_max', '')
    remote   = request.GET.get('remote', '')
    visa     = request.GET.get('visa_sponsorship', '')

    if title:
        jobs = jobs.filter(title__icontains=title)
    if skills:
        jobs = jobs.filter(skills__icontains=skills)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if salary_min:
        jobs = jobs.filter(salary_min__gte=salary_min)
    if salary_max:
        jobs = jobs.filter(salary_max__lte=salary_max)
    if remote in ['true', 'false']:
        jobs = jobs.filter(is_remote=(remote == 'true'))
    if visa in ['true', 'false']:
        jobs = jobs.filter(visa_sponsorship=(visa == 'true'))

    context = {
        'jobs': jobs,
        'filters': {
            'title': title, 'skills': skills, 'location': location,
            'salary_min': salary_min, 'salary_max': salary_max,
            'remote': remote, 'visa_sponsorship': visa,
        },
    }
    return render(request, 'jobs/job_search.html', context)


@login_required
def job_recommendations(request):
    try:
        profile = request.user.profile
    except Exception:
        return render(request, 'jobs/recommendations.html', {'jobs': [], 'no_profile': True})

    user_skills = profile.skill_list()
    if not user_skills:
        return render(request, 'jobs/recommendations.html', {'jobs': [], 'no_skills': True})

    scored = []
    for job in Job.objects.all():
        job_skills = [s.strip().lower() for s in job.skills.split(',') if s.strip()]
        matches = sum(1 for s in user_skills if s in job_skills)
        if matches > 0:
            scored.append((matches, job))

    scored.sort(key=lambda x: x[0], reverse=True)
    jobs = [{'job': job, 'matches': matches} for matches, job in scored]

    return render(request, 'jobs/recommendations.html', {'jobs': jobs, 'user_skills': user_skills})


def job_map(request):
    """#7 page with the interactive Leaflet map. Jobs are loaded from map_data via JS."""
    return render(request, 'jobs/job_map.html')


def _default_radius(user):
    """#9 a logged-in user's saved commute radius, or None."""
    if user.is_authenticated:
        profile = Profile.objects.filter(user=user).first()
        if profile:
            return profile.commute_radius
    return None


def map_data(request):
    """
    GET /jobs/map-data/?lat=&lng=&radius=

    - No lat/lng: every job (#7).
    - lat/lng given: only jobs within `radius` miles, closest first (#8).
      If radius is left out, the user's saved commute radius is used (#9).
    """
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    radius = request.GET.get('radius')

    try:
        lat = float(lat) if lat else None
        lng = float(lng) if lng else None
        radius = float(radius) if radius else _default_radius(request.user)
    except ValueError:
        return JsonResponse({'error': 'lat, lng and radius must be numbers'}, status=400)

    if (lat is None) != (lng is None):
        return JsonResponse({'error': 'lat and lng must be given together'}, status=400)
    if lat is not None and not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return JsonResponse({'error': 'lat/lng out of range'}, status=400)
    if radius is not None and radius <= 0:
        return JsonResponse({'error': 'radius must be positive'}, status=400)

    results = []
    for job in Job.objects.all():
        distance = None
        if lat is not None:
            distance = haversine_miles(lat, lng, job.latitude, job.longitude)
            if radius is not None and distance > radius:
                continue
        results.append({
            'id': job.id,
            'title': job.title,
            'location': job.location,
            'latitude': job.latitude,
            'longitude': job.longitude,
            'salary_min': job.salary_min,
            'salary_max': job.salary_max,
            'is_remote': job.is_remote,
            'visa_sponsorship': job.visa_sponsorship,
            'distance_miles': round(distance, 1) if distance is not None else None,
        })

    if lat is not None:
        results.sort(key=lambda j: j['distance_miles'])

    return JsonResponse({
        'center': {'lat': lat, 'lng': lng} if lat is not None else None,
        'radius_miles': radius,
        'count': len(results),
        'jobs': results,
    })
