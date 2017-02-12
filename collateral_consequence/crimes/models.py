"""Models for and related to Crimes."""
from django.db import models

# Create your models here.

CRIME_TYPES = [
    ("---", "Choose a Crime Type"),
    ("fel", "Felony"),
    ("misd", "Misdemeanor"),
    ("viol", "Violation"),
]
CRIME_CLASSES = [
    ("---", "Choose a Class of Crime"),
    ('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D'), ('e', 'E'), ('f', 'F')
]
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


class Crime(models.Model):
    """An individual crime."""

    name = models.CharField(max_length=255)
    crime_type = models.CharField(
        max_length=40,
        choices=CRIME_TYPES,
        default="---"
    )
    crime_class = models.CharField(
        max_length=5,
        choices=CRIME_CLASSES,
        default="---"
    )
    sex_offense = models.BooleanField(default=False)
    county = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=3, default="---", choices=STATES)

    def __str__(self):
        """Representation of the Crime model."""
        outstr = "Crime: {name}; {crime_type};"
        outstr += " Class {crime_class}; Location: {location}"
        return outstr.format(
            name=self.name,
            crime_type=self.crime_type,
            crime_class=self.crime_class,
            location=self.state
        )


class SecondaryOffense(models.Model):
    """A secondary offense triggered by a crime."""

    pass
