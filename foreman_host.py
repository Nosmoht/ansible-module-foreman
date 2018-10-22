#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to manage Foreman host resources.
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

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
  ip:
    description: IP to use
    required: false
    default: false
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
  ip:
    description: IP address
    required: false
    default: None
  location:
    description: Location name (Only useful with Katello)
    required: false
    default: None
  mac:
    description: MAC address
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
  ptable:
    description: Which Partition table should be used, if build is set true
    required: false
    default: None
  pxe_loader:
    description: PXE Loader
    required: False
    default: None
  puppet_proxy:
    description: The puppet smart proxy, the host should be assigned to
    required: false
    default: None
  puppet_ca_proxy:
    description: The puppet ca smart proxy, the host should be assigned to
    default: None   
  realm:
    description: realm
    required: false
    default: None
  root_pass:
    description: root password
    required: false
    default: None
  subnet:
    description: Name of subnet to use for this host
    required: false
    default: None
  interfaces:
    description: List of network interfaces
  owner_user_name:
    description: Name of the owner user to use for this host
    required: false
    default: None
  owner_usergroup_name:
    description: Name of the owner usergroup to use for this host
    required: false
    default: None
  compute_attributes:
    description: compute attributes (can contain nested volume_attributes)
    required: false
    default: None
  content_source:
    description: content source (smart proxy or capsule)
    default: None
  content_view:
    description: content view (also requires lifecycle environment)
    default: None
  lifecycle_environment:
    description: lifecycle environment (also requires content view)
    default: None
  interfaces_attributes:
    description: interface attributes (can contain nested compute_attributes)
    required: false
    default: None
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
  foreman_pass:
    description: Password to be used to authenticate user on Foreman
    required: true
  foreman_ssl:
    description: Enable SSL when connecting to Foreman API
    required: false
    default: true
