# Generated by Django 5.0.6 on 2024-06-27 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_alter_user_organization"),
    ]

    operations = [
        migrations.AlterField(
            model_name="organization",
            name="name",
            field=models.CharField(
                help_text="Укажите наименование организации",
                max_length=255,
                verbose_name="Наименование организации",
            ),
        ),
    ]
