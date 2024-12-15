#!/usr/bin/env python
import re
import os
import sys
import json
import argparse
#from slugify import slugify
from logica.common import logica_lib
from django.utils import timezone

from pyparsing import ParseException, pprint
import jinja2

from django.core.management.base import BaseCommand, CommandError

from usm.settings import BASE_DIR
from .grammar import XREF_GRAMMAR
from ...models import Domain, Section, Requirement, Constraint
from workflows.tenant_models import Tenant

def strip(s):
    return re.sub(r"^[\s\n\t]*(.*)[\s\n\t\r]*", r"\1", s)

def goal(domain, section, requirement, constraint):
    return f"{domain.slug}_{section.slug}_{requirement.slug}_{constraint.slug}".replace("-", "_")

class Command(BaseCommand):
    help = "Update cross-references in the database for certain domain"

    def add_arguments(self, parser):
        parser.add_argument('--domain', type=str, help="Slug for the domain to be updated")
        parser.add_argument('--tenant', type=str, help="Tenant for the domain to be updated")
        parser.add_argument('--update-structure', help="Update the database structure. Defaults to only verifying that the structure corresponds to the source code.", nargs='?', const=True)

    def process_xref_source(self, domain_slug):
        try:
            xref_path = os.path.join(BASE_DIR, f'compliances/management/commands/{domain_slug}.xref')
            with open(xref_path, 'r') as f:
                data = f.read()
            try:
                bnf = XREF_GRAMMAR()
                tokens = bnf.parse_string(data)
                pprint.pprint(tokens.as_dict())
                #print(tokens.dump())
                if tokens['domain']['slug'] != domain_slug:
                    raise Exception(f"Domain in XREF source code {xref_path} is '{tokens['domain']['slug']}', was expecting '{domain_slug}'")
            except ParseException as err:
                print(err)
                print(err.line)
                print(" " * (err.column - 1) + "^")
                raise err
            return tokens
        except Exception as ex:
            raise CommandError("Failed to read and process XREF source: " + str(ex))

    def render_xref(self, tenant_id, domain_slug, tokens):
        TEMPLATE_FILE = 'compliances/management/commands/xref.template'
        try:
            templateLoader = jinja2.FileSystemLoader(searchpath=BASE_DIR)
            templateEnv = jinja2.Environment(loader=templateLoader)
            print(TEMPLATE_FILE)
            templateEnv.globals['goal'] = goal
            template = templateEnv.get_template(TEMPLATE_FILE)
            out = template.render(domain=tokens['domain'], terms=tokens['domain']['terms'], sections=tokens['domain']['sections'])
            print(out)
            return out
        except Exception as ex:
            raise CommandError("Failed to render the XREF template: " + str(ex))

    def get_qualifiers(self, token):
        return dict((q['name'], q['value']) for q in token['qualifiers'])

    def update_structure(self, tenant_id, domain_slug, tokens):
        domain_qualifiers = self.get_qualifiers(tokens['domain'])

        now = timezone.now()
        domain, _ = Domain.unscoped.update_or_create(tenant_id=tenant_id, slug=domain_slug, defaults={"name": domain_qualifiers['name'], "description": strip(tokens['domain']['doc'])}) #, 'created_at': now, 'modified_at': now})
        for section_index, section_token in enumerate(tokens['domain']['sections']):
            section_qualifiers = self.get_qualifiers(section_token)
            section, _ = Section.unscoped.update_or_create(tenant_id=tenant_id, index=section_index, slug=section_token['slug'], domain_id=domain.id, defaults={"title": section_qualifiers['title'], "description": strip(section_token['doc'])})
            for req_index, req_token in enumerate(section_token['requirements']):
                req, _ = Requirement.unscoped.update_or_create(tenant_id=tenant_id, index=req_index, slug=req_token['slug'], section_id=section.id, defaults={"text": strip(req_token['doc'])})
                for constr_index, constr_token in enumerate(req_token['constraints']):
                    constraint, _ = Constraint.unscoped.update_or_create(tenant_id=tenant_id, index=constr_index, slug=constr_token['slug'], requirement_id=req.id, defaults={"text": strip(constr_token['doc'])})

    def validate_constraint(self, tenant_id, constraint, constraint_token, for_update=False):
        return True

    def validate_requirement(self, tenant_id, requirement, requirement_token, for_update=False):
        constraints = dict((x['slug'], x) for x in requirement_token['constraints'])
        for constraint in requirement.constraints(manager='unscoped').all():
            if constraint.slug not in constraints:
                raise CommandError(f"Validating structure failed: database constraint '{constraint.slug}' does not exist in XREF file")
            constraint_token = constraints[constraint.slug]
            del constraints[constraint.slug]
            self.validate_constraint(tenant_id, constraint, constraint_token, for_update=for_update)
        if not for_update:
            for slug, requirement in constraints.items():
                raise CommandError(f"Validating structure failed: XREF constraint '{slug}' does not exist in the database")

    def validate_section(self, tenant_id, section, section_token, for_update=False):
        requirements = dict((x['slug'], x) for x in section_token['requirements'])
        for requirement in section.requirements(manager='unscoped').all():
            if requirement.slug not in requirements:
                raise CommandError(f"Validating structure failed: database requirement '{requirement.slug}' does not exist in XREF file")
            requirement_token = requirements[requirement.slug]
            del requirements[requirement.slug]
            self.validate_requirement(tenant_id, requirement, requirement_token, for_update=for_update)
        if not for_update:
            for slug, requirement in requirements.items():
                raise CommandError(f"Validating structure failed: XREF requirement '{slug}' does not exist in the database")

    def validate_domain(self, tenant_id, domain_slug, tokens, for_update=False):
        domain = None
        try:
            domain = Domain.unscoped.get(slug=domain_slug)
        except Domain.DoesNotExist:
            if not for_update:
                raise CommandError(f"Validating structure failed: domain '{domain_slug}' does not exist in the database")
            return
            
        sections = dict((x['slug'], x) for x in tokens['domain']['sections'])
        for section in domain.sections(manager='unscoped').all():
            if section.slug not in sections:
                raise CommandError(f"Validating structure failed: database section '{section.slug}' does not exist in XREF file")
            section_token = sections[section.slug]
            del sections[section.slug]
            self.validate_section(tenant_id, section, section_token, for_update=for_update)
        if not for_update:
            for slug, section in sections.items():
                raise CommandError(f"Validating structure failed: XREF section '{slug}' does not exist in the database")

    def validate_structure(self, tenant_id, domain_slug, tokens, for_update=False):
        self.validate_domain(tenant_id, domain_slug, tokens, for_update=for_update)

    def update_status(self, tenant_id, domain_slug, tokens, logica_source):
        domain = Domain.unscoped.get(slug=domain_slug)
        for section in domain.sections(manager='unscoped').all():
            for requirement in section.requirements(manager='unscoped').all():
                for constraint in requirement.constraints(manager='unscoped').filter(status__in=[Constraint.STATUS_IMPLEMENTED, Constraint.STATUS_NON_COMPLIANT, Constraint.STATUS_COMPLIANT]):
                    goal = constraint.get_goal()
                    result = logica_lib.RunPredicateFromString(logica_source, "_Goal_" + goal)
                    try:
                        new_status = None
                        if int(result['r'].values[0]) == 1:
                            new_status = Constraint.STATUS_COMPLIANT
                        else:
                            new_status = Constraint.STATUS_NON_COMPLIANT
                        if new_status != constraint.status:
                            breakpoint()
                            if new_status == Constraint.STATUS_COMPLIANT:
                                self.stdout.write(self.style.SUCCESS(f'Constraint {constraint.slug} status changed to compliant'))
                            else:
                                assert new_status == Constraint.STATUS_NON_COMPLIANT, "Must be non-compliant"
                                if constraint.status == Constraint.STATUS_COMPLIANT:
                                    self.stdout.write(self.style.WARNING(f'Constraint {constraint.slug} status regressed from compliant back to non-compliant'))
                                else:
                                    self.stdout.write(self.style.WARNING(f'Constraint {constraint.slug} status changed to non-compliant'))
                            constraint.status = new_status
                            constraint.save()
                    except Exception as ex:
                        print(str(ex))
                        breakpoint()
                        pass

    def handle(self, *args, **options):
        tenant_id = options['tenant']
        if not tenant_id:
            raise CommandError("tenant is required")
        breakpoint()
        tenant = Tenant.objects.filter(id=tenant_id).first()
        if not tenant:
            raise CommandError("tenant not found")
        domain_slug = options['domain']
        if not domain_slug:
            raise CommandError("domain is required")
        tokens = self.process_xref_source(domain_slug)
        self.validate_structure(tenant_id, domain_slug, tokens, for_update=options['update_structure'])
        if options['update_structure']:
            self.update_structure(tenant_id, domain_slug, tokens)
        domain_slug = options['domain']
        logica_source = self.render_xref(tenant_id, domain_slug, tokens)
        print(logica_source)
        self.update_status(tenant_id, domain_slug, tokens, logica_source)

if __name__ == "__main__":
    main()
