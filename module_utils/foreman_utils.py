# -*- coding: utf-8 -*-
# (c) Radim Janča (Cesnet) 2018

try:
    from foreman.foreman import *
except ImportError:
    module.fail_json(msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')


def init_foreman_client(module):
    return Foreman(hostname=module.params['foreman_host'],
                   port=module.params['foreman_port'],
                   username=module.params['foreman_user'],
                   password=module.params['foreman_pass'],
                   ssl=module.params['foreman_ssl'])


def equal_dict_lists(l1, l2, compare_key='name'):
    s1 = set(map(lambda x: x[compare_key], l1))
    s2 = set(map(lambda x: x[compare_key], l2))
    return s1 == s2


def dict_list_to_list(alist, key):
    result = list()
    if alist:
        for item in alist:
            result.append(item.get(key, None))
    return result


def get_resource_ids(resource_type, module, theforeman, resource_names, search_field='name'):
    result = []
    for i in range(0, len(resource_names)):
        try:
            resource = theforeman.search_resource(resource_type=resource_type, data={search_field: resource_names[i]})
            if not resource:
                module.fail_json(msg='Could not find {type} {name}'.format(
                    type=resource_type,name=resource_names[i]))
            result.append(resource.get('id'))
        except ForemanError as e:
            module.fail_json(msg='Search for {type} \'{name}\' throws an Error: {err}'.format(
                type=resource_type,name=resource_names[i],err=e.message))
    return result

def get_organization_ids(module, theforeman, organizations):
    return get_resource_ids(ORGANIZATIONS, module, theforeman, organizations)
def get_location_ids(module, theforeman, locations):
    return get_resource_ids(LOCATIONS, module, theforeman, locations)
def get_operatingsystem_ids(module, theforeman, operating_systems):
    return get_resource_ids(OPERATINGSYSTEMS, module, theforeman, operating_systems, search_field='title')


def organizations_equal(data, resource):
    if 'organization_ids' in data:
        if not ('organizations' in resource):
            return False
        else:
            organization_ids = dict_list_to_list(resource['organizations'], 'id')
            if set(data['organization_ids']) != set(organization_ids):
                return False
    return True


def locations_equal(data, resource):
    if 'location_ids' in data:
        if not ('locations' in resource):
            return False
        else:
            location_ids = dict_list_to_list(resource['locations'], 'id')
            if set(data['location_ids']) != set(location_ids):
                return False
    return True


def operatingsystems_equal(data, resource):
    if 'operatingsystem_ids' in data:
        if not ('operatingsystems' in resource):
            return False
        else:
            operatingsystem_ids = dict_list_to_list(resource['operatingsystems'], 'id')
            if set(data['operatingsystem_ids']) != set(operatingsystem_ids):
                return False
    return True
