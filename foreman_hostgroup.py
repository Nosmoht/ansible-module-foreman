#!/usr/bin/env python
# -*- coding: utf-8 -*-

from foreman import Foreman

def ensure(module):
    changed = False
    # Set parameters
    name = module.params['name']
    architecture = module.params['architecture']
    domain = module.params['domain']
    environment = module.params['environment']
    medium = module.params['medium']
    operatingsystem = module.params['operatingsystem']
    partition_table = module.params['partition_table']
    smart_proxy = module.params['smart_proxy']
    subnet = module.params['subnet']
    state = module.params['state']
    foreman_host = module.params['foreman_host']
    foreman_port = module.params['foreman_port']
    foreman_user = module.params['foreman_user']
    foreman_pass = module.params['foreman_pass']
    theforeman = Foreman(hostname=foreman_host, port=foreman_port, username=foreman_user, password=foreman_pass)
    hostgroup = theforeman.get_hostgroup_by_name(name=name)
    if not hostgroup and state == 'present':
        theforeman.create_hostgroup(name=name,
                                    architecture=architecture,
                                    domain=domain,
                                    environment=environment,
                                    medium=medium,
                                    operatingsystem=operatingsystem,
                                    partition_table=partition_table,
                                    smart_proxy=smart_proxy,
                                    subnet=subnet)
        changed = True
    if hostgroup and state == 'absent':
        theforeman.delete_hostgroup(name=name)
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
