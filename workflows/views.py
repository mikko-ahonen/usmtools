import json
import logging
import tempfile

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

from taggit.models import Tag

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Q, Prefetch
from django.utils.safestring import mark_safe
from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, FormView, TemplateView, RedirectView
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, FileResponse
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from extra_views import ModelFormSetView

from django.contrib import messages

from .rasci import RASCI

from . import forms
from .models import Service, Routine, Step, Profile, Activity, Responsibility, Instruction, Customer, Share, OrganizationUnit, Tenant, ServiceCustomer, Task, Action
from .export import export_as_usm_dif
from .diagrams import diagram

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


class GetShareMixin():
    share = None

    def get_share(self, share_id):
        if self.share is None:
            self.share = Share.objects.get(pk=share_id)
        return self.share


class GetServiceMixin():
    service = None

    def get_service(self, service_id):
        if self.service is None:
            self.service = Service.objects.get(pk=service_id)
        return self.service


class GetOrganizationUnitMixin():
    ou = None

    def get_org_unit(self, id):
        if self.ou is None:
            self.ou = OrganizationUnit.objects.get(pk=id)
        return self.ou


class GetProfileMixin():
    profile = None

    def get_profile(self, profile_id):
        if self.profile is None:
            self.profile = Profile.objects.get(pk=profile_id)
        return self.profile


class GetCustomerMixin():
    customer = None

    def get_customer(self, customer_id):
        if self.customer is None:
            self.customer = Customer.objects.get(pk=customer_id)
        return self.customer


class GetServiceCustomerMixin():
    service_customer = None

    def get_service_customer(self, service_customer_id):
        if self.service_customer is None:
            self.service_customer = ServiceCustomer.objects.get(pk=service_customer_id)
        return self.service_customer


class GetRoutineMixin():
    routine = None

    def get_routine(self, routine_id):
        if self.routine is None:
            self.routine = Routine.objects.get(pk=routine_id)
        return self.routine


class GetActivityMixin():
    activity = None

    def get_activity(self, activity_id):
        if self.activity is None:
            self.activity = Activity.objects.filter(pk=activity_id).select_related('step').select_related('step__routine').select_related('step__routine__service').first()
        return self.activity


class GetResponsibilityMixin():
    responsibility = None

    def get_responsibility(self, responsibility_id):
        if self.responsibility is None:
            self.responsibility = Responsibility.objects.filter(pk=responsibility_id).select_related('profile').select_related('action').select_related('action__activity').select_related('action__activity__step').select_related('action__activity__step__routine').first()
        return self.responsibility


class GetInstructionMixin():
    instruction = None

    def get_instruction(self, instruction_id):
        if self.instruction is None:
            self.instruction = Instruction.objects.filter(pk=instruction_id).select_related('responsibility__action').select_related('responsibility__action__activity').select_related('responsibility__action__activity__step').select_related('responsibility__action__activity__step__routine').select_related('responsibility__action__activity__step__routine__service').first()
        return self.instruction


class GetStepMixin():
    step = None

    def get_step(self, step_id):
        if self.step is None:
            self.step = Step.objects.filter(pk=self.kwargs.get('pk')).select_related('routine').select_related('routine__service').first()
        return self.step


class GetActionMixin():
    action = None

    def get_action(self, action_id):
        if self.action is None:
            self.action = Action.objects.filter(pk=action_id).select_related('activity').select_related('activity__step').select_related('activity__step__routine').select_related('activity__step__routine__service').first()
        return self.action


class GetTaskMixin():
    _task = None

    def get_task(self, task_id):
        if self._task is None:
            self._task = Task.objects.filter(pk=task_id).first()
        return self._task

class UpdateModifiedByMixin():
    def form_valid(self, form):
       object = form.save(commit=False)
       form.modified_by = self.request.user
       form.save()
       return super().form_valid(form)

#######################################################################################################################
#
# Tenant
#

class TenantList(LoginRequiredMixin, ListView):
    model = Tenant
    template_name = 'workflows/tenant-list.html'
    context_object_name = 'tenants'

    def get_queryset(self, **kwargs):
        qs = super().get_queryset()
        if self.request.user.is_anonymous:
            qs = Tenant.objects.none()
        else:
            if not self.request.user.is_superuser:
                qs = qs.filter(owner=self.request.user)
        return qs

