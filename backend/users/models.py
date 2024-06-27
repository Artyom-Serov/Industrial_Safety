from django.contrib.auth.models import AbstractUser
from django.db import models


class Organization(models.Model):
    """Модель организации."""
    name = models.CharField(
        max_length=255, verbose_name="Наименование организации"
    )

    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Модель управления пользователем."""
    organization = models.ForeignKey(
        Organization, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Организация"
    )
    email = models.EmailField(
        unique=True, verbose_name="Адрес электронной почты"
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']
