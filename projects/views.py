import math
import logging

from collections import defaultdict
from datetime import timedelta

from django.http import HttpResponseRedirect
from django.utils.dateparse import parse_date
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, get_object_or_404
from django_filters.views import FilterView
from django.views.generic import ListView, DetailView, FormView, RedirectView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.translation import gettext as _
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.encoding import iri_to_uri
from django.shortcuts import redirect

from workflows.models import Tenant
from workflows.views import TenantMixin
from workflows.tenant import current_tenant_id

from .filters import SprintFilter, ReleaseFilter, StoryFilter
from .models import Project, Release, Epic, Sprint, Backlog, Team, Story
from . import forms

logger = logging.getLogger(__name__)

class GetTenantMixin():
    tenant = None

    def get_tenant(self, tenant_id=None):
        if self.tenant is None:
            if tenant_id is None:
                tenant_id = self.kwargs['tenant_id']
            self.tenant = Tenant.objects.get(pk=tenant_id)
        return self.tenant


class TenantMixin(LoginRequiredMixin, GetTenantMixin, UserPassesTestMixin):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['tenant'] = self.get_tenant()
        return context

    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        tenant = self.get_tenant()
        return tenant.owner_id == user.pk


class GetProjectMixin():
    project = None

    def get_project(self, id):
        if self.project is None:
            self.project = Project.objects.get(pk=id)
        return self.project


class UpdateModifiedByMixin():
    def form_valid(self, form):
       object = form.save(commit=False)
       form.modified_by = self.request.user
       form.save()
       return super().form_valid(form)


class ProjectList(TenantMixin, ListView):
    model = Project
    template_name = 'projects/project-list.html'
    context_object_name = 'projects'

    def get_queryset(self, **kwargs):
        if self.request.user.is_superuser:
            return Project.unscoped.all()
        else:
            return Project.objects.all()
        return qs

class ProjectDetail(TenantMixin, DetailView):
    model = Project
    template_name = 'projects/project-detail.html'
    context_object_name = 'project'


class ProjectSprints(TenantMixin, DetailView):
    model = Project
    template_name = 'projects/project-sprints.html'
    context_object_name = 'project'
    project = None

    def get_project(self):
        if not self.project:
            project_id = self.kwargs['pk']
            self.project = get_object_or_404(Project, pk=project_id)
        return self.project

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        project = self.get_project()
        context['domain'] = project.domains.first()
        context['project'] = project
        if hasattr(project, 'roadmap'):
            context['roadmap'] = project.roadmap
        return context

class ProjectRoadmap(TenantMixin, FilterView):
    model = Release
    template_name = 'projects/project-roadmap.html'
    context_object_name = 'releases'
    filterset_class = ReleaseFilter
    project = None

    def get_project(self):
        if not self.project:
            project_id = self.kwargs['pk']
            self.project = get_object_or_404(Project, pk=project_id)
        return self.project

    def get_context_data(self, *args, **kwargs):
        tenant_id = self.kwargs.get('tenant_id')
        context = super().get_context_data(*args, **kwargs)
        project = self.get_project()
        context['domain'] = project.domains.first()
        context['project'] = project
        if hasattr(project, 'roadmap'):
            context['roadmap'] = project.roadmap
        return context

    def get_queryset(self, form_class=None):
        tenant_id = self.kwargs['tenant_id']
        project_id = self.kwargs['pk']
        project = self.get_project()
        if hasattr(project, 'roadmap'):
            roadmap_id = project.roadmap.id # cannnot use project.roadmap_id because of one-to-one relationship
            return Release.objects.filter(board_id=project.roadmap.id, status__in=[Release.STATUS_NEW, Release.STATUS_READY, Release.STATUS_ONGOING]).order_by('index')
        return Release.objects.none()


class ProjectBacklog(TenantMixin, FilterView):
    model = Sprint
    template_name = 'projects/project-backlog.html'
    context_object_name = 'sprints'
    filterset_class = SprintFilter
    project = None

    def get_project(self):
        if not self.project:
            project_id = self.kwargs['pk']
            self.project = get_object_or_404(Project, pk=project_id)
        return self.project

    def get_context_data(self, *args, **kwargs):
        tenant_id = self.kwargs.get('tenant_id')
        project = self.get_project()
        context = super().get_context_data(*args, **kwargs)
        context['domain'] = project.domains.first()
        context['project'] = project
        if hasattr(project, 'backlog'):
            context['backlog'] = project.backlog
        return context

    def get_queryset(self, form_class=None):
        tenant_id = self.kwargs['tenant_id']
        project = self.get_project()
        if hasattr(project, 'backlog'):
            backlog_id = project.backlog.id # cannnot use project.roadmap_id because of one-to-one relationship
            return Sprint.objects.filter(board_id=project.backlog.id, status__in=[Sprint.STATUS_NEW, Sprint.STATUS_READY, Sprint.STATUS_ONGOING]).order_by('index')
        else:
            return Sprint.objects.none()