class TenantCreate(LoginRequiredMixin, CreateView):
    model = Tenant
    template_name = 'workflows/modals/tenant-create-or-update.html'
    context_object_name = 'tenant'
    form_class = forms.TenantCreateOrUpdate

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.owner = self.request.user
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('workflows:tenant-list'))


class TenantUpdate(UserPassesTestMixin, UpdateView, UpdateModifiedByMixin):
    model = Tenant
    template_name = 'workflows/modals/tenant-create-or-update.html'
    form_class = forms.TenantCreateOrUpdate

    def get_success_url(self):
        return reverse_lazy('workflows:tenant-list')

    def get_tenant(self):
        return Tenant.objects.get(pk=self.kwargs['pk'])

    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        tenant = self.get_tenant()
        return tenant.owner_id == user.pk


class TenantDelete(UserPassesTestMixin, DeleteView):
    model = Tenant
    template_name = 'workflows/modals/tenant-delete.html'
    context_object_name = 'tenant'

    def get_success_url(self):
        return reverse_lazy('workflows:tenant-list')

    def get_tenant(self):
        return Tenant.objects.get(pk=self.kwargs['pk'])

    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        tenant = self.get_tenant()
        return tenant.owner_id == user.pk

#######################################################################################################################
#
# Organization unit
#

class OrganizationUnitList(TenantMixin, ListView):
    model = OrganizationUnit
    template_name = 'workflows/organization-unit-list.html'
    context_object_name = 'organization_units'

    def get_queryset(self, **kwargs):
        qs = super().get_queryset()
        qs = qs.filter(parent=None)
        return qs


class OrganizationUnitDetail(TenantMixin, DetailView):
    model = OrganizationUnit
    template_name = 'workflows/organization-unit-detail.html'
    context_object_name = 'organization_unit'


class OrganizationUnitUpdate(TenantMixin, UpdateView, UpdateModifiedByMixin):
    model = OrganizationUnit
    template_name = 'workflows/modals/organization-unit-create-or-update.html'
    form_class = forms.OrganizationUnitCreateOrUpdate

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('workflows:organization-unit-list', kwargs={'tenant_id': tenant_id})


class OrganizationUnitCreate(TenantMixin, CreateView):
    model = OrganizationUnit
    template_name = 'workflows/modals/organization-unit-create-or-update.html'
    context_object_name = 'organization_unit'
    form_class = forms.OrganizationUnitCreateOrUpdate
    parent = None

    def get_parent(self):
        if not self.parent:
            parent_id = self.kwargs.get('pk', None)
            self.parent = OrganizationUnit.objects.filter(id=parent_id).first()
        return self.parent

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['parent'] = self.get_parent()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['parent'] = self.get_parent()
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
        return reverse_lazy('workflows:organization-unit-list', kwargs={'tenant_id': tenant_id})



class OrganizationUnitDelete(TenantMixin, DeleteView):
    model = OrganizationUnit
    template_name = 'workflows/modals/organization-unit-delete.html'
    context_object_name = 'organization_unit'

    def delete(self, request, *args, **kwargs):
        """Display error message if integrity error"""
        try:
            return(super().delete(request, *args, **kwargs))
        except IntegrityError:
            messages.error(request, "Organization unit can be deleted only if it has no children")
            return render(request, template_name=self.template_name, context=self.get_context_data())

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('workflows:organization-unit-list', kwargs={'tenant_id': tenant_id})


    
#######################################################################################################################
#
# PROFILE
#

class ProfileList(TenantMixin, ListView):
    model = Profile
    template_name = 'workflows/profile-list.html'
    context_object_name = 'profiles'

    def get_queryset(self, **kwargs):
        qs = super().get_queryset()
        return qs


class ProfileDetail(TenantMixin, DetailView):
    model = Profile
    template_name = 'workflows/profile-detail.html'
    context_object_name = 'profile'


