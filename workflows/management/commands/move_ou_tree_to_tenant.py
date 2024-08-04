from django.core.management.base import BaseCommand, CommandError
from workflows.models import OrganizationUnit

class Command(BaseCommand):
    help = 'Sets password for certain user to 123'

    def add_arguments(self, parser):
        parser.add_argument('org_unit_id', type=str)
        parser.add_argument('tenant_id', type=str)

    def handle(self, *args, **options):
        ou_id = options['org_unit_id']
        tenant_id = options['tenant_id']
        ou = OrganizationUnit.unscoped.get(pk=ou_id)
        if ou.parent != None:
            raise("Only root organization units may be moved")
        ou.tenant_id = tenant_id
        ou.save()
        for subou in ou.children.all():
            set_tenant_for_descendants(subou, tenant_id)
        self.stdout.write(self.style.SUCCESS(f'Successfully moved organization unit {ou_id} to tenant {tenant_id}'))

def set_tenant_for_descendants(o, tenant_id):
    o.tenant_id = tenant_id
    o.save()
    for child in o.children.all():
        set_tenant_for_descendants(child, tenant)
