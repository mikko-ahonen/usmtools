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
import pandas as pd
import numpy as np
import math

#from pyparsing import ParseException, pprint
#import jinja2

from django.core.management.base import BaseCommand, CommandError

#from usm.settings import BASE_DIR
#from .grammar import XREF_GRAMMAR
from ...models import Domain, Section, Control, Requirement, Constraint, Category, Statement
from workflows.tenant_models import Tenant

def strip(s):
    return re.sub(r"^[\s\n\t]*(.*)[\s\n\t\r]*", r"\1", s)

def isnan(s):
    if s == None:
        return True
    if s == np.nan:
        return True
    if isinstance(s, float) and math.isnan(s):
        return True
    if isinstance(s, str) and s == "":
        return True

def get_parent_docid(docid):
    a = str(docid).split('.')
    if len(a) == 1:
        return None
    return ".".join(a[:-1])

class Command(BaseCommand):
    help = "Update cross-references in the database for certain domain"

    def add_arguments(self, parser):
        parser.add_argument('--domain', type=str, help="Slug for the domain to be updated")
        parser.add_argument('--tenant', type=str, help="Tenant for the domain to be updated")

    def parse_docids(self, section_identifier):
        if isnan(section_identifier) or section_identifier == 'section':
            return None, None, None

        section_identifier = re.sub(r"(\d)#(\d)$", r"\1.#\2", section_identifier)
        annex = False

        control_docid = None
        section_identifier = str(section_identifier)
        if section_identifier == 'nan':
            return None, None, None
        if section_identifier.startswith("Annex"):
            annex = True
            section_identifier = section_identifier.replace("Annex A ", "")
        a = section_identifier.split('.')
        rv = []
        for i in range(1, len(a) + 1):
            rv.append(".".join(a[:i]))
        if not annex and a[-1].isalpha():
            req_docid = rv.pop(-1)
        else:
            req_docid = None
        if not annex and len(rv) > 1:
            control_docid = rv.pop(-1)
        try:
            section_docid = rv.pop(-1)
        except IndexError:
            breakpoint()
            pass

        return section_docid, control_docid, req_docid

    def parse_section_title(self, line):
        if isnan(line[3]):
            return line[1]
        else:
            return line[3]

    def parse_control_title(self, line):
        return line[4]

    def parse_requirement_text(self, line):
        if line[2].startswith("Annex"):
            return line[4]
        else:
            return line[4]

    def parse_statement_text(self, line):
        return line[5]

    def parse_constraint_text(self, line):
        return line[6]

    def get_category(self, tenant, domain, line):
        name = 'No category'
        if len(line) < 9:
            pass
            breakpoint()
        try:
            for i in range(7, 9):
                if not isnan(line[i]):
                    name = line[i]
        except IndexError:
            pass
            breakpoint()
        category, created = Category.objects.get_or_create(tenant_id=tenant.id, name=name, domain_id=domain.id)
        return category

    def update_structures(self, tenant):
        now = timezone.now()
        domain, _ = Domain.unscoped.update_or_create(tenant=tenant, slug="iso-27001", defaults={"name": "ISO 27001", "description": "ISO 27001 V.2022"})
        parent_sections = {}
        df = pd.read_excel("fixtures/iso27k/iso27k.xlsx", sheet_name=1, dtype=str, header=None)
        if True:
            #tsv_file = csv.reader(f) #, dialect=csv.excel_tab) #delimiter="\t")
            last_section_docid = None
            last_control_docid = None
            last_control_title = None
            last_req_text = None
            last_statement_text = None
            last_constraint_text = None
            parent_section = None
            section_idx = 0
            control_idx = 0
            requirement_idx = 0
            statement_idx = 0
            constraint_idx = 0
            doc = None
            for line in df.values.tolist():

                if "ANNEX A" in str(line[1]):
                    doc = "Annex A"
                    continue
                if line[1] == "ISO/IEC 27001 Main clauses":
                    doc = "Main clauses"
                    continue
                if len(line) < 3:
                    print("\n".join(line))
                    continue

                if isnan(line[1]) and isnan(line[2]):
                    breakpoint()
                    continue

                if isnan(line[4]):
                    if m := re.match(r"^([\d\.]+) (.*)", str(line[2])):
                        section_docid = m.group(1)
                        section_title = m.group(2)
                    else:
                        if isnan(line[2]):
                            # bug in the data
                            section_docid = line[1]
                        else:
                            section_docid = line[2]
                        section_title = line[3] if not isnan(line[3]) else line[4]
                    section_idx += 1
                    parent_section_docid = get_parent_docid(section_docid)
                    if not parent_section_docid:
                        parent = None
                    else:
                        parent = parent_sections[parent_section_docid]

                    try:
                        parent_section = Section.unscoped.get(tenant=tenant, doc=doc, domain_id=domain.id, docid=section_docid)
                    except Section.DoesNotExist:
                        if isnan(section_title):
                            breakpoint()
                        parent_section = Section.unscoped.create(tenant=tenant, doc=doc, docid=section_docid, domain_id=domain.id, index=section_idx, title=section_title, parent=parent)
                        parent_sections[section_docid] = parent_section

                    continue

                section_docid, control_docid, req_docid = self.parse_docids(line[2])

                if not section_docid:
                    continue

                print(section_docid)
                print(control_docid)
                print(req_docid)

                if section_docid != last_section_docid:
                    parent_section_docid = get_parent_docid(section_docid)
                    if parent_section_docid is None:
                        parent = None
                    else:
                        parent = parent_sections[parent_section_docid]
                    section_title = self.parse_section_title(line)
                    section_idx += 1
                    try:
                        section = Section.unscoped.get(tenant=tenant, doc=doc, domain_id=domain.id, docid=section_docid)
                    except Section.DoesNotExist:
                        if isnan(section_title):
                            breakpoint()
                        section = Section.unscoped.create(tenant=tenant, doc=doc, docid=section_docid, domain_id=domain.id, index=section_idx, title=section_title, parent=parent)

                    last_section_docid = section_docid

                if doc == "Annex A":
                    control_title = self.parse_control_title(line)
                elif (control_docid and (control_docid == last_control_docid or re.match(r'.#\d+$', control_docid))):
                    control_title = self.parse_control_title(line)
                    if control_title != last_control_title:
                        control.description += "\n" + control_title
                        control.save()
                        last_control_title = control_title

                if doc == "Annex A" or (control_docid and control_docid != last_control_docid):
                    if control_title != last_control_title:
                        control_idx += 1
                        last_control_title = control_title
                        control, _ = Control.unscoped.update_or_create(tenant=tenant, docid=control_docid, section_id=section.id, defaults={"index": control_idx ,"description": control_title})

                    req_text = self.parse_requirement_text(line)
                    if req_text != last_req_text:
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
