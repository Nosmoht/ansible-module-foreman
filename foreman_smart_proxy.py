#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from foreman import Foreman
    from foreman.foreman import ForemanError
except ImportError:
    foremanclient_found = False
else:
    foremanclient_found = True

def ensure(module):
    name = module.params['name']
    url = module.params['url']
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
        smart_proxy = theforeman.get_smart_proxy(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get smart proxy: ' + e.message)

    if not smart_proxy and state == 'present':
        data['url'] = url
        try:
            theforeman.create_smart_proxy(data=data)
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not create smart proxy: ' + e.message)

    if smart_proxy and state == 'absent':
        try:
            theforeman.delete_smart_proxy(data=subnet)
            return True
        except:
            module.fail_json(msg='Could not delete smart proxy: ' + e.message)
    return False

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(Type='str', required=True),
            url=dict(Type='str', required=True),
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