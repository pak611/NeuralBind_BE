# Generated by Django 4.1.3 on 2023-08-14 02:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("nb_app", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="formdata", old_name="uploaded_file", new_name="pdb_file",
        ),
    ]
