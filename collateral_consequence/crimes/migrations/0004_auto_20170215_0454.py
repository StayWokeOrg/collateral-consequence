# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-15 04:54
from __future__ import unicode_literals

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('crimes', '0003_auto_20170215_0409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consequence',
            name='offense_cat',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('---', 'Choose a Category'), ('corruption', 'Public corruption offenses'), ('misdem', 'Any misdemeanor'), ('moral', 'Crime of moral turpitude'), ('child_supp', 'Child Support offenses'), ('driving', 'Motor vehicle offenses'), ('drugs', 'Controlled substances offenses'), ('sex', 'Sex offenses'), ('violence', 'Crimes of violence including "person offenses"'), ('rec_license', 'Recreational license offense'), ('fraud', 'Crimes involving fraud dishonesty misrepresentation or money-laundering'), ('any', 'Any offense (including felony, misdemeanor, and lesser offense)'), ('felony', 'Any felony'), ('weapons', 'Weapons offenses'), ('election', 'Election-related offenses'), ('misc', 'Other')], default='---', max_length=255),
        ),
    ]
