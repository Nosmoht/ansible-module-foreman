#!/usr/bin/env python
# -*- coding: utf-8 -*-

from foreman import Foreman

def ensure(module):
    name = module.params['name']
    network = module.params['network']
    mask = module.params['mask']
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
    subnet = theforeman.get_subnet(data=data)
    if not subnet and state == 'present':
        data['network'] = network
        data['mask'] = mask
        theforeman.create_subnet(data=data)
        return True
    if subnet and state == 'absent':
        theforeman.delete_subnet(data=subnet)
        return True
    return False

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(Type='str', required=True),
            network=dict(Type='str', required=True),
            mask=dict(Type='str', required=True),
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
