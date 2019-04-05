from django.db import models

from tom_observations.models import ObservationRecord
from tom_targets.models import Target

class ObservationTemplate(models.Model):
    template = models.BooleanField(default=False)
    observation = models.ForeignKey(ObservationRecord, on_delete=models.CASCADE)

    def __str__(self):
        return "Template of {}".format(self.observation)


class TimeLapse(models.Model):
    target          = models.ForeignKey(Target, null=True, on_delete=models.CASCADE)
    timestamp       = models.DateTimeField(null=False, blank=False, db_index=True)
    timelapse_mpeg  = models.FileField(blank=True, null=True)
    timelapse_webm  = models.FileField(blank=True, null=True)
    num_observations= models.IntegerField(default=0)
    active          = models.BooleanField(default=False)

    def __str__(self):
        return "Timelapse of {}".format(self.target)
