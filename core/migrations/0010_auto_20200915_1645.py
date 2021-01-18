# Generated by Django 3.0.8 on 2020-09-15 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20200915_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='label',
            field=models.CharField(blank=True, choices=[('P', 'primary'), ('Se', 'secondary'), ('Su', 'success'), ('W', 'warning'), ('Dan', 'danger'), ('Dar', 'dark'), ('L', 'light')], max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='label',
            field=models.CharField(blank=True, choices=[('P', 'primary'), ('Se', 'secondary'), ('Su', 'success'), ('W', 'warning'), ('Dan', 'danger'), ('Dar', 'dark'), ('L', 'light')], max_length=3, null=True),
        ),
    ]