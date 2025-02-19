from django.contrib import admin

from ordered_model.admin import OrderedModelAdmin

from .models import OrganizationUnit, Service, Routine, Profile, Step, Activity, Responsibility, Account, Instruction, Tenant, Customer, Action


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


class AccountAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

    exclude = ['created_by', 'modified_by',]


class OrganizationUnitAdmin(BaseAdmin):
    list_display = ('tenant', 'id', 'name', 'parent')

class TenantAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

    list_display = ('id', 'name')

class ServiceAdmin(BaseAdmin):
    list_display = ('tenant', 'id', 'name', 'is_meta', 'is_global_template', 'parent')

class RoutineAdmin(BaseAdmin, OrderedModelAdmin):
    list_display = ('id', 'name', 'is_template', 'is_public', 'move_up_down_links')

class ProfileAdmin(BaseAdmin, OrderedModelAdmin):
    list_display = ('tenant', 'id', 'name', 'move_up_down_links')

class StepAdmin(BaseAdmin, OrderedModelAdmin):
    list_display = ('tenant', 'id', 'name', 'routine', 'move_up_down_links')
    
class ActivityAdmin(BaseAdmin, OrderedModelAdmin):
    list_display = ('tenant', 'id', 'name', 'step', 'move_up_down_links')

class ActionAdmin(BaseAdmin, OrderedModelAdmin):
    list_display = ('tenant', 'id', 'activity', 'title', 'move_up_down_links')

class ResponsibilityAdmin(BaseAdmin, OrderedModelAdmin):
    list_display = ('tenant', 'id', 'types', 'action', 'profile', 'move_up_down_links')

class InstructionAdmin(BaseAdmin):
    list_display = ('tenant', 'id') #, 'responsible')

class CustomerAdmin(BaseAdmin):
    list_display = ('tenant', 'id', 'name', 'customer_type')

admin.site.register(Tenant, TenantAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(OrganizationUnit, OrganizationUnitAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Routine, RoutineAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Step, StepAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(Responsibility, ResponsibilityAdmin)
admin.site.register(Instruction, InstructionAdmin)
admin.site.register(Customer, CustomerAdmin)
