import re

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError

from projects.mixins import GitHubCleanMixin
from .constants import (
    PASSWORD_LABEL, EMAIL_LABEL, PHONE_PATTERN, LOGIN_ERROR_MESSAGE,
    PHONE_ERROR_MESSAGE, OLD_PASSWORD_ERROR_MESSAGE, NEW_PASSWRODS_ERROR_MESSAGE,
    PHONE_START_NUMBER_BAD, PHONE_START_NUMBER_GOOD, EXCEPT_FIRST_DIGIT,
    OLD_PASSWORD_LABEL, NEW_PASSWORD1_LABEL, NEW_PASSWORD2_LABEL, GITHUB_LABEL,
    NAME_LABEL, SURNAME_LABEL, PHONE_LABEL, ABOUT_LABEL, AVATAR_LABEL
)

User = get_user_model()


class RegisterForm(forms.ModelForm):
    '''Registration form for a new user'''
    password = forms.CharField(widget=forms.PasswordInput(), label=PASSWORD_LABEL)
    name = forms.CharField(
        label=NAME_LABEL,
    )
    surname = forms.CharField(
        label=SURNAME_LABEL,
    )

    class Meta:
        model = User
        fields = ('name', 'surname', 'email', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    '''Login form contains email and password'''
    email = forms.EmailField(label=EMAIL_LABEL)
    password = forms.CharField(widget=forms.PasswordInput(), label=PASSWORD_LABEL)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise ValidationError(LOGIN_ERROR_MESSAGE)
            cleaned_data['user'] = user
        return cleaned_data


class ProfileEditForm(GitHubCleanMixin, forms.ModelForm):
    '''Profile edit form with phone number validation'''
    name = forms.CharField(
        label=NAME_LABEL,
    )
    surname = forms.CharField(
        label=SURNAME_LABEL,
    )
    avatar = forms.ImageField(
        label=AVATAR_LABEL,
        required=False,
        widget=forms.FileInput()
    )
    phone = forms.CharField(
        label=PHONE_LABEL,
        required=False
    )
    github_url = forms.URLField(
        label=GITHUB_LABEL,
        required=False
    )
    about = forms.CharField(
        label=ABOUT_LABEL,
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-input'
        })
    )

    class Meta:
        model = User
        fields = ('name', 'surname', 'avatar', 'about', 'phone', 'github_url')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if not phone:
            return phone

        phone_pattern = re.compile(PHONE_PATTERN)
        if not phone_pattern.match(phone):
            raise ValidationError(PHONE_ERROR_MESSAGE)

        if phone.startswith(PHONE_START_NUMBER_BAD):
            normalized_phone = PHONE_START_NUMBER_GOOD + phone[EXCEPT_FIRST_DIGIT:]
        else:
            normalized_phone = phone

        user_queryset = User.objects.filter(phone=normalized_phone)
        if self.instance and self.instance.pk:
            user_queryset = user_queryset.exclude(pk=self.instance.pk)

        if user_queryset.exists():
            raise ValidationError(PHONE_ERROR_MESSAGE)

        return normalized_phone


class ChangePasswordForm(forms.Form):
    '''Change password based on old password and new password fields'''
    old_password = forms.CharField(widget=forms.PasswordInput(), label=OLD_PASSWORD_LABEL)
    new_password1 = forms.CharField(widget=forms.PasswordInput(), label=NEW_PASSWORD1_LABEL)
    new_password2 = forms.CharField(widget=forms.PasswordInput(), label=NEW_PASSWORD2_LABEL)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError(OLD_PASSWORD_ERROR_MESSAGE)
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError(NEW_PASSWRODS_ERROR_MESSAGE)
        return cleaned_data
