from collections import defaultdict
from datetime import timedelta
from django.utils.dateparse import parse_date
import math

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, FormView, RedirectView, TemplateView
from django.utils.translation import gettext as _
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.db import transaction

from workflows.models import Tenant
from workflows.views import TenantMixin
from workflows.tenant import current_tenant_id

from projects.models import Project, Release, Epic, Roadmap, Story, Backlog
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
        domain_id = self.kwargs['domain_id']
        domain = get_object_or_404(Domain, tenant_id=tenant_id, id=domain_id)
        context['targets'] = Target.objects.filter(project_id=project_id)
        context['root_sections'] = domain.root_sections.order_by('-doc', 'index')
        context['ordered_categories'] = domain.categories.filter(tenant_id=tenant_id, domain=domain_id).order_by('index')
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

class DomainConstraints(TenantMixin, ListView):
    model = Constraint
    template_name = 'compliances/domain-constraints.html'
    context_object_name = 'constraints'

    def get_queryset(self, **kwargs):
        tenant_id = self.kwargs['tenant_id']
        domain_id = self.kwargs['pk']
        qs = Constraint.unscoped.filter(tenant_id=tenant_id, domain_id=domain_id)
        return qs.order_by('text')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant_id = self.kwargs['tenant_id']
        domain_id = self.kwargs['pk']
        domain = get_object_or_404(Domain, tenant_id=tenant_id, pk=domain_id)
        context['domain'] = domain
        return context

class DomainProjectCreateBacklog(TenantMixin, TemplateView):
    template_name = 'compliances/domain-project-create-backlog.html'
    #form_class = forms.BacklogCreateForm

    def get_sprints_and_stories(self, tenant, project):
        sprint_stories = defaultdict(list)
        team_sprints = defaultdict(list)
        sprints = []
        team_stories = defaultdict(list)
        for release in project.roadmap.releases.all().order_by('start_date'):
            for epic in release.epics.all().order_by('index'):
                # No category => Create generic story for all the teams
                if not epic.category:
                    for team in project.teams:
                        story = Story(tenant=tenant, name=_('Common') + ': ' + epic.name[:100], description=epic.description, epic=epic, tenant_id=tenant.id, constraint=None)
                        team_id = str(team.id)
                        team_stories[team_id].append(story)
                    continue
                for constraint in epic.category.constraints.all():
                    story = Story(tenant=tenant, name=epic.category.name + ': ' + constraint.text[:100], description=constraint.text, epic=epic, tenant_id=tenant.id, constraint=constraint, team=epic.category.team)
                    team_id = str(epic.category.team.id)
                    team_stories[team_id].append(story)

        teams = defaultdict(dict)

        for team in project.teams:
            team_id = str(team.id)
            team_sprints, team_sprint_stories = self.get_team_sprints_and_stories(tenant, project, team, team_stories[team_id])
            teams[team_id] = {
                'team': team,
                'sprints': team_sprints,
                'sprint_stories': team_sprint_stories,
            }

        return teams

    def get_team_sprints_and_stories(self, tenant, project, team, stories):

        number_of_sprints = self.get_number_of_sprints(stories, project.storypoints_in_sprint)

        start_date = None
        end_date = None
        for i in range(number_of_sprints):
            if not start_date:
                start_date = project.start_date
            else:
                start_date = end_date + timedelta(days=1)

            end_date = start_date + timedelta(project.sprint_length_in_days)
            sprint_name = f'Team {team.name} sprint {i + 1}'
            sprint = Sprint(tenant=tenant, name=sprint_name, start_date=start_date, end_date=end_date, tenant_id=tenant.id, team=team)
            sprints.append(sprint)

            for story in self.get_sprint_stories(stories, project.storypoints_in_sprint, i):
                sprint_stories[sprint.name].append(story)

        return sprints, sprint_stories

    # TODO: does not use story points
    def get_number_of_sprints(self, stories, number_of_storypoints_in_sprint):
        return math.ceil(len(stories)/number_of_storypoints_in_sprint)

    # TODO: does not use story points
    def get_sprint_stories(self, stories, number_of_storypoints_in_sprint, i):
        return stories[number_of_storypoints_in_sprint * i:number_of_storypoints_in_sprint * (i + 1)]

    def create_backlog(self, project, sprints, stories_in_sprints):
        backlog = Backlog(project=project)
        backlog.save()
        for sprint in sprints:
            sprint.board = backlog
            sprint.save()
            for story in stories_in_sprints[sprint.name]:
                story.sprint = sprint
                story.save()
        return backlog

    def post(self, request, tenant_id, pk, project_id):
        context = self.get_context(request, tenant_id, pk, project_id)

        if request.POST.get("create", False):
            with transaction.atomic():
                backlog = self.create_backlog(context['domain'], context['project'], context['sprints'], context['stories_in_sprints'])
                return reverse('compliances:domain-list', kwargs={"tenant_id": tenant_id, "pk": pk})
        else:
            return render(request, self.template_name, context)


    def get_context(self, request, tenant_id, pk, project_id):
        tenant = get_object_or_404(Tenant, pk=tenant_id)
        domain = get_object_or_404(Domain, pk=pk)
        project = get_object_or_404(Project, pk=project_id)
        team_sprints_and_stories = self.get_sprints_and_stories(tenant, project)
        return {
            'domain': domain,
            'project': project,
            'team_sprints_and_stories': team_sprints_and_stories,
            'tenant': tenant,
        }

    def get(self, request, tenant_id, pk, project_id):
        context = self.get_context(request, tenant_id, pk, project_id)
        return render(request, self.template_name, context)

