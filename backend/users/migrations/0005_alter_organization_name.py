# Generated by Django 5.0.6 on 2024-06-27 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_alter_organization_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="organization",
            name="name",
            field=models.CharField(
                max_length=255, verbose_name="Наименование организации"
            ),
        ),
    ]
