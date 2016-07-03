#!/usr/bin/env python3
import argparse
import pwd
import grp
import os
import glob

parser = argparse.ArgumentParser('changes owner of all python files to given user')
parser.add_argument("user", help="the user that should own all python files")
parser.add_argument("-d", "--dryrun", help="only show files that would get modified", action="store_true")
args = parser.parse_args()
uid = pwd.getpwnam(args.user).pw_uid
gid = grp.getgrnam(args.user).gr_gid
print('We change the permissions to {}:{}').format(uid,gid)
for file in glob.glob('./**/migrations/*.py'):
    print(file)
    if not args.dryrun:
        os.chown(file, uid, gid)
