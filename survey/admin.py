import logging
from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin

from .models import USMSurvey, Answer

logger = logging.getLogger(__name__)

class BaseAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

class USMSurveyAdmin(BaseAdmin):
    exclude = ['created_by', 'modified_by',]

class AnswerAdmin(BaseAdmin):
    list_display = ('id', 'question', 'low', 'high', 'text_en')
    exclude = ['created_by', 'modified_by',]

admin.site.register(USMSurvey, USMSurveyAdmin)
admin.site.register(Answer, AnswerAdmin)
