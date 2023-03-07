from django.contrib import admin

# Register your models here.

from .models import Event, Inviter, Invitee, Schedule, DateRange

admin.site.register(Event)
admin.site.register(Inviter)
admin.site.register(Invitee)
admin.site.register(Schedule)
admin.site.register(DateRange)