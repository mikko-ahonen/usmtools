from django.contrib import admin

from ordered_model.admin import OrderedModelAdmin

from .models import Project, Release, Backlog, Roadmap, Sprint, Epic, Story

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


class ProjectAdmin(BaseAdmin):
    list_display = ('tenant_id', 'id', 'name', 'prefix', 'domain')

class ReleaseAdmin(BaseAdmin):
    list_display = ('tenant_id', 'id', 'name', 'start_date', 'end_date', 'project')

class RoadmapAdmin(BaseAdmin):
    list_display = ('tenant_id', 'id', 'name', 'start_date', 'end_date', 'project')

class SprintAdmin(BaseAdmin):
    list_display = ('tenant_id', 'id', 'name', 'start_date', 'end_date', 'project')

class BacklogAdmin(BaseAdmin):
    list_display = ('tenant_id', 'id', 'name', 'start_date', 'end_date', 'project')

class EpicAdmin(BaseAdmin):
    list_display = ('tenant_id', 'id', 'name')

class StoryAdmin(BaseAdmin):
    list_display = ('tenant_id', 'id', 'name')

admin.site.register(Project, ProjectAdmin)
admin.site.register(Roadmap, RoadmapAdmin)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(Sprint, SprintAdmin)
admin.site.register(Epic, EpicAdmin)
admin.site.register(Story, StoryAdmin)