class ProfileUpdate(TenantMixin, UpdateView, UpdateModifiedByMixin):
    model = Profile
    template_name = 'workflows/modals/profile-create.html'
    form_class = forms.ProfileCreateOrUpdate

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('workflows:profile-list', kwargs={'tenant_id': tenant_id})

class ProfileCreate(TenantMixin, GetServiceMixin, CreateView):
    model = Profile
    template_name = 'workflows/modals/profile-create.html'
    context_object_name = 'profile'
    form_class = forms.ProfileCreateOrUpdate

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
        return reverse_lazy('workflows:profile-list', kwargs={'tenant_id': tenant_id})

class ProfileDelete(TenantMixin, DeleteView):
    model = Profile
    template_name = 'workflows/modals/profile-delete.html'
    context_object_name = 'profile'

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('workflows:profile-list', kwargs={'tenant_id': tenant_id})

class ProfileUp(TenantMixin, GetProfileMixin, View):
    def get(self, request, tenant_id=None, pk=None, types=''):
        profile = self.get_profile(pk)
        profile.up()
        tenant_id = self.kwargs.get('tenant_id')
        return HttpResponseRedirect(reverse_lazy('workflows:profile-list', kwargs={'tenant_id': tenant_id}))

class ProfileDown(TenantMixin, GetProfileMixin, View):
    def get(self, request, tenant_id=None, pk=None, types=''):
        profile = self.get_profile(pk)
        profile.down()
        tenant_id = self.kwargs.get('tenant_id')
        return HttpResponseRedirect(reverse_lazy('workflows:profile-list', kwargs={'tenant_id': tenant_id}))


#######################################################################################################################
#
# CUSTOMER
#

class CustomerList(TenantMixin, ListView):
    model = Customer
    template_name = 'workflows/customer-list.html'
    context_object_name = 'customers'


class CustomerUpdate(TenantMixin, UpdateView, UpdateModifiedByMixin):
    model = Customer
    template_name = 'workflows/modals/customer-create-or-update.html'
    form_class = forms.CustomerCreateOrUpdate

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('workflows:customer-list', kwargs={'tenant_id': tenant_id})

class CustomerCreate(TenantMixin, CreateView):
    model = Customer
    template_name = 'workflows/modals/customer-create-or-update.html'
    context_object_name = 'customer'
    form_class = forms.CustomerCreateOrUpdate

    def form_valid(self, form):
        tenant = self.get_tenant()
        self.object = form.save(commit=False)
        self.object.tenant = tenant
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url()) 

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('workflows:customer-list', kwargs={'tenant_id': tenant_id})


class CustomerDelete(TenantMixin, DeleteView):
    model = Customer
    template_name = 'workflows/modals/customer-delete.html'
    context_object_name = 'customer'

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('workflows:customer-list', kwargs={'tenant_id': tenant_id})

    
#######################################################################################################################
#
# Shares
#
class ShareDelete(TenantMixin, GetShareMixin, View):
    def get(self, request, pk=None):
        share_id = self.kwargs.get('pk')
        share = self.get_share(share_id)
        share.delete()
        messages.info(request, _("Share was removed"))
        return HttpResponseRedirect(self.get_success_url()) 

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        share_id = self.kwargs.get('pk')
        share = self.get_share(share_id)
        return reverse_lazy('workflows:service-detail', kwargs={'tenant_id': tenant_id, 'pk': share.service_id})


#######################################################################################################################
#
# Services
#

class ServiceList(TenantMixin, ListView):
    model = Service
    template_name = 'workflows/service-list.html'
    context_object_name = 'services'

    def get_queryset(self, **kwargs):
        qs = super().get_queryset()
        qs = qs.filter(parent=None)
        return qs


class ServiceCustomerAdd(TenantMixin, GetServiceMixin, CreateView):
    model = ServiceCustomer
    template_name = 'workflows/modals/service-customer-add.html'
    context_object_name = 'service_customer'
    form_class = forms.ServiceCustomerAdd

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['service'] = self.get_service(self.kwargs.get('pk'))
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        tenant_id = self.kwargs.get('tenant_id')
        service_id = self.kwargs.get('pk')
        service = self.get_service(service_id)
        kwargs['tenant_id'] = tenant_id
        kwargs['exclude_customer_ids'] = [ sc.customer_id for sc in service.service_customers.all() ]
        return kwargs

    def form_valid(self, form):
        tenant = self.get_tenant()
        self.object = form.save(commit=False)
        service_id = self.kwargs.get('pk')
        self.object.service_id = service_id
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.service_id = service_id
        self.object.tenant = tenant
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        service_id = self.kwargs.get('pk')
        tenant_id = self.kwargs.get('tenant_id')
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        service_id = self.kwargs.get('pk')
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('workflows:service-detail', kwargs={'tenant_id': tenant_id, 'pk': service_id})


