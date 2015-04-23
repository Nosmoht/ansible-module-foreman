#!/usr/bin/env python
# -*- coding: utf-8 -*-

import operator

DOCUMENTATION = '''
---
module: foreman_user
short_description: Manage Foreman Users using Foreman API v2
description:
- Manage Foreman Architectures using Foreman API v2
options:
  admin:
    description: Is an admin account
    required: False
    default: 'false'
    choices: ['true','false']
  auth:
    description: Authorization method
    required: False
    default: 'Internal'
  login:
    description: Name of architecture
    required: True
    default: null
    aliases: ['name']
  firstname:
    description: User's firstname
    required: False
    default: null
  lastname:
    description: User's lastname
    required: False
    default: null
  mail:
    description: Mail address
    required: False
    default: null
  password:
    description: Password
    required: False
    default: null
  state:
    description: State of architecture
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
    default: null
  foreman_pass:
    description: Password to be used to authenticate user on Foreman
    required: true
    default: null
notes:
- Requires the python-foreman package to be installed. See https://github.com/Nosmoht/python-foreman.
author: Thomas Krahn
'''

EXAMPLES = '''
- name: Ensure ARM Architecture is present
  foreman_architecture:
    name: ARM
    state: present
    foreman_user: admin
    foreman_pass: secret
'''

try:
    from foreman.foreman import *

    foremanclient_found = True
except ImportError:
    foremanclient_found = False


def ensure(module):
    login = module.params['login']
    state = module.params['state']

    foreman_host = module.params['foreman_host']
    foreman_port = module.params['foreman_port']
    foreman_user = module.params['foreman_user']
    foreman_pass = module.params['foreman_pass']

    theforeman = Foreman(hostname=foreman_host,
                         port=foreman_port,
                         username=foreman_user,
                         password=foreman_pass)

    data = {'login': login}

    try:
        user = theforeman.search_user(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get user: {0}'.format(e.message))

    for key in ['admin', 'auth_source_name', 'firstname', 'lastname', 'mail', 'password']:
        if key in module.params:
            data[key] = module.params[key]

    if not user and state == 'present':
        try:
            user = theforeman.create_user(data=data)
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not create user: {0}'.format(e.message))

    if user:
        if state == 'absent':
            try:
                theforeman.delete_user(id=user.get('id'))
                return True
            except ForemanError as e:
                module.fail_json(msg='Could not delete user: {0}'.format(e.message))

        if not all(user.get(key, data[key]) == data[key] for key in data):
            try:
                theforeman.update_user(id=user.get('id'), data=data)
                return True
            except ForemanError as e:
                module.fail_json(msg='Could not update user: {0}'.format(e.message))

    return False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            admin=dict(type='bool', default=False, choices=BOOLEANS),
            auth_source_name=dict(type='str', default='Internal', aliases=['auth']),
            login=dict(type='str', required=True, aliases=['name']),
            firstname=dict(type='str', required=False),
            lastname=dict(type='str', required=False),
            mail=dict(type='str', required=False),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            password=dict(type='str', required=False),
            foreman_host=dict(type='str', default='127.0.0.1'),
            foreman_port=dict(type='str', default='443'),
            foreman_user=dict(type='str', required=True),
            foreman_pass=dict(type='str', required=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    changed = ensure(module)
    module.exit_json(changed=changed, name=module.params['name'])

# import module snippets
from ansible.module_utils.basic import *

main()
