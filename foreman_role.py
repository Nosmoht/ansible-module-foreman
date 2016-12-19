#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to manage Foreman role resources.
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
module: foreman_role
short_description: Manage Foreman Role using Foreman API v2
description:
- Create, update and delete Foreman Role using Foreman API v2
options:
  name:
    description: Role name
    required: false
    default: None
  state:
    description: Role state
    required: false
    default: 'present'
    choices: ['present', 'absent']
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
- name: Ensure Role
  foreman_role:
    name: MyRole
    state: present
    foreman_host: foreman.example.com
    foreman_port: 443
    foreman_user: admin
    foreman_pass: secret
'''

try:
    from foreman.foreman import *

    foremanclient_found = True
except ImportError:
    foremanclient_found = False


def ensure(module):
    name = module.params['name']
    state = module.params['state']

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

    data = {'name': name}

    try:
        role = theforeman.search_role(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get role: {0}'.format(e.message))

    if not role and state == 'present':
        try:
            role = theforeman.create_role(data=data)
            return True, role
        except ForemanError as e:
            module.fail_json(msg='Could not create role: {0}'.format(e.message))

    if role:
        if state == 'absent':
            try:
                role = theforeman.delete_role(id=role.get('id'))
                return True, role
            except ForemanError as e:
                module.fail_json(msg='Could not delete role: {0}'.format(e.message))

    return False, role


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            foreman_host=dict(type='str', default='127.0.0.1'),
            foreman_port=dict(type='str', default='443'),
            foreman_user=dict(type='str', required=True),
            foreman_pass=dict(type='str', required=True, no_log=True),
            foreman_ssl=dict(type='bool', default=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    changed, role = ensure(module)
    module.exit_json(changed=changed, role=role)


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