class DomainProjectCreateRoadmap(TenantMixin, FormView):
    template_name = 'compliances/domain-project-create-roadmap.html'
    form_class = forms.RoadmapCreateForm

    def get_releases_and_epics(self, project, targets, start_date, release_length_in_days, epics_in_release):
        epic_names = {}
        domain = project.domains.all().first()
        for target in targets.order_by('name'):
            for category in Category.objects.filter(domain=domain).order_by('index'):
                epic_name = str(category) + " " + str(target)
                epic_names[epic_name] = category
        epics = [Epic(name=name, category=category) for name, category in epic_names.items()]
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
    response = render(request, template, {
        "tenant_id": tenant_id,
        "project": project,
        "targets": targets,
        "domain": domain,
        "root_sections": domain.root_sections.order_by('-doc', 'index'),
    })
    response["HX-Retarget"] = "#targets"
    return response

def teams(request, project):
    tenant_id = current_tenant_id()
    teams = Team.objects.filter(project_id=project.id)
    template = "compliances/_teams.html"
    domain = project.domains.first()
    response = render(request, template, {
        "tenant_id": tenant_id, 
        "project": project, 
        "teams": teams, 
        "domain": domain,
        "ordered_categories": domain.categories.filter(tenant_id=tenant_id, domain=domain.id).order_by('index'),
    })
    response["HX-Retarget"] = "#teams"
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

# TODO: check permissions
def create_team_for_project(request, tenant_id, pk):
    project = get_object_or_404(Project, tenant_id=tenant_id, pk=pk)
    form = forms.TeamForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.instance.tenant_id = tenant_id
        form.instance.project_id = pk
        team = form.save()

    return teams(request, project)

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

def team_category_select(request, tenant_id, team_id, category_id):
    if request.method == "POST":
        new_value = (request.POST.get("selected", "off") == "on")

        category = get_object_or_404(Category, tenant_id=tenant_id, id=category_id)
        team = get_object_or_404(Team, tenant_id=tenant_id, id=team_id)

        category.team_id = team.id

        return HttpResponse("OK")
    else:
        raise Http404(f"Invalid method: {request.method}")
