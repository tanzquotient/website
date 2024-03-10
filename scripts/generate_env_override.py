# Script to generate a fresh overrides.yml.
#
# The generated overrides contains variables from two sources:
#  - known variables in need of overriding in a dev environment (hardcoded in DEV_OVERRIDES)
#  - all variables whose default is "overrideme"

import argparse
import os
import yaml

# Location to store output file in
VARIABLES_FILE = "variables.yml"
OVERRIDE_FILE = "overrides.yml"
DEV_OVERRIDES = "configurations/dev-overrides.yml"

import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Generate the environment overrides")
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overrides file, if it already exists",
    )
    args = parser.parse_args()

    if os.path.exists(OVERRIDE_FILE) and not args.force:
        print(f"{OVERRIDE_FILE} already exists - skipping")
        sys.exit(0)

    # Load variables
    with open(VARIABLES_FILE) as var_file:
        variables = yaml.safe_load(var_file)

    # Load dev overrides
    with open(DEV_OVERRIDES) as var_file:
        dev_overrides = yaml.safe_load(var_file)

    # Combine dev_overrides and "overrideme"s
    overrides = dev_overrides
    for key in variables.keys():
        default = 1
        default_value = variables[key][default]
        if default_value == "overrideme":
            overrides[key] = overrides.get(key, default_value)

    # Write overrides.yml file
    with open(OVERRIDE_FILE, "w") as override_file:
        for key, value in overrides.items():
            line = "{}: {}\n".format(key, value)
            override_file.write(line)
