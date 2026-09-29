from django.db import models

# Create your models here.
class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    skills = models.TextField(blank=True)
    preferred_education = models.CharField(max_length=200, blank=True)

    company_name = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200)

    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)

    is_remote = models.BooleanField(default=False)
    visa_sponsorship = models.BooleanField(default=False)

    latitude = models.FloatField()
    longitude = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
