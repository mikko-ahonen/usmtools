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
import random

#from pyparsing import ParseException, pprint
#import jinja2

from django.core.management.base import BaseCommand, CommandError

#from usm.settings import BASE_DIR
#from .grammar import XREF_GRAMMAR
from ...models import Domain, Section, Requirement, Requirement, Constraint, Category, Statement, ConstraintStatement
from workflows.tenant_models import Tenant

def strip(s):
    return re.sub(r"^[\s\n\t]*(.*)[\s\n\t\r]*", r"\1", s)

def isnan(s):
    if s == None:
        return True
    if s == "nan":
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

        requirement_docid = None
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
            requirement_docid = rv.pop(-1)
        try:
            section_docid = rv.pop(-1)
        except IndexError:
            breakpoint()
            pass

        return section_docid, requirement_docid, req_docid

    def parse_section_title(self, line):
        if isnan(line[3]):
            return str(line[1])
        else:
            return str(line[3])

    #def parse_requirement_title(self, line):
    #    return line[4]

    def parse_requirement_text(self, line):
        if str(line[2]).startswith("Annex"):
            return str(line[4])
        else:
            return str(line[4])

    def parse_statement_text(self, line):
        return str(line[5])

    def parse_constraint_text(self, line):
        return str(line[6])

    def get_category(self, tenant, domain, line):
        name = 'No category'
        if len(line) < 9:
            pass
            breakpoint()
        try:
            names = []
            for i in range(7, 17):
                if not isnan(line[i]):
                    names.append(str(line[i]))
            name = random.choice(names)
        except IndexError:
            pass
        category, created = Category.unscoped.get_or_create(tenant_id=tenant.id, domain_id=domain.id, name=name)
        return category

    def create_categories(self, tenant, domain):
        for i, name in enumerate("CTM CHM MIR INC OPS RIM TECH SDC ORG SERV".split()):
            Category.unscoped.create(tenant_id=tenant.id, domain_id=domain.id, name=name, index=i)
        Category.unscoped.create(tenant_id=tenant.id, domain_id=domain.id, name="No category", index=9999)

    def update_structures(self, tenant):
        now = timezone.now()
        domain, _ = Domain.unscoped.update_or_create(tenant=tenant, slug="iso-27001", defaults={"name": "ISO 27001", "description": "ISO 27001 V.2022"})
        self.create_categories(tenant, domain)
        parent_sections = {}
        df = pd.read_excel("fixtures/iso27k/iso27k.xlsx", sheet_name=1, dtype=str, header=None)
        if True:
            #tsv_file = csv.reader(f) #, dialect=csv.excel_tab) #delimiter="\t")
            last_section_docid = None
            last_requirement_docid = None
            last_requirement_title = None
            last_req_text = None
            last_statement_text = None
            last_constraint_text = None
            parent_section = None
            section_idx = 0
            requirement_idx = 0
            requirement_idx = 0
            statement_idx = 0
            constraint_idx = 0
            constraint_statement_idx = 0
            doc = None
            for line in df.values.tolist():

                if "ANNEX A" in str(line[1]):
                    doc = "Annex A"
                    continue

                if line[1] == "ISO/IEC 27001 Main clauses":
                    doc = "Main clauses"
                    statement = None
                    requirement = None
                    last_statement_text = None
                    last_constraint_text = None
                    section = None
                    continue

                if len(line) < 3:
                    print("\n".join(line))
                    continue

                if isnan(line[1]) and isnan(line[2]):
                    continue

                if isnan(line[4]):
                    if m := re.search(r"^([\d\.]+) (.*)", str(line[2])):
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
                        parent = parent_sections[doc + '-' + parent_section_docid]

                    try:
                        parent_section = Section.unscoped.get(tenant=tenant, doc=doc, domain_id=domain.id, docid=section_docid)
                    except Section.DoesNotExist:
                        if isnan(section_title):
                            breakpoint()
                        parent_section = Section.unscoped.create(tenant=tenant, doc=doc, docid=section_docid, domain_id=domain.id, index=section_idx, title=section_title, parent=parent)
                        parent_sections[doc + '-' + section_docid] = parent_section

                    continue

                section_docid, requirement_docid, req_docid = self.parse_docids(line[2])

                #if doc != "Annex A" and not requirement_docid:
                #    requirement = None
                #    requirement = None
                #    statement = None
                #    constraint = None

                if not section_docid:
                    section = None
                    continue

                print(section_docid)
                print(requirement_docid)
                print(req_docid)

                if section_docid != last_section_docid:
                    parent_section_docid = get_parent_docid(section_docid)
                    if parent_section_docid is None:
                        parent = None
                    else:
                        parent = parent_sections[doc + '-' + parent_section_docid]
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
                    requirement_title = self.parse_requirement_text(line)
                elif requirement_docid and requirement and requirement_docid == last_requirement_docid: # or re.search(r'.#\d+$', requirement_docid))):
                    requirement_title = self.parse_requirement_text(line)
                    if requirement_title != last_requirement_title:
                        requirement.text += "\n" + requirement_title
                        requirement.save()
                        last_requirement_title = requirement_title

                if doc == "Annex A" or (requirement_docid and requirement_docid != last_requirement_docid):
                    requirement_title = self.parse_requirement_text(line)
                    if requirement_title != last_requirement_title:
                        requirement_idx += 1
                        last_requirement_title = requirement_title
                        requirement, _ = Requirement.unscoped.update_or_create(tenant=tenant, docid=requirement_docid, section_id=section.id, defaults={"index": requirement_idx ,"text": requirement_title})
                        last_req_text = None
                        statement = None
                        last_statement_text = None
                        constraint = None
                        last_constraint_text = None

                    statement_text = self.parse_statement_text(line)
                    if ((doc != "Annex A" and not statement) or (not isnan(statement_text))) and statement_text != last_statement_text:
                        if requirement is None:
                            breakpoint()
                        #if isnan(statement) and doc == "Annex A":
                        #    breakpoint()
                        statement_idx += 1
                        if isnan(statement_text):
                            statement_text = "Not defined"
                        statement, _ = Statement.unscoped.update_or_create(tenant=tenant, requirement_id=requirement.id, text=statement_text, defaults={"index": statement_idx})
                        last_statement_text = statement_text

                    constraint_text = self.parse_constraint_text(line)
                    if not isnan(constraint_text) and constraint_text != last_constraint_text:
                        constraint_idx += 1
                        constraint_category = self.get_category(tenant, domain, line)
                        try:
                            constraint = Constraint.unscoped.get(tenant=tenant, domain_id=domain.id, text=constraint_text)
                        except Constraint.DoesNotExist:
                            constraint = Constraint.unscoped.create(tenant=tenant, domain_id=domain.id, text=constraint_text, category=constraint_category, index=constraint_idx)
                        constraint_statement_idx += 1

                        ConstraintStatement.unscoped.create(tenant=tenant, statement=statement, constraint=constraint, index=constraint_statement_idx)
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
