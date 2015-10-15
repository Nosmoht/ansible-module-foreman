#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to manage Foreman hostgroup resources.
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: foreman_hostgroup
short_description: Manage Foreman Hostgroup using Foreman API v2
description:
- Manage Foreman Hostgroup using Foreman API v2
options:
  architecture:
    description: Architecture name
    required: False
    default: None
  domain:
    description: Domain name
    required: False
    default: None
  environment:
    description: Environment name
    required: False
    default: None
  medium:
    description: Medium name
    required: False
    default: None
  name:
    description: Hostgroup name
    required: True
  operatingsystem:
    description: Operatingsystem name
    required: False
    default: None
  partition_table:
    description: Partition table name
    required: False
    default: None
  smart_proxy:
    description: Smart Proxy name
    required: False
    default: None
  subnet:
    description: Subnet name
    required: False
    default: None
  state:
    description: Hostgroup state
    required: false
    default: present
    choices: ["present", "absent"]
  foreman_host:
    description: Hostname or IP address of Foreman system
    required: false
    default: 127.0.0.1
  foreman_port:
    description: Port of Foreman API
    required: false
    default: 443
  foreman_user:
    description: Username to be used to authenticate on Foreman
    required: true
  foreman_pass:
    description: Password to be used to authenticate user on Foreman
    required: true
notes:
- Requires the python-foreman package to be installed. See https://github.com/Nosmoht/python-foreman.
version_added: "2.0"
author: "Thomas Krahn (@nosmoht)"
'''

EXAMPLES = '''
- name: Ensure Hostgroup
  foreman_hostgroup:
    name: MyHostgroup
    state: present
    architecture: x86_64
    domain: MyDomain
    operatingsystem: MyOS
    subnet: MySubnet
    foreman_host: 127.0.0.1
    foreman_port: 443
    foreman_user: admin
    foreman_pass: secret
