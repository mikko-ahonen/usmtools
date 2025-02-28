from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import PermissionRequiredMixin

from .models import CrossReference
from compliances.models import Section, Requirement, Statement, Constraint, Definition, Domain
from .forms import CrossReferenceCreateOrUpdate, SectionCreateOrUpdate, RequirementCreateOrUpdate, StatementCreateOrUpdate, ConstraintCreateOrUpdate 

class UpdateModifiedByMixin():
    def form_valid(self, form):
       object = form.save(commit=False)
       form.modified_by = self.request.user
       form.save()
       return super().form_valid(form)


class GetCrossReferenceMixin():
    _xref = None

    def get_cross_reference(self, xref_id):
        if self._xref is None:
            self._xref = CrossReference.objects.get(pk=xref_id)
        return self._xref


class GetSectionMixin():
    _section = None

    def get_section(self, section_id):
        if self._section is None:
            self._section = Section.objects.get(pk=section_id)
        return self._section


class CrossReferenceList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = CrossReference
    template_name = 'xref/cross-reference-list.html'
    context_object_name = 'cross_references'
    permission_required = 'xref.view_cross_reference'


class CrossReferenceDetail(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'xref.view_cross-reference'

    model = CrossReference
    template_name = 'xref/cross-reference-detail.html'
    context_object_name = 'xref'


class CrossReferenceCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = CrossReference
    template_name = 'xref/modals/create-or-update.html'
    form_class = CrossReferenceCreateOrUpdate
    permission_required = 'xref.add_cross_reference'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('cross-reference')
        context['help_text'] = _('Create a new cross-reference for the standard or framework you want to cross-reference to the USM method. Cross-references are templates and shered between all tenants, and can be accessed by anybody with the cross-references permisisons.')
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        #self.object.owner = self.request.user
        self.object.domain = Domain.objects.create(tenant_id=None, name=self.object.name, description=self.object.description)
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('xref:cross-reference-detail', kwargs={'pk': self.object.id }))


class CrossReferenceUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView, UpdateModifiedByMixin):
    model = CrossReference
    template_name = 'xref/modals/create-or-update.html'
    form_class = CrossReferenceCreateOrUpdate
    permission_required = 'xref.change_cross-reference'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('cross-reference')
        context['help_text'] = _('Create a new cross-reference for the standard or framework you want to cross-reference to the USM method. Cross-references are templates and shered between all tenants, and can be accessed by anybody with the cross-references permisisons.')
        return context

    def get_success_url(self):
        return reverse_lazy('xref:cross-reference-list')


class CrossReferenceDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = CrossReference
    template_name = 'xref/modals/delete.html'
    permission_required = 'xref.delete_cross-reference'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('cross-reference')
        return context

    def get_success_url(self):
        return reverse_lazy('xref:cross-reference-list')


class SectionCreate(LoginRequiredMixin, PermissionRequiredMixin, GetSectionMixin, GetCrossReferenceMixin, CreateView):
    model = Section
    form_class = SectionCreateOrUpdate
    template_name = 'xref/modals/create-or-update.html'
    permission_required = 'xref.add_section'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('section')
        context['help_text'] = _('You should create a new section for each section and subsection of the specification you are cross-referencing.')
        return context

    def form_valid(self, form):
        if not form.cleaned_data['index']:
            form.cleaned_data['docid'].split('.')[-1]
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        xref_id = self.kwargs.get('cross_reference_id', None)
        if xref_id:
            xref = self.get_cross_reference(xref_id)
            self.object.domain_id = xref.domain_id
        else:
            parent_section_id = self.kwargs.get('pk', None)
            if parent_section_id:
                self.object.parent = self.get_section(parent_section_id)
                self.object.domain_id = self.object.parent.domain_id
                xref_id = self.object.parent.domain.xref.id

        if not xref_id:
            raise ValueError("No parent section or cross-reference")

        self.object.save()

        return HttpResponseRedirect(reverse_lazy('xref:cross-reference-detail', kwargs={'pk': xref_id}))


class SectionUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView, UpdateModifiedByMixin):
    model = Section
    template_name = 'xref/modals/create-or-update.html'
    form_class = SectionCreateOrUpdate
    permission_required = 'xref.change_section'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('section')
        context['help_text'] = _('You should create a new section for each section and subsection of the specification you are cross-referencing.')
        return context

    def get_success_url(self):
        return reverse_lazy('xref:cross-reference-detail', kwargs={'pk': self.object.cross-reference_id})


class SectionDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Section
    template_name = 'xref/modals/delete.html'
    permission_required = 'xref.delete_section'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('section')
        return context

    def get_success_url(self):
        return reverse_lazy('xref:cross-reference-detail', kwargs={'pk': self.object.cross_reference_id})


class SectionDetail(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Section
    template_name = 'xref/section-detail.html'
    context_object_name = 'section'
    permission_required = 'xref.view_cross_reference'

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
    model = Requirement
    template_name = 'xref/section-detail.html'
    context_object_name = 'section'
    permission_required = 'xref.view_cross_reference'

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
    model = Section
    template_name = 'xref/section-detail.html'
    context_object_name = 'section'
    permission_required = 'xref.view_cross-reference'

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
        context['help_text'] = _('You should decompose the section into requirements.')
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        #self.object.owner = self.request.user
        self.object.start_pos = 1
        self.object.end_pos = 1
        section_id = self.kwargs['pk']
        self.object.section_id = section_id
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('xref:requirement-detail', kwargs={'pk': section_id, 'requirement_id': self.object.id}))


class RequirementUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView, UpdateModifiedByMixin):
    model = Requirement
    template_name = 'xref/modals/create-or-update.html'
    form_class = RequirementCreateOrUpdate
    permission_required = 'xref.change_requirement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('requirement')
        context['help_text'] = _('You should decompose the section into requirements.')
        return context

    def get_success_url(self):
        return reverse_lazy('xref:section-detail', kwargs={'pk': self.object.section_id})


class RequirementDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Requirement
    template_name = 'xref/modals/delete.html'
    permission_required = 'xref.delete_requirement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('requirement')
        return context

    def get_success_url(self):
        return reverse_lazy('xref:section-detail', kwargs={'pk': self.object.section_id})


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
        return HttpResponseRedirect(reverse_lazy('xref:statement-detail', kwargs={'pk': self.object.requirement.section_id, 'requirement_id': self.object.requirement_id, 'statement_id': self.object.id}))


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
        return reverse_lazy('xref:secrion-detail', kwargs={'pk': self.object.requirement.section_id})


class StatementDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Statement
    template_name = 'xref/modals/delete.html'
    permission_required = 'xref.delete_statement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('statement')
        return context

    def get_success_url(self):
        return reverse_lazy('xref:section-detail', kwargs={'pk': self.object.requirement.section_id})


class ConstraintCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Constraint
    template_name = 'xref/modals/create-or-update.html'
    form_class = ConstraintCreateOrUpdate
    permission_required = 'xref.add_constraint'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('constraint')
        context['help_text'] = _('You often need to create formal constraints that cover the USM statement.')
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
        return HttpResponseRedirect(reverse_lazy('xref:statement-detail', kwargs={'pk': statement.requirement.section_id, 'requirement_id': statement.requirement_id, 'statement_id': statement_id}))


class ConstraintUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView, UpdateModifiedByMixin):
    model = Constraint
    template_name = 'xref/modals/create-or-update.html'
    form_class = ConstraintCreateOrUpdate
    permission_required = 'xref.change_constraint'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('constraint')
        context['help_text'] = _('You should create one or more formal constraints that cover the USM statement.')
        return context

    def get_success_url(self):
        #constraint_id = self.kwargs['pk']
        statement_id = self.kwargs['statement_id']
        statement = get_object_or_404(Statement, pk=statement_id)
        return reverse_lazy('xref:statement-detail', kwargs={'pk': statement.requirement.section_id, 'requirement_id': statement.requirement_id, 'statement_id': statement_id})


class ConstraintDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Constraint
    template_name = 'xref/modals/delete.html'
    permission_required = 'xref.delete_constraint'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('constraint')
        return context

    def get_success_url(self):
        #constraint_id = self.kwargs['pk']
        statement_id = self.kwargs['statement_id']
        statement = get_object_or_404(Statement, pk=statement_id)
        return reverse_lazy('xref:statement-detail', kwargs={'pk': statement.requirement.section_id, 'requirement_id': statement.requirement_id, 'statement_id': statement_id})
