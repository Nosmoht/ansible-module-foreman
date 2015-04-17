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
        location = theforeman.search_location(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get location: ' + e.message)

    if not location and state == 'present':
        try:
            theforeman.create_location(data=data)
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not create location: ' + e.message)

    if location and state == 'absent':
        try:
            theforeman.delete_location(id=location.get('id'))
            return True
        except ForemanError as e:
            module.fail_json('Could not delete location: ' + e.message)

    return False

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(Type='str', required=True),
            state=dict(Type='str', Default='present', choices=['present', 'absent']),
            foreman_host=dict(Type='str', Default='127.0.0.1'),
            foreman_port=dict(Type='str', Default='443'),
            foreman_user=dict(Type='str', required=True),
            foreman_pass=dict(Type='str', required=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required')

    changed = ensure(module)
    module.exit_json(changed=changed, name=module.params['name'])

# import module snippets
from ansible.module_utils.basic import *
main()