class ServiceCustomerRemove(TenantMixin, GetServiceCustomerMixin, DeleteView):
    model = ServiceCustomer
    template_name = 'workflows/modals/service-customer-remove.html'
    context_object_name = 'service_customer'

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        service_customer_id = self.kwargs.get('pk')
        service_customer = self.get_service_customer(service_customer_id)
        return reverse_lazy('workflows:service-detail', kwargs={'tenant_id': tenant_id, 'pk': service_customer.service_id})

    def form_valid(self, form):
        return HttpResponseRedirect(self.get_success_url())

class ServiceCreate(TenantMixin, CreateView):
    model = Service
    template_name = 'workflows/modals/service-create.html'
    context_object_name = 'service'
    form_class = forms.ServiceCreateOrUpdate

    def form_valid(self, form):
        tenant = self.get_tenant()
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.tenant = tenant
        self.object.owner = self.request.user
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('workflows:service-detail', kwargs={'tenant_id': tenant.id, 'pk': self.object.id}))
    

class ServiceUpdate(TenantMixin, UpdateView, UpdateModifiedByMixin):
    model = Service
    template_name = 'workflows/modals/service-create.html'
    form_class = forms.ServiceCreateOrUpdate

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        service_id = self.kwargs.get('pk')
        return reverse_lazy('workflows:service-detail', kwargs={'tenant_id': tenant_id, 'pk': service_id})


class ServiceDetail(TenantMixin, GetServiceMixin, DetailView):
    model = Service
    template_name = 'workflows/service-detail.html'
    context_object_name = 'service'

    def get_object(self, **kwargs):
        service_id = self.kwargs['pk']
        return self.get_service(service_id)
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['open_share_popup'] = self.request.GET.get('open_share_popup', None) != None
        return context


class ServiceDelete(TenantMixin, DeleteView):
    model = Service
    template_name = 'workflows/modals/service-delete.html'
    context_object_name = 'service'

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('workflows:service-list', kwargs={'tenant_id': tenant_id})


class UserServiceList(TenantMixin, ListView):
    model = Service
    template_name = 'workflows/user-service-list.html'
    context_object_name = 'services'

    def get_queryset(self, **kwargs):
        qs = super().get_queryset()
        qs = qs.filter(parent=None).order_by('name')
        if not self.request.user.is_superuser:
            qs = qs.filter(owner=self.request.user)
        qs = qs.prefetch_related('routines')
        return qs


class ServiceShare(TenantMixin, CreateView):
    model = Share
    template_name = 'workflows/modals/service-share.html'
    #fields = ['name', 'scope', 'routine']
    form_class = forms.ServiceShare

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        service_id = self.kwargs['pk']
        kwargs['service'] = self.get_service(service_id)
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        service_id = self.kwargs['pk']
        context['service'] = self.get_service(service_id)
        context['shares'] = Share.objects.filter(service_id=service_id)
        return context

    def get_queryset(self, **kwargs):
        qs = super().get_queryset()
        service_id = self.kwargs['pk']
        qs = qs.filter(routine__service_id=service_id)
        return qs

    def form_valid(self, form):
        tenant = self.get_tenant()
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.tenant = tenant
        self.object.save()
        #messages.info(self.request, _("Share with name %(name)s to routine %(routine)s created" % {'name': self.object.name, 'routine': self.object.routine}))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        service_id = self.kwargs.get('pk')
        return reverse_lazy('workflows:service-detail', kwargs={'tenant_id': tenant_id, 'pk': service_id}) + '?open_share_popup=1'

#######################################################################################################################
#
# ROUTINE
#

