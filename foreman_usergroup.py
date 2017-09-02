#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to manage Foreman usergroup resources.
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
module: foreman_usergroup
short_description: Manage Foreman Usergroup using Foreman API v2
description:
- Create and delete Foreman Usergroups using Foreman API v2
options:
  name:
    description: name of the usergroup
    required: true
  users:
    description: user of this usergroup. Users are identified by their
    login.
    required: false
  usergroups:
    description: usergroups of this usergroup. Usergroups can be
    nested.
    required: false
  roles:
    description: roles assigned to this usergroup
    required: false
  state:
    description: State of usergroup
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
- This module does currently not update already existing groups
version_added: "2.0"
author: "Thomas Krahn (@nosmoht)"
'''

EXAMPLES = '''
- name: Ensure a simple usergroup
  foreman_usergroup:
    name: poweradmins
    roles:
      - "Edit hostgroups"
      - Manager
    users:
      - user1
      - user2
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


def get_ids(module, theforeman, res_type, names, field='name'):
    result = []
    try:
        searcher = getattr(theforeman, "search_{0}".format(res_type))
    except AttributeError:
        module.fail_json(msg="Don't know how to search for {0}".format(res_type))

    for name in names:
        try:
            res = searcher(data={field: name})
            if not res:
                module.fail_json(msg="Could not find '{0}' of type {1}".format(name, res_type))
            result.append(res.get('id'))
        except ForemanError as e:
            module.fail_json(msg="Could not get '{0}' of type {1}: {2}".format(name,
                                                                               res_type,
                                                                               e.message))
    return result


def ensure(module):
    name = module.params['name']
    state = module.params['state']
    roles = module.params['roles']
    users = module.params['users']
    usergroups = module.params['usergroups']

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

    data = dict(name=name)

    try:
        usergroup = theforeman.search_usergroup(data)
    except ForemanError as e:
        module.fail_json(msg='Could not get usergroup: {0}'.format(e.message))

    if not usergroup and state == 'present':
        if usergroups:
            data['usergroup_ids'] = get_ids(module, theforeman, 'usergroup', usergroups)
        if roles:
            data['role_ids'] = get_ids(module, theforeman, 'role', roles)
        if users:
            data['user_ids'] = get_ids(module, theforeman, 'user', users, field='login')

        try:
            usergroup = theforeman.create_usergroup(data=data)
            return True, usergroup
        except ForemanError as e:
            module.fail_json(msg='Could not create usergroup: {0}'.format(e.message))

    if usergroup and state == 'absent':
        try:
            usergroup = theforeman.delete_usergroup(id=usergroup['id'])
        except ForemanError as e:
            module.fail_json(msg='Could not delete usergroup: {0}'.format(e.message))
        return True, usergroup

    return False, usergroup


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=['present', 'absent']),
            name=dict(type='str', required=True),
            roles=dict(type='list', required=False),
            users=dict(type='list', required=False),
            usergroups=dict(type='list', required=False),
            foreman_host=dict(type='str', default='127.0.0.1'),
            foreman_port=dict(type='str', default='443'),
            foreman_user=dict(type='str', required=True),
            foreman_pass=dict(type='str', required=True, no_log=True),
            foreman_ssl=dict(type='bool', default=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    changed, usergroup = ensure(module)
    module.exit_json(changed=changed, usergroup=usergroup)


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
