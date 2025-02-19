from .models import Tenant, Service, Routine, Profile, OrganizationUnit, Customer

def uuid_as_str(uuid):
    return str(uuid) if uuid else None

def export_as_usm_dif(tenant):

    return {
        'usm_dif_version': '2.0.0',
        'source_system': {
            'vendor': 'USM Coach',
            'name': 'usm.tools',
            'version': '0.2.0',
            'instance': '6a831346-fc7d-45cc-9b66-2ea0040f7278',
        },
        'export-version': '2.0.,0',
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
                        'responsibilities': [ {
                            'id': uuid_as_str(responsibility.id),
                            'types': responsibility.types,
                            'organization': {
                                'id': uuid_as_str(responsibility.organization_unit.id),
                                'name': responsibility.organization_unit.name,
                            } if responsibility.organization_unit else None,
                            'profile': {
                                'id': uuid_as_str(responsibility.profile.id),
                                'name': responsibility.profile.name,
                            } if responsibility.profile else None,
                            'instruction': {
                                'id': uuid_as_str(i.id),
                                'description': i.description,
                            } if responsibility.instruction else None,
                        } for responsibility in action.responsibility.all() ],
                    } for activity in step.activities.all() ],
                } for step in routine.steps.all() ]
            } for routine in service.routines.all() ]
        } for service in tenant.services.all() ],
    }
