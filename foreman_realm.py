#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to manage Foreman realm resources.
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
module: foreman_realm
short_description: Manage Foreman Realm using Foreman API v2
description:
- Create, update and delete Foreman Realms using Foreman API v2
options:
  name:
    description: Realm name
    required: true
  realm_proxy:
    description: Realm smart proxy to use
    required: true
  realm_type:
    description: Realm type (e.g FreeIPA)
    required: true
  state:
    description: Realm state
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
- name: Ensure Realm
  foreman_realm:
    name: MyRealm
    realm_proxy: http://localhost:3000
    realm_type: FreeIPA
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


def get_resources(resource_type, resource_specs):
    result = []
    for item in resource_specs:
        search_data = dict()
        if isinstance(item, dict):
            for key in item:
                search_data[key] = item[key]
        else:
            search_data['name'] = item
        try:
            resource = theforeman.search_resource(resource_type=resource_type, data=search_data)
            if not resource:
                module.fail_json(
                    msg='Could not find resource type {resource_type} defined as {spec}'.format(
                        resource_type=resource_type,
                        spec=item))
            result.append(resource)
        except ForemanError as e:
            module.fail_json(msg='Could not search resource type {resource_type} defined as {spec}: {error}'.format(
                resource_type=resource_type, spec=item, error=e.message))
    return result


def ensure(module):
    global theforeman

    name = module.params['name']
    realm_proxy = module.params['realm_proxy']
    realm_type = module.params['realm_type']
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
        realm = theforeman.search_realm(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get realm: {0}'.format(e.message))

    data['realm_type'] = realm_type
    data['realm_proxy_id'] = get_resources(resource_type='smart_proxies', resource_specs=[realm_proxy])[0].get('id')
    if not realm and state == 'present':
        try:
            realm = theforeman.create_realm(data=data)
            return True, realm
        except ForemanError as e:
            module.fail_json(msg='Could not create realm: {0}'.format(e.message))

    if realm:
        if state == 'absent':
            try:
                realm = theforeman.delete_realm(id=realm.get('id'))
                return True, realm
            except ForemanError as e:
                module.fail_json(msg='Could not delete realm: {0}'.format(e.message))

        elif not all(data[key] == realm[key] for key in data):
            try:
                realm = theforeman.update_realm(id=realm.get('id'), data=data)
                return True, realm
            except ForemanError as e:
                module.fail_json(msg='Could not update realm: {0}'.format(e.message))

    return False, realm


def main():
    global module

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            realm_proxy=dict(type='str', required=True),
            realm_type=dict(type='str', required=True),
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

    changed, realm = ensure(module)
    module.exit_json(changed=changed, realm=realm)


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
