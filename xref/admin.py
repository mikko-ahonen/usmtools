from django.contrib import admin

from ordered_model.admin import OrderedModelAdmin

from .models import CrossReference

class BaseAdmin(OrderedModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

class CrossReferenceAdmin(BaseAdmin):
    list_display = ('id', 'name')

admin.site.register(CrossReference, CrossReferenceAdmin)
