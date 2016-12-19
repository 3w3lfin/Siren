from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.shortcuts import render, get_object_or_404 
from shutil import copyfile, copy, copy2
import string
import sys
import os
import random
from django.conf import settings
from .models import Module, Analysis
import subprocess
import stat

#generate random string
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


#run analysis
@shared_task
def run(module_id, analysis_id, path):
    
    #prepare folder
    analysis = get_object_or_404(Analysis, pk = analysis_id)
    module = get_object_or_404(Module, pk = module_id)
    os.mkdir(path)
    path_tmp = os.path.join(path, "conf")
    os.mkdir(path_tmp)
    path_tmp1 = os.path.join(path_tmp, "in")
    path_tmp2 = os.path.join(path_tmp, "out")
    os.mkdir(path_tmp1)
    os.mkdir(path_tmp2)
    path_tmp = os.path.join(path, "input")
    os.mkdir(path_tmp)
    path_tmp = os.path.join(path, "output")
    os.mkdir(path_tmp)
    path_tmp = os.path.join(path, "log")
    os.mkdir(path_tmp)
    path_tmp = os.path.join(path, "tmp")
    os.mkdir(path_tmp)
    
    #copy code
    init_path = os.path.join(settings.BASE_DIR, module.init.file.url)
    init_new_path = os.path.join(path, "init.sh")
    copy2(init_path, init_new_path)
    for code in module.code.all():
        code_path = os.path.join(settings.BASE_DIR, code.file.url)
        new_path = os.path.join(path, code.cl_name)
        copy2(code_path, new_path)
        
    conf_path = os.path.join(path, "conf/in/in.conf")
    f = open(conf_path, 'w+')
    for param in module.param.params.all():
        
        #prepare files
        if param.par_type == "F":
            file_path = os.path.join(settings.BASE_DIR, param.file.file.url)
            new_path = os.path.join(path, "input")
            new_path = os.path.join(new_path, param.file.cl_name)
            copyfile(file_path, new_path)
            
        #prepare params   
        else :
            st = param.name + ";" + param.value + "\n"
            f.write(st)
    f.close()
    
    #run init
    st = os.stat(init_new_path)
    os.chmod(init_new_path, st.st_mode | stat.S_IEXEC)
    child = subprocess.Popen(init_new_path, cwd=path, shell=True)
    child.wait()
    return 0
