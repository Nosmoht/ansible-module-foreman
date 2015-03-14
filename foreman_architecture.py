#!/usr/bin/env python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: foreman_architecture
short_description: Manage Foreman Architectures using Foreman API v2
description:
- Create and delete Foreman Architectures using Foreman API v2
options:
  name:
    description: Name of architecture
    required: true
    default: null
    aliases: []
  state:
    description: State of architecture
    required: false
    default: present
    choices: ["present", "absent"]
notes:
- Requires the python-foreman package to be installed.
author: Thomas Krahn
'''

EXAMPLES = '''
- name: Ensure ARM Architecture is present
  foreman_architecture:
    name: ARM
    state: present
- name: Ensure i386 Architecture is absent
  foreman_architecture:
    name: i386
    state: absent
'''

def ensure(module):
    changed = False
    # Set parameters
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
        arch = theforeman.get_architecture(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get architecture: ' + e.message)

    if not arch and state == 'present':
        try:
            arch = theforeman.create_architecture(data)
            changed = True
        except ForemanError as e:
            module.fail_json(msg='Could not create architecture: ' + e.message)

    if arch and state == 'absent':
        try:
            theforeman.delete_architecture(data=arch)
            changed = True
        except ForemanError as e:
            module.fail_json(msg='Could not delete architecture: ' + e.message)
    return changed

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

    changed = ensure(module)
    module.exit_json(changed=changed, name=module.params['name'])

# import module snippets
from ansible.module_utils.basic import *
main()
