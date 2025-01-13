from .models import Tenant, Service, Routine, Profile, OrganizationUnit, Customer

def uuid_as_str(uuid):
    return str(uuid) if uuid else None

def export_as_usm_dif(tenant):

    return {
        'usm_dif_version': '1.0.0',
        'source_system': {
            'vendor': 'usm.coach',
            'name': 'bpm-tool',
            'version': '0.1.0',
            'instance': '6a831346-fc7d-45cc-9b66-2ea0040f7278',
        },
        'export-version': '1.0.,0',
        'tenant': {
            'id': uuid_as_str(tenant.id),
            'name': tenant.name,
            'created_at': tenant.created_at.isoformat(),
            'created_by': {
                'id': uuid_as_str(tenant.created_by.id),
                'first_name': tenant.created_by.first_name,
                'last_name': tenant.created_by.last_name,
                'email': tenant.created_by.email,
            } if tenant.created_by else None,
            'modified_at': tenant.modified_at.isoformat(),
            'modified_by': {
                'id': uuid_as_str(tenant.modified_by.id),
                'first_name': tenant.modified_by.first_name,
                'last_name': tenant.modified_by.last_name,
                'email': tenant.modified_by.email,
            } if tenant.modified_by else None,
        },
        'profiles': [ {
            'id': uuid_as_str(profile.id),
            'name': profile.name,
        } for profile in tenant.profiles.all() ],
        'customers': [ {
            'id': uuid_as_str(customer.id),
            'name': customer.name,
            'type': customer.customer_type,
        } for customer in tenant.customers.all() ],
        'organization_units': [ {
            'id': uuid_as_str(ou.id),
            'parent': uuid_as_str(ou.parent_id),
            'name': ou.name,
        } for ou in tenant.organization_units.all() ],
        'services': [ {
            'id': uuid_as_str(service.id),
            'name': uuid_as_str(service.name),
            'parent': uuid_as_str(service.parent_id),
            'description': uuid_as_str(service.description),
            'customers': [ uuid_as_str(cs.customer_id) for cs in service.service_customers.all() ],
            'routines': [ {
                'id': uuid_as_str(routine.id),
                'name': uuid_as_str(routine.name),
                'description': uuid_as_str(routine.description),
                'steps': [ {
                    'id': uuid_as_str(step.id),
                    'sort_index': step.index,
                    'name': step.name,
                    'description': step.description,
                    'process': step.process,
                    'activities': [ {
                        'id': uuid_as_str(activity.id),
                        'sort_index': activity.index,
                        'description': step.description,
                        'responsibles': [ {
                            'id': uuid_as_str(responsible.id),
                            'types': responsible.types,
                            'organization': {
                                'id': uuid_as_str(responsible.organization_unit.id),
                                'name': responsible.organization_unit.name,
                            } if responsible.organization_unit else None,
                            'profile': {
                                'id': uuid_as_str(responsible.profile.id),
                                'name': responsible.profile.name,
                            } if responsible.profile else None,
                            'work_instructions': [ {
                                'id': uuid_as_str(wi.id),
                                'description': wi.description,
                            } for wi in responsible.work_instructions.all() ],
                        } for responsible in activity.responsibles.all() ],
                    } for activity in step.activities.all() ],
                } for step in routine.steps.all() ]
            } for routine in service.routines.all() ]
        } for service in tenant.services.all() ],
    }
