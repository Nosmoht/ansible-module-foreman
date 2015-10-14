Ansible library Foreman
==========

# Table of Contents
- [Description](#description)
- [Requirements](#requirements)
- [Examples](#examples)
- [License](#license)
- [Author information](#author information)

# Description
Ansible library to configure [Foreman] and manage hosts.

With the current implementation it's possible to create, update and delete the following Foreman Resources
- Architectures
- Compute Attributes
- Compute Profiles
- Compute Resources
- Config Templates
- Domains
- Environments
- Hosts
- Hostgroups
- Locations (needs Katello)
- Medium
- Operatingsystems
- Operatingsystem default templates
- Organizations (need s Katello)
- Partition Tables
- Roles
- Smart Proxies
- Subnets
- Users

# Requirements
[python-foreman] >= 0.12.11 is required to be installed on the system where Ansible is started from.

# Examples
The following parameters are always required so the module knows how to connect to the Foreman [API v2].
They are replaced in the examples by three dots (...).

```yaml
foreman_host: foreman.example.com
foreman_port: 443
foreman_user: admin
foreman_pass: password
```

## Architecture
```yaml
- name: Ensure Architecture
  foreman_architecture:
    name: x86_64
    state: present
    foreman_host: foreman.example.com
    foreman_port: 443
    foreman_user: admin
    foreman_pass: password
```

## Compute Profile
```yaml
- name: Ensure Compute Profile
  foreman_compute_profile:
    name: 1-Small
    foreman_host: foreman.example.com
    foreman_port: 443
    foreman_user: admin
    foreman_pass: password
```

## Compute Resource
```yaml
- name: Ensure Compute Resource
  foreman_compute_resource:
    name: VMwareCluster01
    state: present
    url: vsphere.example.com
    provider: VMWare
    user: ansible
    password: secret
    server: vsphere.example.com
    ...
```

## Compute Attribute
This is an example to configure VMware vSphere attributes.
```yaml
- name: Ensure Compute Attribute
  foreman_compute_attribute:
    compute_profile: 1-Small
    compute_resource: VMwareCluster1
    vm_attributes:
      cluster: Cluster1
      corespersocket: 1
      cpus: 1
      guest_id: otherGuest64
      hardware_version: vmx-10
      interfaces_attributes:
      '0':
        _delete: ''
        network: network-40
        type: VirtualVmxnet3
      '1':
        _delete: ''
        network: network-40
        type: VirtualVmxnet3
      new_interfaces:
        _delete: ''
        network: network-40
        type: VirtualVmxnet3
        memory_mb: 1024
      path: /Datacenters/DC01/vm/example
      scsi_controller_type: ParaVirtualSCSIController
      volumes_attributes:
        '0':
          _delete: ''
          datastore: DS01
          eager_zero: true
          name: Hard disk
          size_gb: 16
          thin: true
        new_volumes:
          _delete: ''
          datastore: DS01
          eager_zero: true
          name: Hard disk
          size_gb: 16
          thin: true
    ...
```

## Config Template
### Deploy existing file
```yaml
- name: Ensure Config Template
  foreman_config_template:
    name: CoreOS Cloud-config
    locked: false
    operatingsystems:
    - CoreOS
    template_file: files/coreos-cloud-config
    snippet: true
    state: present
    ...
```
### Deploy content
```yaml
- name: Ensure Config Template
  foreman_config_template:
    name: CoreOS Cloud-config
    locked: false
    operatingsystems:
    - CoreOS
    template: "Some content"
    snippet: true
    state: present
...
```

## Domain
```yaml
- name: Ensure Domain
  foreman_domain:
    name: example.com
    state: present
    ...
```

## Environments
```yaml
- name: Ensure Environment
  foreman_environment:
    name: Production
    state: present
    ...
```
## Host
### Provision using installation from medium
```yaml
- name: Ensure Host
  foreman_host:
    name: ansible-host-01
    state: running
    architecture: x86_64
    domain: example.com
    environment: production
    medium: CoreOS
    provision_method: build
    root_pass: topsecret
```

### Provision by clone from image
```yaml
- name: Ensure Host
  foreman_host:
    name: ansible-host-03
    state: running
    compute_resource: VMwareCluster01
    hostgroup: Hostgroup01
    image: CoreOS Image
    provision_method: image
...
```
### Provision using a hostgroup
```yaml
- name: Ensure Host
  foreman_host:
    name: ansible-host-02
    state: running
    compute_resource: VMwareCluster01
    hostgroup: Hostgroup01
    provision_method: build
    ...
```
### Delete host
To delete a host Foreman must know the FQDN. Use one of the following methods:
```yaml
- name: Ensure absent host
  foreman_host:
    name: ansible-host-01
    domain: example.com
    state: absent
    ...
```
or
```yaml
- name: Ensure absent host
  foreman_host:
    name: ansible-host-01.example.com
    state: absent
...
```
## Hostgroup
```yaml
- name: Ensure Hostgroup
  foreman_hostgroup:
    name: Hostgroup01
    architecture: x86_64
    domain: example.com
    environment: production
    medium: CoreOS mirror
    operatingsystem: CoreOS
    partition_table: CoreOS Partition Table
    subnet: example.com
    state: present
    ...
```

## Location
```
- name: Ensure Location
  foreman_location:
    name: Location01
    state: present
    ...
```

## Medium
```yaml
- name: Ensure Medium
  foreman_medium:
    name: CoreOS
    path: http://$release.release.core-os.net
    os_family: CoreOS
    state: present
    ...
```

## Operatingsystem
```yaml
- name: Ensure Operatingsystem
  foreman_operatingsystem:
    name: CoreOS
    major: 633
    minor: 0.0
    architectures:
    - x86_64
    media:
    - CoreOS mirror
    ptables:
    - CoreOS default fake
    state: present
  ...
```

## Operatingsystem default template
```yaml
- name: Ensure Operatingsystem default template
  foreman_os_default_template:
    operatingsystem: CoreOS
    config_template: CoreOS PXELinux
    template_kind: PXELinux
    state: present
    ...
```

## Organization
Works only if Katello is used
```yaml
- name: Ensure Organization
  foreman_organization:
    name: MyOrganization
    state: present
    ...
```

## Partition Table
```yaml
- name: Ensure partition table
  foreman_ptable:
    name: MyPartitionTable
    layout: 'some layout'
    os_family: CoreOS
    state: present
    ...
```
## Role
```yaml
- name: Ensure Role
  foreman_role:
    name: MyRole
    state: present
```

## Smart Proxy
```yaml
- name: Ensure Smart Proxy
  foreman_smart_proxy:
    name: SmartProxy01
    url: http://localhost:8443
    state: present
    ...
```

## User
```yaml
- name: Ensure User
  foreman_user:
    login: MyUser
    admin: false
    auth: 'Internal'
    firstname: Testing
    lastname: User
    mail: testing.user@example.com
    password: topsecret
    roles:
    - Manager
    - Viewer
    state: present
```

# License

Copyright 2015 Thomas Krahn

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

# Author

[Thomas Krahn]

[Foreman]: www.theforeman.org
[API v2]: www.theforeman.org/api_v2.html
[python-foreman]: https://github.com/Nosmoht/python-foreman
[Thomas Krahn]: mailto:ntbc@gmx.net
