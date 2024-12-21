from django.contrib import admin

from ordered_model.admin import OrderedModelAdmin

from .models import Domain, Section, Requirement, Constraint, Project, Release, Epic, Term, Category

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


class DomainAdmin(BaseAdmin):
    list_display = ('tenant_id', 'id', 'slug', 'name', 'description')

class ProjectAdmin(BaseAdmin):
    list_display = ('tenant_id', 'id', 'name', 'prefix', 'domain')

class ReleaseAdmin(BaseAdmin):
    list_display = ('tenant_id', 'id', 'name', 'start_date', 'end_date', 'project')

class EpicAdmin(BaseAdmin):
    list_display = ('tenant_id', 'id', 'name', 'release')

class SectionAdmin(BaseAdmin):
    list_display = ('tenant_id', 'id', 'slug', 'title', 'description')

class RequirementAdmin(BaseAdmin):
    list_display = ('tenant_id', 'id', 'slug', 'text')

class TermAdmin(BaseAdmin):
    list_display = ('tenant_id', 'id', 'name', 'definition')

class CategoryAdmin(BaseAdmin):
    list_display = ('tenant_id', 'id', 'slug', 'name')

#class CategoryInline(admin.TabularInline):
#    model = Constraint.categories.through
#    verbose_name = "Category"
#    verbose_name_plural = "Categories"
    
class ConstraintAdmin(BaseAdmin):
    list_display = ('tenant_id', 'id', 'slug', 'text', 'category')
#    inlines = (CategoryInline,)

admin.site.register(Domain, DomainAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(Epic, EpicAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Requirement, RequirementAdmin)
admin.site.register(Term, TermAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Constraint, ConstraintAdmin)