class ProjectSprint(TenantMixin, FilterView):
    model = Story
    template_name = 'projects/project-sprint.html'
    context_object_name = 'stories'
    filterset_class = StoryFilter
    project = None

    def get_filterset_kwargs(self, filterset_class):
        filterset_kwargs = super().get_filterset_kwargs(filterset_class)
        data = getattr(self.request, self.request.method, {}).copy()
        if self.request.method == 'POST' and self.request.GET:
            data.update(self.request.GET)
        filterset_kwargs.update({
            'data': data,
        })
        return filterset_kwargs

    def post(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        tenant_id = self.kwargs.get('tenant_id')
        context = super().get_context_data(*args, **kwargs)
        project_id = self.kwargs['pk']
        project = get_object_or_404(Project, pk=project_id)

        context['project'] = project
        context['domain'] = project.domains.first()

        team_id = self.kwargs.get('team_id', None)
        if team_id:
            team = get_object_or_404(Team, id=team_id)
            context['team'] = team
            context['sprint'] = team.current_sprint
            context['statuses'] = team.current_sprint.lists.order_by('index')
        else:
            sprint_id = self.kwargs.get('sprint_id', None)
            if not sprint_id:
                ValueError("team_id or sprint_id required")
            sprint = get_object_or_404(Sprint, id=sprint_id)
            context['team'] = sprint.team
            context['sprint'] = sprint
            context['statuses'] = sprint.lists.order_by('index')
        story_id = self.kwargs.get('story_id', None)
        if story_id:
            context['open_story_id'] = story_id

        return context

    def get_queryset(self, form_class=None):
        tenant_id = self.kwargs['tenant_id']
        project_id = self.kwargs['pk']
        team_id = self.kwargs.get('team_id')
        return Sprint.objects.filter(project_id=project_id, team_id=team_id, status=Sprint.STATUS_ONGOING)


class ProjectReports(TenantMixin, DetailView):
    model = Project
    template_name = 'projects/project-reports.html'
    context_object_name = 'project'


class SafeRedirectMixin():

    def get_safe_redirect_url(self, default=None):
        next_url = self.request.GET.get('next_url', None) or self.request.POST.get('next_url', None)
        if next_url:
            if url_has_allowed_host_and_scheme(next_url, None):
                return iri_to_uri(next_url)
            raise DisallowedRedirect("Suspicious URL " + next_url)
        return default

class ProjectUpdate(TenantMixin, UpdateView, UpdateModifiedByMixin, SafeRedirectMixin):
    model = Project
    template_name = 'projects/modals/project-create-or-update.html'
    form_class = forms.ProjectCreateOrUpdate

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        url = self.get_safe_redirect_url(default=reverse_lazy('projects:project-list', kwargs={'tenant_id': tenant_id}))
        return url

    def get_initial(self):
        initial = super().get_initial()
        initial['next_url'] = self.get_safe_redirect_url()

        return initial

class ProjectCreate(TenantMixin, CreateView):
    model = Project
    template_name = 'projects/modals/project-create-or-update.html'
    context_object_name = 'project'
    form_class = forms.ProjectCreateOrUpdate

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        tenant = self.get_tenant()
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.tenant = tenant
        self.object.save()
        return HttpResponseRedirect(self.get_success_url()) 

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('projects:project-list', kwargs={'tenant_id': tenant_id})


class ProjectDelete(TenantMixin, DeleteView):
    model = Project
    template_name = 'projects/modals/project-delete.html'
    context_object_name = 'project'

    def delete(self, request, *args, **kwargs):
        """Display error message if integrity error"""
        try:
            return(super().delete(request, *args, **kwargs))
        except IntegrityError:
            messages.error(request, "Project can be deleted only if it has no children")
            return render(request, template_name=self.template_name, context=self.get_context_data())

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('projects:project-list', kwargs={'tenant_id': tenant_id})
