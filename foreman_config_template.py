#!/usr/bin/env python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: foreman_config_template
short_description:
- Manage Foreman Provision Templates using Foreman API v2.
description:
- Create, update and and delete Foreman provision templates using Foreman API v2
options:
  name:
    description: Provision template name
    required: true
    default: null
    aliases: []
  locked:
    description: Whether or not the template is locked for editing
    required: false
    default: false
  template:
    description: RAW template content
    required: false
  template_file:
    description: Path and filename to load the template from
    required: false
  template_kind:
    description: Template Kind name (not implemented yet)
    required: false
  snippet:
    description: Define if template is a snippet or not
    required: false
    default: false
  state:
    description: Provision template state
    required: false
    default: 'present'
    choices: ['present', 'absent']
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

EXAMPLES = '''
- name: Ensure Config Template
  foreman_config_template:
    name: CoreOS Cloud-config
    locked: false
    template_file: /tmp/coreos-cloud-config
    snippet: true
    state: present
    foreman_host: 127.0.0.1
    foreman_port: 443
    foreman_user: admin
    foreman_pass: secret
'''

try:
    from foreman.foreman import *

    foremanclient_found = True
except ImportError:
    foremanclient_found = False


def ensure(module):
    updateable_keys = ['locked', 'snippet', 'template', 'template_kind']
    locked = module.params['locked']
    name = module.params['name']
    state = module.params['state']
    snippet = module.params['snippet']
    template = module.params['template']
    template_file = module.params['template_file']
    template_kind = module.params['template_kind']

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
        config_template = theforeman.search_config_template(data=data)
        if config_template:
            config_template = theforeman.get_config_template(id=config_template.get('id'))
    except ForemanError as e:
        module.fail_json(msg='Could not get config template: {0}'.format(e.message))

    if state == 'present':
        if not template and not template_file:
            module.fail_json(msg='Either template or template_file must be defined')
        elif template and template_file:
            module.fail_json(msg='Only one of either template or template_file must be defined')
        elif template:
            data['template'] = template
        else:
            try:
                with open(template_file) as f:
                    data['template'] = f.read()
            except IOError as e:
                module.fail_json(msg='Could not open file {0}: {1}'.format(template_file, e.message))

        data['locked'] = locked
        data['snippet'] = snippet
        data['template_kind'] = template_kind

        if not config_template:
            try:
                config_template = theforeman.create_config_template(data=data)
                return True, config_template
            except ForemanError as e:
                module.fail_json(msg='Could not create config template: {0}'.format(e.message))

        if not all(data.get(key, None) == config_template.get(key, None) for key in updateable_keys):
            try:
                config_template = theforeman.update_config_template(id=config_template.get('id'), data=data)
                return True, config_template
            except ForemanError as e:
                module.fail_json(msg='Could not update config template: {0}'.format(e.message))

    else:
        if config_template:
            try:
                config_template = theforeman.delete_config_template(id=config_template.get('id'))
                return True, config_template
            except ForemanError as e:
                module.fail_json(msg='Could not delete config template: {0}'.format(e.message))

    return False, config_template


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            locked=dict(type='bool', default=False),
            template=dict(type='str', default=None),
            template_file=dict(type='str', default=None),
            template_kind=dict(type='str', default=None),
            snippet=dict(type='bool', default=False),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            foreman_host=dict(type='str', default='127.0.0.1'),
            foreman_port=dict(type='str', default='443'),
            foreman_user=dict(type='str', required=True),
            foreman_pass=dict(type='str', required=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    changed, config_template = ensure(module)
    module.exit_json(changed=changed, config_template=config_template)

# import module snippets
from ansible.module_utils.basic import *

main()
