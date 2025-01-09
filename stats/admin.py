from django.contrib import admin

from .models import Dataset, Datapoint

class DatapointInline(admin.TabularInline):
    model = Datapoint
    extra = 10

class DatasetAdmin(admin.ModelAdmin):
    inlines = [DatapointInline]

admin.site.register(Dataset, DatasetAdmin)
