#!/usr/bin/env python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: foreman_host
short_description: Create, update and delete hosts with Foreman using Foreman API v2
description:
- Create and delete hosts using Foreman API v2
options:
  name:
    description: Hostgroup name
    required: false
    default: None
  architecture:
    description: Architecture name
    required: false
    default: x86_64
  build:
    description: Boolean to define if host should be builded
    required: false
    default: false
  compute_profile:
    description: Compute Profile name
    required: false
    default: None
  compute_resource:
    description: Compute Resource name
    required: false
    default: None
  domain:
    description: Domain name
    required: false
    default: None
  enabled:
    description: Host enabled
    required: false
    choices: BOOLEANS
  environment:
    description: Name of environment used by default
    required: false
    default: None
  hostgroup:
    description: Hostgroup name
    required: false
    default: None
  image:
    description: Image name to be used if creating from image
    required: false
    default: None
  location:
    description: Location name (Only useful with Katello)
    required: false
    default: None
  managed:
    description: Should Foreman manage the host
    required: false
    default: false
  medium:
    description: Medium name
    required: false
    default: None
  operatingsystem:
    descrtiption: Operatingsystem name
    required: false
    default: None
  organization:
    description: Organization name (only useful with Katello)
    required: false
    default: None
  parameters:
    description: List of parameters and values
    required: false
    default: None
  provision_method:
    description: How to provision the host
    required: false
    default: None
    choices: ['build', 'image']
  root_pass:
    description: root password
    required: false
    default: None
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


def get_resource(resource_type, resource_func, resource_name):
    try:
        result = resource_func(data=dict(name=resource_name))
        if not result:
            module.fail_json(msg='{resource_type} {resource_name} not found'.format(resource_type=resource_type,
                                                                                    resource_name=resource_name))
    except ForemanError as e:
        module.fail_json(
            msg='Error while getting {resource_type}: {error}'.format(resource_type=resource_type, error=e.message))
    return result


