import os
import random
from io import BytesIO

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from .constants import (
    AVATAR_SIZE, DEFAULT_LETTER, FONT_SIZE,
    NAME_MAX_LENGTH, SURNAME_MAX_LENGTH, PHONE_MAX_LENGTH,
    ABOUT_MAX_LENGTH, COLOR_WHITE, BACKGROUND_COLORS
)
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    name = models.CharField(max_length=NAME_MAX_LENGTH, verbose_name='Имя')
    surname = models.CharField(max_length=SURNAME_MAX_LENGTH, verbose_name='Фамилия')
    avatar = models.ImageField(upload_to='avatars/', blank=True, verbose_name='Аватар')
    phone = models.CharField(max_length=PHONE_MAX_LENGTH, unique=True,
                             blank=True, null=True, verbose_name='Номер телефона')
    github_url = models.URLField(blank=True, null=True, verbose_name='Ссылка на GitHub')
    about = models.TextField(max_length=ABOUT_MAX_LENGTH, blank=True,
                             null=True, default='', verbose_name='О себе')

    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Статус персонала')

    # Дополнение (Вариант 1).
    favorites = models.ManyToManyField(
        'projects.Project',
        blank=True,
        related_name='interested_users',
        verbose_name='Избранные проекты'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'phone']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.name} {self.surname} ({self.email})'

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = self.generate_avatar()
        super().save(*args, **kwargs)

    def generate_avatar(self):
        """Генерирует аватарку, используя первую букву имени."""
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
            # Если кастомного шрифта нет, берем дефолтный крупного размера
            font = ImageFont.load_default(size=FONT_SIZE)

        center_x = AVATAR_SIZE[0] // 2
        center_y = AVATAR_SIZE[1] // 2

        draw.text((center_x, center_y), letter, fill=COLOR_WHITE, font=font, anchor="mm")

        buffer = BytesIO()
        image.save(buffer, format='PNG')
        return ContentFile(buffer.getvalue(), name=f'avatar_{
            self.id or random.randint(1, 10000)}.png')
