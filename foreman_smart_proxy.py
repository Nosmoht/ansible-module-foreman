#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to manage Foreman smart proxy resources.
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
module: foreman_smart_proxy
short_description: Manage Foreman smart proxy resources using Foreman API v2
description:
- Create and delete Foreman smart proxy resources using Foreman API v2
options:
  name:
    description: Smart proxy name
    required: true
  state:
    description: Smart proxy state
    required: false
    default: present
    choices: ["present", "absent"]
  url:
    description: Smart proxy URL
    required: false
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

try:
    from foreman.foreman import *

    foremanclient_found = True
except ImportError:
    foremanclient_found = False


def ensure(module):
    updateable_keys = ['url']

    name = module.params['name']
    url = module.params['url']
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
        smart_proxy = theforeman.search_smart_proxy(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get smart proxy: {0}'.format(e.message))

    data['url'] = url

    if not smart_proxy and state == 'present':
        try:
            smart_proxy = theforeman.create_smart_proxy(data=data)
            return True, smart_proxy
        except ForemanError as e:
            module.fail_json(msg='Could not create smart proxy: {0}'.format(e.message))

    if smart_proxy:
        if state == 'absent':
            try:
                smart_proxy = theforeman.delete_smart_proxy(id=smart_proxy.get('id'))
                return True, smart_proxy
            except:
                module.fail_json(msg='Could not delete smart proxy: {0}'.format(e.message))

        if not all(data[key] == smart_proxy[key] for key in updateable_keys):
            try:
                smart_proxy = theforeman.update_smart_proxy(id=smart_proxy.get('id'), data=data)
                return True, smart_proxy
            except ForemanError as e:
                module.fail_json(msg='Could not update smart proxy: {0}'.format(e.message))
    return False, smart_proxy


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            url=dict(type='str', required=False),
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

    changed, smart_proxy = ensure(module)
    module.exit_json(changed=changed, smart_proxy=smart_proxy)


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
