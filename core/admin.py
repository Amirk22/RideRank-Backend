from django.contrib import admin
from .models import User , Rating ,Report , ScoreEvent ,Trip
# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ['__str__','role','trust_score']
    list_filter = ['role']
    readonly_fields = ['trust_score']

admin.site.register(User,UserAdmin)

class TripAdmin(admin.ModelAdmin):
    list_display = ['__str__','start_location','destination']
    date_hierarchy = 'created_at'

admin.site.register(Trip,TripAdmin)

class RatingAdmin(admin.ModelAdmin):
    list_filter = ['score']
admin.site.register(Rating,RatingAdmin)

class ReportAdmin(admin.ModelAdmin):
    list_display = ['__str__','type']
    list_filter = ['type']

admin.site.register(Report, ReportAdmin)

admin.site.register(ScoreEvent)


