from collections import defaultdict

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, FormView, RedirectView
from django.utils.translation import gettext as _
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy

from workflows.models import Tenant
from workflows.views import TenantMixin
from workflows.tenant import current_tenant_id

from .models import Domain, Requirement, Constraint, Target, TargetSection, Project, Release, Epic, Category
from . import forms

class DomainList(TenantMixin, ListView):
    model = Domain
    template_name = 'compliances/domain-list.html'
    context_object_name = 'domains'

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
        project, created = Project.objects.get_or_create(tenant_id=tenant_id, domain=domain, defaults={'name': _('Project for ') + domain.name})
        return reverse_lazy('compliances:project-setup', kwargs={"tenant_id": tenant_id, "pk": project.id})

class DomainDetail(TenantMixin, DetailView):
    model = Domain
    template_name = 'compliances/domain-detail.html'
    context_object_name = 'domain'

class ProjectRoadmapCreate(TenantMixin, FormView):
    template_name = 'compliances/project-roadmap-create.html'
    form_class = forms.RoadmapCreateForm

    def get_releases_and_epics(self, project, targets, start_date, release_length_in_days, epics_in_release):
        breakpoint()
        epics = []
        for target in targets.order_by('name'):
            for category in Category.objects.filter(domain=project.domain).order_by('index'):
                epics.append(Epic(name=category.name + " " + target))
        number_of_releases = int(len(epics)/epics_in_release) + 1
        releases = []
        epics_in_release = defaultdict(list)
        for i in range(number_of_releases):
            release = Release(name=f'0.{i}.0')
            release_epics = epics[100 * i:100 * (i + 1)]
            for epic in release_epics:
                epics_in_release[release.id].append(epic)
            releases.append(release)
        final_release = Release(name='1.0.0')
        releases.append(final_release)
        release_epic = Epic(name=_("Project finalization"), release=final_release)
        epics_in_release[release_epic.id].append(release_epic)
        return releases, epics_in_release

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

            releases, epics = self.get_releases_and_epics(project, targets, start_date, release_length_in_days, epics_in_release)

            if 'confirm' in form.cleaned_data:
                with transaction.atomic():
                    board = Board.objects.create(name=project.name + ' ' + _('roadmap'), type=Board.BOARD_TYPE_ROADMAP, project=project)
                
                    for release in releases:
                        release.save()

                    for release_id, epic in epics.items():
                        epic.release_id = release_id
                        epic.save()

                    for release in releases:
                        l = List.objects.create(name=release.name, board=board, type=List.LIST_TYPE_RELEASE, content_object=release)
                        for epic in release.epics:
                            Task.objects.create(name=epic.name, list=l, type=Task.TASK_TYPE_EPIC, content_object=epic)

                return redirect("boards:board", uuid=board.uuid)
            else:
                context = {
                    'releases': releases,
                    'epics': epics,
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
