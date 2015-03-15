#!/usr/bin/env python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: foreman_compute_resource
short_description: Manage Foreman Compute resources using Foreman API v2
description:
- Create and delete Foreman Compute Resources using Foreman API v2
options:
  name:
    description: Compute Resource name
    required: true
    default: null
    aliases: []
  datacenter: Name of Datacenter (only for Vmware)
    required: false
    default: null
  password:
    description: Password for Ovirt, EC2, Vmware, Openstack. Secret key for EC2
    required: false
    default: null
  provider:
    description: Providers name (e.g. Ovirt, EC2, Vmware, Openstack, EC2, Google)
    required: false
    default: null
  server:
    description: Hostname of Vmware vSphere system
    required: false
    default: null
  state:
    description: Compute Resource state
    required: false
    default: present
    choices: ["present", "absent"]
  tenant:
    description: Tenant name for Openstack
  url:
    description: URL for Libvirt, Ovirt, and Openstack
    required: false
    default: null
  user:
    description: Username for Ovirt, EC2, Vmware, Openstack. Access Key for EC2.
    required: false
    default: null
  foreman_host:
    description: Hostname or IP address of Foreman system
    required: false
    default: 127.0.0.1
  foreman_port:
    description: Port of Foreman API
    required: false
    default: 443
  foreman_user:
    description: Username to be used to authenticate on Foreman
    required: true
    default: null
  foreman_pass:
    description: Password to be used to authenticate user on Foreman
    required: true
    default: null
notes:
- Requires the python-foreman package to be installed.
author: Thomas Krahn
'''

EXAMPLES = '''
- name: Ensure Vmware compute resource
  foreman_compute_resource:
    name: VMware
    datacenter: dc01
    provider: VMware
    server: vsphere.example.com
    url: vsphere.example.com
    user: domain\admin
    password: secret
    state: present
    foreman_user: admin
    foreman_pass: secret
- name: Ensure Openstack compute resource
  foreman_compute_resource:
    name: Openstack
    provider: OpenStack
    tenant: ExampleTenant
    url: https://compute01.example.com:5000/v2.0/tokens
    user: admin
'''

try:
    from foreman import Foreman
    from foreman.foreman import ForemanError
except ImportError:
    foremanclient_found = False
else:
    foremanclient_found = True

def get_required_provider_params(provider):
    provider_name = provider.lower()

    if provider_name == 'ec2':
        return ['user', 'password']
    elif provider_name in ['libvirt', 'ovirt']:
        return ['url', 'user', 'password']
    elif provider_name == 'openstack':
        return ['url', 'user', 'password', 'tenant']
    elif provider_name == 'vmware':
        return [ 'datacenter', 'user', 'password', 'server']

def ensure(module):
    name = module.params['name']
    state = module.params['state']
    provider = module.params['provider']

    if provider:
        provider_params = get_required_provider_params(provider)
        for param in provider_params:
            if not module.params.has_key(param):
                module.fail_json(msg='Parameter ' + param + ' must be defined for provide ' + provider)

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
        resource = theforeman.get_compute_resource(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get compute resource: ' + e.message)

    if not resource and state == 'present':
        data['provider'] = provider
        for param in provider_params:
            data[param] = module.params[param]

        try:
            theforeman.create_compute_resource(data=data)
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not create compute resource: ' + e.message)

    if resource:
        if state == 'absent':
            try:
                theforeman.delete_compute_resource(data=resource)
                return True
            except ForemanError as e:
                module.fail_json(msg='Could not delete compute resource: ' + e.message)

    return False

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(Type='str', required=True),
            datacenter=dict(Type='str'),
            password=dict(Type='str'),
            provider=dict(Type='str'),
            server=dict(Type='str'),
            url=dict(Type='str'),
            user=dict(Type='str'),
            state=dict(Type='str', Default='present', choices=['present', 'absent']),
            tenat=dict(Type='str'),
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
