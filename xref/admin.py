from django.contrib import admin

from ordered_model.admin import OrderedModelAdmin

from .models import Standard, Control, Requirement, Statement, Task

class BaseAdmin(OrderedModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

class StandardAdmin(BaseAdmin):
    list_display = ('id', 'name')

class ControlAdmin(BaseAdmin):
    list_display = ('id', 'name', 'domain', 'status')

class RequirementAdmin(BaseAdmin):
    list_display = ('id', 'text', 'status')

class StatementAdmin(BaseAdmin):
    list_display = ('id', 'text', 'status')

class TaskAdmin(BaseAdmin):
    list_display = ('id', 'subject', 'predicate', 'object')

admin.site.register(Standard, StandardAdmin)
admin.site.register(Control, ControlAdmin)
admin.site.register(Requirement, RequirementAdmin)
admin.site.register(Statement, StatementAdmin)
admin.site.register(Task, TaskAdmin)
