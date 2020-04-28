import argparse
import json

from env.generate_env import generate

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Generate the environment')
    parser.add_argument("type", choices=['default', 'sip'], default='default')
    parser.add_argument('--overrides')
    args = parser.parse_args()

    override = dict()
    if args.overrides:
        with open(args.overrides) as json_file:
            override = json.load(args.override)

    generate(args.type, override)