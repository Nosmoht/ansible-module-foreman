#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to manage Foreman subnet resources.
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
module: foreman_architecture
short_description: Manage Foreman Architectures using Foreman API v2
description:
- Create and delete Foreman Architectures using Foreman API v2
options:
  name:
    description: Subnet name
    required: True
  network:
    description: Subnet network
    required: False
    default: None
  mask:
    description: Netmask for this subnet
    required: False
    default: None
  gateway:
    description: Gateway for this subnet
    required: False
    default: None
  dns_primary:
    description: Primary DNS for this subnet
    required: False
    default: None
  dns_secondary:
    description: Secondary DNS for this subnet
    required: False
    default: None
  ipam:
    description: Enable IP Address auto suggestion for this subnet
    required: False
    default: None
    choices: ['DHCP', 'Internal DB', 'None']),
  ip_from:
    description: Starting IP Address for IP auto suggestion
    required: False
    default: None
  ip_to:
    description: Ending IP Address for IP auto suggestion
    required: False
    default: None
  state:
    description: State of subnet
    required: false
    default: present
    choices: ["present", "absent"]
  vlanid:
    description: VLAN ID for this subnet
    required: False
    default: None
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
author: Thomas Krahn <ntbc@gmx.net>
'''

EXAMPLES = '''
- name: Ensure Subnet
  foreman_subnet:
    name: MySubnet
    network: 192.168.123.0
    mask: 255.255.255.0
    dns_primary: 192.168.123.1
    dns_secondary: 192.168.123.2
    ipam: DHCP
    ip_from: 192.168.123.3
    ip_to: 192.168.123.253
    gateway: 192.168.123.254
    vlanid: 123
    state: present
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


def ensure(module):
    name = module.params['name']
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
        subnet = theforeman.search_subnet(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get subnet: {0}'.format(e.message))

    for key in ['dns_primary', 'dns_secondary', 'gateway', 'ipam', 'mask', 'network', 'network_address', 'vlanid']:
        if key in module.params:
            data[key] = module.params[key]
    if 'ip_from' in module.params:
        data['from'] = module.params['ip_from']
    if 'ip_to' in module.params:
        data['to'] = module.params['ip_to']

    if not subnet and state == 'present':
        try:
            subnet = theforeman.create_subnet(data=data)
            return True, subnet
        except ForemanError as e:
            module.fail_json(msg='Could not create subnet: {0}'.format(e.message))

    if subnet:
        if state == 'absent':
            try:
                subnet = theforeman.delete_subnet(id=subnet.get('id'))
                return True, subnet
            except ForemanError as e:
                module.fail_json(msg='Could not delete subnet: {0}'.format(e.message))

        if not all(data[key] == subnet[key] for key in data):
            try:
                subnet = theforeman.update_subnet(id=subnet.get('id'), data=data)
                return True, subnet
            except ForemanError as e:
                module.fail_json(msg='Could not update subnet: {0}'.format(e.message))

    return False, subnet


def main():
    module = AnsibleModule(
        argument_spec=dict(
            dns_primary=dict(type='str', required=False),
            dns_secondary=dict(type='str', required=False),
            gateway=dict(type='str', required=False),
            name=dict(type='str', required=True),
            network=dict(type='str', required=False),
            mask=dict(type='str', required=False),
            ipam=dict(type='str', required=False, choices=['DHCP', 'Internal DB', 'None']),
            ip_from=dict(type='str', required=False),
            ip_to=dict(type='str', required=False),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            vlanid=dict(type='str', default=None),
            foreman_host=dict(type='str', default='127.0.0.1'),
            foreman_port=dict(type='str', default='443'),
            foreman_user=dict(type='str', required=True),
            foreman_pass=dict(type='str', required=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    changed, subnet = ensure(module)
    module.exit_json(changed=changed, subnet=subnet)

# import module snippets
from ansible.module_utils.basic import *

main()
