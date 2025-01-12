import math
import random

from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType

from workflows.tenant import set_tenant_id
from workflows.tenant_models import Tenant
from projects.models import Project, Sprint, Epic, Story
from stats.models import Dataset, Datapoint

class Command(BaseCommand):
    help = "Create test data for stats"

    def add_arguments(self, parser):
        parser.add_argument('--tenant', type=str, help="Tenant for the domain to be updated")

    def get_tenant(self, options):
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
        return tenant

    def create_object_datasets(self, tenant, object, task_qs):
        burndown, created = Dataset.unscoped.update_or_create(tenant_id=tenant.id, name=str(object) + " burndown", defaults={"content_object": object, "label": "Burndown"})
        if not created:
            burndown.datapoint_set.all().delete()
        ideal, created = Dataset.unscoped.update_or_create(tenant_id=tenant.id, name=str(object) + " ideal", defaults={"content_object": burndown, "label": "Ideal"})
        if not created:
            ideal.datapoint_set.all().delete()
       
        dt = object.start_date

        story_points = 0
        for task in task_qs.all():
            if isinstance(task, Epic):
                story_points += task.get_story_points()
            elif isinstance(task, Story):
                story_points += task.story_points
            
        ideal_story_points_per_day = getattr(object, 'ideal_story_points_per_day', None)

        if ideal_story_points_per_day:
            length_in_days = int(story_points / ideal_story_points_per_day) + 1
        else:
            length_in_days = abs((object.end_date - object.start_date).days)

        if not ideal_story_points_per_day:
            ideal_story_points_per_day = float(story_points / length_in_days)

        for n in range(0, length_in_days + 1):
            ideal_val = abs(length_in_days - n) * ideal_story_points_per_day
            dt  = object.start_date + timedelta(days=n)

            # leave few days off so the graph looks more realistic
            _, _ = Datapoint.objects.update_or_create(dataset=ideal, date=dt, defaults={"value": ideal_val})
            if n < length_in_days - 4:
                randval = random.randint(max(math.ceil(ideal_val) - 4, 0), math.ceil(ideal_val) + 4)
                _, _ = Datapoint.objects.update_or_create(dataset=burndown, date=dt, defaults={"value": randval})

    def create_dataset_for_release(self, tenant, project):
        if current_release := project.get_current_release():
            print(f"  Creating data for release {current_release.name}")
            return self.create_object_datasets(tenant, current_release, current_release.epics)

    def create_dataset_for_project(self, tenant, project):
        print(f"  Creating data for project {project.name} id {project.id}")
        return self.create_object_datasets(tenant, project, project.get_epics())

    def create_datasets_for_current_sprints(self, tenant, project):

        sprint_type = ContentType.objects.get_for_model(Sprint)

        for team in project.teams(manager='unscoped').all():
            print(f"  Processing Team {team.name}")
            sprint = team.current_sprint
            if sprint:
                print(f"    Creating data for sprint {sprint.name}")
                self.create_object_datasets(tenant, sprint, sprint.stories)

    def handle(self, *args, **options):
        tenant = self.get_tenant(options)

        set_tenant_id(tenant.id)

        for project in Project.unscoped.all():
            print(f"Processing project {project.id}:")
            self.create_dataset_for_project(tenant, project)
            self.create_dataset_for_release(tenant, project)
            self.create_datasets_for_current_sprints(tenant, project)
