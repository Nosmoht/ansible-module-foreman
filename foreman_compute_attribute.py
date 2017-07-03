#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to manage Foreman compute attribute resources.
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
module: foreman_compute_attribute
short_description: Manage Foreman Compute Attributes using Foreman API v2
description:
- Create and update Foreman Compute Attributes using Foreman API v2
options:
  compute_resource:
    description: Name of compute resource
    required: true
  compute_profile:
    description: Name of compute profile
    required: true
  vm_attributes:
    description: Hash containing the data of vm_attrs
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
author: "Thomas Krahn (@nosmoht)"
'''

try:
    from foreman.foreman import *

    foremanclient_found = True
except ImportError:
    foremanclient_found = False


def ensure(module):
    compute_profile_name = module.params['compute_profile']
    compute_resource_name = module.params['compute_resource']
    vm_attributes = module.params['vm_attributes']

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

    try:
        compute_resource = theforeman.search_compute_resource(data={'name': compute_resource_name})
        if not compute_resource:
            module.fail_json(msg='Compute resource not found: {0}'.format(compute_resource_name))
    except ForemanError as e:
        module.fail_json(msg='Could not get compute resource: {0}'.format(compute_resource_name))

    try:
        compute_profile = theforeman.search_compute_profile(data={'name': compute_profile_name})
        if not compute_profile:
            module.fail_json(msg='Compute profile {0} not found on {1}'.format(compute_profile_name,
                                                                               compute_resource_name))
    except ForemanError as e:
        module.fail_json(msg='Could not get compute profile {0} on {1}'.format(compute_profile_name,
                                                                               compute_resource_name))

    compute_attributes = theforeman.get_compute_attribute(compute_resource_id=compute_resource.get('id'),
                                                          compute_profile_id=compute_profile.get('id'))

    if compute_attributes:
        compute_attribute = compute_attributes[0]
    else:
        compute_attribute = None

    if not compute_attribute:
        try:
            compute_attribute = theforeman.create_compute_attribute(compute_resource_id=compute_resource.get('id'),
                                                                    compute_profile_id=compute_profile.get('id'),
                                                                    data={'vm_attrs': vm_attributes})
            return True, compute_attribute
        except ForemanError as e:
            module.fail_json(msg='Could not create compute attribute: {0}'.format(e.message))

    if not all(compute_attribute['vm_attrs'].get(key, vm_attributes.get(key)) == vm_attributes.get(key) for key in
               vm_attributes) != 0:
        try:
            compute_attribute = theforeman.update_compute_attribute(id=compute_attribute.get('id'),
                                                                    data=vm_attributes)
            return True, compute_attribute
        except ForemanError as e:
            module.fail_json(msg='Could not update compute attribute: {0}'.format(e.message))

    return False, compute_attribute


def main():
    module = AnsibleModule(
        argument_spec=dict(
            compute_profile=dict(type='str', required=True),
            compute_resource=dict(type='str', required=True),
            vm_attributes=dict(type='dict', required=False),
            foreman_host=dict(type='str', Default='127.0.0.1'),
            foreman_port=dict(type='str', Default='443'),
            foreman_user=dict(type='str', required=True),
            foreman_pass=dict(type='str', required=True, no_log=True),
            foreman_ssl=dict(type='bool', required=False, default=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman is required. See https://github.com/Nosmoht/python-foreman.')

    changed, compute_attribute = ensure(module)
    module.exit_json(changed=changed, compute_attribute=compute_attribute)


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