class RoutineCreate(TenantMixin, GetServiceMixin, CreateView):
    model = Routine
    template_name = 'workflows/modals/routine-create.html'
    form_class = forms.RoutineCreate

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        tenant_id = self.kwargs.get('tenant_id')
        kwargs['tenant_id'] = tenant_id
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['service'] = self.get_service(self.kwargs.get('pk'))
        return context

    def save_steps(self, steps, index=1, depth=0):
        for step in steps:
            activities = [ x for x in Activity.unscoped.filter(step=step) ]
            step.pk = None
            step.index = index
            step.process_depth = depth
            index += 1
            step._state.adding
            step.routine = self.object
            step.tenant = self.object.tenant
            step.save()
            activity_index = 1
            for activity in activities:
                activity.pk = None
                activity.index = activity_index
                activity.step = step
                activity.tenant = self.object.tenant
                activity.save()
                activity_index += 1

            if step.fork_id is not None:
                index = self.save_steps(Step.unscoped.filter(routine_id=step.fork_id), index=index, depth=depth + 1)

        return index

    def form_valid(self, form):
        tenant = self.get_tenant()
        service = self.get_service(self.kwargs.get('pk'))
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.tenant = tenant
        self.object.service = service
        self.object.save()
        form.save_m2m()
        template = form.cleaned_data['template'] 
        if not template.is_template or not template.is_public:
            raise PermissionDenied("Template is not a template or is not public")
        self.based_on = template
        self.save_steps(Step.unscoped.filter(routine_id=template.id)) #.steps.all())

        return HttpResponseRedirect(self.get_success_url()) 


    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        service_id = self.kwargs.get('pk')
        return reverse_lazy('workflows:service-detail', kwargs={'tenant_id': tenant_id, 'pk': service_id})

class RoutineUpdate(TenantMixin, UpdateView, UpdateModifiedByMixin):
    model = Routine
    template_name = 'workflows/modals/routine-create.html'
    form_class = forms.RoutineUpdate

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        tenant_id = self.kwargs.get('tenant_id')
        kwargs['tenant_id'] = tenant_id
        return kwargs

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        routine_id = self.kwargs.get('pk')
        return reverse_lazy('workflows:routine-detail', kwargs={'tenant_id': tenant_id, 'pk': routine_id})


