from django.conf import settings
from django.db import models


class Profile(models.Model):
    # User 1 -- 0..1 Profile
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile'
    )
    headline = models.CharField(max_length=200)
    skills = models.TextField(blank=True, help_text='Comma-separated, e.g. Python, SQL, React')
    education = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    links = models.TextField(blank=True, help_text='One URL per line')

    # #9 preferred commute radius, in miles
    commute_radius = models.PositiveIntegerField(default=10)

    # #5 privacy options
    show_email = models.BooleanField(default=False)
    show_experience = models.BooleanField(default=True)
    is_visible_to_recruiters = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.username}: {self.headline}'

    def skill_list(self):
        """Skills as a clean lowercase list, used for display and #6 recommendations."""
        return [s.strip().lower() for s in self.skills.split(',') if s.strip()]

    def link_list(self):
        return [line.strip() for line in self.links.splitlines() if line.strip()]
