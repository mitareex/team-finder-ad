from django.db import models
from django.conf import settings
from django.urls import reverse

from .constants import (
    OPEN_STATUS,
    STATUS_CHOICES,
    NAME_MAX_LENGTH,
    STATUS_MAX_LENGTH
)


class Project(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH, verbose_name='Название проекта')
    description = models.TextField(blank=True, null=True, verbose_name='Описание проекта')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Автор'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    github_url = models.URLField(blank=True, null=True, verbose_name='Ссылка на GitHub')
    status = models.CharField(
        max_length=STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default=OPEN_STATUS,
        verbose_name='Статус проекта'
    )

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='participated_projects',
        verbose_name='Участники'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('projects:project-details', kwargs={'project_id': self.pk})
