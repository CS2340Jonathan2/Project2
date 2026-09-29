from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'headline', 'skills', 'education', 'experience', 'links',
            'commute_radius',
            'show_email', 'show_experience', 'is_visible_to_recruiters',
        ]
        labels = {
            'commute_radius': 'Preferred commute radius (miles)',
            'show_email': 'Show my email on my profile',
            'show_experience': 'Show my experience on my profile',
            'is_visible_to_recruiters': 'Let recruiters find my profile',
        }
        widgets = {
            'education': forms.Textarea(attrs={'rows': 3}),
            'experience': forms.Textarea(attrs={'rows': 5}),
            'links': forms.Textarea(attrs={'rows': 3}),
            'skills': forms.TextInput(),
        }

    def clean_links(self):
        # Only allow http(s) links so nothing like javascript: ends up in an href
        links = self.cleaned_data['links']
        for line in links.splitlines():
            line = line.strip()
            if line and not line.startswith(('http://', 'https://')):
                raise forms.ValidationError(f'"{line}" must start with http:// or https://')
        return links

    def clean_commute_radius(self):
        radius = self.cleaned_data['commute_radius']
        if radius < 1 or radius > 500:
            raise forms.ValidationError('Choose a radius between 1 and 500 miles.')
        return radius
