from django.core.management.base import BaseCommand, CommandError
from workflows.models import Service, Tenant

class Command(BaseCommand):
    help = 'Fix tenant for subservices of all services that have tenant set'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        fix_services()


def set_tenant_for_descendants(o, tenant_id):
    self.stdout.write(self.style.SUCCESS(f'Set tenant for {o}.'))
    o.tenant_id = tenant_id
    o.save()
    for child in o.children.all():
        set_tenant_for_descendants(child, tenant)

def fix_services():
    for service in Service.unscoped.filter(parent=None):

        if service.is_meta:
            continue

        if service.tenant is None:
            continue

        for subservice in service.children.all():
            set_tenant_for_descendants(subservice, service.tenant_id)
