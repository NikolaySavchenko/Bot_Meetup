# Generated by Django 4.2.1 on 2023-06-24 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetup_bot', '0002_alter_donation_options_alter_form_options_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Donation',
            new_name='Donat',
        ),
        migrations.AlterField(
            model_name='member',
            name='telegram_name',
            field=models.CharField(max_length=200, unique=True, verbose_name='Телеграм'),
        ),
    ]