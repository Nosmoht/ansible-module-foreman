#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from foreman.foreman import *
except ImportError:
    foremanclient_found = False
else:
    foremanclient_found = True

def ensure(module):
    name = module.params['name']
    state = module.params['state']

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
        subnet = theforeman.search_subnet(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get subnet: {0}'.format(e.message))

    if module.params.has_key('network'):
        data['network'] = module.params['network']
    if module.params.has_key('mask'):
        data['mask'] = module.params['mask']
    if module.params.has_key('ipam'):
        data['ipam'] = module.params['ipam']
    if module.params.has_key('ip_from'):
        data['from'] = module.params['ip_from']
    if module.params.has_key('ip_to'):
        data['to'] = module.params['ip_to']
    if module.params.has_key('vlanid'):
        data['vlanid'] = module.params['vlanid']

    if not subnet and state == 'present':
        try:
            theforeman.create_subnet(data=data)
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not create subnet: {0}'.format(e.message))

    if subnet:
        if state == 'absent':
            try:
                theforeman.delete_subnet(id=subnet.get('id'))
                return True
            except ForemanError as e:
                module.fail_json(msg='Could not delete subnet: {0}'.format(e.message))

        if not all(data[key] == subnet[key] for key in data):
            try:
                theforeman.update_subnet(id=subnet.get('id'), data=data)
                return True
            except ForemanError as e:
                module.fail_json(msg='Could not update subnet: {0}'.format(e.message))

    return False

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            network=dict(type='str', required=False),
            mask=dict(type='str', required=False),
            ipam=dict(type='str', required=False, choices=['DHCP', 'Internal DB', 'None']),
            ip_from=dict(type='str', required=False),
            ip_to=dict(type='str', required=False),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            vlanid=dict(type='str', default=None),
            foreman_host=dict(type='str', default='127.0.0.1'),
            foreman_port=dict(type='str', default='443'),
            foreman_user=dict(type='str', required=True),
            foreman_pass=dict(type='str', required=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    changed = ensure(module)
    module.exit_json(changed=changed, name=module.params['name'])

# import module snippets
from ansible.module_utils.basic import *
main()
