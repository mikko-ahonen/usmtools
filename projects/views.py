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

#from compliances.models import Domain, Requirement, Constraint, Target, TargetSection, Category
from .models import Project, Release, Epic
#from boards.models import Board, List, Task

class ProjectList(TenantMixin, ListView):
    model = Project
    template_name = 'compliances/project-list.html'
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
