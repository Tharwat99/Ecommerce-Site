# Generated by Django 3.0.8 on 2020-09-15 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20200915_1356'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('label', models.CharField(blank=True, choices=[('I', 'indigo'), ('Pur', 'purple'), ('Pi', 'pink'), ('R', 'red'), ('O', 'orange'), ('Y', 'yellow'), ('Gre', 'green'), ('T', 'teal'), ('C', 'cyan'), ('Wh', 'white'), ('Gra', 'gray'), ('Pri', 'primary'), ('Se', 'secondary'), ('Su', 'success'), ('War', 'warning'), ('Dan', 'danger'), ('Dar', 'dark'), ('L', 'light')], max_length=3, null=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'Categories'},
        ),
        migrations.RemoveField(
            model_name='category',
            name='code',
        ),
        migrations.RemoveField(
            model_name='item',
            name='label',
        ),
        migrations.AddField(
            model_name='category',
            name='label',
            field=models.CharField(blank=True, choices=[('I', 'indigo'), ('Pur', 'purple'), ('Pi', 'pink'), ('R', 'red'), ('O', 'orange'), ('Y', 'yellow'), ('Gre', 'green'), ('T', 'teal'), ('C', 'cyan'), ('Wh', 'white'), ('Gra', 'gray'), ('Pri', 'primary'), ('Se', 'secondary'), ('Su', 'success'), ('War', 'warning'), ('Dan', 'danger'), ('Dar', 'dark'), ('L', 'light')], max_length=3, null=True),
        ),
        migrations.RemoveField(
            model_name='item',
            name='category',
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.ManyToManyField(to='core.Category'),
        ),
        migrations.AddField(
            model_name='item',
            name='tags',
            field=models.ManyToManyField(to='core.Tag'),
        ),
    ]
