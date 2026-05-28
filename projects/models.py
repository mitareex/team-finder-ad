from django.db import models
from django.conf import settings


STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed')
    ]
NAME_MAX_LENGTH = 200
STATUS_MAX_LENGTH = 6
DEFAULT_STATUS = 'open'


class Project(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    description = models.TextField(blank=True, null=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True, null=True)
    status = models.CharField(
        max_length=STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default=DEFAULT_STATUS
    )

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='participated_projects'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
