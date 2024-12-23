from collections import defaultdict
from datetime import timedelta
from django.utils.dateparse import parse_date
import math

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, FormView, RedirectView
from django.utils.translation import gettext as _
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.db import transaction

from workflows.models import Tenant
from workflows.views import TenantMixin
from workflows.tenant import current_tenant_id

from .models import Domain, Requirement, Constraint, Target, TargetSection, Project, Release, Epic, Category
from boards.models import Board, List, Task
from . import forms

class DomainList(TenantMixin, ListView):
    model = Domain
    template_name = 'compliances/domain-list.html'
    context_object_name = 'domains'

class ProjectList(TenantMixin, ListView):
    model = Project
    template_name = 'compliances/project-list.html'
    context_object_name = 'projects'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_type = ContentType.objects.get_for_model(Project)
        boards = {}
        for project in self.get_queryset().all():
            pk = project.id
            boards[pk] = Board.objects.filter(content_type=project_type, object_id=pk)
        context['boards'] = boards
        return context

    def get_queryset(self, **kwargs):
        if self.request.user.is_superuser:
            return Project.unscoped.all()
        else:
            return Project.objects.all()
        return qs

class ProjectSetup(TenantMixin, DetailView):
    model = Project
    template_name = 'compliances/project-setup.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs['pk']
        context['targets'] = Target.objects.filter(project_id=project_id)
        return context

