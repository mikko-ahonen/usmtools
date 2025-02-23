import logging

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, FormView, TemplateView, RedirectView
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from django.http import HttpResponseRedirect

from workflows.models import Tenant

from .models import Training, Employee, Document, Risk, DataManagement
from . import forms


logger = logging.getLogger(__name__)


#######################################################################################################################
#
# MIXINS
#

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



class UpdateModifiedByMixin():
    def form_valid(self, form):
       object = form.save(commit=False)
       form.modified_by = self.request.user
       form.save()
       return super().form_valid(form)

#######################################################################################################################
#
# Dashboard
#

class Dashboard(TenantMixin, ListView):
    model = DataManagement
    template_name = 'mir/dashboard.html'
    context_object_name = 'data_managements'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['tenant'] = self.get_tenant()
        return context


#######################################################################################################################
#
# Training
#

class TrainingList(TenantMixin, ListView):
    model = Training
    template_name = 'mir/training-list.html'
    context_object_name = 'trainings'


class TrainingUpdate(TenantMixin, UpdateView, UpdateModifiedByMixin):
    model = Training
    template_name = 'mir/modals/training-create-or-update.html'
    form_class = forms.TrainingCreateOrUpdate

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        tenant_id = self.kwargs.get('tenant_id')
        kwargs['tenant_id'] = tenant_id
        return kwargs

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('mir:training-list', kwargs={'tenant_id': tenant_id})

class TrainingCreate(TenantMixin, CreateView):
    model = Training
    template_name = 'mir/modals/training-create-or-update.html'
    context_object_name = 'training'
    form_class = forms.TrainingCreateOrUpdate

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        tenant_id = self.kwargs.get('tenant_id')
        kwargs['tenant_id'] = tenant_id
        return kwargs

    def form_valid(self, form):
        tenant = self.get_tenant()
        self.object = form.save(commit=False)
        self.object.tenant = tenant
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.save()
        form.save_m2m()
        return HttpResponseRedirect(self.get_success_url()) 

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('mir:training-list', kwargs={'tenant_id': tenant_id})


class TrainingDelete(TenantMixin, DeleteView):
    model = Training
    template_name = 'mir/modals/training-delete.html'
    context_object_name = 'training'

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('mir:training-list', kwargs={'tenant_id': tenant_id})

    
#######################################################################################################################
#
# Employee
#

class EmployeeList(TenantMixin, ListView):
    model = Employee
    template_name = 'mir/employee-list.html'
    context_object_name = 'employees'


class EmployeeUpdate(TenantMixin, UpdateView, UpdateModifiedByMixin):
    model = Employee
    template_name = 'mir/modals/employee-create-or-update.html'
    form_class = forms.EmployeeCreateOrUpdate

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        tenant_id = self.kwargs.get('tenant_id')
        kwargs['tenant_id'] = tenant_id
        return kwargs

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('mir:employee-list', kwargs={'tenant_id': tenant_id})

class EmployeeCreate(TenantMixin, CreateView):
    model = Employee
    template_name = 'mir/modals/employee-create-or-update.html'
    context_object_name = 'employee'
    form_class = forms.EmployeeCreateOrUpdate

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        tenant_id = self.kwargs.get('tenant_id')
        kwargs['tenant_id'] = tenant_id
        return kwargs

    def form_valid(self, form):
        tenant = self.get_tenant()
        self.object = form.save(commit=False)
        self.object.tenant = tenant
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.save()
        form.save_m2m()
        return HttpResponseRedirect(self.get_success_url()) 

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('mir:employee-list', kwargs={'tenant_id': tenant_id})


class EmployeeDelete(TenantMixin, DeleteView):
    model = Employee
    template_name = 'mir/modals/employee-delete.html'
    context_object_name = 'employee'

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('mir:employee-list', kwargs={'tenant_id': tenant_id})

#######################################################################################################################
#
# Document
#

class DocumentList(TenantMixin, ListView):
    model = Document
    template_name = 'mir/document-list.html'
    context_object_name = 'documents'


class DocumentUpdate(TenantMixin, UpdateView, UpdateModifiedByMixin):
    model = Document
    template_name = 'mir/modals/create-or-update.html'
    form_class = forms.DocumentCreateOrUpdate

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('mir:document-list', kwargs={'tenant_id': tenant_id})

class DocumentCreate(TenantMixin, CreateView):
    model = Document
    template_name = 'mir/modals/create-or-update.html'
    form_class = forms.DocumentCreateOrUpdate

    def form_valid(self, form):
        tenant = self.get_tenant()
        self.object = form.save(commit=False)
        self.object.tenant = tenant
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.save()
        form.save_m2m()
        return HttpResponseRedirect(self.get_success_url()) 

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('mir:document-list', kwargs={'tenant_id': tenant_id})


class DocumentDelete(TenantMixin, DeleteView):
    model = Document
    template_name = 'mir/modals/delete.html'

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('mir:document-list', kwargs={'tenant_id': tenant_id})
#######################################################################################################################
#
# Risk
#

class RiskList(TenantMixin, ListView):
    model = Risk
    template_name = 'mir/risk-list.html'
    context_object_name = 'risks'


class RiskUpdate(TenantMixin, UpdateView, UpdateModifiedByMixin):
    model = Risk
    template_name = 'mir/modals/create-or-update.html'
    form_class = forms.RiskCreateOrUpdate

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('mir:risk-list', kwargs={'tenant_id': tenant_id})

class RiskCreate(TenantMixin, CreateView):
    model = Risk
    template_name = 'mir/modals/create-or-update.html'
    form_class = forms.RiskCreateOrUpdate

    def form_valid(self, form):
        tenant = self.get_tenant()
        self.object = form.save(commit=False)
        self.object.tenant = tenant
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.save()
        form.save_m2m()
        return HttpResponseRedirect(self.get_success_url()) 

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('mir:risk-list', kwargs={'tenant_id': tenant_id})


class RiskDelete(TenantMixin, DeleteView):
    model = Risk
    template_name = 'mir/modals/delete.html'

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('mir:risk-list', kwargs={'tenant_id': tenant_id})

def data_management_policy(request, tenant_id, pk):

    dm = get_object_or_404(DataManagement, tenant_id=tenant_id, pk=pk)
    if not dm.allow_policy_change:
        raise ValueError("policy for {dm} cannot be changed, built-in data types")
    policy = request.POST.get('policy', None)
    if not policy:
        raise ValueError("policy is required")
    if not DataManagement.is_valid_policy(policy):
        raise ValueError(f"policy value {policy} is not valid")
    dm.policy = policy
    dm.save()
    return HttpResponse("OK")

def data_management_status(request, tenant_id, pk):

    dm = get_object_or_404(DataManagement, tenant_id=tenant_id, pk=pk)
    status = request.POST.get('status', None)
    if not status:
        raise ValueError("status is required")
    if not DataManagement.is_valid_status(status):
        raise ValueError(f"status value {status} is not valid")
    dm.status = status
    dm.save()
    return HttpResponse("OK")
