# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-15 04:04
from __future__ import unicode_literals

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('crimes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consequence',
            name='offense_cat',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('---', 'Choose a Category'), ('corruption', 'Public corruption offense'), ('misdem', 'Any misdemeanor'), ('moral', 'Crime of moral turpitude'), ('child_supp', 'Child Support offense'), ('driving', 'Motor vehicle offense'), ('drugs', 'Controlled substances offense'), ('sex', 'Sex offense'), ('violence', 'Crime of violence'), ('rec_license', 'Recreational license offense'), ('fraud', 'Crime involving fraud'), ('any', 'Any offense (including felony, misdemeanor, and lesser offense)'), ('felony', 'Any felony'), ('weapons', 'Weapons offense'), ('misc', 'Other')], default='---', max_length=15),
        ),
    ]
