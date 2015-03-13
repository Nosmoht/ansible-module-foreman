#!/usr/bin/env python
# -*- coding: utf-8 -*-

from foreman import Foreman
from foreman.foreman import ForemanError

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
        env = theforeman.get_environment(data=data)
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
            theforeman.delete_environment(data=env)
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

    changed = ensure(module)
    module.exit_json(changed=changed, name=module.params['name'])

# import module snippets
from ansible.module_utils.basic import *
main()
