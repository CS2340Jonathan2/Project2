from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from jobs.models import Job

from .models import Application, JobCartItem


@login_required
@require_GET
def cart_list(request):
    items = JobCartItem.objects.filter(user=request.user).select_related('job')
    return render(request, 'cart/cart.html', {'items': items})


@login_required
@require_POST
def add_to_cart(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    _, created = JobCartItem.objects.get_or_create(user=request.user, job=job)
    if created:
        messages.success(request, f'"{job.title}" added to your saved jobs.')
    else:
        messages.info(request, f'"{job.title}" is already in your saved jobs.')
    return redirect('cart:cart_list')


@login_required
@require_POST
def remove_from_cart(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    JobCartItem.objects.filter(user=request.user, job=job).delete()
    messages.success(request, f'"{job.title}" removed from your saved jobs.')
    return redirect('cart:cart_list')


@login_required
@require_POST
def apply_to_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    tailored_note = request.POST.get('tailored_note', '')

    application, created = Application.objects.get_or_create(
        user=request.user,
        job=job,
        defaults={'tailored_note': tailored_note, 'status': 'applied'},
    )

    if not created:
        messages.error(request, f'You have already applied to "{job.title}".')
        return redirect('cart:cart_list')

    JobCartItem.objects.filter(user=request.user, job=job).delete()
    messages.success(request, f'Application submitted for "{job.title}".')
    return redirect('cart:application_list')


@login_required
@require_GET
def application_list(request):
    applications = Application.objects.filter(
        user=request.user
    ).select_related('job').order_by('-applied_at')
    return render(request, 'cart/applications.html', {'applications': applications})
