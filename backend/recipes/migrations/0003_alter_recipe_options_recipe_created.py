# Generated by Django 4.2.1 on 2023-05-30 14:52

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0002_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="recipe",
            options={
                "verbose_name": "рецепт",
                "verbose_name_plural": "рецепты",
            },
        ),
        migrations.AddField(
            model_name="recipe",
            name="created",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="дата создания",
            ),
            preserve_default=False,
        ),
    ]