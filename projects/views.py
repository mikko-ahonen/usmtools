import math
import logging

from collections import defaultdict
from datetime import timedelta

from django.http import HttpResponseRedirect
from django.utils.dateparse import parse_date
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, get_object_or_404
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

from .models import Project, Release, Epic
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


class ProjectDashboard(TenantMixin, DetailView):
    model = Project
    template_name = 'projects/project-dashboard.html'
    context_object_name = 'project'

    def get_context_data(self, *args, **kwargs):
        tenant_id = self.kwargs.get('tenant_id')
        context = super().get_context_data(*args, **kwargs)
        project = self.get_object()
        context['domain'] = project.domains.first()
        return context

class ProjectRoadmap(TenantMixin, DetailView):
    model = Project
    template_name = 'projects/project-roadmap.html'
    context_object_name = 'project'


class ProjectBacklog(TenantMixin, DetailView):
    model = Project
    template_name = 'projects/project-backlog.html'
    context_object_name = 'project'


class ProjectSprint(TenantMixin, DetailView):
    model = Project
    template_name = 'projects/project-sprint.html'
    context_object_name = 'project'


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
