#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to manage Foreman external_usergroup resources.
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
module: foreman_external_usergroup
short_description: Manage Foreman External Usergroup using Foreman API v2
description:
- Create and delete Foreman External Usergroups using Foreman API v2
options:
  name:
    description: name of the external usergroup
    required: true
  auth_source:
    description: auth source of this usergroup
    required: true
  usergroup:
    description: usergroup to link to.
    required: true
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
author: "Guido Gúnther (@agx)"
'''

EXAMPLES = '''
- name: Ensure LDAP group wheel is linked to foreman usergroup admin
  foreman_external_usergroup:
    name: wheel
    auth_source: LDAP-Server
    usergroup: admin
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


def get_id(module, theforeman, res_type, name, field='name'):
    result = None
    try:
        searcher = getattr(theforeman, "search_{0}".format(res_type))
    except AttributeError:
        module.fail_json(msg="Don't know how to search for {0}".format(res_type))

    try:
        res = searcher(data={field: name})
        if not res:
            module.fail_json(msg="Could not find '{0}' of type {1}".format(name, res_type))
        result = res.get('id')
    except ForemanError as e:
        module.fail_json(msg="Could not get '{0}' of type {1}: {2}".format(name,
                                                                           res_type,
                                                                           e.message))
    return result


def ensure(module):
    name = module.params['name']
    state = module.params['state']
    auth_source = module.params['auth_source']
    usergroup = module.params['usergroup']
    ext_group = None

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
        group = theforeman.search_usergroup({'name': usergroup})
    except ForemanError as e:
        module.fail_json(msg='Could not get group usergroup: {0}'.format(e.message))

    data = dict(name=name)
    try:
        ext_groups = theforeman.get_external_usergroups(group['id'])
    except ForemanError as e:
        module.fail_json(msg='Could not get external usergroups for {0}: {1}'.format(name, e.message))

    for e in ext_groups:
        if e['name'] == name:
            ext_group = e
            break

    if not ext_group and state == 'present':
        data['usergroup_id'] = group['id']
        data['auth_source_id'] = get_id(module, theforeman, 'auth_source_ldap', auth_source)

        try:
            ext_group = theforeman.create_external_usergroup(group['id'], data=data)
            return True, ext_group
        except ForemanError as e:
            module.fail_json(msg='Could not create external usergroup: {0}'.format(e.message))

    if ext_group and state == 'absent':
        try:
            ext_group = theforeman.delete_external_usergroup(group_id=group['id'], ext_group_id=ext_group['id'])
        except ForemanError as e:
            module.fail_json(msg='Could not delete external usergroup: {0}'.format(e.message))
        return True, ext_group

    return False, ext_group


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=['present', 'absent']),
            name=dict(type='str', required=True),
            usergroup=dict(type='str', required=True),
            auth_source=dict(type='str', required=True),
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
