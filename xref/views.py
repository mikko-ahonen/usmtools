from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import PermissionRequiredMixin

from .models import Standard, Control, Requirement, Statement, Substatement
from .forms import StandardCreateOrUpdate, ControlCreateOrUpdate, RequirementCreateOrUpdate, StatementCreateOrUpdate, SubstatementCreateOrUpdate

class UpdateModifiedByMixin():
    def form_valid(self, form):
       object = form.save(commit=False)
       form.modified_by = self.request.user
       form.save()
       return super().form_valid(form)


class StandardList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Standard
    template_name = 'xref/standard-list.html'
    context_object_name = 'standards'
    permission_required = 'xref.view_standard'

    permission_required = 'xref.view_standard'


class StandardDetail(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'xref.view_standard'

    model = Standard
    template_name = 'xref/standard-detail.html'
    context_object_name = 'standard'


class StandardCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Standard
    template_name = 'xref/modals/create-or-update.html'
    form_class = StandardCreateOrUpdate
    permission_required = 'xref.add_standard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('standard')
        context['help_text'] = _('You should create a new standard for each standard or framework you want to map to USM.')
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        #self.object.owner = self.request.user
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('xref:standard-detail', kwargs={'pk': self.object.id }))


class StandardUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView, UpdateModifiedByMixin):
    model = Standard
    template_name = 'xref/modals/create-or-update.html'
    form_class = StandardCreateOrUpdate
    permission_required = 'xref.change_standard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('standard')
        context['help_text'] = _('You should create a new standard for each standard or framework you want to map to USM.')
        return context

    def get_success_url(self):
        return reverse_lazy('xref:standard-list')


class StandardDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Standard
    template_name = 'xref/modals/delete.html'
    permission_required = 'xref.delete_standard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('standard')
        return context

    def get_success_url(self):
        return reverse_lazy('xref:standard-list')


class ControlCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Standard
    form_class = ControlCreateOrUpdate
    template_name = 'xref/modals/create-or-update.html'
    permission_required = 'xref.add_control'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('control')
        context['help_text'] = _('You should create a new control for each part of your standard.')
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        #self.object.owner = self.request.user
        standard_id = self.kwargs['pk']
        self.object.standard_id = standard_id
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('xref:standard-detail', kwargs={'pk': standard_id}))


class ControlUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView, UpdateModifiedByMixin):
    model = Control
    template_name = 'xref/modals/create-or-update.html'
    form_class = ControlCreateOrUpdate
    permission_required = 'xref.change_control'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('control')
        context['help_text'] = _('You should create a new control for each part of your standard.')
        return context

    def get_success_url(self):
        return reverse_lazy('xref:standard-detail', kwargs={'pk': self.object.standard_id})


class ControlDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Control
    template_name = 'xref/modals/delete.html'
    permission_required = 'xref.delete_control'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('control')
        return context

    def get_success_url(self):
        return reverse_lazy('xref:standard-detail', kwargs={'pk': self.object.standard_id})


