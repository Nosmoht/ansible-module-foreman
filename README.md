# ansible-library-foreman
Ansible library to configure [Foreman] and manage hosts.

# Requirements
[python-foreman] >= 0.11.4 is required to be installed on the system where Ansible is started from.

# Examples
The following parameters are always required so the module knows how to connect to the Foreman [API v2].
The are replaced in the examples by three dots (...).

```
foreman_host: foreman.example.com
foreman_port: 443
foreman_user: admin
foreman_pass: password
```
## Architecture
```
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

```
- name: Ensure Compute Profile
  foreman_compute_profile:
    name: 1-Small
    foreman_host: foreman.example.com
    foreman_port: 443
    foreman_user: admin
    foreman_pass: password
```

## Compute Resource
```
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
```
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
## Domain
```
- name: Ensure Domain
  foreman_domain:
    name: example.com
    state: present
    ...
```
## Environments
```
- name: Ensure Environment
  foreman_environment:
    name: Production
    state: present
    ...
```
## Host
### Provision by Medium
```
- name: Ensure Host
  foreman_host:
    name: ansible-host-01
    state: running
    architecture: x86_64
    compute_profile: 1-Small
    compute_resource: VMwareCluster01
    domain: example.com
    environment: Production
    hostgroup: Hostgroup01
    location: Somewhere
    operatingsystem: CoreOS
    organization: Example Org.
    medium: CoreOS Medium
    ...
```
### Provision by Image
```
- name: Ensure Host
  foreman_host:
    name: ansible-host-01
    state: running
    architecture: x86_64
    compute_profile: 1-Small
    compute_resource: VMwareCluster01
    domain: example.com
    environment: Production
    hostgroup: Hostgroup01
    image: CoreOS Image
    location: Somewhere
    operatingsystem: CoreOS
    organization: Example Org.
...
```
## Delete host
To delete a host Foreman must know the FQDN. Use one of the following methods:
```
- name: Ensure absent host
  foreman_host:
    name: ansible-host-01
    domain: example.com
    state: absent
    ...
```
or
```
- name: Ensure absent host
  foreman_host:
    name: ansible-host-01.example.com
    state: absent
...
```
## Hostgroup
```
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
```
- name: Ensure Medium
  foreman_medium:
    name: CoreOS
    path: http://$release.release.core-os.net
    state: present
    ...
```

## Operatingsystem
```
- name: Ensure Operatingsystem
  foreman_operatingsystem:
    name: CentOS
    major: 6
    minor: 6
    state: present
  ...
```

## Organization
Works only if Katello is used
```
- name: Ensure Organization
  foreman_organization:
    name: MyOrganization
    state: present
    ...
```

## Role
```
- name: Ensure Role
  foreman_role:
    name: MyRole
    state: present
```

## Smart Proxy
```
- name: Ensure Smart Proxy
  foreman_smart_proxy:
    name: SmartProxy01
    url: http://localhost:8443
    state: present
    ...
```

## User
```
- name: Ensure User
  foreman_user:
    login: MyUser
    firstname: Testing
    lastname: User
    mail: testing.user@example.com
    password: topsecret
    admin: false
    auth: 'Internal'
    state: present
```

# License

GPL

# Author
[Thomas Krahn]

[Foreman]: www.theforeman.org
[API v2]: www.theforeman.org/api_v2.html
[python-foreman]: https://github.com/Nosmoht/python-foreman
[Thomas Krahn]: mailto:ntbc@gmx.net
