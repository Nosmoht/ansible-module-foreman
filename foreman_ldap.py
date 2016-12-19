#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to manage Foreman ldap resources.
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
module: foreman_ldap
short_description:
- Manage Foreman Ldap auth sources using Foreman API v2.
description:
- Create, opdate and and delete Foreman Ldaps using Foreman API v2
options:
  name:
    description: LDAP name
    required: True
  host:
    description: LDAP host to use
    required: True
  state:
    description: Ldap state
    required: False
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
- name: A test ldap server
  foreman_ldap:
    name: Test LDAP
    host: 127.0.0.1
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


def get_user_ids(module, theforeman, users):
    result = []
    for i in range(0, len(users)):
        try:
            user = theforeman.search_user(data={'login': users[i]})
            if not user:
                module.fail_json('Could not find user {0}'.format(users[i]))
            result.append(user.get('id'))
        except ForemanError as e:
            module.fail_json('Could not get user: {0}'.format(e.message))
    return result


def ensure(module):
    name = module.params['name']
    state = module.params['state']

    foreman_host = module.params['foreman_host']
    foreman_port = module.params['foreman_port']
    foreman_user = module.params['foreman_user']
    foreman_pass = module.params['foreman_pass']
    foreman_ssl = module.params['foreman_ssl']

    cmp_keys = ['host', 'port', 'base_dn', 'attr_login', 'attr_firstname',
                'attr_lastname', 'attr_mail', 'attr_photo', 'onthefly_register',
                'usergroup_sync', 'ldap_filter']
    keys = cmp_keys + ['groups_base', 'server_type']

    theforeman = Foreman(hostname=foreman_host,
                         port=foreman_port,
                         username=foreman_user,
                         password=foreman_pass,
                         ssl=foreman_ssl)

    data = {'name': name}

    try:
        ldap = theforeman.search_auth_source_ldap(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get ldap: {0}'.format(e.message))

    for key in keys:
        if module.params[key]:
            data[key] = module.params[key]

    if not ldap and state == 'present':
        try:
            theforeman.create_auth_source_ldap(data=data)
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not create ldap: {0}'.format(e.message))

    if ldap:
        if state == 'absent':
            try:
                theforeman.delete_auth_source_ldap(id=ldap.get('id'))
                return True
            except ForemanError as e:
                module.fail_json('Could not delete ldap: {0}'.format(e.message))

        if not all(data.get(key) == ldap.get(key) for key in cmp_keys):
            try:
                ldap = theforeman.update_auth_source_ldap(id=ldap.get('id'), data=data)
                return True, ldap
            except ForemanError as e:
                module.fail_json(msg='Could not update hostgroup: {0}'.format(e.message))

    return False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            host=dict(type='str', required=True),
            port=dict(type='int', required=False, default=389),
            base_dn=dict(type='str', required=False),
            attr_login=dict(type='str', required=False),
            attr_firstname=dict(type='str', required=False),
            attr_lastname=dict(type='str', required=False),
            attr_mail=dict(type='str', required=False),
            attr_photo=dict(type='str', required=False),
            onthefly_register=dict(type='bool', required=False),
            usergroup_sync=dict(type='bool', required=False),
            groups_base=dict(type='str', required=False),
            server_type=dict(type='str', required=False, choices=['posix', 'free_ipa', 'active_directory']),
            ldap_filter=dict(type='str', required=False),
            foreman_host=dict(type='str', default='127.0.0.1'),
            foreman_port=dict(type='str', default='443'),
            foreman_user=dict(type='str', required=True),
            foreman_pass=dict(type='str', required=True, no_log=True),
            foreman_ssl=dict(type='bool', default=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    changed = ensure(module)
    module.exit_json(changed=changed, name=module.params['name'])


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
