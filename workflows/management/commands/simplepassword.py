from django.core.management.base import BaseCommand, CommandError
from workflows.models import Account

class Command(BaseCommand):
    help = 'Sets password for certain user to 123'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+', type=str)

    def handle(self, *args, **options):
        for username in options['username']:
            try:
                user = Account.objects.get(username=username)
            except Account.DoesNotExist:
                raise CommandError('Account "%s" does not exist' % username)

            user.set_password('123')
            user.save()

            self.stdout.write(self.style.SUCCESS('Successfully changed password for username %s to 123' % username))
