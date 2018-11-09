#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to get status form Foreman host resources.
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
module: foreman_host
short_description: Get Foreman host info using Foreman API v2
description:
- Get Foreman host info using Foreman API v2
options:
  name:
    description: Hostgroup name
    required: true
    default: None
  domain:
    description: Domain name
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
except ImportError:
    foremanclient_found = False
else:
    foremanclient_found = True

try:
    from ansible.module_utils.foreman_utils import *

    has_import_error = False
except ImportError as e:
    has_import_error = True
    import_error_msg = str(e)


def ensure():
    name = module.params['name']
    domain_name = module.params['domain']

    theforeman = init_foreman_client(module)

    if domain_name:
        if domain_name in name:
            host_name = name
        else:
            host_name = '{name}.{domain}'.format(name=name, domain=domain_name)
    else:
        host_name = name

    data = dict(name=host_name)

    try:
        host = theforeman.search_host(data=data)
        if host:
            host = theforeman.get_host(id=host.get('id'))
            return False, host
    except ForemanError as e:
        module.fail_json(msg='Error while searching host: {0}'.format(e.message))

    module.fail_json(msg="Host '{host}' does not exist.'".format(host=host_name))


def main():
    global module
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            domain=dict(type='str', default=None),
            foreman_host=dict(type='str', default='127.0.0.1'),
            foreman_port=dict(type='str', default='443'),
            foreman_user=dict(type='str', required=True),
            foreman_pass=dict(type='str', required=True, no_log=True),
            foreman_ssl=dict(type='bool', default=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(
            msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    changed, host = ensure()
    module.exit_json(changed=changed, host=host)


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
