from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from jobs.models import Job

from .models import Application, JobCartItem


@login_required
@require_GET
def cart_list(request):
    items = JobCartItem.objects.filter(user=request.user).select_related('job')

    results = [
        {
            'id': item.id,
            'job_id': item.job.id,
            'title': item.job.title,
            'company_name': item.job.company_name,
            'location': item.job.location,
            'is_remote': item.job.is_remote,
            'saved_at': item.saved_at,
        }
        for item in items
    ]

    return JsonResponse({
        'count': len(results),
        'jobs': results,
    })


@login_required
@require_POST
def add_to_cart(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    item, created = JobCartItem.objects.get_or_create(
        user=request.user,
        job=job,
    )

    return JsonResponse({
        'message': 'Job saved',
        'created': created,
        'job_id': job.id,
    })


@login_required
@require_POST
def remove_from_cart(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    deleted, _ = JobCartItem.objects.filter(
        user=request.user,
        job=job,
    ).delete()

    return JsonResponse({
        'message': 'Job removed',
        'removed': deleted > 0,
    })


@login_required
@require_POST
def apply_to_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    tailored_note = request.POST.get('tailored_note', '')

    application, created = Application.objects.get_or_create(
        user=request.user,
        job=job,
        defaults={
            'tailored_note': tailored_note,
            'status': 'applied',
        }
    )

    if not created:
        return JsonResponse(
            {'error': 'You have already applied to this job'},
            status=400
        )

    JobCartItem.objects.filter(
        user=request.user,
        job=job,
    ).delete()

    return JsonResponse({
        'message': 'Application submitted',
        'application_id': application.id,
        'job_id': job.id,
        'status': application.status,
        'tailored_note': application.tailored_note,
    }, status=201)


@login_required
@require_GET
def application_list(request):
    applications = Application.objects.filter(
        user=request.user
    ).select_related('job')

    results = [
        {
            'id': application.id,
            'job_id': application.job.id,
            'title': application.job.title,
            'company_name': application.job.company_name,
            'status': application.status,
            'tailored_note': application.tailored_note,
            'applied_at': application.applied_at,
            'updated_at': application.updated_at,
        }
        for application in applications
    ]

    return JsonResponse({
        'count': len(results),
        'applications': results,
    })