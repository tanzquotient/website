#!/usr/bin/env python3

import argparse
import os
import yaml

# Location to store output file in
VARIABLES_FILE = 'variables.yml'
OVERRIDE_FILE = 'overrides.yml'
DEV_OVERRIDES = 'configurations/dev-overrides.yml'


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Generate the environment overrides')
    parser.add_argument('-f', '--force', action='store_true', help='Overrides file, if it already exists')
    args = parser.parse_args()

    if os.path.exists(OVERRIDE_FILE) and not args.force:
        raise SystemExit('{} already exists - skipping'.format(OVERRIDE_FILE))

    # Load variables
    with open(VARIABLES_FILE) as var_file:
        variables = yaml.safe_load(var_file)

    # Load dev overrides
    with open(DEV_OVERRIDES) as var_file:
        dev_overrides = yaml.safe_load(var_file)

    # Store overrides to dict
    overrides = dev_overrides
    for key in variables.keys():
        default = 1
        value = variables[key][default]
        if value == 'overrideme':
            overrides[key] = overrides.get(key, value)

    # Write .env file
    with open(OVERRIDE_FILE, 'w') as override_file:
        for key, value in overrides.items():
            line = "{}: {}\n".format(key, value)
            override_file.write(line)
