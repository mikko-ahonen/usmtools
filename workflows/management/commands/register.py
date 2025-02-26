# necessary imports
import secrets
import string
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from workflows.models import Account

# define the alphabet
letters = string.ascii_letters
digits = string.digits
special_chars = string.punctuation

alphabet = letters + digits # + special_chars

def generate_password(pwd_length=12):
    pwd = ''
    for i in range(pwd_length):
      pwd += ''.join(secrets.choice(alphabet))
    return pwd

email_text = """
Hello,

You requested to be added to USM BPM tool private beta. Here are your credentials:

Username: {username}
Password: {password}

You can log in from:

http://usm.tools/accounts/login/

Please do not hesitate to contact me if there is an issue or if you have some ideas how to develop the tool to be more useful.

Br,

Mikko
"""

def send_password_email(user, password):
    send_mail(
        "USM BPM Tool Private Beta",
        email_text.format(username=user.username, password=password),
        "mikko@usm.coach",
        [user.email],
        fail_silently=False,
    )

class Command(BaseCommand):
    help = 'Register user, create a random password'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('first_name', type=str)
        parser.add_argument('last_name', type=str)
        parser.add_argument('email', type=str)

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = Account.objects.get(username=username)
        except Account.DoesNotExist:
            user = Account.objects.create(username=username, first_name=options['first_name'], last_name=options['last_name'], email=options['email'])
            pwd = generate_password()
            user.set_password(pwd)
            user.save()
            send_password_email(user, pwd)
            self.stdout.write(self.style.SUCCESS(f'Successfully created user with username {username} and password {pwd}'))
            return

        raise CommandError(f'Profile with username "{username}" already exists')
