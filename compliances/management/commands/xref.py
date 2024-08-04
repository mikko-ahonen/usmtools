#!/usr/bin/env python
import os
import sys
import json
import argparse
#from slugify import slugify

from pyparsing import ParseException, pprint
import jinja2

from django.core.management.base import BaseCommand, CommandError

from config.settings import BASE_DIR
from .grammar import XREF_GRAMMAR

class Command(BaseCommand):
    help = "Update cross-references in the database for certain domain"

    def add_arguments(self, parser):
        parser.add_argument('--domain', type=str, help="Slug for the domain to be updated")
        parser.add_argument('--update-structure', type=str, help="Update the database structure. Defaults to only verifying that the structure corresponds to the source code.")

    def process_xref_source(self, domain_slug):
        try:
            xref_path = os.path.join(BASE_DIR, f'compliances/management/commands/{domain_slug}.xref')
            with open(xref_path, 'r') as f:
                data = f.read()
            try:
                bnf = XREF_GRAMMAR()
                tokens = bnf.parse_string(data)
                #pprint.pprint(tokens.as_dict())
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

    def render_xref(self, domain_slug, tokens):
        TEMPLATE_FILE = 'compliances/management/commands/xref.template'
        try:
            templateLoader = jinja2.FileSystemLoader(searchpath=BASE_DIR)
            templateEnv = jinja2.Environment(loader=templateLoader)
            print(TEMPLATE_FILE)
            template = templateEnv.get_template(TEMPLATE_FILE)
            out = template.render(terms=tokens['domain']['terms'], requirements=tokens['domain']['sections'])
            print(out)
            return out
        except Exception as ex:
            raise CommandError("Failed to render the XREF template: " + ex)

    def update_structure(self, domain_slug, tokens):
        domain = Domain.objects.update_or_create(slug=domain_slug, defaults={"description": tokens['domain']['doc']})
        for section_token in tokens['domain']['sections']:
            section = Section.objects.update_or_create(slug=section_token['slug'], defaults={"title": section_token['qualifiers']['title']['value'], "description": section_token['doc']})
            for req_token in section_token['requirements']:
                req = Requirement.objects.update_or_create(slug=req_token['slug'], defaults={"title": section_token['qualifiers']['title']['value'], "text": section_token['doc']})
                for constr_token in req_token['constraints']:
                    constraint = Constraint.objects.update_or_create(slug=constr_token['slug'], defaults={"text": constr_token['doc']})

    def validate_constraint(self, constraint, constraint_token, for_update=False):
        return True

    def validate_requirement(self, requirement, requirement_token, for_update=False):
        constraints = dict((x['slug'], x) for x in section_token['constraints'])
        for constraint in requirement.constraints:
            if constraint.slug not in constraints:
                raise CommandError("Validating structure failed: database constraint '{constraint.slug}' does not exist in XREF file")
            contraint_token = constraints[constraint.slug]
            del constraints[constraint.slug]
            self.validate_constraint(constraint, constraint_token, for_update=for_update)
        if not for_update:
            for slug, requirement in constraints:
                raise CommandError("Validating structure failed: XREF contraint '{slug}' does not exist in the database")

    def validate_section(self, section, section_token, for_update=False):
        requirements = dict((x['slug'], x) for x in section_token['requirements'])
        for requirement in section.requirements:
            if requirement.slug not in requirements:
                raise CommandError("Validating structure failed: database requirement '{requirement.slug}' does not exist in XREF file")
            requirement_token = requirements[requirement.slug]
            del requirements[requirement.slug]
            self.validate_requirement(requirement, requirement_token, for_update=for_update)
        if not for_update:
            for slug, requirement in requirements:
                raise CommandError("Validating structure failed: XREF requirement '{slug}' does not exist in the database")

    def validate_domain(self, domain, tokens, for_update=False):
        domain = Domain.objects.get(domain_slug)
        sections = dict((x['slug'], x) for x in tokens['domain']['sections'])
        for section in domain.sections:
            if section.slug not in sections:
                raise CommandError("Validating structure failed: database section '{section.slug}' does not exist in XREF file")
            section_token = sections[section.slug]
            del sections[section.slug]
            self.validate_section(section, section_token, for_update=False)
        if not for_update:
            for slug, section in sections:
                raise CommandError("Validating structure failed: XREF section '{slug}' does not exist in the database")

    def validate_structure(self, domain_slug, tokens, for_update=False):
        validate_domain(domain_slug, tokens, for_update=for_update)

    def update_status(self, domain_slug, tokens):
        domain = Domain.objects.get(domain_slug)
        for section in domain.sections:
            pass
            
    def handle(self, *args, **options):
        domain_slug = options['domain']
        if not domain_slug:
            raise CommandError("domain is required")
        tokens = self.process_xref_source(domain_slug)
        self.validate_structure(domain_slug, tokens, for_update=options['update_structure'])
        if options['update_structure']:
            self.update_structure(domain_slug, tokens)
        domain_slug = options['domain']
        out = self.render_xref(domain_slug, tokens)
        print(out)

if __name__ == "__main__":
    main()
