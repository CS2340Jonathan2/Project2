from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileForm
from .models import Profile


@login_required
def profile_edit(request):
    """#1 create a profile, or edit it if one exists. Also where #5 privacy and #9 radius are set."""
    profile = Profile.objects.filter(user=request.user).first()
    creating = profile is None

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Profile created.' if creating else 'Profile updated.')
            return redirect('profiles:detail', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profiles/profile_form.html', {'form': form, 'creating': creating})


def profile_detail(request, username):
    """#5 privacy-aware profile page. The owner (and staff) always see everything."""
    user = get_object_or_404(get_user_model(), username=username)
    profile = get_object_or_404(Profile, user=user)

    is_owner = request.user == user
    full_access = is_owner or request.user.is_staff

    if not full_access and not profile.is_visible_to_recruiters:
        raise Http404('Profile not found')

    context = {
        'profile': profile,
        'is_owner': is_owner,
        'show_email': full_access or profile.show_email,
        'show_experience': full_access or profile.show_experience,
    }
    return render(request, 'profiles/profile_detail.html', context)
