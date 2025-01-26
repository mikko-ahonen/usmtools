from django.core.management.base import BaseCommand, CommandError
from workflows.models import Routine
from workflows.diagrams import diagram

class Command(BaseCommand):
    help = 'Sets password for certain user to 123'

    def add_arguments(self, parser):
        parser.add_argument('routine', nargs='+', type=str)

    def handle(self, *args, **options):
        for routine_id in options['routine']:
            try:
                routine = Routine.unscoped.get(id=routine_id)
            except Routine.DoesNotExist:
                raise CommandError('Routine "%s" does not exist' % username)

            fn = diagram(routine, 'process_map.png')
            if fn:
                self.stdout.write(self.style.SUCCESS(f'Successfully wrote diagram to {fn}'))
            else:
                self.stdout.write(self.style.ERROR(f'Failed to generate diagram'))
