# Generated by Django 5.0.6 on 2024-06-27 05:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="organization",
            options={
                "verbose_name": "Организация",
                "verbose_name_plural": "Организации",
            },
        ),
        migrations.AlterModelOptions(
            name="user",
            options={
                "ordering": ["id"],
                "verbose_name": "Пользователь",
                "verbose_name_plural": "Пользователи",
            },
        ),
    ]
