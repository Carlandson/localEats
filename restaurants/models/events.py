from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from .content import EventsPage

class Event(models.Model):
    events_page = models.ForeignKey(EventsPage, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    images = GenericRelation('Image')

    @property
    def image(self):
        """Returns the first image associated with this event"""
        return self.images.first()