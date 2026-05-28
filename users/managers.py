from django.contrib.auth.models import BaseUserManager
from .constants import IS_STUFF_ERROR_MESSAGE, IS_SUPERUSER_ERROR_MESSAGE


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, phone, password=None, **extra_fields):
        if not email:
            raise ValueError('Email является обязательным полем')
        email = self.normalize_email(email)

        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        user = self.model(
            email=email,
            name=name,
            surname=surname,
            phone=phone,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(IS_STUFF_ERROR_MESSAGE)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(IS_SUPERUSER_ERROR_MESSAGE)

        return self.create_user(email, name, surname, phone, password, **extra_fields)
