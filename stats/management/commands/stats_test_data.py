import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError

from workflows.tenant_models import Tenant
from projects.models import Project
from stats.models import Dataset, Datapoint

class Command(BaseCommand):
    help = "Create test data for stats"

    def add_arguments(self, parser):
        parser.add_argument('--tenant', type=str, help="Tenant for the domain to be updated")

    def handle(self, *args, **options):
        tenant_id = options['tenant']
        if not tenant_id:
            qs = Tenant.objects.all()
            if len(qs) == 1:
                tenant = qs.first()
            else:
                raise CommandError("tenant is required")
        else:
            tenant = Tenant.objects.filter(id=tenant_id).first()
        if not tenant:
            raise CommandError("tenant not found")

        print(f"Tenant {tenant.id}:")

        for project in Project.unscoped.all():
            print(f"Processing project {project.id}:")
            for team in project.teams(manager='unscoped').all():
                print(f"  Team {team.name}")
                sprint = team.current_sprint
                if sprint:
                    print(f"    Sprint {sprint.name}")
                    burndown, created = Dataset.unscoped.get_or_create(tenant_id=tenant_id, name=sprint.name + " burndown", defaults={"content_object": sprint, "label": "Burndown"})
                    ideal, created = Dataset.unscoped.get_or_create(tenant_id=tenant_id, name=sprint.name + " ideal", defaults={"content_object": burndown, "label": "Ideal"})
                    dt = sprint.start_date
                    story_count = sprint.stories.count()
                    length_in_days = abs((sprint.end_date - sprint.start_date).days)
                    ideal_story_count_per_day = int(story_count / length_in_days)
                    while dt < sprint.end_date - timedelta(days=4):
                        ideal_val = abs((dt - sprint.start_date).days) * ideal_story_count_per_day
                        _, _ = Datapoint.unscoped.get_or_create(dataset=ideal, date=dt, defaults={"value": ideal_val})
                        _, _ = Datapoint.unscoped.get_or_create(dataset=burndown, date=dt, defaults={"value": random.randint(min(ideal_val - 4, 0), ideal_val + 4)})
                        dt += timedelta(days=1)
