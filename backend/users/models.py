from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель управления пользователем."""
    organization_name = models.CharField(
        max_length=255, verbose_name="Наименование организации"
    )
    email = models.EmailField(
        unique=True, verbose_name="Адрес электронной почты"
    )
