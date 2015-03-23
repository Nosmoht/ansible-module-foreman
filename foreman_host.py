#!/usr/bin/env python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: foreman_host
short_description: Create and delete hosts with Foreman using Foreman API v2
description:
- Create and delete hosts using Foreman API v2
options:
  enabled:
    description: Host enabled
    required: false
    choices: BOOLEANS
  managed:
    description: Should Foreman manage the host
    required: false
    default: null
  subnet:
    description: Name of subnet to use for this host
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
- Requires the python-foreman package to be installed. See https://github.com/Nosmoht/python-foreman.
author: Thomas Krahn
'''

try:
    from foreman.foreman import *
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
    name = module.params['name']
    architecture_name = module.params[ARCHITECTURE]
    build = module.params['build']
    compute_profile_name = module.params[COMPUTE_PROFILE]
    compute_resource_name = module.params[COMPUTE_RESOURCE]
    domain_name = module.params[DOMAIN]
    enabled = module.params['enabled']
    environment_name = module.params[ENVIRONMENT]
    hostgroup_name = module.params[HOSTGROUP]
    image_name = module.params['image']
    location_name = module.params[LOCATION]
    managed = module.params['managed']
    medium_name = module.params[MEDIUM]
    operatingsystem_name = module.params[OPERATINGSYSTEM]
    organization_name = module.params[ORGANIZATION]
    parameters = module.params['parameters']
    provision_method = module.params['provision_method']
    root_pass = module.params['root_pass']
    state = module.params['state']
    subnet_name = module.params[SUBNET]
    foreman_host = module.params['foreman_host']
    foreman_port = module.params['foreman_port']
    foreman_user = module.params['foreman_user']
    foreman_pass = module.params['foreman_pass']

    theforeman = Foreman(hostname=foreman_host,
                         port=foreman_port,
                         username=foreman_user,
                         password=foreman_pass)

    data = {}

    if domain_name in name:
        host_name = name
    else:
        host_name = name + '.' + domain_name

    try:
        host = theforeman.search_host(data={'name': host_name})
    except ForemanError as e:
        module.fail_json(msg='Could not find host %s: %s' % (host_name, e.message))

    if not host:
        if state == 'absent':
            return False

        data['name'] = host_name
        # Architecture
        if architecture_name:
            architecture = get_resource(module=module,
                                        resource_type=ARCHITECTURE,
                                        resource_func=theforeman.search_architecture,
                                        resource_name=architecture_name)
        data['architecture_id'] = architecture.get('id')

        # Build
        data['build'] = build

        # Compute Profile
        if compute_profile_name:
            compute_profile = get_resource(module=module,
                                           resource_type=COMPUTE_PROFILE,
                                           resource_func=theforeman.search_compute_profile,
                                           resource_name=compute_profile_name)
            data['compute_profile_id'] = compute_profile.get('id')

        # Compute Resource
        if compute_resource_name:
            compute_resource = get_resource(module=module,
                                           resource_type=COMPUTE_RESOURCE,
                                           resource_func=theforeman.search_compute_resource,
                                           resource_name=compute_resource_name)
            data['compute_resource_id'] = compute_resource.get('id')

            # Image
            if image_name:
                compute_resource_images = compute_resource.get('images')
                if not compute_resource_images:
                    module.fail_json(msg='Compute Resource %s has no images' % (compute_resource_name))
                images = filter(lambda x: x['name'] == image_name, compute_resource_images)
                if len(images) == 0:
                    module.fail_json(msg='Could not find image %s in compute resource %s' % (image_name, compute_resource_name))
                if len(images) > 1:
                    module.fail_json(msg='Found %i images named %s in compute resource %s' % (len(images), image_name, compute_resource_images))
                data['image_id'] = images[0].get('id')

        # Domain
        if domain_name:
            domain = get_resource(module=module,
                                  resource_type=DOMAIN,
                                  resource_func=theforeman.search_domain,
                                  resource_name=domain_name)
            data['domain_id'] = domain.get('id')

        # Enabled
        data['enabled'] = enabled

        # Environment
        if environment_name:
            environment = get_resource(module=module,
                                       resource_type=ENVIRONMENT,
                                       resource_func=theforeman.search_environment,
                                       resource_name=environment_name)
            data['environment_id'] = environment.get('id')

        # Hostgroup
        if hostgroup_name:
            hostgroup = get_resource(module=module,
                                     resource_type=HOSTGROUP,
                                     resource_func=theforeman.search_hostgroup,
                                     resource_name=hostgroup_name)
            data['hostgroup_id'] = hostgroup.get('id')

        # Location
        if location_name:
            location = get_resource(module=module,
                                    resource_type=LOCATION,
                                    resource_func=theforeman.search_location,
                                    resource_name=location_name)
            data['location_id'] = location.get('id')

        # Managed
        data['managed'] = managed

        # Medium
        if medium_name:
            medium = get_resource(module=module,
                                  resource_type=MEDIUM,
                                  resource_func=theforeman.search_medium,
                                  resource_name=medium_name)
            data['medium_id'] = medium.get('id')

        # Organization
        if organization_name:
            organization = get_resource(module=module,
                                        resource_type=ORGANIZATION,
                                        resource_func=theforeman.search_organization,
                                        resource_name=organization_name)
            data['organization_id'] = organization.get('id')

        # Operatingssystem
        if operatingsystem_name:
            operatingsystem = get_resource(module=module,
                                           resource_type=OPERATINGSYSTEM,
                                           resource_func=theforeman.search_operatingsystem,
                                           resource_name=operatingsystem_name)
            data['operatingsystem_id'] = operatingsystem.get('id')

        # Provision Method
        if provision_method:
            data['provision_method'] = provision_method

        # Root password
        if root_pass:
            data['root_pass'] = root_pass

        # Subnet
        if subnet_name:
            subnet = get_resource(module=module,
                                  resource_type=SUBNET,
                                  resource_func=theforeman.search_subnet,
                                  resource_name=subnet_name)
            data['subnet_id'] = subnet.get('id')

        try:
            host = theforeman.create_host(data=data)
        except ForemanError as e:
            module.fail_json(msg='Could not create host: ' + e.message)

        changed = True

    if state == 'absent':
        try:
            theforeman.delete_host(data=host)
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not delete host: ' + e.message)

    # Parameters
    if parameters:
        host_parameters = theforeman.get_host_parameters(host_id=host.get('id'))

        for param in parameters:
            host_params = [item for item in host_parameters if item.get('name') == param.get('name')]
            if not host_params:
                try:
                    theforeman.create_host_parameter(host_id=host.get('id'), data=param)
                except ForemanError as e:
                    module.fail_json(msg='Could not create paramater %s: %s' % (param.get('name'), e.message))
                changed = True
            elif host_params[0]['value'] != param.get('value'):
                try:
                    theforeman.update_host_parameter(host_id=host.get('id'), parameter_id=host_params[0].get('id'), data=param)
                except ForemanError as e:
                    module.fail_json(msg='Could not update parameter %s: %s' % (param.get('name'), e.message))
                changed = True

    try:
        host_power_state = theforeman.get_host_power(host_id=host.get('id')).get('power')
    except ForemanError as e:
        module.fail_json(msg='Could not get host power state: ' + e.message)

    if state == 'rebooted':
        try:
            theforeman.reboot_host(host_id=host.get('id'))
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not reboot host: ' + e.message)
    elif state == 'running' and host_power_state != 'poweredOn':
        try:
            theforeman.poweron_host(host_id=host.get('id'))
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not power on host: ' + e.message)
    elif state == 'stopped' and host_power_state != 'poweredOff':
        try:
            theforeman.poweroff_host(host_id=host.get('id'))
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not power off host: ' + e.message)

    return changed

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(Type='str', required=True),
            architecture=dict(Type='str', default='x86_64'),
            build=dict(type='bool', default=False),
            compute_profile=dict(Type='str', required=False),
            compute_resource=dict(Type='str', required=False),
            domain=dict(Type='str', required=False),
            enabled=dict(Type='str', default=False),
            environment=dict(Type='str', required=False),
            hostgroup=dict(Type='str', required=False),
            image=dict(Type='str', required=False),
            location=dict(Type='str', required=False),
            managed=dict(Type='str', default=False),
            medium=dict(Type='str', required=False),
            operatingsystem=dict(Type='str', required=False),
            organization=dict(Type='str', required=False),
            parameters=dict(Type='str', required=False),
            provision_method=dict(Type='str', required=False, choices=['build', 'image']),
            root_pass=dict(Type='str', required=False),
            state=dict(Type='str', default='present',
                                       choices=['present', 'absent', 'running', 'stopped', 'rebooted']),
            subnet=dict(Type='str', required=False),
            foreman_host=dict(Type='str', default='127.0.0.1'),
            foreman_port=dict(Type='str', default='443'),
            foreman_user=dict(Type='str', required=True),
            foreman_pass=dict(Type='str', required=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    changed = ensure(module)
    module.exit_json(changed=changed, name=module.params['name'])

# import module snippets
from ansible.module_utils.basic import *
main()
