import subprocess
import os
import io
from django.conf import settings
from .models import FileComment, FileCode, Project, File, Analysis
from django.contrib.auth.models import User
from git import Repo
from shutil import copyfile, copy, copy2
from django.core.signals import request_finished
from django.dispatch import receiver
from .signals import analysis_end

#save project and create project folder
def handle_new_project(name, user):
    project = Project(name = name["name"], creator = user)
    project.save()    
    dir = os.path.join('app/static', project.name + "_" + str(project.id),"")
    os.mkdir(dir)
    project.path = dir
    project.save()
    return project
    
#create service folder in repo
def new_repo(file, service, user, file_name, is_init):
    
    #create service folder
    service_name = service.name
    path = os.path.join(settings.BASE_DIR, "app/static/repo")
    folder_name = service_name + "_" + str(service.id)
    folder_path = os.path.join(path, folder_name)
    try:
        os.mkdir(folder_path)
    except:
        pass
    
    #copy file to new folder in git dir
    new_file_path = os.path.join(folder_path, file_name)
    file_path = os.path.join(settings.BASE_DIR, file.file.url)
    copyfile(file_path, new_file_path)
    
    #symlink in folder
    tmp, ext = os.path.splitext(file.path)
    folder_name = service.name + "_" + str(service.id)
    os.symlink(new_file_path, os.path.join('app/static', folder_name, str(file.ad_name) + "_" + str(file.id) + ext))
    file_code = FileCode(name = file_name, user = user)
    file_code.save()
    file_code.file.add(file)
    file_code.save()
    file.user_name = "v1"
    file.save()
    if is_init:
        service.init.add(file_code)
        com = "Init script " + file_name
    else:
        service.code.add(file_code)
        com = "Code " + file_name
    new_com = FileComment(file=file, user = user, comment = com)
    new_com.save()
    service.save()
    repo = Repo(path)
    repo.index.add([new_file_path])
    repo.index.commit(com)
 
def update_code(service, new_init, init, text, comment):
    init.file.add(new_init)
    init.save()
    
    #update repo
    path = os.path.join(settings.BASE_DIR, "app/static/repo")
    folder_name = service.name + "_" + str(service.id)
    folder_path = os.path.join(path, folder_name)
    
    #open init file in git dir and change text
    new_file_path = os.path.join(folder_path, init.name)
    with open(new_file_path, "wt") as fp:
        fp.truncate()
        fp.write(text)
    
    #commit
    repo = Repo(path)
    repo.index.add([new_file_path])
    repo.index.commit(comment)

#handle uploaded test file
def handle_uploaded_file(f, choice):
    nr = File.objects.number(choice)
    nr = nr + 1
    dir = os.path.join(settings.BASE_DIR, choice.name, str(nr))
    with open(dir, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    file = File(number = nr, project = choice)
    file.save()
    retcode = subprocess.call("/usr/bin/Rscript --vanilla -e 'source(\"temp/plot.R\")'", shell=True)
    
@receiver(analysis_end)
def my_callback(sender, **kwargs):
    print("Request finished!")
