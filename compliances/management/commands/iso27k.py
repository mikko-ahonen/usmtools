#!/usr/bin/env python
import csv
import re
#import os
#import sys
#import json
#import glob
import argparse
##from slugify import slugify
#from logica.common import logica_lib
from django.utils import timezone
from pathlib import Path

#from pyparsing import ParseException, pprint
#import jinja2

from django.core.management.base import BaseCommand, CommandError

#from usm.settings import BASE_DIR
#from .grammar import XREF_GRAMMAR
from ...models import Domain, Section, Control, Requirement, Constraint, Category, Statement
from workflows.tenant_models import Tenant

def strip(s):
    return re.sub(r"^[\s\n\t]*(.*)[\s\n\t\r]*", r"\1", s)

class Command(BaseCommand):
    help = "Update cross-references in the database for certain domain"

    def add_arguments(self, parser):
        parser.add_argument('--domain', type=str, help="Slug for the domain to be updated")
        parser.add_argument('--tenant', type=str, help="Tenant for the domain to be updated")

    def parse_docids(self, section_identifier):
        if '#' in section_identifier:
            section_identifier.replace(".#1", "")
            section_identifier.replace("#1", "")
        a = section_identifier.split('.')
        if len(a) == 0:
            return None, None, None
        if len(a) == 1:
            return a[0], None, None
        if len(a) == 2:
            return a[0], ".join(a[:2]), None
        return a[0], ".".join(a[:2]), ".".join(a[:])

    def parse_section_title(self, line):
        return line[1]

    def parse_control_title(self, line):
        return line[3]

    def parse_requirement_text(self, line):
        if line[2].startswith("Annex"):
            return line[4]
        else:
            return None


    def parse_statement_text(self, line):
        return line[5]

    def parse_constraint_text(self, line):
        return line[6]

    def get_category(self, tenant, domain, line):
        name = 'No category'
        for i in range(7, 10):
            if line[i] != '':
                name = line[i]
        category, created = Category.objects.get_or_create(tenant_id=tenant.id, name=name, domain_id=domain.id)
        return category

    def update_structures(self, tenant):
        now = timezone.now()
        domain, _ = Domain.unscoped.update_or_create(tenant=tenant, slug="iso-27001", defaults={"name": "ISO 27001", "description": "ISO 27001 V.2022"})
        with open("fixtures/iso27k/xref-iso27k.tsv") as f:
            tsv_file = csv.reader(f, delimiter="\t")
            last_section_docid = None
            last_control_docid = None
            last_req_docid = None
            last_statement_text = None
            last_constraint_text = None
            section_idx = 0
            control_idx = 0
            requirement_idx = 0
            statement_idx = 0
            constraint_idx = 0
            for line in tsv_file:
                if len(line) < 3:
                    continue
                section_docid, control_docid, req_docid = self.parse_docids(line[2])

                if not section_docid:
                    continue

                if section_docid != last_section_docid:
                    section_title = self.parse_section_title(line)
                    section_idx += 1
                    section, _ = Section.unscoped.update_or_create(tenant=tenant, docid=section_docid, domain_id=domain.id, defaults={"index": section_idx, "title": section_title})
                
                if subsection_docid != last_subsection_docid:
                    subsection_title = self.parse_subsection_title(line)
                    subsection_idx += 1
                    subsection, _ = Subsection.unscoped.update_or_create(tenant=tenant, docid=section_docid, domain_id=domain.id, defaults={"index": section_idx, "title": section_title})
                
                if control_docid != last_control_docid: 
                    control_title = self.parse_control_title(line)
                    control_idx += 1
                    control, _ = Control.unscoped.update_or_create(tenant=tenant, docid=control_docid, subsection_id=subsection.id, defaults={"index": control_idx ,"title": control_title})

                if req_docid != last_req_docid: 
                    req_text = self.parse_requirement_text(line)
                    requirement_idx += 1
                    req, _ = Requirement.unscoped.update_or_create(tenant=tenant, docid=req_docid, control_id=control.id, defaults={"text": req_text, "index": requirement_idx})
                statement_text = self.parse_statement_text(line)

                if statement_text != last_statement_text:
                    statement_idx += 1
                    statement, _ = Statement.unscoped.update_or_create(tenant=tenant, requirement_id=req.id, defaults={"text": statement_text, "index": statement_idx})
                    last_statement_text = statement_text

                constraint_text = self.parse_constraint_text(line)
                if constraint_text != last_constraint_text:
                    constraint_idx += 1
                    constraint_category = self.get_category(tenant, domain, line)
                    constraint, _ = Constraint.unscoped.update_or_create(tenant=tenant, statement_id=statement.id, defaults={"text": constraint_text, "category": constraint_category, "index": constraint_idx})
                    last_constraint_text = constraint_text

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
        self.update_structures(tenant)

if __name__ == "__main__":
    main()
