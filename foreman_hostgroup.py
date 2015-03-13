#!/usr/bin/env python
# -*- coding: utf-8 -*-

from foreman import Foreman

def ensure(module):
    changed = False
    # Set parameters
    name = module.params['name']
    architecture_name = module.params['architecture']
    domain_name = module.params['domain']
    environment_name = module.params['environment']
    medium_name = module.params['medium']
    operatingsystem_name = module.params['operatingsystem']
    partition_table_name = module.params['partition_table']
    smart_proxy_name = module.params['smart_proxy']
    subnet_name = module.params['subnet']
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
    hostgroup = theforeman.get_hostgroup(data=data)

    if not hostgroup and state == 'present':
        # Architecture
        if architecture_name:
            architecture = theforeman.get_architecture(data={'name': architecture_name})
            if not architecture:
                module.fail_json(msg='Architecture not found: ' + architecture_name)
            data['architecture_id'] = architecture.get('id')

        # Domain
        if domain_name:
            domain = theforeman.get_domain(data={'name': domain_name})
            if not domain:
                module.fail_json(msg='Domain not found: ' + domain_name)
            data['domain_id'] = domain.get('id')

        # Environment
        if environment_name:
            environment = theforeman.get_environment(data={'name': environment_name})
            if not environment:
                module.fail_json(msg='Environment not found: ' + environment_name)
            data['environment_id'] = environment.get('id')

        # Medium
        if medium_name:
            medium = theforeman.get_medium(data={'name':medium_name})
            if not medium:
                module.fail_json(msg='Medium not found: ' + medium_name)
            data['medium_id'] = medium.get('id')

        # Operatingsystem
        if operatingsystem_name:
            operatingsystem = theforeman.get_operatingsystem(data={'name': operatingsystem_name})
            if not operatingsystem:
                module.fail_json(msg='Operatingsystem not found: ' + operatingsystem_name)
            data['operatingsystem_id'] = operatingsystem.get('id')

        # Partition Table
        if partition_table_name:
            partition_table = theforeman.get_partition_table(data={'name': partition_table_name})
            if not partition_table:
                module.fail_json(msg='Partition Table not found: ' + partition_table_name)
            data['ptable_id'] = partition_table.get('id')

        # Smart Proxy
        if smart_proxy_name:
            smart_proxy = theforeman.get_smart_proxy(data={'name':smart_proxy_name})
            if not smart_proxy:
                module.fail_json(msg='Smart Proxy not found: ' + smart_proxy_name)
            data['puppet_proxy_id'] = smart_proxy.get('id')

        # Subnet
        if subnet_name:
            subnet = theforeman.get_subnet(data={'name':subnet_name})
            if not subnet:
                module.fail_json(msg='Subnet not found: ' + subnet_name)
            data['subnet_id'] = subnet.get('id')

        theforeman.create_hostgroup(data=data)
        changed = True

    if hostgroup and state == 'absent':
        theforeman.delete_hostgroup(data=hostgroup)
        changed = True
    return changed

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(Type='str', required=True),
            architecture=dict(Type='str'),
            domain=dict(Type='str'),
            environment=dict(Type='str'),
            medium=dict(Type='str'),
            operatingsystem=dict(Type='str'),
            partition_table=dict(Type='str'),
            smart_proxy=dict(Type='str'),
            subnet=dict(Type='str'),
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
