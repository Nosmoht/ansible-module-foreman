#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to manage Foreman global parameters.
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
module: foreman_global_parameter
short_description: Manage Foreman global parameter using Foreman API v2
description:
- Update Foreman global parameter using Foreman API v2
options:
  name:
    description: Global parameter name
    required: true
  value:
    description: parameter value
    required: true
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
author: "Radim Janca <janca@cesnet.cz>"
'''

EXAMPLES = '''
- name: Ensure Global parameter
  foreman_global_parameter:
    name: baud
    value: 115200
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
    global theforeman

    name = module.params['name']
    value = module.params['value']
    state = module.params['state']
    global_parameter = None

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
        global_parameter = theforeman.search_common_parameter(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get global parameter: {0}'.format(e.message))

    data['value'] = value

    if state == 'present':
        if not global_parameter:
            try:
                global_parameter = theforeman.create_common_parameter(data=data)
                return True, global_parameter
            except ForemanError as e:
                module.fail_json(msg='Could not create global parameter: {0}'.format(e.message))
        else:
            if data['value'] != global_parameter['value']:
                try:
                    global_parameter = theforeman.update_resource(resource_type='common_parameters',
                                                                  resource_id=global_parameter.get('id'),
                                                                  data=data)
                    return True, global_parameter
                except ForemanError as e:
                    module.fail_json(msg='Could not update global parameter: {0}'.format(e.message))

    if state == 'absent':
        if global_parameter:
            try:
                global_parameter = theforeman.delete_common_parameter(id=global_parameter.get('id'))
                return True, global_parameter
            except ForemanError as e:
                module.fail_json(msg='Could not remove global parameter: {0}'.format(e.message))

    return False, global_parameter

def main():
    global module

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            value=dict(type='str', required=True),
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

    changed, global_parameter = ensure(module)
    module.exit_json(changed=changed, global_parameter=global_parameter)

# import module snippets
from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
