"""Models for and related to Crimes."""
from django.db import models
from multiselectfield import MultiSelectField

# Create your models here.

STATES = [
    ('---', 'Choose a State'),
    ('AK', 'Alaska'),
    ('AL', 'Alabama'),
    ('AR', 'Arkansas'),
    ('AZ', 'Arizona'),
    ('CA', 'California'),
    ('CO', 'Colorado'),
    ('CT', 'Connecticut'),
    ('DC', 'Washington, D.C.'),
    ('DE', 'Delaware'),
    ('FED', 'Federal'),
    ('FL', 'Florida'),
    ('GA', 'Georgia'),
    ('HI', 'Hawaii'),
    ('IA', 'Iowa'),
    ('ID', 'Idaho'),
    ('IL', 'Illinois'),
    ('IN', 'Indiana'),
    ('KS', 'Kansas'),
    ('KY', 'Kentucky'),
    ('LA', 'Louisiana'),
    ('MA', 'Massachusetts'),
    ('MD', 'Maryland'),
    ('ME', 'Maine'),
    ('MI', 'Michigan'),
    ('MN', 'Minnesota'),
    ('MO', 'Missouri'),
    ('MS', 'Mississippi'),
    ('MT', 'Montana'),
    ('NC', 'North Carolina'),
    ('ND', 'North Dakota'),
    ('NE', 'Nebraska'),
    ('NH', 'New Hampshire'),
    ('NJ', 'New Jersey'),
    ('NM', 'New Mexico'),
    ('NV', 'Nevada'),
    ('NY', 'New York'),
    ('OH', 'Ohio'),
    ('OK', 'Oklahoma'),
    ('OR', 'Oregon'),
    ('PA', 'Pennsylvania'),
    ('PR', 'Puerto Rico'),
    ('RI', 'Rhode Island'),
    ('SC', 'South Carolina'),
    ('SD', 'South Dakota'),
    ('TN', 'Tennessee'),
    ('TX', 'Texas'),
    ('UT', 'Utah'),
    ('VT', 'Vermont'),
    ('VA', 'Virginia'),
    ('VI', 'Virgin Islands'),
    ('WA', 'Washington'),
    ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'),
    ('WY', 'Wyoming')
]

DURATIONS = [
    ('---', 'Choose a Consequence Duration'),
    ('none', 'None'),
    ('bkg', 'Background Check/General Relief'),
    ('perm', 'Permanent/Unspecified'),
    ('spec', 'Specific Term'),
    ("cond", "Conditional")
]

CONSEQUENCE_TYPES = [
    ('---', 'Choose some consequence types'),
    ('bkg', 'Background Check'),
    ('disc', 'Discretionary'),
    ('waiv', 'Discretionary (waiver)'),
    ('auto', 'Mandatory/Automatic')
]

OFFENSE_CATEGORIES = [
    ('---', 'Choose a Category'),
    ('corruption', 'Public corruption offense'),
    ('misdem', 'Any misdemeanor'),
    ('moral', 'Crime of moral turpitude'),
    ('child_supp', 'Child Support offense'),
    ('driving', 'Motor vehicle offense'),
    ('drugs', 'Controlled substances offense'),
    ('sex', 'Sex offense'),
    ('violence', 'Crime of violence'),
    ('rec_license', 'Recreational license offense'),
    ('fraud', 'Crime involving fraud'),
    ('any', 'Any offense (including felony, misdemeanor, and lesser offense)'),
    ('felony', 'Any felony'),
    ('weapons', 'Weapons offense'),
    ('misc', 'Other')
]

CONSEQUENCE_CATEGORIES = [
    ('---', 'Choose a Category'),
    ('edu', 'Education'),
    ('family', 'Family/domestic rights'),
    ('govnt_bens', 'Government benefits'),
    ('govnt_contract', 'Government contracting and program participation'),
    ('govnt_loans', 'Government loans and grants'),
    ('housing', 'Housing'),
    ('jobs', 'Employment'),
    ('judicial', 'Judicial Rights'),
    ('prof_lic', 'Occupational and professional license and certification'),
    ('relief', 'General Relief Provision'),
    ('registration_lims', 'Registration, notification, and residency restrictions'),
    ('rec_weapons_lic', 'Recreational license, including firearms'),
    ('business_lic', 'Business license and other property rights'),
    ('driving_lic', 'Motor vehicle licensure'),
    ('voting', 'Political and civic participation'),
]


class Consequence(models.Model):
    """An individual crime."""

    title = models.CharField(max_length=255)
    citation = models.CharField(max_length=255)
    consequence_details = models.TextField()

    duration_desc = models.TextField()

    state = models.CharField(max_length=3, default="---", choices=STATES)
    duration = models.CharField(
        max_length=5, choices=DURATIONS, default="---"
    )

    offense_cat = MultiSelectField(
        choices=OFFENSE_CATEGORIES,
        max_length=15,
        max_choices=14,
        default='---'
    )
    consequence_cat = MultiSelectField(
        choices=CONSEQUENCE_CATEGORIES,
        max_length=20,
        max_choices=15,
        default='---'
    )
    consequence_type = MultiSelectField(
        choices=CONSEQUENCE_TYPES,
        max_length=5,
        max_choices=4,
        default='---'
    )

    def __str__(self):
        """Representation of the Consequence model."""
        outstr = "Consequence: {title}; Location: {location}"
        return outstr.format(
            title=self.title,
            location=self.state
        )
