#!/usr/bin/env python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: foreman_host
short_description: Create and delete hosts with Foreman using Foreman API v2
description:
- Create and delete hosts using Foreman API v2
options:
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
    from foreman import Foreman
    from foreman.foreman import ForemanError
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
    architecture_name = module.params['architecture']
    build = module.params['build']
    compute_profile_name = module.params['compute_profile']
    compute_resource_name = module.params['compute_resource']
    domain_name = module.params['domain']
    enabled = module.params['enabled']
    environment_name = module.params['environment']
    hostgroup_name = module.params['hostgroup']
    image_name = module.params['image']
    location_name = module.params['location']
    managed = module.params['managed']
    medium_name = module.params['medium']
    operatingsystem_name = module.params['operatingsystem']
    organization_name = module.params['organization']
    root_pass = module.params['root_pass']
    state = module.params['state']
    subnet_name = module.params['subnet']
    foreman_host = module.params['foreman_host']
    foreman_port = module.params['foreman_port']
    foreman_user = module.params['foreman_user']
    foreman_pass = module.params['foreman_pass']

    theforeman = Foreman(hostname=foreman_host,
                         port=foreman_port,
                         username=foreman_user,
                         password=foreman_pass)

    data = {}

    if domain_name and domain_name in name:
        data['name'] = name
    else:
        data['name'] = name + '.' + domain_name

    try:
        host = theforeman.get_host(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not find host: ' + e.message)

    if not host:
        if state == 'absent':
            return False

        # Architecture
        if architecture_name:
            architecture = get_resource(module=module,
                                        resource_type='architecture',
                                        resource_func=theforeman.get_architecture,
                                        resource_name=architecture_name)
        data['architecture_id'] = architecture.get('id')
        data['build'] = build

        # Compute Profile
        if compute_profile_name:
            compute_profile = get_resource(module=module,
                                           resource_type='compute profile',
                                           resource_func=theforeman.get_compute_profile,
                                           resource_name=compute_profile_name)
            data['compute_profile_id'] = compute_profile.get('id')

        # Compute Resource
        if compute_resource_name:
            compute_resource = get_resource(module=module,
                                           resource_type='compute resource',
                                           resource_func=theforeman.get_compute_resource,
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
                data['provision_method'] = 'image'

        # Domain
        if domain_name:
            domain = get_resource(module=module,
                                  resource_type='domain',
                                  resource_func=theforeman.get_domain,
                                  resource_name=domain_name)
            data['domain_id'] = domain.get('id')

        if enabled:
            data['enabled'] = enabled

        # Environment
        if environment_name:
            environment = get_resource(module=module,
                                       resource_type='environment',
                                       resource_func=theforeman.get_environment,
                                       resource_name=environment_name)
            data['environment_id'] = environment.get('id')

        # Hostgroup
        if hostgroup_name:
            hostgroup = get_resource(module=module,
                                     resource_type='hostgroup',
                                     resource_func=theforeman.get_hostgroup,
                                     resource_name=hostgroup_name)
            data['hostgroup_id'] = hostgroup.get('id')

        # Location
        if location_name:
            location = get_resource(module=module,
                                    resource_type='location',
                                    resource_func=theforeman.get_location,
                                    resource_name=location_name)
            data['location_id'] = location.get('id')

        # Managed
        if managed:
            data['managed'] = managed

        # Medium
        if medium_name:
            medium = get_resource(module=module,
                                  resource_type='medium',
                                  resource_func=theforeman.get_medium,
                                  resource_name=medium_name)
            data['medium_id'] = medium.get('id')
            data['provision_method'] = 'build'

        # Organization
        if organization_name:
            organization = get_resource(module=module,
                                        resource_type='organization',
                                        resource_func=theforeman.get_organization,
                                        resource_name=organization_name)
            data['organization_id'] = organization.get('id')

        # Operatingssystem
        if operatingsystem_name:
            operatingsystem = get_resource(module=module,
                                           resource_type='operatingsystem',
                                           resource_func=theforeman.get_operatingsystem,
                                           resource_name=operatingsystem_name)
            data['operatingsystem_id'] = operatingsystem.get('id')

        # Root password
        if root_pass:
            data['root_pass'] = root_pass

        # Subnet
        if subnet_name:
            subnet = get_resource(module=module,
                                  resource_type='subnets',
                                  resource_func=theforeman.get_subnet,
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

    try:
        host_power_state = theforeman.get_host_power(host_id=host.get('name')).get('power')
    except ForemanError as e:
        module.fail_json(msg='Could not get host power state: ' + e.message)

    if state == 'rebooted':
        try:
            theforeman.reboot_host(host_id=host.get('name'))
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not reboot host: ' + e.message)
    elif state == 'running' and host_power_state != 'poweredOn':
        try:
            theforeman.poweron_host(host_id=host.get('name'))
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not power on host: ' + e.message)
    elif state == 'stopped' and host_power_state != 'poweredOff':
        try:
            theforeman.poweroff_host(host_id=host.get('name'))
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not power off host: ' + e.message)

    return changed

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name                = dict(Type='str', required=True),
            architecture        = dict(Type='str', default='x86_64'),
            build               = dict(type='bool', default=False),
            compute_profile     = dict(Type='str', required=False),
            compute_resource    = dict(Type='str', required=False),
            domain              = dict(Type='str', required=False),
            enabled             = dict(Type='str', required=False),
            environment         = dict(Type='str', required=False),
            hostgroup           = dict(Type='str', required=False),
            image               = dict(Type='str',required=False),
            location            = dict(Type='str', required=False),
            managed             = dict(Type='str', required=False),
            medium              = dict(Type='str', required=False),
            operatingsystem     = dict(Type='str', required=False),
            organization        = dict(Type='str', required=False),
            root_pass           = dict(Type='str', required=False),
            state               = dict(Type='str', default='present',
                                       choices=['present', 'absent', 'running', 'stopped', 'rebooted']),
            subnet              = dict(Type='str', required=False),
            foreman_host        = dict(Type='str', default='127.0.0.1'),
            foreman_port        = dict(Type='str', default='443'),
            foreman_user        = dict(Type='str', required=True),
            foreman_pass        = dict(Type='str', required=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    changed = ensure(module)
    module.exit_json(changed=changed, name=module.params['name'])

# import module snippets
from ansible.module_utils.basic import *
main()