'''

try:
    from foreman.foreman import *
except ImportError:
    foremanclient_found = False
else:
    foremanclient_found = True


def get_resource(module, resource_type, resource_func, resource_name, search_title=False):
    """
    Look for a resource within Foreman Database. Return the resource if found or fail.
    If the Resource could not be found by name search by title.

    :param module:
    :param resource_type:
    :param resource_func:
    :param resource_name:
    :return:
    """
    try:
        result = resource_func(data=dict(name=resource_name))
        if not result and search_title:
            result = resource_func(data=dict(title=resource_name))
        if not result:
            module.fail_json(msg='{0} {1} not found'.format(resource_type, resource_name))
    except ForemanError as e:
        module.fail_json(msg='Error while getting {0}: {1}'.format(resource_type, e.message))
    return result


def ensure(module):
    # Changes in one of the following keys fails with:
    # <key> is not allowed as nested parameter for hostgroups. Allowed parameters are puppetclass_id, location_id, organization_id
    # Strange as for example the Compute Profile can be changed via UI
    hostgroup_nonupdateable_keys = ['architecture_id', 'compute_profile_id', 'domain_id', 'environment_id',
                                    'medium_id', 'operatingsystem_id', 'subnet_id', 'ptable_id', 'smart_proxy_id']
    hostgroup_updateable_keys = ['puppetclass_id', 'location_id', 'organization_id']

    name = module.params['name']
    architecture_name = module.params[ARCHITECTURE]
    compute_profile_name = module.params[COMPUTE_PROFILE]
    domain_name = module.params[DOMAIN]
    environment_name = module.params[ENVIRONMENT]
    medium_name = module.params[MEDIUM]
    operatingsystem_name = module.params[OPERATINGSYSTEM]
    partition_table_name = module.params['partition_table']
    smart_proxy_name = module.params[SMART_PROXY]
    subnet_name = module.params[SUBNET]
    state = module.params['state']

    foreman_host = module.params['foreman_host']
    foreman_port = module.params['foreman_port']
    foreman_user = module.params['foreman_user']
    foreman_pass = module.params['foreman_pass']

    theforeman = Foreman(hostname=foreman_host,
                         port=foreman_port,
                         username=foreman_user,
                         password=foreman_pass)

    data = {'name': name}

    try:
        hostgroup = theforeman.search_hostgroup(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get hostgroup: {0}'.format(e.message))

    # Architecture
    if architecture_name:
        architecture = get_resource(module=module,
                                    resource_type=ARCHITECTURE,
                                    resource_func=theforeman.search_architecture,
                                    resource_name=architecture_name)
        data['architecture_id'] = architecture.get('id')

    # Compute Profile
    if compute_profile_name:
        compute_profile = get_resource(module=module,
                                       resource_type=COMPUTE_PROFILE,
                                       resource_func=theforeman.search_compute_profile,
                                       resource_name=compute_profile_name)
        data['compute_profile_id'] = compute_profile.get('id')

    # Domain
    if domain_name:
        domain = get_resource(module=module,
                              resource_type=DOMAIN,
                              resource_func=theforeman.search_domain,
                              resource_name=domain_name)
        data['domain_id'] = domain.get('id')

    # Environment
    if environment_name:
        environment = get_resource(module=module,
                                   resource_type=ENVIRONMENT,
                                   resource_func=theforeman.search_environment,
                                   resource_name=environment_name)
        data['environment_id'] = environment.get('id')

    # Medium
    if medium_name:
        medium = get_resource(module=module,
                              resource_type=MEDIUM,
                              resource_func=theforeman.search_medium,
                              resource_name=medium_name)
        data['medium_id'] = medium.get('id')

    # Operatingssystem
    if operatingsystem_name:
        operatingsystem = get_resource(module=module,
                                       resource_type=OPERATINGSYSTEM,
                                       resource_func=theforeman.search_operatingsystem,
                                       resource_name=operatingsystem_name,
                                       search_title=True)
        data['operatingsystem_id'] = operatingsystem.get('id')

    # Partition Table
    if partition_table_name:
        partition_table = get_resource(module=module,
                                       resource_type=PARTITION_TABLE,
                                       resource_func=theforeman.search_partition_table,
                                       resource_name=partition_table_name)
        data['ptable_id'] = partition_table.get('id')

    # Smart Proxy
    if smart_proxy_name:
        smart_proxy = get_resource(module=module,
                                   resource_type=SMART_PROXY,
                                   resource_func=theforeman.search_smart_proxy,
                                   resource_name=smart_proxy_name)
        data['puppet_proxy_id'] = smart_proxy.get('id')

    # Subnet
    if subnet_name:
        subnet = get_resource(module=module,
                              resource_type=SUBNET,
                              resource_func=theforeman.search_subnet,
                              resource_name=subnet_name)
        data['subnet_id'] = subnet.get('id')

    if not hostgroup and state == 'present':
        try:
            hostgroup = theforeman.create_hostgroup(data=data)
            return True, hostgroup
        except ForemanError as e:
            module.fail_json(msg='Could not create hostgroup: {0}'.format(e.message))

    if hostgroup:
        if state == 'absent':
            try:
                hostgroup = theforeman.delete_hostgroup(id=hostgroup.get('id'))
                return True, hostgroup
            except ForemanError as e:
                module.fail_json(msg='Could not delete hostgroup: {0}'.format(e.message))

        if not all(data.get(key, None) == hostgroup.get(key, None) for key in hostgroup_updateable_keys):
            try:
                for key in hostgroup_nonupdateable_keys:
                    data.pop(key, None)
                hostgroup = theforeman.update_hostgroup(id=hostgroup.get('id'), data=data)
                return True, hostgroup
            except ForemanError as e:
                module.fail_json(msg='Could not update hostgroup: {0}'.format(e.message))

    return False, hostgroup


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            architecture=dict(type='str', default=None),
            compute_profile=dict(type='str', default=None),
            domain=dict(type='str', default=None),
            environment=dict(type='str', default=None),
            medium=dict(type='str', default=None),
            operatingsystem=dict(type='str', default=None),
            partition_table=dict(type='str', default=None),
            smart_proxy=dict(type='str', default=None),
            subnet=dict(type='str', default=None),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            foreman_host=dict(type='str', default='127.0.0.1'),
            foreman_port=dict(type='str', default='443'),
            foreman_user=dict(type='str', required=True),
            foreman_pass=dict(type='str', required=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    changed, hostgroup = ensure(module)
    module.exit_json(changed=changed, hostgroup=hostgroup)

# import module snippets
from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
