# Generated by Django 5.1.6 on 2025-02-09 15:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("happsay_app", "0003_alter_todolist_options"),
    ]

    operations = [
        migrations.RenameField(
            model_name="todolist",
            old_name="user_id_fk",
            new_name="user",
        ),
    ]
