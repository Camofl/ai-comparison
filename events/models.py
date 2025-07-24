from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField()
    date = models.DateField()

    def __str__(self):
        return self.title


class Participant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    email = models.EmailField()

    def __str__(self):
        return self.name
