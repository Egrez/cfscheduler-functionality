from django.db import models

# Create your models here.

class Event(models.Model):
    event_id = models.CharField(max_length=14, primary_key=True)
    share_id = models.CharField(max_length=14)  # new
    name = models.CharField(max_length=40)
    duration = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        indexes = [
            models.Index(fields=['share_id'])
        ]

class DateRange(models.Model):
    date_range_id = models.AutoField(primary_key=True)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

class Inviter(models.Model):
    inviter_id = models.CharField(max_length=14, primary_key=True)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50)
    meeting_details = models.CharField(max_length=250, null=True, blank=True)

class Schedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    inviter = models.ForeignKey('Inviter', on_delete=models.CASCADE)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    is_booked = models.BooleanField()

class Invitee(models.Model):
    invitee_id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    message = models.CharField(max_length=250, null=True, blank=True)

class OauthCredentials(models.Model):
    token = models.CharField(max_length=256)
    refresh_token = models.CharField(max_length=256)
    token_uri = models.CharField(max_length=256)
    client_id = models.CharField(max_length=256)
    client_secret = models.CharField(max_length=256)