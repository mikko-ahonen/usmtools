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
from django.urls import reverse_lazy, reverse
from django.db import transaction

from workflows.models import Tenant
from workflows.views import TenantMixin
from workflows.tenant import current_tenant_id

from projects.models import Project, Release, Epic, Roadmap
from boards.models import Board
from .models import Domain, Requirement, Constraint, Target, TargetSection, Category, Team
from . import forms

class DomainList(TenantMixin, ListView):
    model = Domain
    template_name = 'compliances/domain-list.html'
    context_object_name = 'domains'

class DomainProjectSetup(TenantMixin, DetailView):
    model = Project
    template_name = 'compliances/domain-project-setup.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant_id = self.kwargs['tenant_id']
        project_id = self.kwargs['pk']
        project = get_object_or_404(Project, tenant_id=tenant_id, pk=project_id)
        context['targets'] = Target.objects.filter(project_id=project_id)
        context['teams'] = Team.objects.filter(project_id=project_id)
        return context

class DomainCreateProject(TenantMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        tenant_id = self.kwargs['tenant_id']
        domain_id = self.kwargs['pk']
        domain = get_object_or_404(Domain, tenant_id=tenant_id, pk=domain_id)
        project, created = Project.objects.get_or_create(tenant_id=tenant_id, defaults={'name': domain.name + ' ' + _('project')})
        project.domains.add(domain)
        return reverse('compliances:domain-list', kwargs={"tenant_id": tenant_id})

class DomainDetail(TenantMixin, DetailView):
    model = Domain
    template_name = 'compliances/domain-detail.html'
    context_object_name = 'domain'

class DomainSpec(TenantMixin, DetailView):
    model = Domain
    template_name = 'compliances/domain-spec.html'
    context_object_name = 'domain'

class DomainProjectCreateBacklog(TenantMixin, FormView):
    template_name = 'compliances/domain-project-create-backlog.html'
    #form_class = forms.BakclogCreateForm

    def create_backlog_from_roadmap(self, tenant, project, sprint_length_in_days, number_of_stories_in_sprint):
        backlog = Backlog(project=project)
        backlog.save()
        for release in project.roadmap.releases:
            stories = []
            for epic in release.epics:
                for constraint in epic.statement.constraints:
                    story = Story(name=epic.target + ': ' + constraint.text, description=constraint.description, epic=epic, tenant_id=tenant.id, constraint=constraint)
                    stories.append(story)
        number_of_sprints = math.ceil(len(stories)/number_of_stories_in_sprint)
        for i in range(number_of_sprints):
            end_date = start_date + timedelta(sprint_length_in_days)
            sprint_name = f'Sprint {i + 1}'
            sprint = Sprint(name=sprint_name, start_date=start_date, end_date=end_date, board=backlog, tenant_id=tenant.id)
            sprint.save()
            this_sprint_stories = stories[number_of_stories_in_sprint * i:number_of_stories_in_sprint * (i + 1)]
            for story in this_sprint_stories:
                story.sprint = sprint
                story.save()
            backlog.sprints.add(sprint)
            start_date = end_date + timedelta(days=1)
        end_date = start_date + timedelta(sprin_length_in_days)

    def get_redirect_url(self, *args, **kwargs):
        tenant_id = self.kwargs['tenant_id']
        domain_id = self.kwargs['domain_id']
        domain = get_object_or_404(Domain, tenant_id=tenant_id, pk=domain_id)
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, tenant_id=tenant_id, pk=project_id)
        backlog = self.create_backlog(domain, project)
        return reverse('boards:board', kwargs={"tenant_id": tenant_id, "board_type": backlog.board_type, "board_uuid": backlog.uuid})

class DomainProjectCreateRoadmap(TenantMixin, FormView):
    template_name = 'compliances/domain-project-create-roadmap.html'
    form_class = forms.RoadmapCreateForm

    def get_releases_and_epics(self, project, targets, start_date, release_length_in_days, epics_in_release):
        epic_names = {}
        domain = project.domains.all().first()
        for target in targets.order_by('name'):
            for category in Category.objects.filter(domain=domain).order_by('index'):
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
            release_name = f'0.{i + 1}.0'
            release = Release(name=release_name, start_date=start_date, end_date=end_date)
            this_release_epics = epics[epics_in_release * i:epics_in_release * (i + 1)]
            for epic in this_release_epics:
                release_epics[release_name].append(epic)
            releases.append(release)
            start_date = end_date + timedelta(days=1)
        end_date = start_date + timedelta(release_length_in_days)
        final_release = Release(name='1.0.0', start_date=start_date, end_date=end_date)
        releases.append(final_release)
        release_epic = Epic(name=_("Project finalization"), list=final_release)
        release_epics[final_release.name].append(release_epic)
        return releases, release_epics

    def post(self, request, tenant_id, pk, project_id):

        form = self.form_class(request.POST)
        tenant = get_object_or_404(Tenant, pk=tenant_id)

        if form.is_valid():

            start_date = form.cleaned_data['start_date']
            release_length_in_days =  form.cleaned_data['release_length_in_days']
            epics_in_release =  form.cleaned_data['epics_in_release']

            project = get_object_or_404(Project, tenant_id=tenant_id, pk=project_id)
            targets = Target.objects.filter(project_id=project_id).prefetch_related('target_sections', 'target_sections__section')

            releases, epics_in_releases = self.get_releases_and_epics(project, targets, start_date, release_length_in_days, epics_in_release)

            if request.POST.get("create", False):
                with transaction.atomic():
                    roadmap = Roadmap.objects.create(name=project.name + ' ' + _('roadmap'), tenant_id=tenant.id, project=project)

                    releases_by_name = {}
                    for release_idx, release in enumerate(releases):
                        release.tenant_id = tenant.id
                        release.board_id = roadmap.id
                        release.project_id = project.id
                        release.index = release_idx
                        releases_by_name[release.name] = release
                        release.save()

                    for release_name, epics in epics_in_releases.items():
                        for epic_idx, epic in enumerate(epics):
                            epic.tenant_id = tenant.id
                            epic.list_id = releases_by_name[release_name].id
                            epic.index = epic_idx
                            epic.save()

                return redirect("boards:board", tenant_id=tenant.id, board_type=Board.BOARD_TYPE_ROADMAP, board_uuid=roadmap.uuid)
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
        project_id = self.kwargs['project_id']
        tenant_id = self.kwargs['tenant_id']
        project = get_object_or_404(Project, tenant_id=tenant_id, pk=project_id)
        targets = Target.objects.filter(project_id=project_id).prefetch_related('target_sections', 'target_sections__section')
        context = super().get_context_data(**kwargs)
        context['project'] = project
        context['targets'] = targets
        return context

class DomainProjectTargetAudit(TenantMixin, DetailView):
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
    domain = project.domains.first()
    response = render(request, template, {"tenant_id": tenant_id, "project": project, "targets": targets, "domain": domain})
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
