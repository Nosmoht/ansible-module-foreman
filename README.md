# ansible-library-foreman
Ansible library to configure [Foreman] and manage hosts.

# Requirements
[python-foreman] >= 0.6.1 is required to be installed on the system where Ansible is started from.

# Examples
The following parameters are always required so the module knows how to connect to the Foreman [API v2].

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
```
## Host
```
- name: Ensure Host
  foreman_host:
    name: ansible-host-01.example.com
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
Not implemented yet. Coming soon.

## Operatingsystem
Not implemented yet. Coming soon.

## Organization
Not implemented yet. Coming soon.

## Smart Proxy
```
- name: Esnure Smart Proxy
  foreman_smart_proxy:
    name: SmartProxy01
    url: http://localhost:8443
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
