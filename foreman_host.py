#!/usr/bin/env python
# -*- coding: utf-8 -*-

from foreman import Foreman

def ensure(module):
    changed = False
    # Set parameters
    name = module.params['name']
    architecture = module.params['architecture']
    compute_profile = module.params['compute_profile']
    compute_resource = module.params['compute_resource']
    domain = module.params['domain']
    environment = module.params['environment']
    hostgroup = module.params['hostgroup']
    location = module.params['location']
    medium = module.params['medium']
    operatingsystem = module.params['operatingsystem']
    organization = module.params['organization']    
    state = module.params['state']
    foreman_host = module.params['foreman_host']
    foreman_port = module.params['foreman_port']
    foreman_user = module.params['foreman_user']
    foreman_pass = module.params['foreman_pass']
    theforeman = Foreman(hostname=foreman_host, port=foreman_port, username=foreman_user, password=foreman_pass)
    host = theforeman.get_host_by_name(name=name)
    if not host:
        host = theforeman.create_host(name=name, architecture=architecture, compute_profile=compute_profile,
                        compute_resource=compute_resource, domain=domain, environment=environment, hostgroup=hostgroup, location=location,
                        medium=medium, operatingsystem=operatingsystem, organization=organization)
        changed = True
    host_state = theforeman.get_host_power(host_id=host.get('name')).get('power')
    if state == 'running' and host_state != 'poweredOn':
        theforeman.poweron_host(host_id=host.get('name'))
        changed = True
    if state == 'stopped' and host_state != 'poweredOff':
        theforeman.poweroff_host(host_id=host.get('name'))
        changed = True
    return changed

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(Type='str', required=True),
            architecture=dict(Type='str', Default='x86_64'),
            compute_profile=dict(Type='str'),
            compute_resource=dict(Type='str'),
            domain=dict(Type='str'),
            environment=dict(Type='str'),
            hostgroup=dict(Type='str'),
            location=dict(Type='str'),
            medium=dict(Type='str'),
            operatingsystem=dict(Type='str'),
            organization=dict(Type='str'),
            state=dict(Type='str', Default='present', choices=['present', 'absent', 'running', 'stopped']),
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
