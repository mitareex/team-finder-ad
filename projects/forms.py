from django import forms

from .models import Project
from .constants import (
    NAME_LABEL,
    DESCRIPTION_LABEL,
    GITHUB_LABEL, STATUS_LABEL,
    STATUS_CHOICES
    )
from .mixins import GitHubCleanMixin


class ProjectForm(GitHubCleanMixin, forms.ModelForm):
    '''Create and edit form for project'''
    name = forms.CharField(
        label=NAME_LABEL,
        widget=forms.TextInput(attrs={
            'placeholder': 'Название проекта',
            'class': 'form-input'
        })
    )
    description = forms.CharField(
        label=DESCRIPTION_LABEL,
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Описание проекта',
            'rows': 4
        })
    )
    github_url = forms.URLField(
        label=GITHUB_LABEL,
        required=False,
        widget=forms.URLInput(attrs={'placeholder': 'https://github.com/username/repo'})
    )

    status = forms.ChoiceField(
        label=STATUS_LABEL,
        choices=STATUS_CHOICES,
        widget=forms.Select()
    )

    class Meta:
        model = Project
        fields = ('name', 'description', 'github_url', 'status')