def ensure():
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

    if domain_name in name:
        host_name = name
    else:
        host_name = '{name}.{domain}'.format(name=name, domain=domain_name)

    data = dict(name=host_name)

    try:
        host = theforeman.search_host(data=data)
    except ForemanError as e:
        module.fail_json(msg='Error while searching host: {0}'.format(e.message))

    if state == 'absent':
        if host:
            try:
                host = theforeman.delete_host(id=host.get('id'))
                return True, host
            except ForemanError as e:
                module.fail_json(msg='Could not delete host: {0}'.format(e.message))
        return False, host

    if not host:

        # Architecture
        if architecture_name:
            architecture = get_resource(resource_type=ARCHITECTURE,
                                        resource_func=theforeman.search_architecture,
                                        resource_name=architecture_name)
            data['architecture_id'] = architecture.get('id')

        # Build
        data['build'] = build

        # Compute Profile
        if compute_profile_name:
            compute_profile = get_resource(resource_type=COMPUTE_PROFILE,
                                           resource_func=theforeman.search_compute_profile,
                                           resource_name=compute_profile_name)
            data['compute_profile_id'] = compute_profile.get('id')

        # Compute Resource
        if compute_resource_name:
            compute_resource = get_resource(resource_type=COMPUTE_RESOURCE,
                                            resource_func=theforeman.search_compute_resource,
                                            resource_name=compute_resource_name)
            data['compute_resource_id'] = compute_resource.get('id')

            # Image
            if image_name:
                compute_resource_images = compute_resource.get('images')
                if not compute_resource_images:
                    module.fail_json(msg='Compute Resource {0} has no images'.format(compute_resource_name))
                images = filter(lambda x: x['name'] == image_name, compute_resource_images)
                if len(images) == 0:
                    module.fail_json(
                        msg='Could not find image {image_name} in compute resource {compute_resource}'.format(
                            image_name=image_name, compute_resource=compute_resource_name))
                if len(images) > 1:
                    module.fail_json(
                        msg='Found {count} images named {image_name} in compute resource {compute_resource}'.format(
                            count=len(images), image_name=image_name, compute_resource=compute_resource_images))
                image = images[0]
                data['image_id'] = image.get('id')

        # Domain
        if domain_name:
            domain = get_resource(resource_type=DOMAIN,
                                  resource_func=theforeman.search_domain,
                                  resource_name=domain_name)
            data['domain_id'] = domain.get('id')

        # Enabled
        data['enabled'] = enabled

        # Environment
        if environment_name:
            environment = get_resource(resource_type=ENVIRONMENT,
                                       resource_func=theforeman.search_environment,
                                       resource_name=environment_name)
            data['environment_id'] = environment.get('id')

        # Hostgroup
        if hostgroup_name:
            hostgroup = get_resource(resource_type=HOSTGROUP,
                                     resource_func=theforeman.search_hostgroup,
                                     resource_name=hostgroup_name)
            data['hostgroup_id'] = hostgroup.get('id')

        # Location
        if location_name:
            location = get_resource(resource_type=LOCATION,
                                    resource_func=theforeman.search_location,
                                    resource_name=location_name)
            data['location_id'] = location.get('id')

        # Managed
        data['managed'] = managed

        # Medium
        if medium_name:
            medium = get_resource(resource_type=MEDIUM,
                                  resource_func=theforeman.search_medium,
                                  resource_name=medium_name)
            data['medium_id'] = medium.get('id')

        # Organization
        if organization_name:
            organization = get_resource(resource_type=ORGANIZATION,
                                        resource_func=theforeman.search_organization,
                                        resource_name=organization_name)
            data['organization_id'] = organization.get('id')

        # Operatingssystem
        if operatingsystem_name:
            operatingsystem = get_resource(resource_type=OPERATINGSYSTEM,
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
            subnet = get_resource(resource_type=SUBNET,
                                  resource_func=theforeman.search_subnet,
                                  resource_name=subnet_name)
            data['subnet_id'] = subnet.get('id')

        try:
            host = theforeman.create_host(data=data)
        except ForemanError as e:
            module.fail_json(msg='Could not create host: {0}'.format(e.message))

        changed = True

    host_id = host.get('id')

    # Parameters
    if parameters:
        host_parameters = theforeman.get_host_parameters(host_id=host_id)

        for param in parameters:
            host_params = [item for item in host_parameters if item.get('name') == param.get('name')]
            if not host_params:
                try:
                    theforeman.create_host_parameter(host_id=host_id, data=param)
                except ForemanError as e:
                    module.fail_json(
                        msg='Could not create host parameter {param_name}: {error}'.format(param_name=param.get('name'),
                                                                                           error=e.message))
                changed = True
            elif host_params[0]['value'] != param.get('value'):
                try:
                    theforeman.update_host_parameter(host_id=host_id, parameter_id=host_params[0].get('id'),
                                                     data=param)
                except ForemanError as e:
                    module.fail_json(
                        msg='Could not update host parameter {param_name}: {error}'.format(param_name=param.get('name'),
                                                                                           error=e.message))
                changed = True

    try:
        host_power = theforeman.get_host_power(host_id=host_id)
    except ForemanError as e:
        module.fail_json(msg='Could not get host power information: {0}'.format(e.message))

    host_power_state = host_power.get('power')

    if state == 'rebooted':
        try:
            theforeman.reboot_host(host_id=host_id)
            changed = True
        except ForemanError as e:
            module.fail_json(msg='Could not reboot host: {0}'.format(e.message))
    elif state == 'running' and host_power_state != 'poweredOn':
        try:
            theforeman.poweron_host(host_id=host_id)
            changed = True
        except ForemanError as e:
            module.fail_json(msg='Could not power on host: {0}'.format(e.message))
    elif state == 'stopped' and host_power_state != 'poweredOff':
        try:
            theforeman.poweroff_host(host_id=host_id)
            changed = True
        except ForemanError as e:
            module.fail_json(msg='Could not power off host: {0}'.format(e.message))

    return changed, host


def main():
    global module
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            architecture=dict(type='str', default='x86_64'),
            build=dict(type='bool', default=False),
            compute_profile=dict(type='str', default=None),
            compute_resource=dict(type='str', default=None),
            domain=dict(type='str', default=None),
            enabled=dict(type='bool', default=False),
            environment=dict(type='str', default=None),
            hostgroup=dict(type='str', default=None),
            image=dict(type='str', default=None),
            location=dict(type='str', default=None),
            managed=dict(type='bool', default=False),
            medium=dict(type='str', default=None),
            operatingsystem=dict(type='str', default=None),
            organization=dict(type='str', default=None),
            parameters=dict(type='str', default=None),
            provision_method=dict(type='str', required=False, choices=['build', 'image']),
            root_pass=dict(type='str', default=None),
            state=dict(type='str', default='present',
                       choices=['present', 'absent', 'running', 'stopped', 'rebooted']),
            subnet=dict(type='str', default=None),
            foreman_host=dict(type='str', default='127.0.0.1'),
            foreman_port=dict(type='str', default='443'),
            foreman_user=dict(type='str', required=True),
            foreman_pass=dict(type='str', required=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    changed, host = ensure()
    module.exit_json(changed=changed, host=host)

# import module snippets
from ansible.module_utils.basic import *

main()
