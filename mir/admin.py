from django.contrib import admin

from .models import Training, Employee, TrainingOrganized, TrainingAttended

class BaseAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

    # This is copy-paste from admin.ModelAdmin
    def get_queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        qs = self.model.unscoped.get_queryset()
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

class TrainingAdmin(BaseAdmin):
    list_display = ('id', 'name')

class EmployeeAdmin(BaseAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email')

class TrainingAttendedAdmin(BaseAdmin):
    list_display = ('id', 'employee', 'date', 'training')

class TrainingOrganizedAdmin(BaseAdmin):
    list_display = ('id', 'training', 'date')

admin.site.register(Training, TrainingAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(TrainingOrganized, TrainingOrganizedAdmin)
admin.site.register(TrainingAttended, TrainingAttendedAdmin)
