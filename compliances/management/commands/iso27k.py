import os.path
import argparse

from django.core.management.base import BaseCommand, CommandError

from workflows.tenant_models import Tenant

from ...imports import import_excel

class Command(BaseCommand):
    help = "Update cross-references in the database based on Excel file"

    def add_arguments(self, parser):
        parser.add_argument('--tenant', type=str, help="Tenant for the domain to be updated")
        parser.add_argument('--file', type=str, help="Input file")

    def handle(self, *args, **options):
        tenant_id = options['tenant']
        if not tenant_id:
            qs = Tenant.objects.all()
            if len(qs) == 1:
                tenant = qs.first()
            else:
                raise CommandError(f"tenant is required ({len(qs)} matches)")
        else:
            tenant = Tenant.objects.filter(id=tenant_id).first()
        if not tenant:
            raise CommandError("tenant not found")

        if not options['file'] or not os.path.exists(options['file']):
            raise CommandError(f"input file {options['file']} not found")
        
        import_excel(tenant, options['file'])
