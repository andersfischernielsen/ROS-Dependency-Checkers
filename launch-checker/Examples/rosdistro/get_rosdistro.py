#!/usr/bin/env python3

import yaml
import os
import urllib.request


def fetch_repo(url, branch):
    print(f'getting {url} on branch {branch}...')
    git = f'git clone --single-branch -b {branch} {url}'
    os.system(git)


url = 'https://raw.githubusercontent.com/ros/rosdistro/master/melodic/distribution.yaml'
response = urllib.request.urlopen(url)
data = response.read()
text = data.decode('utf-8')
data_loaded = yaml.safe_load(text)
repos = data_loaded['repositories']

for repo in repos:
    url = None
    branch = None
    try:
        if 'source' in repos[repo].keys():
            url = repos[repo]['source']['url']
            branch = repos[repo]['source']['version']
        if not url or not branch:
            continue
        try:
            fetch_repo(url, branch)
        except Exception as e:
            print("Couldn't fetch %s" % url)
            print("%s" % e)
    except Exception as e:
        print("Couldn't fetch %s" % url)
        print("%s" % e)