class RoutineDetail(TenantMixin, GetRoutineMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        tenant_id = self.kwargs.get('tenant_id')
        routine_id = self.kwargs.get('pk')
        routine = self.get_routine(routine_id)
        step = routine.steps.order_by('index').first()
        return reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': step.id})


class RoutineDelete(TenantMixin, GetRoutineMixin, DeleteView):
    model = Routine
    template_name = 'workflows/modals/routine-delete.html'
    context_object_name = 'routine'

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        routine_id = self.kwargs.get('pk')
        routine = self.get_routine(routine_id)
        return reverse_lazy('workflows:service-detail', kwargs={'tenant_id': tenant_id, 'pk': routine.service_id})


class MediaTypeMixin():
    def accepts_media_type(self, request, media_type):
        if 'HTTP_ACCEPT' not in request.META:
            return False
        accept = request.META['HTTP_ACCEPT']
        media_types = []
        for media_range in [m.strip() for m in accept.split(',') if m]:
            parts = media_range.split(";")
            media_types.append(parts[0].strip().lower())
        return media_type in media_types

class TenantExport(TenantMixin, MediaTypeMixin, View):
    def get(self, request, tenant_id=None):
        tenant = self.get_tenant()
        data = export_as_usm_dif(tenant)

        if self.accepts_media_type(request, 'text/html'):
            response = json.dumps(data, sort_keys=True, indent=4)
            formatter = HtmlFormatter(style='colorful')
            response = highlight(response, JsonLexer(), formatter)
            style = "<style>" + formatter.get_style_defs() + "</style><br>"
            return HttpResponse(mark_safe(style + response))

        else:
            return JsonResponse(data, safe=False, json_dumps_params={'indent': 4})


class RoutineDetailPrintable(TenantMixin, DetailView):
    model = Routine
    template_name = 'workflows/routine-detail-printable.html'
    context_object_name = 'routine'


class RoutineDiagram(TenantMixin, GetRoutineMixin, View):
    def get(self, request, tenant_id=None, pk=None):
        tenant = self.get_tenant(tenant_id=tenant_id)
        routine = self.get_routine(pk)

        with tempfile.TemporaryDirectory() as tmpdirname:
            fn = diagram(routine, tmpdirname + f'/process-map-{str(routine.id)}.png')
            response = FileResponse(open(fn, 'rb'), as_attachment=True, content_type='image/png')

        return response

#######################################################################################################################
#
# STEP
#

class StepDetail(TenantMixin, DetailView):
    model = Step
    template_name = 'workflows/step-detail.html'
    context_object_name = 'step'

    def get_queryset(self, **kwargs):
        qs = super().get_queryset()
        activities_prefetch = Prefetch('activities', queryset=Activity.objects.order_by('index'))
        actions_prefetch = Prefetch('activities__actions', queryset=Action.objects.order_by('index'))
        qs = qs.select_related('routine').prefetch_related(activities_prefetch).prefetch_related(actions_prefetch).prefetch_related('activities__actions__responsibilities')

        return qs


class StepSkip(TenantMixin, GetStepMixin, View):
    def post(self, *args, **kwargs):
        tenant_id = self.kwargs.get('tenant_id')
        step_id = self.kwargs.get('pk')
        step = self.get_step(step_id)
        step.skipped = True
        step.save()
        url = reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': step.id})
        return HttpResponse(
            status=204, headers={"HX-Redirect": url}
        )

class StepUnskip(TenantMixin, GetStepMixin, View):
    def post(self, *args, **kwargs):
        tenant_id = self.kwargs.get('tenant_id')
        step_id = self.kwargs.get('pk')
        step = self.get_step(step_id)
        step.skipped = False
        step.save()
        url = reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': step.id})
        return HttpResponse(
            status=204, headers={"HX-Redirect": url}
        )


#######################################################################################################################
#
# TASK
#
class TaskDetail(TenantMixin, DetailView):
    model = Task
    template_name = 'workflows/task-detail.html'
    context_object_name = 'task'

class TaskCreate(TenantMixin, GetProfileMixin, CreateView):
    model = Task
    template_name = 'workflows/modals/create-or-update.html'
    form_class = forms.TaskCreateOrUpdate

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        profile_id = self.kwargs.get('pk')
        profile = self.get_profile(profile_id)
        kwargs['profile'] = profile
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        profile_id = self.kwargs.get('pk')
        profile = self.get_profile(profile_id)
        context['profile'] = profile
        context['verbose_name'] = _('task')
        return context

    def form_valid(self, form):
        tenant = self.get_tenant()
        profile_id = self.kwargs.get('pk')
        profile = self.get_profile(profile_id)
        self.object = form.save(commit=False)
        self.object.tenant = tenant
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.profile = profile
        self.object.save()

        return HttpResponseRedirect(self.get_success_url()) 

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        new_task = self.object
        return reverse_lazy('workflows:profile-detail', kwargs={'tenant_id': tenant_id, 'pk': new_task.profile_id})

class TaskUpdate(TenantMixin, GetTaskMixin, UpdateView, UpdateModifiedByMixin):
    model = Task
    template_name = 'workflows/modals/create-or-update.html'
    form_class = forms.TaskCreateOrUpdate

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        task_id = self.kwargs.get('pk')
        task = self.get_task(task_id)
        kwargs['profile'] = task.profile
        return kwargs

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        task_id = self.kwargs.get('pk')
        task = self.get_task(task_id)
        return reverse_lazy('workflows:profile-detail', kwargs={'tenant_id': tenant_id, 'pk': task.profile_id})

class TaskDelete(TenantMixin, GetTaskMixin, DeleteView):
    model = Task
    template_name = 'workflows/modals/delete.html'
    context_object_name = 'task'

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        task_id = self.kwargs.get('pk')
        task = self.get_task(activity_id)
        return reverse_lazy('workflows:profile-detail', kwargs={'tenant_id': tenant_id, 'pk': task.profile_id})



#######################################################################################################################
#
# ACTIVITY
#

class ActivityCreate(TenantMixin, GetStepMixin, CreateView):
    model = Activity
    template_name = 'workflows/modals/activity-create.html'
    context_object_name = 'activity'
    form_class = forms.ActivityCreateOrUpdate

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        step_id = self.kwargs.get('pk')
        step = self.get_step(step_id)
        context['step'] = step
        context['routine'] = step.routine
        context['service'] = step.routine.service
        return context

    def form_valid(self, form):
        tenant = self.get_tenant()
        step_id = self.kwargs.get('pk')
        step = self.get_step(step_id)
        self.object = form.save(commit=False)
        self.object.tenant = tenant
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.step = step
        self.object.save()

        return HttpResponseRedirect(self.get_success_url()) 

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        new_activity = self.object
        return reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': new_activity.step_id}) + '#activity-' + str(new_activity.id)


class ActivityUpdate(TenantMixin, GetActivityMixin, UpdateView, UpdateModifiedByMixin):
    model = Activity
    template_name = 'workflows/modals/activity-create.html'
    form_class = forms.ActivityCreateOrUpdate

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        activity_id = self.kwargs.get('pk')
        activity = self.get_activity(activity_id)
        return reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': activity.step_id}) + '#activity-' + str(activity.id)


class ActivityDelete(TenantMixin, GetActivityMixin, DeleteView):
    model = Activity
    template_name = 'workflows/modals/activity-delete.html'
    context_object_name = 'activity'

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        activity_id = self.kwargs.get('pk')
        activity = self.get_activity(activity_id)
        return reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': activity.step_id}) + '#activity-' + str(activity.step_id)

class ActivityUp(TenantMixin, GetActivityMixin, View):
    def get(self, request, tenant_id=None, pk=None, types=''):
        activity = self.get_activity(pk)
        activity.up()
        tenant_id = self.kwargs.get('tenant_id')
        return HttpResponseRedirect(reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': activity.step_id}) + '#activity-' + str(activity.step_id))

class ActivityDown(TenantMixin, GetActivityMixin, View):
    def get(self, request, tenant_id=None, pk=None, types=''):
        activity = self.get_activity(pk)
        activity.down()
        tenant_id = self.kwargs.get('tenant_id')
        return HttpResponseRedirect(reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': activity.step_id}) + '#activity-' + str(activity.step_id))


class ActivitySkip(TenantMixin, GetActivityMixin, View):
    def post(self, request, tenant_id=None, pk=None):
        activity = self.get_activity(pk)
        activity.skipped = True
        activity.save()
        url = reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': activity.step.id})
        return HttpResponse(
            status=204, headers={"HX-Redirect": url}
        )

class ActivityUnskip(TenantMixin, GetActivityMixin, View):
    def post(self, request, tenant_id=None, pk=None):
        activity = self.get_activity(pk)
        activity.skipped = False
        activity.save()
        url = reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': activity.step.id})
        return HttpResponse(
            status=204, headers={"HX-Redirect": url}
        )


#######################################################################################################################
#
# ACTION
#

class ActionCreateOrUpdate(TenantMixin, GetActivityMixin, CreateView):
    model = Action
    template_name = 'workflows/modals/action-create-or-update.html'
    context_object_name = 'action'
    form_class = forms.ActionCreateOrUpdate

    def form_valid(self, form):
        tenant = self.get_tenant()
        activity_id = self.kwargs.get('pk')
        activity = self.get_activity(activity_id)
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.activity = activity
        self.object.tenant = tenant
        self.object.save()

        return HttpResponseRedirect(self.get_success_url()) 

    def form_invalid(self, form):
        activity_id = self.kwargs.get('pk')
        tenant_id = self.kwargs.get('tenant_id')
        activity = self.get_activity(activity_id)
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return HttpResponseRedirect(reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': activity.step_id}) + '#activity-' + str(activity.id))

    def get_success_url(self):
        activity_id = self.kwargs.get('pk')
        tenant_id = self.kwargs.get('tenant_id')
        activity = self.get_activity(activity_id)
        return reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': activity.step_id}) + '#activity-' + str(activity.id)


class ActionDelete(TenantMixin, GetActionMixin, DeleteView):
    model = Action
    template_name = 'workflows/modals/action-delete.html'
    context_object_name = 'action'

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        action_id = self.kwargs.get('pk')
        action = self.get_action(action_id)
        return reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': action.activity.step_id}) + '#activity-' + str(action.activity.id)


class ActionUpdate(TenantMixin, GetActionMixin, UpdateView, UpdateModifiedByMixin):
    model = Action
    template_name = 'workflows/modals/action-create-or-update.html'
    form_class = forms.ActionCreateOrUpdate

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        action = self.get_object()
        tenant_id = self.kwargs.get('tenant_id')
        kwargs['tenant_id'] = tenant_id
        kwargs['exclude_profile_ids'] = [ r.profile_id for r in action.activity.actions.all() if r.profile_id ]
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.modified_by = self.request.user
        self.object.save()

        return HttpResponseRedirect(self.get_success_url()) 

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        action_id = self.kwargs.get('pk')
        action = self.get_action(action_id)
        context['object'] = action
        return context

    def form_invalid(self, form):
        action = self.get_object()
        tenant_id = self.kwargs.get('tenant_id')
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return HttpResponseRedirect(reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': action.activity.step_id}) + '#activity-' + str(action.activity.id))

    def get_success_url(self):
        action = self.get_object()
        tenant_id = self.kwargs.get('tenant_id')
        return reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': action.activity.step_id}) + '#activity-' + str(action.activity.id)


class ActionUp(TenantMixin, GetActionMixin, View):
    def get(self, request, tenant_id=None, pk=None, types=''):
        action = self.get_action(pk)
        action.up()
        tenant_id = self.kwargs.get('tenant_id')
        return HttpResponseRedirect(reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': action.activity.step_id}) + '#activity-' + str(action.activity_id))


class ActionDown(TenantMixin, GetActionMixin, View):
    def get(self, request, tenant_id=None, pk=None, types=''):
        action = self.get_action(pk)
        action.down()
        tenant_id = self.kwargs.get('tenant_id')
        return HttpResponseRedirect(reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': action.activity.step_id}) + '#activity-' + str(action.activity_id))

#######################################################################################################################
#
# INSTRUCTION
#

class InstructionCreate(TenantMixin, GetResponsibilityMixin, CreateView):
    model = Instruction
    template_name = 'workflows/modals/instruction-create-or-update.html'
    context_object_name = 'instruction'
    form_class = forms.InstructionCreateOrUpdate

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        responsibility_id = self.kwargs.get('pk')
        responsibility = self.get_responsibility(responsibility_id)
        context['responsibility'] = responsibility
        return context

    def form_valid(self, form):
        tenant = self.get_tenant()
        responsibility_id = self.kwargs.get('pk')
        responsibility = self.get_responsibility(responsibility_id)
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.responsibility = responsibility
        self.object.tenant = tenant
        self.object.save()
        return HttpResponseRedirect(self.get_success_url()) 

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        new_instruction = self.object
        return reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': new_instruction.responsibility.action.activity.step_id}) + '#activity-' + str(new_instruction.responsibility.action.activity_id)


class InstructionUpdate(TenantMixin, GetInstructionMixin, UpdateView, UpdateModifiedByMixin):
    model = Instruction
    template_name = 'workflows/modals/instruction-create-or-update.html'
    form_class = forms.InstructionCreateOrUpdate

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        instruction_id = self.kwargs.get('pk')
        instruction = self.get_instruction(instruction_id)
        return reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': instruction.responsibility.action.activity.step_id}) + '#activity-' + str(instruction.responsibility.action.activity_id)


class InstructionDelete(TenantMixin, GetInstructionMixin, DeleteView):
    model = Instruction
    template_name = 'workflows/modals/instruction-delete.html'
    context_object_name = 'instruction'

    def get_success_url(self):
        tenant_id = self.kwargs.get('tenant_id')
        instruction_id = self.kwargs.get('pk')
        instruction = self.get_instruction(instruction_id)
        return reverse_lazy('workflows:step-detail', kwargs={'tenant_id': tenant_id, 'pk': instruction.responsibility.action.activity.step_id}) + '#activity-' + str(instruction.responsibility.action.activity_id)
