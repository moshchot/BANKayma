#!/usr/bin/env python3

import os.path
import subprocess
import sys

import yaml

odoo_version = "16.0"
remote_name = "oca"

if len(sys.argv) != 2 or not os.path.isfile(sys.argv[1]):
    # pylint: disable=print-used
    print("Pass a repos.yml")
    sys.exit(1)

with open(sys.argv[1], "r") as repos_file:
    repos = yaml.safe_load(repos_file)
    for repo, repo_config in repos.items():
        if "." in repo:
            continue
        remote = repo_config.get("remotes", {}).get(remote_name)
        if not remote:
            continue
        git_call = subprocess.run(
            'git ls-remote %s | grep "refs/heads/%s$" | cut -f1'
            % (remote, odoo_version),
            shell=True,
            capture_output=True,
            check=True,
        )
        new_hash = git_call.stdout.strip().decode("utf8")
        repo_config["merges"] = [
            merge
            if not merge.startswith(remote_name + " ")
            else "%s %s" % (remote_name, new_hash)
            for merge in repo_config["merges"]
        ]

yaml.dump(repos, open(sys.argv[1], "w"))
