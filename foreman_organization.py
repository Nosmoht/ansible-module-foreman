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

    data = {'name': name}

    try:
        organization = theforeman.search_organization(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get organization: {0}'.format(e.message))

    if not organization and state == 'present':
        try:
            theforeman.create_organization(data=data)
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not create organization: {0}'.format(e.message))

    if organization and state == 'absent':
        try:
            theforeman.delete_organization(id=organization.get('id'))
            return True
        except ForemanError as e:
            module.fail_json('Could not delete organization: {0}'.format(e.message))

    return False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
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
