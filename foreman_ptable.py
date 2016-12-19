#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to manage Foreman partition table resources.
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
module: foreman_ptable
short_description: Manage Foreman Partition Tables using Foreman API v2
description:
- Create, update and delete Foreman Partition Tables using Foreman API v2
options:
  name:
    description:
    - Partition Table name
    required: true
  layout:
    description:
    - Partition Table layout
    required: false
  os_family:
    description:
    - OS family
    required: false
  state:
    description:
    - Partition Table state
    required: false
    default: 'present'
    choices: ['present', 'absent']
  foreman_host:
    description:
    - Hostname or IP address of Foreman system
    required: false
    default: 127.0.0.1
  foreman_port:
    description:
    - Port of Foreman API
    required: false
    default: 443
  foreman_user:
    description:
    - Username to be used to authenticate on Foreman
    required: true
  foreman_pass:
    description:
    - Password to be used to authenticate user on Foreman
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
- name: Ensure Partition Table
  foreman_ptable:
    name: FreeBSD
    layout: 'some layout'
    state: present
    foreman_user: admin
    foreman_pass: secret
    foreman_host: foreman.example.com
    foreman_port: 443
'''

try:
    from foreman.foreman import *
except ImportError:
    foremanclient_found = False
else:
    foremanclient_found = True


def ensure():
    name = module.params['name']
    layout = module.params['layout']
    state = module.params['state']
    os_family = module.params['os_family']

    data = dict(name=name)

    try:
        ptable = theforeman.search_partition_table(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get partition table: {0}'.format(e.message))

    data['layout'] = layout
    data['os_family'] = os_family

    if not ptable and state == 'present':
        try:
            ptable = theforeman.create_partition_table(data)
        except ForemanError as e:
            module.fail_json(msg='Could not create partition table: {0}'.format(e.message))
        return True, ptable

    if ptable and state == 'absent':
        try:
            ptable = theforeman.delete_partition_table(id=ptable.get('id'))
        except ForemanError as e:
            module.fail_json(msg='Could not delete partition table: {0}'.format(e.message))
        return True, ptable

    if ptable and state == 'present':
        try:
            ptable = theforeman.get_partition_table(id=ptable.get('id'))
        except ForemanError as e:
            module.fail_json(msg='Could not get partition table to update: {0}'.format(e.message))
        if ptable.get('layout') == layout:
            return False, ptable
        else:
            try:
                ptable = theforeman.update_partition_table(id=ptable.get('id'), data=data)
            except ForemanError as e:
                module.fail_json(msg='Could not update partition table: {0}'.format(e.message))
            return True, ptable

    return False, ptable


def main():
    global module
    global theforeman

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            layout=dict(type='str', required=False),
            os_family=dict(type='str', required=False),
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

    changed, ptable = ensure()
    module.exit_json(changed=changed, ptable=ptable)


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
