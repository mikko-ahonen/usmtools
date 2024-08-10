from django.contrib import admin

from ordered_model.admin import OrderedModelAdmin

from .models import Domain as FooDomain
from .models import Section, Requirement, Constraint

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


class FooDomainAdmin(BaseAdmin):
    list_display = ('id', 'slug', 'name', 'description')

class SectionAdmin(BaseAdmin):
    list_display = ('id', 'slug', 'title', 'description')

class RequirementAdmin(BaseAdmin):
    list_display = ('id', 'slug', 'text')

class ConstraintAdmin(BaseAdmin):
    list_display = ('id', 'slug', 'text')

admin.site.register(FooDomain, FooDomainAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Requirement, RequirementAdmin)
admin.site.register(Constraint, ConstraintAdmin)
