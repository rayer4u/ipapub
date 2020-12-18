# Generated by Django 3.0.11 on 2020-12-17 09:16

from django.db import migrations, models
import ipapub.contenttyperestrictedfilefield
import ipapub.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UpFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=200)),
                ('file', ipapub.contenttyperestrictedfilefield.ContentTypeRestrictedFileField(blank=True, null=True, upload_to=ipapub.models.PathAndRename2('upload'))),
                ('icons', ipapub.contenttyperestrictedfilefield.ContentTypeRestrictedFileField(upload_to=ipapub.models.PathAndRename('package'))),
                ('iconb', ipapub.contenttyperestrictedfilefield.ContentTypeRestrictedFileField(upload_to=ipapub.models.PathAndRename('package'))),
                ('plist', models.FileField(upload_to='package')),
                ('pub', models.FileField(upload_to='package')),
                ('signed', ipapub.contenttyperestrictedfilefield.ContentTypeRestrictedFileField(blank=True, null=True, upload_to=ipapub.models.PathAndRename('package'))),
                ('status', models.CharField(blank=True, max_length=10)),
                ('user', models.CharField(max_length=10)),
                ('label', models.CharField(blank=True, max_length=200)),
                ('up_date', models.DateTimeField(auto_now_add=True, verbose_name='upload date')),
                ('from_ip', models.GenericIPAddressField(blank=True, null=True)),
            ],
        ),
    ]