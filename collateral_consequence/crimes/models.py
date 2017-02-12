"""Models for and related to Crimes."""
from django.db import models

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
]
CONSEQUENCES_TYPE = [
    ('---', 'Choose a Consequence Type'),
    ('none', 'None'),
    ('bkg', 'Background Check'),
    ('waiv', 'Discretionary (waiver)'),
    ('rel', 'General Relief'),
    ('auto', 'Mandatory/Automatic'),
    ('disc', 'Discretionary'),
]
CONSEQUENCES_CATS = [
    ('---', 'Choose a Consequence Category'),
    ('none', 'None'),
    ('rec_lic', 'Recreational license'),
    ('job', 'Employment'),
    ('bens', 'Government benefits'),
    ('prof_lic', 'Occupational and professional license and certification'),
    ('vote', 'Political and civic participation'),
    ('gen', 'General Relief Provision'),
    ('govt_con', 'Government contracting and program participation'),
    ('restr', 'Registration, notification, and residency restrictions'),
    ('business_lic', 'Business license and other property rights'),
    ('family', 'Family/domestic rights'),
    ('housing', 'Housing'),
    ('drivers_lic', 'Motor vehicle licensure'),
    ('rights', 'Judicial Rights'),
    ('education', 'Education'),
    ('govt_loans', 'Government loans and grants'),
]


class Crime(models.Model):
    """An individual crime."""

    title = models.CharField(max_length=255)
    citation = models.CharField(max_length=255)
    state = models.CharField(max_length=3, default="---", choices=STATES)

    sex_offense = models.BooleanField(default=False)
    fraud = models.BooleanField(default=False)
    recreational_license = models.BooleanField(default=False)
    controlled_substances = models.BooleanField(default=False)
    any_offense = models.BooleanField(default=False)
    any_felony = models.BooleanField(default=False)
    any_misdemeanor = models.BooleanField(default=False)
    motor_vehicle = models.BooleanField(default=False)
    moral_turpitude = models.BooleanField(default=False)
    corruption = models.BooleanField(default=False)
    election_related = models.BooleanField(default=False)
    weapons = models.BooleanField(default=False)
    violence = models.BooleanField(default=False)
    child_support = models.BooleanField(default=False)

    consequence_category = models.CharField(
        max_length=50,
        choices=CONSEQUENCES_CATS,
        default='---'
    )
    consequence_details = models.TextField()
    consequence_type = models.CharField(
        max_length=5, choices=CONSEQUENCES_TYPE, default="---"
    )
    duration = models.CharField(
        max_length=5, choices=DURATIONS, default="---"
    )

    def __str__(self):
        """Representation of the Crime model."""
        outstr = "Crime: {title}; Location: {location}"
        return outstr.format(
            title=self.title,
            location=self.state
        )
