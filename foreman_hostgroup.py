#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from foreman import Foreman
    from foreman.foreman import ForemanError
    from foreman.constants import *
except ImportError:
    foremanclient_found = False
else:
    foremanclient_found = True

def get_resource(module, resource_type, resource_func, resource_name):
    try:
        result = resource_func(data={'name': resource_name})
        if not result:
            module.fail_json(msg="%s %s not found" % (resource_type, resource_name))
    except ForemanError as e:
        module.fail_json(msg="Error while getting %s: %s" % (resource_type, e.message))
    return result

def ensure(module):
    changed = False
    # Set parameters
    name = module.params['name']
    architecture_name = module.params[ARCHITECTURE]
    domain_name = module.params[DOMAIN]
    environment_name = module.params[ENVIRONMENT]
    medium_name = module.params[MEDIUM]
    operatingsystem_name = module.params[OPERATINGSYSTEM]
    partition_table_name = module.params['partition_table']
    smart_proxy_name = module.params[SMART_PROXY]
    subnet_name = module.params[SUBNET]
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
        hostgroup = theforeman.search_hostgroup(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get hostgroup: ' + e.message)

    if not hostgroup and state == 'present':
        # Architecture
        if architecture_name:
            architecture = get_resource(module=module,
                                        resource_type=ARCHITECTURE,
                                        resource_func=theforeman.search_architecture,
                                        resource_name=architecture_name)
        data['architecture_id'] = architecture.get('id')

        # Domain
        if domain_name:
            domain = get_resource(module=module,
                                  resource_type=DOMAIN,
                                  resource_func=theforeman.search_domain,
                                  resource_name=domain_name)
            data['domain_id'] = domain.get('id')

        # Environment
        if environment_name:
            environment = get_resource(module=module,
                                       resource_type=ENVIRONMENT,
                                       resource_func=theforeman.search_environment,
                                       resource_name=environment_name)
            data['environment_id'] = environment.get('id')

        # Medium
        if medium_name:
            medium = get_resource(module=module,
                                  resource_type=MEDIUM,
                                  resource_func=theforeman.search_medium,
                                  resource_name=medium_name)
            data['medium_id'] = medium.get('id')

        # Operatingssystem
        if operatingsystem_name:
            operatingsystem = get_resource(module=module,
                                           resource_type=OPERATINGSYSTEM,
                                           resource_func=theforeman.search_operatingsystem,
                                           resource_name=operatingsystem_name)
            data['operatingsystem_id'] = operatingsystem.get('id')

        # Partition Table
        if partition_table_name:
            partition_table = get_resource(module=module,
                                           resource_type=PARTITION_TABLE,
                                           resource_func=theforeman.search_partition_table,
                                           resource_name=partition_table_name)
            data['ptable_id'] = partition_table.get('id')

        # Smart Proxy
        if smart_proxy_name:
            partition_table = get_resource(module=module,
                                           resource_type=SMART_PROXY,
                                           resource_func=theforeman.search_smart_proxy,
                                           resource_name=smart_proxy_name)
            data['puppet_proxy_id'] = smart_proxy.get('id')

        # Subnet
        if subnet_name:
            subnet = get_resource(module=module,
                                  resource_type=SUBNET,
                                  resource_func=theforeman.search_subnet,
                                  resource_name=subnet_name)
            data['subnet_id'] = subnet.get('id')

        try:
            theforeman.create_hostgroup(data=data)
            changed = True
        except ForemanError as e:
            module.fail_json(msg='Could not create hostgroup: ' + e.message)

    if hostgroup and state == 'absent':
        try:
            theforeman.delete_hostgroup(id=hostgroup.get('id'))
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not delete hostgroup: ' + e.message)

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

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required')

    changed = ensure(module)
    module.exit_json(changed=changed, name=module.params['name'])

# import module snippets
from ansible.module_utils.basic import *
main()