class ControlDetail(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Control
    template_name = 'xref/control-detail.html'
    context_object_name = 'control'
    permission_required = 'xref.view_standard'

    def get(self, request, pk=None):
        o = self.get_object()
        r = o.requirements.first()
        if r:
            return HttpResponseRedirect(reverse_lazy('xref:requirement-detail', kwargs={'pk': o.id, 'requirement_id': r.id}))
        return super().get(request, pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selections'] = { }
        return context

class RequirementDetail(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Control
    template_name = 'xref/control-detail.html'
    context_object_name = 'control'
    permission_required = 'xref.view_standard'

    def get(self, request, pk=None, requirement_id=None):
        o = self.get_object()
        r = get_object_or_404(Requirement, pk=requirement_id)
        s = r.statements.first()
        if s:
            return HttpResponseRedirect(reverse_lazy('xref:statement-detail', kwargs={'pk': o.id, 'requirement_id': r.id, 'statement_id': s.id}))
        return super().get(request, pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_requirement = get_object_or_404(Requirement, pk=self.kwargs['requirement_id'])
        context['selections'] = {
            'requirement_id': str(self.kwargs['requirement_id']),
        }
        context['selected_requirement'] = selected_requirement
        return context

class StatementDetail(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Control
    template_name = 'xref/control-detail.html'
    context_object_name = 'control'
    permission_required = 'xref.view_standard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_requirement = get_object_or_404(Requirement, pk=self.kwargs['requirement_id'])
        selected_statement = get_object_or_404(Statement, pk=self.kwargs['statement_id'])
        context['selections'] = {
            'requirement_id': str(self.kwargs['requirement_id']),
            'statement_id': str(self.kwargs['statement_id']),
        }
        context['selected_requirement'] = selected_requirement
        context['selected_statement'] = selected_statement
        return context


class RequirementCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Requirement
    template_name = 'xref/modals/create-or-update.html'
    form_class = RequirementCreateOrUpdate
    permission_required = 'xref.add_requirement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('requirement')
        context['help_text'] = _('You should decompose the control into requirements.')
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        #self.object.owner = self.request.user
        self.object.start_pos = 1
        self.object.end_pos = 1
        control_id = self.kwargs['pk']
        self.object.control_id = control_id
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('xref:requirement-detail', kwargs={'pk': control_id, 'requirement_id': self.object.id}))


class RequirementUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView, UpdateModifiedByMixin):
    model = Requirement
    template_name = 'xref/modals/create-or-update.html'
    form_class = RequirementCreateOrUpdate
    permission_required = 'xref.change_requirement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('requirement')
        context['help_text'] = _('You should decompose the control into requirements.')
        return context

    def get_success_url(self):
        return reverse_lazy('xref:control-detail', kwargs={'pk': self.object.control_id})


class RequirementDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Requirement
    template_name = 'xref/modals/delete.html'
    permission_required = 'xref.delete_requirement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('requirement')
        return context

    def get_success_url(self):
        return reverse_lazy('xref:control-detail', kwargs={'pk': self.object.control_id})


class StatementCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Statement
    template_name = 'xref/modals/create-or-update.html'
    form_class = StatementCreateOrUpdate
    permission_required = 'xref.add_statement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('statement')
        context['help_text'] = _('You should create one or more USM statements to cover the requirement.')
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        #self.object.owner = self.request.user
        requirement_id = self.kwargs['pk']
        self.object.requirement_id = requirement_id
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('xref:statement-detail', kwargs={'pk': self.object.requirement.control_id, 'requirement_id': self.object.requirement_id, 'statement_id': self.object.id}))


class StatementUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView, UpdateModifiedByMixin):
    model = Statement
    template_name = 'xref/modals/create-or-update.html'
    form_class = StatementCreateOrUpdate
    permission_required = 'xref.change_statement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('statement')
        context['help_text'] = _('You should create one or more USM statements to cover the requirement.')
        return context

    def get_success_url(self):
        return reverse_lazy('xref:control-detail', kwargs={'pk': self.object.requirement.control_id})


class StatementDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Statement
    template_name = 'xref/modals/delete.html'
    permission_required = 'xref.delete_statement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('statement')
        return context

    def get_success_url(self):
        return reverse_lazy('xref:control-detail', kwargs={'pk': self.object.requirement.control_id})


class SubstatementCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Substatement
    template_name = 'xref/modals/create-or-update.html'
    form_class = SubstatementCreateOrUpdate
    permission_required = 'xref.add_substatement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('substatement')
        context['help_text'] = _('You should create one or more formal substatements to cover the USM statement.')
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        #self.object.owner = self.request.user
        statement_id = self.kwargs['pk']
        statement = get_object_or_404(Statement, pk=statement_id)
        self.object.save()
        self.object.statements.add(statement)
        return HttpResponseRedirect(reverse_lazy('xref:statement-detail', kwargs={'pk': statement.requirement.control_id, 'requirement_id': statement.requirement_id, 'statement_id': statement_id}))


class SubstatementUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView, UpdateModifiedByMixin):
    model = Substatement
    template_name = 'xref/modals/create-or-update.html'
    form_class = SubstatementCreateOrUpdate
    permission_required = 'xref.change_substatement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('substatement')
        context['help_text'] = _('You should create one or more formal substatements to cover the USM statement.')
        return context

    def get_success_url(self):
        substatement_id = self.kwargs['pk']
        statement_id = self.kwargs['statement_id']
        statement = get_object_or_404(Statement, pk=statement_id)
        return reverse_lazy('xref:statement-detail', kwargs={'pk': statement.requirement.control_id, 'requirement_id': statement.requirement_id, 'statement_id': statement_id})


class SubstatementDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Substatement
    template_name = 'xref/modals/delete.html'
    permission_required = 'xref.delete_substatement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('substatement')
        return context

    def get_success_url(self):
        substatement_id = self.kwargs['pk']
        statement_id = self.kwargs['statement_id']
        statement = get_object_or_404(Statement, pk=statement_id)
        return reverse_lazy('xref:statement-detail', kwargs={'pk': statement.requirement.control_id, 'requirement_id': statement.requirement_id, 'statement_id': statement_id})
