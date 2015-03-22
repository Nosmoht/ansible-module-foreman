#!/usr/bin/env python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: foreman_environment
short_description: Manage Foreman Environment using Foreman API v2
description:
- Create and delete Foreman Environments using Foreman API v2
options:
  name:
    description: Name of environment
    required: true
    default: null
    aliases: []
  state:
    description: State of environment
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
    default: null
  foreman_pass:
    description: Password to be used to authenticate user on Foreman
    required: true
    default: null
notes:
- Requires the python-foreman package to be installed.
author: Thomas Krahn
'''

EXAMPLES = '''
- name: Ensure Production environment is present
  foreman_environment:
    name: Production
    state: present
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
    data = {}
    data['name'] = name

    try:
        env = theforeman.search_environment(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get environment: ' + e.message)

    if not env and state == 'present':
        try:
            theforeman.create_environment(data=data)
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not create environment: ' + e.message)

    if env and state == 'absent':
        try:
            theforeman.delete_environment(id=env.get('id'))
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not delete environment: ' + e.message)

    return False

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(Type='str', required=True),
            state=dict(Type='str', Default='present', choices=['present', 'absent']),
            foreman_host=dict(Type='str', Default='127.0.0.1'),
            foreman_port=dict(Type='str', Default='443'),
            foreman_user=dict(Type='str', required=True),
            foreman_pass=dict(Type='str', required=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required')

    changed = ensure(module)
    module.exit_json(changed=changed, name=module.params['name'])

# import module snippets
from ansible.module_utils.basic import *
main()
