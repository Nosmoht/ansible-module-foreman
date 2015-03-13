#!/usr/bin/env python
# -*- coding: utf-8 -*-

from foreman import Foreman
from foreman.foreman import ForemanError

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
        profile = theforeman.get_compute_profile(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get compute profile: ' + e.message)

    if not profile and state == 'present':
        try:
            theforeman.create_compute_profile(data=data)
            changed = True
        except ForemanError as e:
            module.fail_json(msg='Could not create compute profile: ' + e.message)

    if profile and state == 'absent':
        try:
            theforeman.delete_compute_profile(data=profile)
            changed = True
        except ForemanError as e:
            module.fail_json(msg='Could not delete compute profile: ' + e.message)
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
