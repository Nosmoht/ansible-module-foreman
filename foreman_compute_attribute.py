#!/usr/bin/env python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: foreman_compute_attribute
short_description: Manage Foreman Compute Attributes using Foreman API v2
description:
- Create and update Foreman Compute Attributes using Foreman API v2
options:
  compute_resource:
    description: Name of compute resource
    required: true
    default: null
  compute_profile:
    description: Name of compute profile 
    required: true
    default: null
  vm_attributes:
    description: Hash containing the data of vm_attrs
    required: true
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

try:
    from foreman import Foreman
    from foreman.foreman import ForemanError
    foremanclient_found = True
except ImportError:
    foremanclient_found = False

def ensure(module):
    compute_profile_name = module.params['compute_profile']
    compute_resource_name = module.params['compute_resource']
    vm_attributes = module.params['vm_attributes']

    foreman_host = module.params['foreman_host']
    foreman_port = module.params['foreman_port']
    foreman_user = module.params['foreman_user']
    foreman_pass = module.params['foreman_pass']
    
    theforeman = Foreman(hostname=foreman_host,
                         port=foreman_port,
                         username=foreman_user,
                         password=foreman_pass)

    try:
        compute_resource = theforeman.search_compute_resource(data={'name': compute_resource_name})
        if not compute_resource:
            module.fail_json(msg='Compute resource not found: ' + compute_resource_name)
    except ForemanError as e:
        module.fail_json(msg='Could not get compute resource: ' + e.message)

    try:
        compute_profile = theforeman.search_compute_profile(data={'name': compute_profile_name})
        if not compute_profile:
            module.fail_json(msg='Compute profile not found: ' + compute_profile_name)
    except ForemanError as e:
        module.fail_json(msg='Could not get compute profile: ' + e.message)

    compute_attributes = filter(lambda item: item['compute_profile_name'] == compute_profile_name, 
                                compute_resource.get('compute_attributes'))
    
    if compute_attributes:
        compute_attribute = compute_attributes[0]
    else:
        compute_attribute = None

    if not compute_attribute:
        data = {}
        data['compute_resource_id'] = compute_resource.get('id')
        data['compute_profile_id'] = compute_profile.get('id')
        data['vm_attrs'] = vm_attributes
        try:
            compute_attribute = theforeman.create_compute_attribute(data=data)
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not create compute attribute: ' + e.message)

    if cmp(compute_attribute.get('vm_attrs'), vm_attributes) != 0:
        try:
            compute_attribute['vm_attrs'] = vm_attributes
            theforeman.update_compute_attribute(id=compute_attribute.get('id'), data=compute_attribute)
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not update compute attribute: ' + e.message)

    return False

def main():
    module = AnsibleModule(
        argument_spec=dict(
            compute_profile=dict(Type='str', required=True),
            compute_resource=dict(Type='str', required=True),
            vm_attributes=dict(Type='dict', required=False),
            foreman_host=dict(Type='str', Default='127.0.0.1'),
            foreman_port=dict(Type='str', Default='443'),
            foreman_user=dict(Type='str', required=True),
            foreman_pass=dict(Type='str', required=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman is required')

    changed = ensure(module)
    module.exit_json(changed=changed, 
                     name="%s - %s" % (module.params['compute_resource'], module.params['compute_profile']))

# import module snippets
from ansible.module_utils.basic import *
main()
