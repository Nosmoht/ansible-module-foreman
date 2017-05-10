#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to manage Foreman filter resources.
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
#
# (C) 2017 Guido Günther <agx@sigxcpu.org>

DOCUMENTATION = '''
---
module: foreman_filter
short_description: Manage Foreman Filter using Foreman API v2
description:
- Create and delete Foreman Filters using Foreman API v2
options:
  role:
    description: role this filter belongs tue
    required: true
  resource_type:
    description: resource type this permission affects
    required: true
  permissions:
    description: List of permissions
    required: true
  state:
    description: State of filter
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
  foreman_ssl:
    description: Enable SSL when connecting to Foreman API
    required: false
    default: true
notes:
- Requires the python-foreman package to be installed. See https://github.com/Nosmoht/python-foreman.
version_added: "2.0"
author: "Thomas Krahn (@nosmoht)"
'''

EXAMPLES = '''
- name: Ensure Production filter is present
  foreman_filter:
    role: "Host Power"
    resource: Host
    permissions:
       - power_hosts
    state: present
    foreman_host: 127.0.0.1
    foreman_port: 443
    foreman_user: admin
    foreman_pass: secret
'''

try:
    from foreman.foreman import *

    foremanclient_found = True
except ImportError:
    foremanclient_found = False

def get_permission_ids(module, theforeman, resource_type, permissions):
    result = []
    for i in range(0, len(permissions)):
        try:
            permission = theforeman.search_permission(data={'resource_type': resource_type,
                                                            'name': permissions[i]})
            if not permission:
                module.fail_json(msg='Could not find Permission {0} for {1}'.format(permissions[i],
                                                                                    resource_type))
            result.append(permission.get('id'))
        except ForemanError as e:
            module.fail_json(msg='Could not get Permissions: {0}'.format(e.message))
    return result


def get_role_id(module, theforeman, rolename):
    try:
        role = theforeman.search_role(data={'name': rolename})
        if not role:
            module.fail_json(msg='Could not find role {0}'.format(rolename))
        i = role.get('id')
        if not i:
            module.fail_json(msg='Can\'t find id for {0} in {1}'.format(rolename, role))
    except ForemanError as e:
        module.fail_json(msg='Could not get role: {0}'.format(e.message))
    return role['id']


def ensure(module):
    state = module.params['state']
    role = module.params['role']
    resource_type = module.params['resource_type']
    permissions = module.params['permissions']

    foreman_host = module.params['foreman_host']
    foreman_port = module.params['foreman_port']
    foreman_user = module.params['foreman_user']
    foreman_pass = module.params['foreman_pass']
    foreman_ssl = module.params['foreman_ssl']

    theforeman = Foreman(hostname=foreman_host,
                         port=foreman_port,
                         username=foreman_user,
                         password=foreman_pass,
                         ssl=foreman_ssl)

    data = dict()

    data['permission_ids'] = get_permission_ids(module, theforeman, resource_type, permissions)
    data['role_id'] = get_role_id(module, theforeman, role)

    filters = theforeman.search_filter(data={'role_id': data['role_id']})
    if not filters and state == 'present':
        try:
            filtr = theforeman.create_filter(data=data)
            return True, filtr
        except ForemanError as e:
            module.fail_json(msg='Could not create filter: {0}'.format(e.message))

    if filters:
        if type(filters) != type([]):
            filters = [filters]

        if state == 'present':
            for f in filters:
                if sorted(p['id'] for p in f['permissions']) == sorted(data['permission_ids']):
                    return False, f
            try:
                # We have no way to decide if perms should be updated so best
                # we can do is create a new one
                filtr = theforeman.create_filter(data=data)
                return True, filtr
            except ForemanError as e:
                module.fail_json(msg='Could not create filter: {0}'.format(e.message))
        elif state == 'absent':
            for f in filters:
                if sorted(p['id'] for p in f['permissions']) == sorted(data['permission_ids']):
                    try:
                        filtr = theforeman.delete_filter(id=f['id'])
                        return True, filtr
                    except ForemanError as e:
                        module.fail_json(msg='Could not delete filter: {0}'.format(e.message))
    return False, filtr


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=['present', 'absent']),
            role=dict(type='str', required=True),
            resource_type=dict(type='str', required=True),
            permissions=dict(type='list', required=True),
            foreman_host=dict(type='str', default='127.0.0.1'),
            foreman_port=dict(type='str', default='443'),
            foreman_user=dict(type='str', required=True),
            foreman_pass=dict(type='str', required=True, no_log=True),
            foreman_ssl=dict(type='bool', default=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    changed, filtr = ensure(module)
    module.exit_json(changed=changed, filter=filtr)


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
