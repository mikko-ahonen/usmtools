from django.core.management.base import BaseCommand, CommandError
from workflows.models import Service, OrganizationUnit

class Command(BaseCommand):
    help = 'Fix level for services and organization units'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        set_tree_levels_for_org_units_and_services()

def set_tree_levels_for_org_units_and_services():
    for service in Service.unscoped.filter(parent=None).all():
        set_level(service, 0)

    for ou in OrganizationUnit.unscoped.filter(parent=None).all():
        set_level(ou, 0)

def set_level(o, level):
    o.level = level 
    o.save()
    print(level)
    print(o.name)
    print(o.children)
    for child in o.__class__.unscoped.filter(parent=o).all():
        print(child)
        set_level(child, level + 1)

