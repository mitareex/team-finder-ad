from django import forms

from users.validators import check_github_domain
from .models import Project


GITHUB_LABEL = 'Ссылка на Github'
NAME_LABEL = 'Название'
DESCRIPTION_LABEL = 'Описание'
STATUS_LABEL = 'Статус'


class ProjectForm(forms.ModelForm):
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
        choices=[('open', 'Открыт'), ('closed', 'Закрыт')],
        widget=forms.Select()
    )

    class Meta:
        model = Project
        fields = ('name', 'description', 'github_url', 'status')

    def clean_github_url(self):
        github_url = self.cleaned_data.get('github_url')

        if github_url:
            check_github_domain(github_url)

        return github_url
