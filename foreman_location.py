#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to manage Foreman location resources.
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
module: foreman_location
short_description:
- Manage Foreman Location using Foreman API v2. This module requires Katello to be installed in addition to Foreman.
description:
- Create, opdate and and delete Foreman Locations using Foreman API v2
options:
  name:
    description: Location name
    required: True
  state:
    description: Location state
    required: False
    default: present
    choices: ["present", "absent"]
  users:
    description: List of usernames assigned to the location
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
- name: Ensure New York Datacenter
  foreman_location:
    name: MY-DC
    state: present
    users:
    - pinky
    - brain
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
    users = module.params['users']

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
        location = theforeman.search_location(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get location: {0}'.format(e.message))

    if users:
        data['user_ids'] = get_user_ids(module, theforeman, users)

    if not location and state == 'present':
        try:
            theforeman.create_location(data=data)
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not create location: {0}'.format(e.message))

    if location:
        if state == 'absent':
            try:
                theforeman.delete_location(id=location.get('id'))
                return True
            except ForemanError as e:
                module.fail_json('Could not delete location: {0}'.format(e.message))

    return False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            users=dict(type='list', required=False),
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
