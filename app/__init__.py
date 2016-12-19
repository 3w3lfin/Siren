# pip install gitpython
import sys
import os
from git import Repo
from django.conf import settings


def startup():
    #create git repo
    dir = os.path.join(settings.BASE_DIR, "app/static")
    repo_dir = os.path.join(dir, 'repo')
    if not os.path.exists(repo_dir):
        file_name = os.path.join(repo_dir, 'README.txt')
        repo = Repo.init(repo_dir)
        #some init info
        f = open(file_name, 'w+')
        f.write('some very important things')
        f.close()
        repo.index.add([file_name])
        repo.index.commit("initial commit")
startup()
