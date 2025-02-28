from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
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


class GetRequirementMixin():
    _requirement = None

    def get_requirement(self, requirement_id):
        if self._requirement is None:
            self._requirement = Requirement.objects.get(pk=requirement_id)
        return self._requirement


class GetStatementMixin():
    _statement = None

    def get_statement(self, statement_id):
        if self._statement is None:
            self._statement = Statement.objects.get(pk=statement_id)
        return self._statement


class GetConstraintMixin():
    _constraint = None

    def get_constraint(self, constraint_id):
        if self._constraint is None:
            self._constraint = Constraint.objects.get(pk=constraint_id)
        return self._constraint


class CrossReferenceList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = CrossReference
    template_name = 'xref/cross-reference-list.html'
    context_object_name = 'cross_references'
    permission_required = 'xref.view_cross_reference'


class CrossReferenceDetail(LoginRequiredMixin, PermissionRequiredMixin, GetCrossReferenceMixin, GetSectionMixin, GetRequirementMixin, GetStatementMixin, GetConstraintMixin, TemplateView):
    permission_required = 'xref.view_cross_reference'

    template_name = 'xref/cross-reference-detail.html'

    def get_context_data(self, **kwargs):
        xref_id = self.kwargs.get('cross_reference_id', None)
        section_id = self.kwargs.get('section_id', None)
        requirement_id = self.kwargs.get('requirement_id', None)
        statement_id = self.kwargs.get('statement_id', None)
        constraint_id = self.kwargs.get('constraint_id', None)

        xref = None
        section = None
        requirement = None
        statement = None
        constraint = None

        if constraint_id:
            constraint = self.get_constraint(constraint_id)
            statement = self.get_statement(statement_id)
        elif statement_id:
            statement = self.get_statement(statement_id)
        elif requirement_id:
            requirement = self.get_requirement(requirement_id)
        elif section_id:
            section = self.get_section(section_id)
        elif xref_id:
            xref = self.get_cross_reference(xref_id)
        else:
            ValueError("No ids")

        if not xref:
            if not section:
                if not requirement:
                    requirement = statement.requirement
                section = requirement.section
            xref = section.domain.cross_reference
    
        context = super().get_context_data(**kwargs)
        context['xref'] = xref
        context['selected_section'] = section
        context['selected_requirement'] = requirement
        context['selected_statement'] = statement
        context['selected_constraint'] = constraint
        return context


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
                xref_id = self.object.parent.domain.cross_reference.id

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
        return HttpResponseRedirect(reverse_lazy('xref:requirement-detail', kwargs={'requirement_id': self.object.id}))


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
        return HttpResponseRedirect(reverse_lazy('xref:statement-detail', kwargs={'statement_id': self.object.id}))


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
        return reverse_lazy('xref:statement-detail', kwargs={'statement_id': self.object.id})


class StatementDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Statement
    template_name = 'xref/modals/delete.html'
    permission_required = 'xref.delete_statement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('statement')
        return context

    def get_success_url(self):
        statement_id = self.kwargs.get('statement_id')
        return reverse_lazy('xref:requirement-detail', kwargs={'requirement_id': self.object.requirement_id})


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
        return HttpResponseRedirect(reverse_lazy('xref:constraint-detail', kwargs={'statement_id': statement_id, 'constraint_id': self.object.id}))


class ConstraintUpdate(LoginRequiredMixin, PermissionRequiredMixin, GetStatementMixin, UpdateView, UpdateModifiedByMixin):
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
        constraint_id = self.kwargs['pk']
        statement_id = self.kwargs['statement_id']
        statement = self.get_statement(statement_id)
        return reverse_lazy('xref:constraint-detail', kwargs={'statement_id': statement_id, 'constraint_id': constraint_id})


class ConstraintDelete(LoginRequiredMixin, GetStatementMixin, PermissionRequiredMixin, DeleteView):
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
        statement = self.get_statement(statement_id)
        return reverse_lazy('xref:statement-detail', kwargs={'statement_id': statement_id})
