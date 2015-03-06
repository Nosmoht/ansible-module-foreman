#!/usr/bin/env python
# -*- coding: utf-8 -*-

from foreman import Foreman

def ensure(module):
    changed = False
    # Set parameters
    name = module.params['name']
    password = module.params['password']
    provider = module.params['provider']
    server = module.params['server']
    state = module.params['state']
    url = module.params['url']
    user = module.params['user']
    foreman_host = module.params['foreman_host']
    foreman_port = module.params['foreman_port']
    foreman_user = module.params['foreman_user']
    foreman_pass = module.params['foreman_pass']
    theforeman = Foreman(hostname=foreman_host, port=foreman_port, username=foreman_user, password=foreman_pass)
    resource = theforeman.get_compute_resource_by_name(name=name)
    if not resource and state == 'present':
        theforeman.create_compute_resource(name=name, user=user, password=password, provider=provider, server=server, url=url)
        changed = True
    if resource and state == 'absent':
        theforeman.delete_compute_resource(name=name)
        changed = True
    return changed

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(Type='str', required=True),
            password=dict(Type='str'),
            provider=dict(Type='str'),
            server=dict(Type='str'),
            url=dict(Type='str', required=True),
            user=dict(Type='str'),
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