class DomainCreateProject(TenantMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        tenant_id = self.kwargs['tenant_id']
        domain_id = self.kwargs['pk']
        domain = get_object_or_404(Domain, tenant_id=tenant_id, pk=domain_id)
        project, created = Project.objects.get_or_create(tenant_id=tenant_id, domain=domain, defaults={'name': domain.name + _('project')})
        return reverse_lazy('compliances:project-setup', kwargs={"tenant_id": tenant_id, "pk": project.id})

class DomainDetail(TenantMixin, DetailView):
    model = Domain
    template_name = 'compliances/domain-detail.html'
    context_object_name = 'domain'

class ProjectBacklogCreate(TenantMixin, RedirectView):

    def get_sprints_and_stories(self, project):
        for release in project.releases:
            stories = []
            for epic in release.epics:
                for constraint in epic.category.constraints:
                    story = Story(name=constraint, type=TASK_TYPE_STORY)
                    Task.objects.create(name=constraint.name, description=constraint.description, type=Task.TASK_TYPE_STORY, content_object=story)

    def get_redirect_url(self, *args, **kwargs):
        tenant_id = self.kwargs['tenant_id']
        project_id = self.kwargs['pk']
        domain = get_object_or_404(Domain, tenant_id=tenant_id, pk=domain_id)
        project, created = Project.objects.get_or_create(tenant_id=tenant_id, domain=domain, defaults={'name': domain.name + _('project')})
        return reverse_lazy('compliances:project-setup', kwargs={"tenant_id": tenant_id, "pk": project.id})

class ProjectRoadmapCreate(TenantMixin, FormView):
    template_name = 'compliances/project-roadmap-create.html'
    form_class = forms.RoadmapCreateForm

    def get_releases_and_epics(self, project, targets, start_date, release_length_in_days, epics_in_release):
        epic_names = {}
        for target in targets.order_by('name'):
            for category in Category.objects.filter(domain=project.domain).order_by('index'):
                epic_name = str(category) + " " + str(target)
                epic_names[epic_name] = 1
        epics = [Epic(name=name) for name in epic_names.keys()]
        number_of_releases = math.ceil(len(epics)/epics_in_release)
        releases = []
        release_epics = defaultdict(list)
        if isinstance(start_date, str):
            start_date = parse_date(start_date)
        for i in range(number_of_releases):
            end_date = start_date + timedelta(release_length_in_days)
            release = Release(name=f'0.{i + 1}.0', start_date=start_date, end_date=end_date)
            this_release_epics = epics[epics_in_release * i:epics_in_release * (i + 1)]
            for epic in this_release_epics:
                release_epics[release.id].append(epic)
            releases.append(release)
            start_date = end_date + timedelta(days=1)
        end_date = start_date + timedelta(release_length_in_days)
        final_release = Release(name='1.0.0', start_date=start_date, end_date=end_date)
        releases.append(final_release)
        release_epic = Epic(name=_("Project finalization"), release=final_release)
        release_epics[final_release.id].append(release_epic)
        return releases, release_epics

    def post(self, request, tenant_id, pk):

        form = self.form_class(request.POST)
        tenant = get_object_or_404(Tenant, pk=tenant_id)

        if form.is_valid():

            start_date = form.cleaned_data['start_date']
            release_length_in_days =  form.cleaned_data['release_length_in_days']
            epics_in_release =  form.cleaned_data['epics_in_release']

            #tenant_id = self.kwargs['tenant_id']
            #project_id = self.kwargs['pk']
            project = get_object_or_404(Project, tenant_id=tenant_id, pk=pk)
            targets = Target.objects.filter(project_id=pk).prefetch_related('target_sections', 'target_sections__section')

            releases, epics_in_releases = self.get_releases_and_epics(project, targets, start_date, release_length_in_days, epics_in_release)

            if request.POST.get("create", False):
                with transaction.atomic():
                    board = Board.objects.create(name=project.name + ' ' + _('roadmap'), type=Board.BOARD_TYPE_ROADMAP, content_object=project, tenant_id=tenant.id, task_entity_name=_('epic'), list_entity_name=_("release"), max_columns=1, show_list_count=False)

                    for release in releases:
                        release.tenant_id = tenant.id
                        release.project_id = project.id
                        release.save()

                    for release_id, epics in epics_in_releases.items():
                        for epic in epics:
                            epic.tenant_id = tenant.id
                            epic.release_id = release_id
                            epic.save()

                    for release_idx, release in enumerate(releases):
                        l = List.objects.create(name=release.name, board=board, type=List.LIST_TYPE_RELEASE, content_object=release, tenant_id=tenant.id, index=release_idx)
                        for epic_idx, epic in enumerate(epics_in_releases[release.id]):
                            Task.objects.create(label=epic.name, list=l, type=Task.TASK_TYPE_EPIC, content_object=epic, tenant_id=tenant.id, index=epic_idx)

                return redirect("boards:board", board_uuid=board.uuid)
            else:
                context = {
                    'form': form,
                    'releases': releases,
                    'epics': epics_in_releases,
                    'tenant': tenant,
                }
                return render(request, self.template_name, context)

        # if there were errors in form
        # we have to display same page with errors
        context = {
            'form': form,
            'tenant': tenant,
        }

        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        tenant_id = self.kwargs['tenant_id']
        project = get_object_or_404(Project, tenant_id=tenant_id, pk=pk)
        targets = Target.objects.filter(project_id=pk).prefetch_related('target_sections', 'target_sections__section')
        context = super().get_context_data(**kwargs)
        context['project'] = project
        context['targets'] = targets
        return context

class DeploymentBoard(TenantMixin, DetailView):
    model = Domain
    template_name = 'compliances/deployment-board.html'
    context_object_name = 'domain'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        domain_id = self.kwargs['pk']
        context['columns'] = [
            {
                'name': _("Non-compliant"),
                'statuses': ['new', 'ongoing', 'implemented', 'non-compliant', 'failed'],
            },
            {
                'name': _("Compliant"),
                'statuses': ['compliant'],
            },
            {
                'name': _("Audited"),
                'statuses': ['audited'],
            },
        ]
        context['constraints'] = Constraint.objects.filter(requirement__section__domain_id=domain_id).select_related('requirement', 'requirement__section', 'requirement__section__domain')
        return context

def targets(request, project):
    tenant_id = current_tenant_id()
    targets = Target.objects.filter(project_id=project.id)
    template = "compliances/_targets.html"
    response = render(request, template, {"tenant_id": tenant_id, "project": project, "targets": targets})
    response["HX-Retarget"] = "#targets"
    return response

# TODO: check permissions
def create_target_for_project(request, tenant_id, pk):
    project = get_object_or_404(Project, tenant_id=tenant_id, pk=pk)
    form = forms.TargetForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.instance.tenant_id = tenant_id
        form.instance.project_id = pk
        target = form.save()

    return targets(request, project)

def target_section_select(request, tenant_id, target_id, section_id):
    if request.method == "POST":
        new_value = (request.POST.get("selected", "off") == "on")

        qs = TargetSection.objects.filter(tenant_id=tenant_id, target_id=target_id, section_id=section_id)

        if new_value:
            if not qs.exists():
                TargetSection.objects.create(tenant_id=tenant_id, target_id=target_id, section_id=section_id)
        else:
            if qs.exists():
                qs.delete()

        return HttpResponse("OK")
    else:
        raise Http404(f"Invalid method: {request.method}")
