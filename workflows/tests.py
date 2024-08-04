from django.test import TestCase, override_settings
from django.urls import reverse  

from .models import Account, Service, OrganizationUnit, Profile, Workflow, Step, Activity, Responsible, WorkInstruction, Customer, Tenant, ServiceCustomer

#@override_settings(DEBUG=True)
class ServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.user1 = Account.objects.create(username='user1')
        cls.user2 = Account.objects.create(username='user2')

        cls.user1.set_password('123')
        cls.user1.save()
        cls.user2.set_password('123')
        cls.user2.save()
        cls.tenant = Tenant.objects.create(name="Test User1 Tenant", owner=cls.user1)
        cls.tenant2 = Tenant.objects.create(name="Test User2 Tenant", owner=cls.user2)
        cls.service = Service.objects.create(name="Test Service", tenant=cls.tenant, owner=cls.user1)
        cls.ou = OrganizationUnit.objects.create(name="Test OU", tenant=cls.tenant)
        cls.customer = Customer.objects.create(name="Test Customer", tenant=cls.tenant)
        cls.profile = Profile.objects.create(name="Test Profile", tenant=cls.tenant)
        cls.workflow = Workflow.objects.create(name="Test Workflow", tenant=cls.tenant)
        cls.step = Step.objects.create(name="Test Step", workflow=cls.workflow, tenant=cls.tenant)
        cls.activity = Activity.objects.create(name="Test Activity", step=cls.step, tenant=cls.tenant)
        cls.responsible = Responsible.objects.create(profile=cls.profile, activity=cls.activity, types='RACI', tenant=cls.tenant)
        cls.wi = WorkInstruction.objects.create(description="Test Work Instruction", responsible=cls.responsible, tenant=cls.tenant)
        cls.sc = ServiceCustomer.objects.create(customer=cls.customer, service=cls.service, tenant=cls.tenant)

    def test_service_root_redirect(self):
        response = self.client.get("/app/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[1][0], '/accounts/login/?next=/app/tenants/')

    def test_tenant_list_only_showing_mine(self):
        self.client.login(username='user1', password='123')
        tenant_id = str(self.tenant.pk)
        tenant2_id = str(self.tenant2.pk)
        response = self.client.get(f"/app/tenants/")
        self.assertContains(response, "Test User1 Tenant")
        self.assertNotContains(response, "Test User2 Tenant")

    def test_service_not_loggedin_redirects_to_login(self):
        response = self.client.get("/app/tenants/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][0], '/accounts/login/?next=/app/tenants/')

    def test_service_get_by_owner(self):
        self.client.login(username='user1', password='123')
        tenant_id = str(self.tenant.pk)
        service_id = str(self.service.pk)
        response = self.client.get(f"/app/{tenant_id}/services/{service_id}/")
        self.assertEqual(response.status_code, 200)

    def test_service_get_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        service_id = str(self.service.pk)
        response = self.client.get(f"/app/{tenant_id}/services/{service_id}/")
        self.assertEqual(response.status_code, 403)
     
    def test_tenant_create(self):
        self.client.login(username='user1', password='123')
        response = self.client.get(f"/app/tenants/create/")
        self.assertEqual(response.status_code, 200)
     
    def test_tenant_delete(self):
        self.client.login(username='user1', password='123')
        tenant_id = str(self.tenant.pk)
        response = self.client.get(f"/app/{tenant_id}/delete/")
        self.assertEqual(response.status_code, 200)
     
    def test_tenant_delete_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        response = self.client.get(f"/app/{tenant_id}/delete/")
        self.assertEqual(response.status_code, 403)
     
    def test_tenant_update(self):
        self.client.login(username='user1', password='123')
        tenant_id = str(self.tenant.pk)
        response = self.client.get(f"/app/{tenant_id}/update/")
        self.assertEqual(response.status_code, 200)
     
    def test_tenant_update_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        response = self.client.get(f"/app/{tenant_id}/update/")
        self.assertEqual(response.status_code, 403)
     
    def test_service_create(self):
        self.client.login(username='user1', password='123')
        tenant_id = str(self.tenant.pk)
        response = self.client.get(f"/app/{tenant_id}/services/create/")
        self.assertEqual(response.status_code, 200)
     
    def test_service_ou_create(self):
        self.client.login(username='user1', password='123')
        tenant_id = str(self.tenant.pk)
        response = self.client.get(f"/app/{tenant_id}/organization-units/create/")
        self.assertEqual(response.status_code, 200)

    def test_service_ou_delete_protected_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.ou.pk)
        response = self.client.get(f"/app/{tenant_id}/organization-units/{id}/delete/")
        self.assertEqual(response.status_code, 403)

    def test_service_ou_update_protected_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.ou.pk)
        response = self.client.post(f"/app/{tenant_id}/organization-units/{id}/update/")
        self.assertEqual(response.status_code, 403)

    def test_ou_list(self):
        self.client.login(username='user1', password='123')
        tenant_id = str(self.tenant.pk)
        response = self.client.get(f"/app/{tenant_id}/organization-units/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test OU")
     
    def test_ou_list_only_showing_mine(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant2.pk)
        response = self.client.get(f"/app/{tenant_id}/organization-units/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Test OU")
        self.assertContains(response, "You have not defined any organizations")
     
    def test_service_list(self):
        self.client.login(username='user1', password='123')
        tenant_id = str(self.tenant.pk)
        response = self.client.get(f"/app/{tenant_id}/services/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Service")
     
    def test_service_list_only_showing_mine(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant2.pk)
        response = self.client.get(f"/app/{tenant_id}/services/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Test Service")
        self.assertContains(response, "You have not defined any services yet")
     
    def test_service_delete_protected_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.service.pk)
        response = self.client.get(f"/app/{tenant_id}/services/{id}/delete/")
        self.assertEqual(response.status_code, 403)
     
    def test_service_update_protected_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.service.pk)
        response = self.client.post(f"/app/{tenant_id}/services/{id}/update/")
        self.assertEqual(response.status_code, 403)
     
    def test_service_share_protected_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.service.pk)
        response = self.client.get(f"/app/{tenant_id}/services/{id}/share/")
        self.assertEqual(response.status_code, 404)
     
    def test_service_profile_create_protected_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.service.pk)
        response = self.client.get(f"/app/{tenant_id}/services/{id}/profiles/create/")
        self.assertEqual(response.status_code, 404)

    def test_service_workflow_create_protected_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.service.pk)
        response = self.client.get(f"/app/{tenant_id}/services/{id}/workflows/create/")
        self.assertEqual(response.status_code, 403)

    def test_profile_update_protected_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.profile.pk)
        response = self.client.post(f"/app/{tenant_id}/profiles/{id}/update/")
        self.assertEqual(response.status_code, 403)

    def test_profile_delete_protected_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.profile.pk)
        response = self.client.get(f"/app/{tenant_id}/profiles/{id}/delete/")
        self.assertEqual(response.status_code, 403)

    def test_profile_up_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.profile.pk)
        response = self.client.get(f"/app/{tenant_id}/profiles/{id}/up/")
        self.assertEqual(response.status_code, 403)
     
    def test_profile_down_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.profile.pk)
        response = self.client.get(f"/app/{tenant_id}/profiles/{id}/down/")
        self.assertEqual(response.status_code, 403)
     
    def test_customer_update_protected_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.customer.pk)
        response = self.client.post(f"/app/{tenant_id}/customers/{id}/update/")
        self.assertEqual(response.status_code, 403)

    def test_customer_delete_protected_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.customer.pk)
        response = self.client.get(f"/app/{tenant_id}/customers/{id}/delete/")
        self.assertEqual(response.status_code, 403)

    def test_workflow_get_by_owner(self):
        self.client.login(username='user1', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.workflow.pk)
        response = self.client.get(f"/app/{tenant_id}/workflows/{id}/")
        self.assertEqual(response.status_code, 200)

    def test_workflow_get_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.workflow.pk)
        response = self.client.get(f"/app/{tenant_id}/workflows/{id}/")
        self.assertEqual(response.status_code, 403)
     
    def test_workflow_delete_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.workflow.pk)
        response = self.client.get(f"/app/{tenant_id}/workflows/{id}/delete/")
        self.assertEqual(response.status_code, 403)
     
    def test_workflow_update_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.workflow.pk)
        response = self.client.post(f"/app/{tenant_id}/workflows/{id}/update/")
        self.assertEqual(response.status_code, 403)
     
    def test_export(self):
        self.client.login(username='user1', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.workflow.pk)
        response = self.client.get(f"/app/{tenant_id}/export/")
        self.assertEqual(response.status_code, 200)
     
    def test_export_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.workflow.pk)
        response = self.client.get(f"/app/{tenant_id}/export/")
        self.assertEqual(response.status_code, 403)
     
    def test_activity_create_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.step.pk)
        response = self.client.get(f"/app/{tenant_id}/steps/{id}/activities/create/")
        self.assertEqual(response.status_code, 403)
     
    def test_activity_delete_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.activity.pk)
        response = self.client.get(f"/app/{tenant_id}/activities/{id}/delete/")
        self.assertEqual(response.status_code, 403)
     
    def test_activity_update_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.activity.pk)
        response = self.client.post(f"/app/{tenant_id}/activities/{id}/update/")
        self.assertEqual(response.status_code, 403)
     
    def test_activity_up_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.activity.pk)
        response = self.client.get(f"/app/{tenant_id}/activities/{id}/up/")
        self.assertEqual(response.status_code, 403)
     
    def test_activity_down_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.activity.pk)
        response = self.client.get(f"/app/{tenant_id}/activities/{id}/down/")
        self.assertEqual(response.status_code, 403)
     
    def test_responsible_create_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.activity.pk)
        response = self.client.get(f"/app/{tenant_id}/activities/{id}/responsibles/create/")
        self.assertEqual(response.status_code, 403)

    def test_responsible_delete_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.responsible.pk)
        response = self.client.get(f"/app/{tenant_id}/responsibles/{id}/delete/")
        self.assertEqual(response.status_code, 403)
     
    def test_responsible_add_responsibilities_by_owner(self):
        self.client.login(username='user1', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.responsible.pk)
        response = self.client.get(f"/app/{tenant_id}/responsibles/{id}/add-responsibilities/C/")
        self.assertEqual(response.status_code, 200)

    def test_responsible_add_responsibilities_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.responsible.pk)
        response = self.client.get(f"/app/{tenant_id}/responsibles/{id}/add-responsibilities/C/")
        self.assertEqual(response.status_code, 403)
     
    def test_responsible_remove_responsibilities_by_owner(self):
        self.client.login(username='user1', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.responsible.pk)
        response = self.client.get(f"/app/{tenant_id}/responsibles/{id}/remove-responsibilities/C/")
        self.assertEqual(response.status_code, 200)

    def test_responsible_remove_responsibilities_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.responsible.pk)
        response = self.client.get(f"/app/{tenant_id}/responsibles/{id}/remove-responsibilities/C/")
        self.assertEqual(response.status_code, 403)
     
    def test_create_work_instruction(self):
        self.client.login(username='user1', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.responsible.pk)
        response = self.client.get(f"/app/{tenant_id}/responsibles/{id}/work-instructions/create/")
        self.assertEqual(response.status_code, 200)
     
    def test_work_instruction_delete(self):
        self.client.login(username='user1', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.wi.pk)
        response = self.client.get(f"/app/{tenant_id}/work-instructions/{id}/delete/")
        self.assertEqual(response.status_code, 200)
     
    def test_work_instruction_update(self):
        self.client.login(username='user1', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.wi.pk)
        response = self.client.get(f"/app/{tenant_id}/work-instructions/{id}/update/")
        self.assertEqual(response.status_code, 200)
     
    def test_create_work_instruction_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.responsible.pk)
        response = self.client.post(f"/app/{tenant_id}/responsibles/{id}/work-instructions/create/")
        self.assertEqual(response.status_code, 403)
     
    def test_work_instruction_delete_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.wi.pk)
        response = self.client.get(f"/app/{tenant_id}/work-instructions/{id}/delete/")
        self.assertEqual(response.status_code, 403)
     
    def test_work_instruction_update_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.wi.pk)
        response = self.client.post(f"/app/{tenant_id}/work-instructions/{id}/update/")
        self.assertEqual(response.status_code, 403)
     
    #def test_user_service_list(self):
    #    self.client.login(username='user1', password='123')
    #    tenant_id = str(self.tenant.pk)
    #    response = self.client.get(f"/app/{tenant_id}/user/services/")
    #    self.assertEqual(response.status_code, 200)
    #    self.assertContains(response, "Test Service")
     
    #def test_user_service_list_only_showing_mine(self):
    #    self.client.login(username='user2', password='123')
    #    tenant_id = str(self.tenant2.pk)
    #    response = self.client.get(f"/app/{tenant_id}/user/services/")
    #    self.assertEqual(response.status_code, 200)
    #    self.assertNotContains(response, "Test Service")
    #    self.assertContains(response, "You do not have access to any services")

    def test_workflow_detail_by_owner(self):
        self.client.login(username='user1', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.workflow.pk)
        response = self.client.get(f"/app/{tenant_id}/workflows/{id}/")
        self.assertEqual(response.status_code, 200)

    def test_workflow_detail_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.workflow.pk)
        response = self.client.get(f"/app/{tenant_id}/workflows/{id}/")
        self.assertEqual(response.status_code, 403)

    def test_workflow_detail_printable_by_owner(self):
        self.client.login(username='user1', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.workflow.pk)
        response = self.client.get(f"/app/{tenant_id}/workflows/{id}/printable/")
        self.assertEqual(response.status_code, 200)

    def test_workflow_detail_printable_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        id = str(self.workflow.pk)
        response = self.client.get(f"/app/{tenant_id}/workflows/{id}/printable/")
        self.assertEqual(response.status_code, 403)

    def test_service_customer_add_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        service_id = str(self.service.pk)
        response = self.client.get(f"/app/{tenant_id}/services/{service_id}/customers/add/")
        self.assertEqual(response.status_code, 403)

    def test_service_customer_add_by_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant2.pk)
        service = Service.objects.create(name="Test User2 Service", tenant=self.tenant2, owner=self.user2)
        response = self.client.get(f"/app/{tenant_id}/services/{service.id}/customers/add/")
        self.assertEqual(response.status_code, 200)

    def test_service_customer_remove_by_non_owner(self):
        self.client.login(username='user2', password='123')
        tenant_id = str(self.tenant.pk)
        service_customer_id = str(self.sc.pk)
        response = self.client.get(f"/app/{tenant_id}/service-customers/{service_customer_id}/remove/")
        self.assertEqual(response.status_code, 403)

    def test_service_customer_remove_by_owner(self):
        self.client.login(username='user1', password='123')
        tenant_id = str(self.tenant.pk)
        service_customer_id = str(self.sc.pk)
        response = self.client.get(f"/app/{tenant_id}/service-customers/{service_customer_id}/remove/")
        self.assertEqual(response.status_code, 200)

