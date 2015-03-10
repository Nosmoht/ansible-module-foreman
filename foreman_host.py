#!/usr/bin/env python
# -*- coding: utf-8 -*-

from foreman import Foreman

def ensure(module):
    changed = False
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
    theforeman = Foreman(hostname=foreman_host,
                         port=foreman_port,
                         username=foreman_user,
                         password=foreman_pass)
    data = {}
    data['name'] = name
    host = theforeman.get_host(data=data)

    if not host:
        if state == 'absent':
            return False
        data['architecture_id'] = theforeman.get_architecture(data={'name': architecture}).get('id')
        data['compute_profile_id'] = theforeman.get_compute_profile(data={'name': compute_profile}).get('id')
        data['compute_resource_id'] = theforeman.get_compute_resource(data={'name': compute_resource}).get('id')
        data['domain_id'] = theforeman.get_domain(data={'name': domain}).get('id')
        data['environment_id'] = theforeman.get_environment(data={'name': environment}).get('id')
        data['hostgroup_id'] = theforeman.get_hostgroup(data={'name': hostgroup}).get('id')
        data['location_id'] = theforeman.get_location(data={'name': location}).get('id')
        data['medium_id'] = theforeman.get_medium(data={'name' :medium}).get('id')
        data['organization_id'] = theforeman.get_organization(data={'name': organization}).get('id')
        data['operatingsystem_id'] = theforeman.get_operatingsystem(data={'name': operatingsystem}).get('id')

        host = theforeman.create_host(data=data)
        changed = True

    if state == 'absent':
        theforeman.delete_host(data=host)
        return True

    host_power_state = theforeman.get_host_power(host_id=host.get('name')).get('power')
    if state == 'rebooted':
        theforeman.reboot_host(host_id=host.get('name'))
        return True
    elif state == 'running' and host_power_state != 'poweredOn':
        theforeman.poweron_host(host_id=host.get('name'))
        return True
    elif state == 'stopped' and host_power_state != 'poweredOff':
        theforeman.poweroff_host(host_id=host.get('name'))
        return True
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
            state=dict(Type='str', Default='present', choices=['present', 'absent', 'running', 'stopped', 'rebooted']),
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
