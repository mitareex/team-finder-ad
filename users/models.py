import os
import random
from io import BytesIO

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont


AVATAR_SIZE = (200, 200)
TEXT_COORDINATES = (85, 80)
DEFAULT_LETTER = 'U'
FONT_SIZE = 48
NAME_MAX_LENGTH = 124
SURNAME_MAX_LENGTH = 124
PHONE_MAX_LENGTH = 12
ABOUT_MAX_LENGTH = 256
TEXT_COLOR = (255, 255, 255)  # Белый
BACKGROUND_COLORS = [
    (100, 149, 237),  # Васильково-синий
    (143, 188, 143),  # Тёмно-морской зелёный
    (244, 164, 96),   # Светло-каштановый
    (218, 112, 214),  # Светло-лиловый
    (176, 224, 230),  # Бледно-голубой
    (250, 128, 114),  # Оранжево-розовый
]
IS_STUFF_ERROR_MESSAGE = 'Superuser must have is_stuff=True.'
IS_SUPERUSER_ERROR_MESSAGE = 'Superuser must have is_superuser=True.'


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, phone, password=None, **extra_fields):
        if not email:
            raise ValueError
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


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    surname = models.CharField(max_length=SURNAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    phone = models.CharField(max_length=PHONE_MAX_LENGTH, unique=True, blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    about = models.TextField(max_length=ABOUT_MAX_LENGTH, blank=True, null=True, default='')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Дополнение (Вариант 1).
    favorites = models.ManyToManyField(
        'projects.Project',
        blank=True,
        related_name='interested_users'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'phone']

    def __str__(self):
        return f'{self.name} {self.surname} ({self.email})'

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = self.generate_avatar()
        super().save(*args, **kwargs)

    def generate_avatar(self):
        '''Generates avatar using the first letter of name'''
        bg_color = random.choice(BACKGROUND_COLORS)

        image = Image.new('RGB', AVATAR_SIZE, color=bg_color)
        draw = ImageDraw.Draw(image)

        letter = self.name[0].upper() if self.name else DEFAULT_LETTER

        font_path = os.path.join(
            settings.BASE_DIR,
            'static',
            'fonts',
            'Neue_Haas_Grotesk_Display_Pro_75_Bold.otf'
        )

        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, size=FONT_SIZE)
        else:
            font = ImageFont.load_default()

        draw.text(TEXT_COORDINATES, letter, fill=TEXT_COLOR, font=font)

        buffer = BytesIO()
        image.save(buffer, format='PNG')
        return ContentFile(buffer.getvalue(), name=f'avatar_{self.name}.png')