notes:
- Requires the python-foreman package to be installed. See https://github.com/Nosmoht/python-foreman.
version_added: "2.0"
author: "Thomas Krahn (@nosmoht)"
'''
import copy

try:
    from foreman.foreman import *
except ImportError:
    foremanclient_found = False
else:
    foremanclient_found = True


def get_resource(resource_type, resource_func, resource_name, search_title=False):
    try:
        result = resource_func(data=dict(name=resource_name))
        if not result:
            result = resource_func(data=dict(title=resource_name))
        if not result:
            module.fail_json(msg='{resource_type} {resource_name} not found'.format(resource_type=resource_type,
                                                                                    resource_name=resource_name))
    except ForemanError as e:
        module.fail_json(
            msg='Error while getting {resource_type}: {error}'.format(resource_type=resource_type, error=e.message))
    return result


def filter_host(h):
    """Filter all _name parameters since we only care about the IDs and convert
    ids to strings since this is what we need to feed back to foreman

    >>> filter_host({"a_name": "foo", "a_id": 1})
    {'a_id': '1'}
    """
    filtered = {}
    keep = ['title', 'name', 'root_pass']
    for k, v in h.items():
        if k.endswith('_id') and v is not None:
            filtered[k] = str(v)
        elif k in keep:
            filtered[k] = v
    return filtered


def resolve_subnet_names(interfaces, theforeman):
    for iface in interfaces:
        # get subnet id if subnet name specified
        iface_subnet_name = iface.pop('subnet', None)
        if iface_subnet_name:
            iface_subnet = get_resource(resource_type=SUBNET,
                                        resource_func=theforeman.search_subnet,
                                        resource_name=iface_subnet_name)
            iface['subnet_id'] = iface_subnet.get('id')


def ensure():
    changed = False
    name = module.params['name']
    architecture_name = module.params[ARCHITECTURE]
    build = module.params['build']
    ip = module.params['ip']
    compute_profile_name = module.params[COMPUTE_PROFILE]
    compute_resource_name = module.params[COMPUTE_RESOURCE]
    domain_name = module.params[DOMAIN]
    enabled = module.params['enabled']
    environment_name = module.params[ENVIRONMENT]
    hostgroup_name = module.params[HOSTGROUP]
    image_name = module.params['image']
    ip = module.params['ip']
    location_name = module.params[LOCATION]
    mac = module.params['mac']
    managed = module.params['managed']
    medium_name = module.params[MEDIUM]
    operatingsystem_name = module.params[OPERATINGSYSTEM]
    organization_name = module.params[ORGANIZATION]
    parameters = module.params['parameters']
    interfaces = module.params['interfaces']
    provision_method = module.params['provision_method']
    ptable_name = module.params[PARTITION_TABLE]
    pxe_loader = module.params['pxe_loader']
    root_pass = module.params['root_pass']
    puppet_proxy_name = module.params['puppet_proxy']
    puppet_ca_proxy_name = module.params['puppet_ca_proxy']
    state = module.params['state']
    subnet_name = module.params[SUBNET]
    realm_name = module.params['realm']
    interfaces_attributes = module.params['interfaces_attributes']
    owner_user_name = module.params['owner_user_name']
    owner_usergroup_name = module.params['owner_usergroup_name']
    compute_attributes = module.params['compute_attributes'] 
    content_source_name = module.params['content_source']
    content_view_name = module.params['content_view']
    lifecycle_environment_name = module.params['lifecycle_environment']

    foreman_host = module.params['foreman_host']
    foreman_port = module.params['foreman_port']
    foreman_user = module.params['foreman_user']
    foreman_pass = module.params['foreman_pass']
    foreman_ssl = module.params['foreman_ssl']

    theforeman = Foreman(hostname=foreman_host,
                         port=foreman_port,
                         username=foreman_user,
                         password=foreman_pass,
                         ssl=foreman_ssl)

    if domain_name:
        if domain_name in name:
            host_name = name
        else:
            host_name = '{name}.{domain}'.format(name=name, domain=domain_name)
    else:
        host_name = name

    data = dict(name=host_name)

    try:
        host = theforeman.search_host(data=data)
    except ForemanError as e:
        module.fail_json(
            msg='Error while searching host: {0}'.format(e.message))

    # Architecture
    if architecture_name:
        architecture = get_resource(resource_type=ARCHITECTURE,
                                    resource_func=theforeman.search_architecture,
                                    resource_name=architecture_name)
        data['architecture_id'] = architecture.get('id')

    # Build
    data['build'] = build

    # IP
    if ip:
        data['ip'] = ip

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
                module.fail_json(
                    msg='Compute Resource {0} has no images'.format(compute_resource_name))
            images = filter(lambda x: x['name'] ==
                                      image_name, compute_resource_images)
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
                                 resource_name=hostgroup_name,
                                 search_title=True)
        data['hostgroup_id'] = hostgroup.get('id')

    # IP
    if ip:
        data['ip'] = ip

    # Location
    if location_name:
        location = get_resource(resource_type=LOCATION,
                                resource_func=theforeman.search_location,
                                resource_name=location_name)
        data['location_id'] = location.get('id')

    # MAC
    if mac:
        data['mac'] = mac

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

    # Ptable 
    if ptable_name:
       ptable = get_resource(resource_type=PARTITION_TABLES,
                              resource_func=theforeman.search_partition_table,
                              resource_name=ptable_name)
       #return True, ptable
       data['ptable_id'] = ptable.get('id')

    # PXE loader
    if pxe_loader:
        data['pxe_loader'] = pxe_loader

    # Root password
    if root_pass:
        data['root_pass'] = root_pass

    # Puppet Smart Proxy
    if puppet_proxy_name:
        puppet_proxy = get_resource(resource_type=SMART_PROXY,
                               resource_func=theforeman.search_smart_proxy,
                               resource_name=puppet_proxy_name)
        data['puppet_proxy_id'] = str(puppet_proxy.get('id'))

    # Puppet CA Smart Proxy
    if puppet_ca_proxy_name:
        puppet_ca_proxy = get_resource(resource_type=SMART_PROXY,
                               resource_func=theforeman.search_smart_proxy,
                               resource_name=puppet_ca_proxy_name)
        data['puppet_ca_proxy_id'] = str(puppet_ca_proxy.get('id'))



    # Subnet
    if subnet_name:
        subnet = get_resource(resource_type=SUBNET,
                              resource_func=theforeman.search_subnet,
                              resource_name=subnet_name)
        data['subnet_id'] = subnet.get('id')

    # Realm
    if realm_name:
        realm = get_resource(resource_type=REALM,
                              resource_func=theforeman.search_realm,
                              resource_name=realm_name)
        data['realm_id'] = realm.get('id')

    # Content source
    if content_source_name:
        content_source = get_resource(resource_type=SMART_PROXY,
                              resource_func=theforeman.search_smart_proxy,
                              resource_name=content_source_name)
        data['content_source_id'] = content_source.get('id')

    # Content view
    if content_view_name:
        if 'content_facet_attributes' not in data:
            data['content_facet_attributes'] = {}

        resource_type = "../../katello/api/organizations/{0}/content_views".format(organization.get('id'))
        search = {'name': content_view_name}
        content_view = theforeman.search_resource(resource_type=resource_type, data=search)
        data['content_facet_attributes']['content_view_id'] = content_view.get('id')

    # Lifecycle environment
    if lifecycle_environment_name:
        if 'content_facet_attributes' not in data:
            data['content_facet_attributes'] = {}

        resource_type = "../../katello/api/organizations/{0}/environments".format(organization.get('id'))
        search = {'name': lifecycle_environment_name}
        lifecycle_environment = theforeman.search_resource(resource_type=resource_type, data=search)
        data['content_facet_attributes']['lifecycle_environment_id'] = lifecycle_environment.get('id')

    # Owner
    if owner_user_name:
        user = get_resource(resource_type=USER,
                              resource_func=theforeman.search_user,
                              resource_name=owner_user_name)
        data['owner_id'] = user.get('id')
        data['owner_type'] = 'User'

    if owner_usergroup_name:
        usergroup = get_resource(resource_type=USERGROUP,
                              resource_func=theforeman.search_usergroup,
                              resource_name=owner_usergroup_name)
        data['owner_id'] = usergroup.get('id')
        data['owner_type'] = 'Usergroup'

    # compute attributes
    if compute_attributes:
        data['compute_attributes'] = compute_attributes

    # interface attributes
    if interfaces_attributes:
        resolve_subnet_names(interfaces_attributes, theforeman)
        data['interfaces_attributes'] = interfaces_attributes

    if not host and state == 'present':
        try:
            host = theforeman.create_host(data=data)
            changed = True
        except ForemanError as e:
            module.fail_json(
                msg='Could not create host: {0}'.format(e.message))
    elif host:
        if state == 'absent':
            try:
                host = theforeman.delete_host(id=host.get('id'))
                return True, host
            except ForemanError as e:
                module.fail_json(
                    msg='Could not delete host: {0}'.format(e.message))

        cmp_host = filter_host(host)
        updatable_data = copy.copy(data)
        updatable_data.pop('compute_attributes', None)
        updatable_data.pop('interfaces_attributes', None)
        if any(updatable_data.get(key, None) != cmp_host.get(key, None) for key in updatable_data.keys()):
            try:
                host = theforeman.update_host(id=host.get('id'), data={'host': updatable_data})
                changed = True
            except ForemanError as e:
                module.fail_json(msg='Could not update host: {0}'.format(e.message))

    host_id = host.get('id')

    # Parameters
    if parameters:
        try:
            host_parameters = theforeman.get_host_parameters(host_id=host_id)
        except ForemanError as e:
            module.fail_json(
                msg='Could not get host parameters: {0}'.format(e.message))

        # Delete parameters which are not defined
        for host_param in host_parameters:
            host_param_name = host_param.get('name')
            defined_params = [item for item in parameters if item.get(
                'name') == host_param_name]
            if not defined_params:
                try:
                    theforeman.delete_host_parameter(
                        host_id=host_id, parameter_id=host_param.get('id'))
                except ForemanError as e:
                    module.fail_json(msg='Could not delete host parameter {name}: {error}'.format(
                        name=host_param_name))
                changed = True

        # Create and update parameters
        for param in parameters:
            host_params = [item for item in host_parameters if item.get(
                'name') == param.get('name')]
            if not host_params:
                try:
                    theforeman.create_host_parameter(
                        host_id=host_id, data=param)
                except ForemanError as e:
                    module.fail_json(
                        msg='Could not create host parameter {param_name}: {error}'.format(param_name=param.get('name'),
                                                                                           error=e.message))
                changed = True
            else:
                for host_param in host_params:
                    host_value = host_param.get('value')
                    param_value = param.get('value')
                    if isinstance(param_value, list):
                        param_value = ','.join(param_value)
                    # Replace \n seems to be needed. Otherwise some strings are
                    # always changed although they look equal
                    if host_value.replace('\n', '') != param_value.replace('\n', ''):
                        try:
                            theforeman.update_host_parameter(host_id=host_id,
                                                             parameter_id=host_param.get(
                                                                 'id'),
                                                             data=param)
                        except ForemanError as e:
                            module.fail_json(
                                msg='Could not update host parameter {param_name}: {error}'.format(
                                    param_name=param.get('name'), error=e.message))
                        changed = True

    # Network Interfaces
    if interfaces:
        resolve_subnet_names(interfaces, theforeman)
        try:
            host_interfaces = theforeman.get_resource('hosts', host_id, component='interfaces').get('results') or []
        except ForemanError as e:
            module.fail_json(
                msg='Could not get host interfaces: {0}'.format(e.message))

        interface_ips = []  # use ip to determine if existing or new interface
                            # i.e. if need to delete, create or update
        has_primary = False
        for iface in interfaces:
            interface_ips.append(iface.get('ip'))
            # clean primary flag, foreman api expecting 'true', 'false' strings
            if 'primary' in iface:
                if iface['primary']:
                    iface['primary'] = 'true'
                    has_primary = True
                else:
                    iface['primary'] = 'false'

        host_interfaces_by_ip = {}
        for host_iface in host_interfaces:
            host_interfaces_by_ip[host_iface.get('ip')] = host_iface

        # Create/update interfaces
        for iface in interfaces:
            interface_ip = iface.get('ip')

            if not has_primary:
                # No interface marked as primary.
                # If ip set with vm - mark it as primary.
                if interface_ip == ip:
                    iface['primary'] = True

            if interface_ip not in host_interfaces_by_ip.keys():
                # Create interface
                try:
                    theforeman.create_resource('hosts', 'interface', iface,
                                               resource_id=host_id, component='interfaces')
                except ForemanError as e:
                    module.fail_json(msg='Could not create host interface {ip}: {error}'.format(
                                     ip=interface_ip, error=e.message))
                changed = True

            else:
                # Update interface
                iface_to_upd = host_interfaces_by_ip[interface_ip]

                # compare fields to determine if need to update
                if 'subnet_id' in iface and iface['subnet_id'] != iface_to_upd.get('subnet_id') \
                    or 'mac'       in iface and iface['mac']       != iface_to_upd.get('mac') \
                    or 'managed'   in iface and iface['managed']   != iface_to_upd.get('managed') \
                    or 'provision' in iface and iface['provision'] != iface_to_upd.get('provision') \
                    or 'virtual'   in iface and iface['virtual']   != iface_to_upd.get('virtual'):

                    try:
                        theforeman.update_resource('hosts', host_id, iface, component='interfaces',
                                                   component_id=host_interfaces_by_ip[interface_ip]['id'])
                    except ForemanError as e:
                        module.fail_json(msg='Could not update host interface {ip}: {error}'.format(
                                         ip=interface_ip, error=e.message))
                    changed = True

    if state in ('rebooted','running','stopped'):
        try:
            host_power = theforeman.get_host_power(host_id=host_id)
        except ForemanError as e:
            # http://projects.theforeman.org/projects/foreman/wiki/ERF42-9958
            if 'ERF42-9958' in e.message:
                power_management_enabled = False
            else:
                module.fail_json(
                    msg='Could not get host power information: {0}'.format(e.message))
        else:
            power_management_enabled = True
        if power_management_enabled:
            host_power_state = host_power.get('power')

            if state == 'rebooted':
                try:
                    theforeman.reboot_host(host_id=host_id)
                    changed = True
                except ForemanError as e:
                    module.fail_json(
                        msg='Could not reboot host: {0}'.format(e.message))
            elif state == 'running' and host_power_state not in ['on', 'poweredOn']:
                try:
                    theforeman.poweron_host(host_id=host_id)
                    changed = True
                except ForemanError as e:
                    module.fail_json(
                        msg='Could not power on host: {0}'.format(e.message))
            elif state == 'stopped' and host_power_state not in ['off', 'poweredOff']:
                try:
                    theforeman.poweroff_host(host_id=host_id)
                    changed = True
                except ForemanError as e:
                    module.fail_json(
                        msg='Could not power off host: {0}'.format(e.message))

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
            ip=dict(type='str', default=None),
            location=dict(type='str', default=None),
            mac=dict(type='str', default=None),
            managed=dict(type='bool', default=False),
            medium=dict(type='str', default=None),
            operatingsystem=dict(type='str', default=None),
            organization=dict(type='str', default=None),
            parameters=dict(type='list', default=None),
            interfaces=dict(type='list', default=None),
            ptable=dict(type='str', default=None),
            pxe_loader=dict(type='str', default=None),
            provision_method=dict(type='str', required=False,
                                  choices=['build', 'image']),
            root_pass=dict(type='str', default=None),
            puppet_proxy=dict(type='str', default=None),
            puppet_ca_proxy=dict(type='str', default=None),
            state=dict(type='str', default='present',
                       choices=['present', 'absent', 'running', 'stopped', 'rebooted']),
            subnet=dict(type='str', default=None),
            realm=dict(type='str', default=None),
            interfaces_attributes=dict(type='list', required=False),
            owner_user_name=dict(type='str', default=None),
            owner_usergroup_name=dict(type='str', default=None),
            compute_attributes=dict(type='dict', required=False),
            content_source=dict(type='str', required=False),
            content_view=dict(type='str', required=False),
            lifecycle_environment=dict(type='str', required=False),
            foreman_host=dict(type='str', default='127.0.0.1'),
            foreman_port=dict(type='str', default='443'),
            foreman_user=dict(type='str', required=True),
            foreman_pass=dict(type='str', required=True, no_log=True),
            foreman_ssl=dict(type='bool', default=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(
            msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    changed, host = ensure()
    module.exit_json(changed=changed, host=host)


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
