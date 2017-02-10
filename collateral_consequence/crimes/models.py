from django.db import models

# Create your models here.

CRIME_TYPES = [
    ("fel", "Felony"),
    ("misd", "Misdemeanor"),
    ("viol", "Violation"),
    ("---", "Choose a Crime Type")
]
CRIME_CLASSES = [
    ("---", "Choose a Class of Crime"),
    ('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D'), ('e', 'E'), ('f', 'F')
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
    state = models.CharField(max_length=255, null=True, blank=True)
