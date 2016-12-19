'''
 * system Siren 1.1.1
 * https://github.com/3w3lfin
 *
 * Copyright 2016, Ewelina Kośmider
 * 
 * Licensed under the MIT license:
 * http://www.opensource.org/licenses/MIT
 '''


import shutil, glob, os, errno, string, random, json, datetime
from io import StringIO
from shutil import copyfile, copy, copy2
from os.path import basename
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import UpdateView
from django.views.generic import CreateView, DeleteView, ListView, View
from django.shortcuts import render, get_object_or_404 , redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.conf import settings
from django.contrib.auth import authenticate
from django.db.models import Q
from django.db.models.aggregates import Max
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.files import File as File_dj
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.forms import modelformset_factory
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.dispatch import receiver
from django.forms.formsets import formset_factory
from celery.result import AsyncResult
from .tasks import run
from .forms import (UploadFileForm, FileCommentForm2, ServiceUserForm, NameFileForm, RegisterFileNameForm, ProjectEditCommForm, 
                    NewUserForm, ParamForm2, ModuleForm, ModuleCommentForm, CommitForm, TextForm, ParamGroupNameForm, ParamForm, 
                    ParamCommForm, InTypeSmall, OutTypeSmall, ServiceCommForm, Params, InType, OutType, ServiceForm, GroupUserForm, 
                    GroupCommForm, GroupDictForm, GroupDescForm, FileCommentForm, GroupForm, FileDictFormSet, CommentFormSet, FileDictForm, 
                    FileCommentForm, BaseLinkFormSet2, UploadFileForm, FileUserForm, NewProjectForm, ShareProjectForm, NewAnalysisForm, 
                    EditUserExtForm, CommentForm, ProjectUserForm, BaseLinkFormSet, ProjectPlanForm, CommentForm, UploadFileForm2)
from .handler import update_code, new_repo, handle_uploaded_file, handle_new_project
from .models import (Picture, ModuleProject, UserComment, UserExtension, Module, ServiceProject, FileCode, Format, Service, ServiceComment, 
                    ServiceUser, Param, ParamGroup, ParamsComment, GroupUser, GroupDict, GroupComment, Filegroup, Groupproject, Group, 
                    Project, Fileproject, FileDict, FileComment,  Analysis, Program, Fileproject, File, UserExtension, Picture, 
                    ProjectStatus, ProjectComment, ProjectUser, FileUser)
from .response import JSONResponse, response_mimetype
from .serialize import serialize, serialize_red

    
###################  
# INDEX SITE
###################

def index(request):
    return render(request, 'app/index.html')
    
###################  
# LOG OUT
###################

def log_out(request):
    return render(request, 'app/logout.html')

###################  
# SIGN UP
###################

class SignView(View):
    
    def post(self, request, *args, **kwargs):
        #create new user
        userform = NewUserForm(request.POST)
        if userform.is_valid():
            new_user = userform.save()
            new_user.set_password(request.POST['password'])
            new_user.save()
            auth_user = authenticate(username=request.POST['username'], password=request.POST['password'])
            if new_user.is_active:
                login(request, auth_user)
                return HttpResponseRedirect('/app/my_site/')
        return render(request, 'app/sign.html', {'userform':userform})
   
    def get(self, request, *args, **kwargs):
        userform = NewUserForm()
        return render(request, 'app/sign.html', {'userform':userform})

#create new user info and folder
@receiver(post_save, sender=User)
def add_user_data(sender, created, **kwargs):
    user = kwargs.get('instance')
    if created:
        try:
            user = get_object_or_404(User, username = user)
            user_ext = UserExtension(user = user, email = user.email)
            user_ext.save()
            dir = os.path.join(settings.BASE_DIR, "app/static")
            dir = os.path.join(dir, user.username,"")
            os.mkdir(dir)
            com = "Hello " + user.username
            com = UserComment(comment = com, about_user = user, add_by = user)
            com.save()
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
                
###################  
# MY SITE
###################

class MySite(View):
    
    def get(self, request):
        
        #site info
        try:
            img_id = Picture.objects.filter(user = request.user).values('user').annotate(max_id=Max('id'))
            img_id = img_id[0]['max_id']
            img = Picture.objects.get(pk = img_id)
        except:
            img = None
        services = Service.objects.filter(user_service__user = self.request.user, is_active = True, user_service__role = "C", user_service__is_active = True)
        my_projects = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = True)
        else_projects = Project.objects.filter(Q(projectuser__who = self.request.user) & Q(is_active = True) & Q(projectuser__isactive = True) & ~Q(projectuser__role = "Cr") &Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "B")))
        my_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "C", is_active = True, file_user_comment__is_active = True)
        else_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "X", is_active = True, file_user_comment__is_active = True)
        else_services = Service.objects.filter(user_service__user = self.request.user, user_service__role = "X", is_active = True, user_service__is_active = True)
        pro_archive = Project.objects.filter(Q(is_del = False) & Q(projectuser__who = self.request.user) & Q(is_active = False) & Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "Cr") | Q(projectuser__role = "B")))
        file_archive = File.objects.filter(Q(is_del = False) & Q(file_user_comment__user = self.request.user) & Q(Q(file_user_comment__role = "C") | Q(file_user_comment__role = "X")) & Q(is_active = False))
        ser_archive = Service.objects.filter(Q(is_del = False) & Q(user_service__user = self.request.user) & Q(Q(user_service__role = "C") | Q(user_service__role = "X")) & Q(is_active = False))
        ext = UserExtension.objects.filter(user = self.request.user).values('user').annotate(max_id=Max('id'))
        ext = ext[0]['max_id']
        user_ext = UserExtension.objects.get(pk = ext)
        user = self.request.user

        #forms
        form_ext = EditUserExtForm(instance = user_ext)
        form_img = UploadFileForm()
        
        return render(request, 'app/my_site.html', {'my_projects': my_projects, 'else_projects' : else_projects, 
                'user' : user, 'services':services, 'user_ext':user_ext, 'form_ext':form_ext, 'form_img':form_img, 'img' : img,
                'my_file':my_file, 'else_file':else_file, 'else_services':else_services,
                'pro_archive':pro_archive, 'file_archive':file_archive, 'ser_archive':ser_archive})
                        
    def post(self, request, *args, **kwargs):
        user = self.request.user
        
        #forms
        form_ext = EditUserExtForm(request.POST)
        form_img = UploadFileForm(request.POST, request.FILES)
        
        #edit image
        if form_img.is_valid():
            file = form_img.save(commit=False)
            file.user = request.user
            file.save()
            files = [serialize(file)]
            data = {'files': files}
            response = JSONResponse(data, mimetype=response_mimetype(request))
            response['Content-Disposition'] = 'inline; filename=files.json'
            return response
            
        #edit personal info
        if "edit_info" in request.POST and form_ext.is_valid():
            new_ext = form_ext.save()
            new_ext.user = request.user
            new_ext.save()
            return HttpResponseRedirect('#')
            
        return HttpResponseRedirect('#')
    
###################  
# NEW PROJECT
###################

class NewProject(View):
    
    def post(self, request, *args, **kwargs):
        
        #site info
        my_projects = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = True)
        else_projects = Project.objects.filter(Q(projectuser__who = self.request.user) & Q(is_active = True) & Q(projectuser__isactive = True) & ~Q(projectuser__role = "Cr") &Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "B")))
        my_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "C", is_active = True, file_user_comment__is_active = True)
        else_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "X", is_active = True, file_user_comment__is_active = True)
        archive = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = False)
        projects = Project.objects.filter(Q(projectuser__who = self.request.user) & Q(is_active = True) & (Q(projectuser__role = "Aw") | Q(projectuser__role = "Cr"))).distinct()
        services = Service.objects.filter(user_service__user = self.request.user, is_active = True, user_service__role = "C", user_service__is_active = True)
        else_services = Service.objects.filter(user_service__user = self.request.user, user_service__role = "X", is_active = True, user_service__is_active = True)
        pro_archive = Project.objects.filter(Q(is_del = False) & Q(projectuser__who = self.request.user) & Q(is_active = False) & Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "Cr") | Q(projectuser__role = "B")))
        file_archive = File.objects.filter(Q(is_del = False) & Q(file_user_comment__user = self.request.user) & Q(Q(file_user_comment__role = "C") | Q(file_user_comment__role = "X")) & Q(is_active = False))
        ser_archive = Service.objects.filter(Q(is_del = False) & Q(user_service__user = self.request.user) & Q(Q(user_service__role = "C") | Q(user_service__role = "X")) & Q(is_active = False))
        
        #forms
        form = NewProjectForm(request.POST)

        #create new project
        if 'new' in request.POST and form.is_valid():
            project_t = handle_new_project(form.cleaned_data, request.user)
            stat = ProjectStatus(status = 'P', project = project_t)
            stat.save()
            usr = ProjectUser(role = 'Cr', who = request.user, project = project_t)
            usr.save()
            path = '/app/show_project/' + str(project_t.id) + "/"
            return HttpResponseRedirect(path)
            
        #create project based on existing one
        if 'not_new' in request.POST and form.is_valid():
            project_t = handle_new_project(form.cleaned_data, request.user)
            stat = ProjectStatus(status = 'P', project = project_t)
            stat.save()
            usr = ProjectUser(role = 'Cr', who = request.user, project = project_t)
            usr.save()
            project = get_object_or_404(Project, pk = request.POST.get('project_id'))
            com = "Base on " + project.name
            com = ProjectComment(comment = com, project = project_t, comment_add_by = request.user)
            com.save()
            things_stay = request.POST.getlist('stay')
            
            #attributes of the new project:
            if("plan" in things_stay):
                plans = ProjectComment.objects.filter(project = project, is_plan = True, is_active = True)
                for plan in plans:
                    new_plan = ProjectComment(comment = plan.comment, project = project_t, comment_add_by = plan.comment_add_by, is_plan = True, p_class = plan.p_class, number = plan.number)
                    new_plan.save()
                    if plan.child != None:
                        new_child = get_object_or_404(ProjectComment, project = project_t, comment = plan.child.comment)
                        new_plan.child = new_child
                        new_plan.save()
            if("analysts_write" in things_stay):
                project_user = ProjectUser.objects.filter(project = project, role = "Aw", isactive = True)
                for pu in project_user:
                    new_pu = ProjectUser(role = 'Aw', who = pu.who, who_add = pu.who_add, comment = pu.comment, project = project_t)
                    new_pu.save()
            if("analysts_read" in things_stay):
                project_user = ProjectUser.objects.filter(project = project, role = "Ar", isactive = True)
                for pu in project_user:
                    new_pu = ProjectUser(role = 'Ar', who = pu.who, who_add = pu.who_add, comment = pu.comment, project = project_t)
                    new_pu.save() 
            if("client" in things_stay):
                project_user = ProjectUser.objects.filter(project = project, role = "C", isactive = True)
                for pu in project_user:
                    new_pu = ProjectUser(role = 'C', who = pu.who, who_add = pu.who_add, comment = pu.comment, project = project_t)
                    new_pu.save()  
            if("boss" in things_stay):
                project_user = ProjectUser.objects.filter(project = project, role = "B", isactive = True)
                for pu in project_user:
                    new_pu = ProjectUser(role = 'B', who = pu.who, who_add = pu.who_add, comment = pu.comment, project = project_t)
                    new_pu.save()               
            if("fileIn" in things_stay):
                files_old = Fileproject.objects.filter(project = project, role = "In", is_active = True)
                for file_old in files_old:
                    file_new = Fileproject(role = 'In', project = project_t, file = file_old.file, user = file_old.user)
                    file_new.save()
                    tmp, ext = os.path.splitext(file_new.file.path)
                    new_Fname = str(file_new.file.id) + "_" + str(file_new.file.ad_name)
                    os.symlink(settings.BASE_DIR + file_new.file.path, os.path.join(file_new.project.path, new_Fname))
            if("fileOut" in things_stay):
                files_old = Fileproject.objects.filter(project = project, role = "Out", is_active = True)
                for file_old in files_old:
                    file_new = Fileproject(role = 'In', project = project_t, file = file_old.file, user = file_old.user)
                    file_new.save() 
                    tmp, ext = os.path.splitext(file_new.file.path)
                    new_Fname = str(file_new.file.id) + "_" + str(file_new.file.ad_name)
                    os.symlink(settings.BASE_DIR + file_new.file.path, os.path.join(file_new.project.path, new_Fname))
            if("group" in things_stay):
                groups = Groupproject.objects.filter(project = project, is_active = True)
                for group_old in groups:
                    new_gr = Groupproject(project = project_t, group = group_old.group, user = group_old.user)
                    new_gr.save()
                    files = Filegroup.objects.filter(group = group_old.group, is_active = True)
                    for fl in files:
                        try:
                            Fileproject.objects.get(role = 'In', project = project_t, file = fl.file, is_active = True)
                        except Fileproject.DoesNotExist:
                            file_new = Fileproject(role = 'In', project = project_t, file = fl.file, user = request.user)
                            file_new.save() 
                            tmp, ext = os.path.splitext(file_new.file.path)
                            new_Fname = str(file_new.file.id) + "_" + str(file_new.file.ad_name)
                            os.symlink(settings.BASE_DIR + file_new.file.path, os.path.join(file_new.project.path, new_Fname))
            if("comments" in things_stay):
                comms = ProjectComment.objects.filter(Q(project = project) & Q(is_active = True)& Q(is_plan = False) &(Q(show = True) | Q(comment_add_by = request.user)))
                for comm in comms:
                    new_comm = ProjectComment(comment = comm.comment, project = project_t, comment_add_by = comm.comment_add_by, show = comm.show)
                    new_comm.save()
            if("Service" in things_stay):
                sers = ServiceProject.objects.filter(Q(project = project) & Q(is_active = True))
                for ser in sers:
                    new_ser = ServiceProject(project = project_t, service = ser.service)
                    new_ser.save()
            if("Module" in things_stay):
                mods = Module.objects.filter(project_module__project = project, is_active = True)
                for mod in mods:
                    serv = ServiceProject.objects.filter(is_active = True, service = mod.service, project = project_t)
                    if not serv:
                        new_ser = ServiceProject(project = project_t, service = mod.service)
                        new_ser.save()
                    new_mod = ModuleProject(project = project_t, module = mod)
                    new_mod.save()
                    
            path = '/app/show_project/' + str(project_t.id) + "/"
            return HttpResponseRedirect(path)
            
        return render(request, 'app/new_project.html', {'archive':archive, 'services':services, 'my_projects': my_projects, 
            'projects':projects, 'form': form, 'else_projects':else_projects, 'my_file':my_file, 'else_file':else_file,
            'else_services':else_services, 'pro_archive':pro_archive, 'file_archive':file_archive, 'ser_archive':ser_archive})
   
    def get(self, request):
        
        #site info
        my_projects = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = True)
        else_projects = Project.objects.filter(Q(projectuser__who = self.request.user) & Q(is_active = True) & Q(projectuser__isactive = True) & ~Q(projectuser__role = "Cr") &Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "B")))
        my_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "C", is_active = True, file_user_comment__is_active = True)
        else_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "X", is_active = True, file_user_comment__is_active = True)
        archive = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = False)
        projects = Project.objects.filter(Q(projectuser__who = self.request.user) & Q(is_active = True) & (Q(projectuser__role = "Aw") | Q(projectuser__role = "Cr"))).distinct()
        services = Service.objects.filter(user_service__user = self.request.user, is_active = True, user_service__role = "C", user_service__is_active = True)
        else_services = Service.objects.filter(user_service__user = self.request.user, user_service__role = "X", is_active = True, user_service__is_active = True)
        pro_archive = Project.objects.filter(Q(is_del = False) & Q(projectuser__who = self.request.user) & Q(is_active = False) & Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "Cr") | Q(projectuser__role = "B")))
        file_archive = File.objects.filter(Q(is_del = False) & Q(file_user_comment__user = self.request.user) & Q(Q(file_user_comment__role = "C") | Q(file_user_comment__role = "X")) & Q(is_active = False))
        ser_archive = Service.objects.filter(Q(is_del = False) & Q(user_service__user = self.request.user) & Q(Q(user_service__role = "C") | Q(user_service__role = "X")) & Q(is_active = False))
        
        #forms
        form = NewProjectForm()

        return render(request, 'app/new_project.html', {'archive':archive, 'services':services, 'my_projects': my_projects, 
                'projects':projects, 'form': form, 'else_projects':else_projects, 'my_file':my_file, 'else_file':else_file,
                'else_services':else_services, 'pro_archive':pro_archive, 'file_archive':file_archive, 'ser_archive':ser_archive})

#save parameters
def save_params(param_group, obj, user):
    s = StringIO(obj)
    for line in s:
        p = line.split(";")
        par_type = p[0]
        if par_type == "N": 
            name = p[1]
            value = p[2]
            try:
                v_min = p[3]
                if v_min == "":
                    v_min = None
            except:
                v_min = None
            try:
                v_max = p[4]
                if v_max == "":
                    v_max = None
            except:
                v_max = None
            try:
                comment = p[5]
            except:
                comment = None
        elif par_type == "F" :
            name = p[1]
            try:
                value = p[2]
            except:
                name = "*"
            try:
                comment = p[3]
            except:
                comment = None
            v_min = None
            v_max = None
        elif par_type == "O":
            name = p[1]
            try:
                value = p[2]
            except:
                name = None
            try:
                comment = p[3]
            except:
                comment = None
            v_min = None
            v_max = None
        else:
            par_type = "O"
            name = p[1]
            try:
                value = p[2]
            except:
                name = None
            try:
                comment = p[3]
            except:
                comment = None
            v_min = None
            v_max = None 
        param = Param(par_type = par_type, name = name, v_min = v_min, v_max = v_max, value = value, comment = comment, user = user)
        param.save()
        param_group.params.add(param)
        param_group.save()
        
###################  
# NEW SERVICE
###################
 
class NewService(View):
    def post(self, request, *args, **kwargs):
        
        #form
        service_name = ServiceForm(request.POST)
        in_type = InType(request.POST)
        out_type = OutType(request.POST)
        params = Params(request.POST)
        
        #create new service
        if service_name.is_valid():
            service = service_name.save(commit=False)
            service_name = service.name
            service.save()
            creator = ServiceUser(role = 'C', service = service, user = request.user, who_add = request.user)
            creator.save()
            #create service folder
            service_nm = service.name + "_" + str(service.id)
            dir = os.path.join('app/static', service_nm ,"")
            os.mkdir(dir)
            
            #add file type
            if in_type.is_valid():
                obj = in_type.cleaned_data['obj_in']
                for i in obj.split(" "):
                    in_f = Format(name = i, user = request.user)
                    in_f.save()
                    service.in_format.add(in_f)
                    service.save()
            if out_type.is_valid():
                obj = out_type.cleaned_data['obj_out']
                for o in obj.split(" "):
                    out_f = Format(name = o, user = request.user)
                    out_f.save()
                    service.out_format.add(out_f)
                    service.save()
            #add parameters
            if params.is_valid():
                param_name = service_name + "_default"
                param_group = ParamGroup(name = param_name, user = request.user)
                param_group.save()
                obj = params.cleaned_data['obj_param']
                save_params(param_group, obj, request.user)
                service.default.add(param_group)
                service.save()
                red = "/app/new_service_2/" + str(service.id) + "/"
                return HttpResponseRedirect(red)
            else:
                service_name = ServiceForm()
        
        #site info
        my_projects = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = True)
        else_projects = Project.objects.filter(Q(projectuser__who = self.request.user) & Q(is_active = True) & Q(projectuser__isactive = True) & ~Q(projectuser__role = "Cr") &Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "B")))
        my_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "C", is_active = True, file_user_comment__is_active = True)
        else_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "X", is_active = True, file_user_comment__is_active = True)
        archive = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = False)
        projects = Project.objects.filter(Q(projectuser__who = self.request.user) & (Q(projectuser__role = "Aw") | Q(projectuser__role = "Cr"))).distinct()
        services = Service.objects.filter(user_service__user = self.request.user, is_active = True, user_service__role = "C", user_service__is_active = True)
        else_services = Service.objects.filter(user_service__user = self.request.user, user_service__role = "X", is_active = True, user_service__is_active = True)
        pro_archive = Project.objects.filter(Q(is_del = False) & Q(projectuser__who = self.request.user) & Q(is_active = False) & Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "Cr") | Q(projectuser__role = "B")))
        file_archive = File.objects.filter(Q(is_del = False) & Q(file_user_comment__user = self.request.user) & Q(Q(file_user_comment__role = "C") | Q(file_user_comment__role = "X")) & Q(is_active = False))
        ser_archive = Service.objects.filter(Q(is_del = False) & Q(user_service__user = self.request.user) & Q(Q(user_service__role = "C") | Q(user_service__role = "X")) & Q(is_active = False))
        
        return render(request, 'app/new_service.html', {'archive':archive, 'params':params, 'out_type':out_type, 'in_type':in_type, 
                'services':services, 'my_projects': my_projects, 'projects':projects, 'service_name' : service_name, 'else_projects':else_projects,
                'my_file':my_file, 'else_file':else_file, 'else_services':else_services, 'pro_archive':pro_archive, 'file_archive':file_archive,
                'ser_archive':ser_archive})
   
    def get(self, request, *args, **kwargs):
        
        #site info
        my_projects = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = True)
        else_projects = Project.objects.filter(Q(projectuser__who = self.request.user) & Q(is_active = True) & Q(projectuser__isactive = True) & ~Q(projectuser__role = "Cr") &Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "B")))
        my_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "C", is_active = True, file_user_comment__is_active = True)
        else_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "X", is_active = True, file_user_comment__is_active = True)
        archive = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = False)
        projects = Project.objects.filter(Q(projectuser__who = self.request.user) & (Q(projectuser__role = "Aw") | Q(projectuser__role = "Cr"))).distinct()
        services = Service.objects.filter(user_service__user = self.request.user, is_active = True, user_service__role = "C", user_service__is_active = True)
        else_services = Service.objects.filter(user_service__user = self.request.user, user_service__role = "X", is_active = True, user_service__is_active = True)
        pro_archive = Project.objects.filter(Q(is_del = False) & Q(projectuser__who = self.request.user) & Q(is_active = False) & Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "Cr") | Q(projectuser__role = "B")))
        file_archive = File.objects.filter(Q(is_del = False) & Q(file_user_comment__user = self.request.user) & Q(Q(file_user_comment__role = "C") | Q(file_user_comment__role = "X")) & Q(is_active = False))
        ser_archive = Service.objects.filter(Q(is_del = False) & Q(user_service__user = self.request.user) & Q(Q(user_service__role = "C") | Q(user_service__role = "X")) & Q(is_active = False))
        
        #forms
        in_type = InType()
        out_type = OutType()
        params = Params()
        service_name = ServiceForm()

        return render(request, 'app/new_service.html', {'archive':archive, 'params':params, 'out_type':out_type, 'in_type':in_type, 
                'services':services, 'my_projects': my_projects, 'projects':projects, 'service_name' : service_name, 'else_projects':else_projects,
                'my_file':my_file, 'else_file':else_file, 'else_services':else_services, 'pro_archive':pro_archive, 'file_archive':file_archive,
                'ser_archive':ser_archive})

class NewService2(View):
    
    def post(self, request, service_id, *args, **kwargs):
        service = get_object_or_404(Service, pk = service_id)
        
        #form
        form_file = UploadFileForm2(request.POST, request.FILES)

        #upload code
        if form_file.is_valid():
            file = form_file.save()
            red_url = "/app/show_service/" + service.name
            files = [serialize_red(file, red_url)]
            data = {'files': files}
            response = JSONResponse(data, mimetype=response_mimetype(request))
            response['Content-Disposition'] = 'inline; filename=files.json'
            creator = FileUser(file = file, user = request.user, who_add = request.user, role = "C")
            creator.save()

            #update repo
            init = request.POST.get("is_init", False)
            if init == "False":
                init = False
            new_repo(file, service, request.user, file.cl_name, init)
        red = "/app/show_service/" + str(service.id)
        return redirect(red)
   
    def get(self, request, service_id, *args, **kwargs):
        
        #site info
        my_projects = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = True)
        else_projects = Project.objects.filter(Q(projectuser__who = self.request.user) & Q(is_active = True) & Q(projectuser__isactive = True) & ~Q(projectuser__role = "Cr") &Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "B")))
        my_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "C", is_active = True, file_user_comment__is_active = True)
        else_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "X", is_active = True, file_user_comment__is_active = True)
        archive = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = False)
        projects = Project.objects.filter(Q(projectuser__who = self.request.user) & (Q(projectuser__role = "Aw") | Q(projectuser__role = "Cr"))).distinct()
        services = Service.objects.filter(user_service__user = self.request.user, is_active = True, user_service__role = "C", user_service__is_active = True)
        else_services = Service.objects.filter(user_service__user = self.request.user, user_service__role = "X", is_active = True, user_service__is_active = True)
        pro_archive = Project.objects.filter(Q(is_del = False) & Q(projectuser__who = self.request.user) & Q(is_active = False) & Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "Cr") | Q(projectuser__role = "B")))
        file_archive = File.objects.filter(Q(is_del = False) & Q(file_user_comment__user = self.request.user) & Q(Q(file_user_comment__role = "C") | Q(file_user_comment__role = "X")) & Q(is_active = False))
        ser_archive = Service.objects.filter(Q(is_del = False) & Q(user_service__user = self.request.user) & Q(Q(user_service__role = "C") | Q(user_service__role = "X")) & Q(is_active = False))
        service = get_object_or_404(Service, pk = service_id)
        service_name = service.name
        
        #form
        form_file = UploadFileForm2()

        return render(request, 'app/new_service2.html', {'archive':archive, 'service_name':service_name, 'services':services, 
                'form_file':form_file, 'my_projects': my_projects, 'projects':projects, 'else_projects':else_projects,
                'my_file':my_file, 'else_file':else_file, 'else_services':else_services, 'pro_archive':pro_archive,
                'file_archive':file_archive, 'ser_archive':ser_archive})

###################  
# FILE
###################

class FileView(View):
    
    def post(self, request, file_id, *args, **kwargs):
        file = get_object_or_404(File, pk = file_id)
        
        #forms
        new_comment = FileCommentForm(request.POST)
        edited_comm = ProjectEditCommForm(request.POST)
        fileform = FileDictForm(request.POST)
        file_name_form = NameFileForm(request.POST, instance = file)
        
        #formset
        LinkFormSet = formset_factory(FileUserForm, formset=BaseLinkFormSet2)
        intersect = User.objects.filter(~Q(Q(file_user__file = file) & Q(Q(file_user__role = "X") | Q(file_user__role = "C")) & Q(file_user__is_active = True)))
        link_formset = LinkFormSet(request.POST, form_kwargs={'queryset':intersect})
    
        #delete file
        if 'del_file' in request.POST:
            file.is_active = False
            file.is_del = True
            file.save()
            #delete permissions
            f_user = FileUser.objects.filter(file = file)
            for f in f_user:
                is_active = False
                f.save()
            #delete comments
            f_comm = FileComment.objects.filter(file = file)
            if f_comm:
                for f in f_comm:
                    is_active = False
                    f.save()
            #unlink from project folders
            f_pro = Fileproject.objects.filter(file = file)
            if f_pro:    
                for f in f_pro:
                    is_active = False
                    f.save()
                    new_Fname = str(file.id) + "_" + str(file.ad_name)
                    os.unlink(os.path.join(f.project.path, new_Fname))
            f_code = FileCode.objects.filter(file = file)
            #delete code
            if f_code:
                for f in f_code:
                    is_active = False
                    f.save()
            #delete from hard drive
            os.remove(settings.BASE_DIR + file.file.url)
            return redirect('/app/my_site')
            
        #archive file
        if 'arch_file' in request.POST:
            file.is_active = False
            file.save()
            return redirect('/app/archive/file/' + str(file.id)) 
            
        #change additional file name
        if 'change_name' in request.POST and file_name_form.is_valid():
            file_update = file_name_form.save()
            return HttpResponseRedirect('#')
        
        #add file to new project
        if "add_to_project" in request.POST:
            project = get_object_or_404(Project, pk = request.POST.get('project_id'))
            fileproject = Fileproject(role = 'In', project = project, file = file, user = request.user)
            fileproject.save()
            new_Fname = str(file.id) + "_" + str(file.ad_name)
            #add symlink to project folder
            os.symlink(settings.BASE_DIR + file.file.url, os.path.join(project.path, new_Fname))
            return HttpResponseRedirect(reverse('file_view', kwargs={'file_id':file.id, 'label': 'Projects'}))
            
        #share file
        if 'share' in request.POST and link_formset.is_valid():
            for link_form in link_formset:
                guest = link_form.save(commit=False)
                guest.role = "X"
                guest.file = file
                guest.who_add = request.user
                guest.save()
                return HttpResponseRedirect(reverse('file_view', kwargs={'file_id':file.id, 'label': 'Share'}))
        
        #add new comment
        if new_comment.is_valid() and 'add_comment' in request.POST:
            comment = new_comment.save(commit=False)
            comment.file = file
            comment.user = request.user
            comment.save()
            return HttpResponseRedirect(reverse('file_view', kwargs={'file_id':file.id, 'label': 'Comments'}))
        
        #edit file comments
        if 'edit_pro_comm' in request.POST and edited_comm.is_valid():
            comment = edited_comm.save(commit=False)
            old_id = request.POST.get('edit_pro_comm', False)
            old_comm = get_object_or_404(FileComment, pk = old_id)
            old_comm.is_active = False
            old_comm.save()
            new_comm = FileComment(comment = comment.comment, file = old_comm.file, user = request.user, show = old_comm.show)
            new_comm.save()
            return HttpResponseRedirect(reverse('file_view', kwargs={'file_id':file.id, 'label': 'Comments'}))
            
        '''
        if  'add_ext' in request.POST and fileform.is_valid():
            ext = fileform.save(commit=False)
            ext.file = file
            ext.user = request.user
            ext.save()
            return HttpResponseRedirect('#')
        if "add_to_group" in request.POST:
            group = get_object_or_404(Group, name = request.POST.get('group_name'))
            filegroup = Filegroup(group = group, file = file, user = request.user)
            filegroup.save()
            return HttpResponseRedirect('#')
        '''
            
        #site info
        can_use = FileUser.objects.filter(file = file, role = "X", is_active = True)
        services = Service.objects.filter(user_service__user = self.request.user, is_active = True, user_service__role = "C", user_service__is_active = True)
        my_projects = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = True)
        else_projects = Project.objects.filter(Q(projectuser__who = self.request.user) & Q(is_active = True) & Q(projectuser__isactive = True) & ~Q(projectuser__role = "Cr") &Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "B")))
        my_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "C", is_active = True, file_user_comment__is_active = True)
        else_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "X", is_active = True, file_user_comment__is_active = True)
        else_services = Service.objects.filter(user_service__user = self.request.user, user_service__role = "X", is_active = True, user_service__is_active = True)
        creator = get_object_or_404(User, file_user__role = 'C', file_user__file = file)
        pro_archive = Project.objects.filter(Q(is_del = False) & Q(projectuser__who = self.request.user) & Q(is_active = False) & Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "Cr") | Q(projectuser__role = "B")))
        file_archive = File.objects.filter(Q(is_del = False) & Q(file_user_comment__user = self.request.user) & Q(Q(file_user_comment__role = "C") | Q(file_user_comment__role = "X")) & Q(is_active = False))
        ser_archive = Service.objects.filter(Q(is_del = False) & Q(user_service__user = self.request.user) & Q(Q(user_service__role = "C") | Q(user_service__role = "X")) & Q(is_active = False))
        file_projects = Fileproject.objects.filter(file = file, user = self.request.user, is_active = True).distinct()
        n_pro = file_projects.count()
        comments = FileComment.objects.filter(Q(file = file) & Q(is_active = True) & (Q(user =  self.request.user) | Q(show = True)))
        project_files = Project.objects.filter(Q(is_active=True) & (~Q(project_file__file = file) | (Q(project_file__file = file) & Q(project_file__is_active = False))) & Q( Q(projectuser__who = self.request.user) & (Q(projectuser__role = "Aw") | Q(projectuser__role = "Cr")))).distinct()
        
        #formset
        LinkFormSet = formset_factory(FileUserForm, formset=BaseLinkFormSet2)
        intersect = User.objects.filter(~Q(Q(file_user__file = file) & Q(Q(file_user__role = "X") | Q(file_user__role = "C")) & Q(file_user__is_active = True)))
        link_formset = LinkFormSet(form_kwargs={'queryset':intersect})
        
        return render(request, 'app/file_view.html', {'project_files': project_files, 'fileform' : fileform, 
                'new_comment':new_comment, 'comments': comments, 'file_projects':file_projects, 'can_use' : can_use, 'creator' : creator, 
                'services':services, 'link_formset' : link_formset, 'file' : file,
                'n_pro':n_pro, 'my_projects':my_projects, 'else_projects':else_projects, 'my_file':my_file, 'else_file':else_file,
                'file_name_form':file_name_form, 'else_services':else_services, 'pro_archive':pro_archive, 'file_archive':file_archive,
                'ser_archive':ser_archive})
   
        
    def get(self, request, file_id, *args, **kwargs):
        
        file = get_object_or_404(File, pk = file_id)
        try:
            #remove user
            if(request.GET['command'] == "remove"):
                remove_user = get_object_or_404(FileUser, file = file, id = request.GET.get('userfile_id'))
                remove_user.is_active = False
                remove_user.save()
                return HttpResponse()
            #show comment
            if(request.GET['command'] == "show"):
                update_com = get_object_or_404(FileComment, pk = request.GET.get('com_id'))
                update_com.show = True
                update_com.save()
                return HttpResponse()
            #hide comment
            if(request.GET['command'] == "hide"):
                update_com = get_object_or_404(FileComment, pk = request.GET.get('com_id'))
                update_com.show = False
                update_com.save()
                return HttpResponse()
            #remove comment
            if(request.GET['command'] == "removebutton"):
                update_com = get_object_or_404(FileComment, pk = request.GET.get('com_id'))
                update_com.is_active = False
                update_com.save()
                return HttpResponse()
            #remove from project
            if(request.GET['command'] == "removeproject"):
                update_com = get_object_or_404(Fileproject,  pk = request.GET.get('project_id'))
                update_com.is_active = False
                update_com.save()
                new_Fname = str(file.id) + "_" + str(file.ad_name)
                os.unlink(os.path.join(update_com.project.path, new_Fname))
                return HttpResponse()
            '''
            if(request.GET['command'] == "removegroup"):
                gr = get_object_or_404(Group, name = request.GET.get('group_id'))
                update_com = get_object_or_404(Filegroup, group = gr, file = file)
                update_com.is_active = False;
                update_com.save()
                return HttpResponse()
            if(request.GET['command'] == "removeext"):
                update_com = get_object_or_404(FileDict, pk = request.GET.get('ext_id'))
                update_com.is_active = False;
                update_com.save()
                return HttpResponse()
            '''
        except:
            pass 
        
        #site info
        can_use = FileUser.objects.filter(file = file, role = "X", is_active = True)
        services = Service.objects.filter(user_service__user = self.request.user, is_active = True, user_service__role = "C", user_service__is_active = True)
        my_projects = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = True)
        else_projects = Project.objects.filter(Q(projectuser__who = self.request.user) & Q(is_active = True) & Q(projectuser__isactive = True) & ~Q(projectuser__role = "Cr") &Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "B")))
        my_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "C", is_active = True, file_user_comment__is_active = True)
        else_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "X", is_active = True, file_user_comment__is_active = True)
        else_services = Service.objects.filter(user_service__user = self.request.user, user_service__role = "X", is_active = True, user_service__is_active = True)
        creator = get_object_or_404(User, file_user__role = 'C', file_user__file = file)
        pro_archive = Project.objects.filter(Q(is_del = False) & Q(projectuser__who = self.request.user) & Q(is_active = False) & Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "Cr") | Q(projectuser__role = "B")))
        file_archive = File.objects.filter(Q(is_del = False) & Q(file_user_comment__user = self.request.user) & Q(Q(file_user_comment__role = "C") | Q(file_user_comment__role = "X")) & Q(is_active = False))
        ser_archive = Service.objects.filter(Q(is_del = False) & Q(user_service__user = self.request.user) & Q(Q(user_service__role = "C") | Q(user_service__role = "X")) & Q(is_active = False))
        file_projects = Fileproject.objects.filter(file = file, user = self.request.user, is_active = True).distinct()
        n_pro = file_projects.count()
        comments = FileComment.objects.filter(Q(file = file) & Q(is_active = True) & (Q(user =  self.request.user) | Q(show = True)))
        project_files = Project.objects.filter(Q(is_active=True) & (~Q(project_file__file = file) | (Q(project_file__file = file) & Q(project_file__is_active = False))) & Q( Q(projectuser__who = self.request.user) & (Q(projectuser__role = "Aw") | Q(projectuser__role = "Cr")))).distinct()
        
        '''
        group_files = Group.objects.filter((~Q(group_file__file = file) | (Q(group_file__file = file) & Q(group_file__is_active = False))) & Q( Q(user_group__user = self.request.user) & (Q(user_group__is_active = True)))).distinct()
        groups = Group.objects.filter(Q(group_file__is_active = True) & Q(group_file__file = file) & (Q(user_group__user = self.request.user) & Q(user_group__is_active = True)))
        exts = FileDict.objects.filter(file = file, is_active = True)
        '''
        
        #form
        file_name_form = NameFileForm(instance = file)
        fileform = FileDictForm()
        new_comment = FileCommentForm()
        
        #formset
        LinkFormSet = formset_factory(FileUserForm, formset=BaseLinkFormSet2)
        intersect = User.objects.filter(~Q(Q(file_user__file = file) & Q(file_user__is_active = True)))
        link_formset = LinkFormSet(form_kwargs={'queryset':intersect})
        
        #archived file
        if file.is_active == False:
                return render(request, 'app/arch_file.html',{'project_files': project_files, 'comments': comments, 'file_projects':file_projects, 
                        'can_use' : can_use, 'creator' : creator, 'services':services, 'file' : file, 'n_pro':n_pro, 'my_projects':my_projects, 
                        'else_projects':else_projects, 'my_file':my_file, 'else_file':else_file, 'else_services':else_services, 
                        'pro_archive':pro_archive, 'file_archive':file_archive, 'ser_archive':ser_archive})
        
            
        return render(request, 'app/file_view.html', {'project_files': project_files, 'fileform' : fileform, 
                'new_comment':new_comment, 'comments': comments, 'file_projects':file_projects, 'can_use' : can_use, 'creator' : creator, 
                'services':services, 'link_formset' : link_formset, 'file' : file,
                'n_pro':n_pro, 'my_projects':my_projects, 'else_projects':else_projects, 'my_file':my_file, 'else_file':else_file,
                'file_name_form':file_name_form, 'else_services':else_services, 'pro_archive':pro_archive, 'file_archive':file_archive,
                'ser_archive':ser_archive})


###################  
# SERVICE
###################
  
class ServiceView(View):
    
    def post(self, request, service_id, *args, **kwargs):
        service = get_object_or_404(Service, pk = service_id)
        
        #forms
        comm = ServiceCommForm(request.POST)
        in_type = InTypeSmall(request.POST)
        out_type = OutTypeSmall(request.POST)
        params = Params(request.POST)
        para_comm = ParamCommForm(request.POST)
        param_from = ParamForm(request.POST)
        new_params = Params(request.POST)
        new_group = ParamGroupNameForm(request.POST)
        edit_init = TextForm(request.POST)
        commit = CommitForm(request.POST)
        form_file = UploadFileForm2(request.POST, request.FILES)
        
        #formset
        LinkFormSet = formset_factory(ServiceUserForm, formset=BaseLinkFormSet2)
        intersect = User.objects.filter(~Q(Q(service_user__service = service) & Q(Q(service_user__role = "X") | Q(service_user__role = "C")) & Q(service_user__is_active = True)))
        link_formset = LinkFormSet(request.POST, form_kwargs={'queryset':intersect})
         
        #share service
        if 'share' in request.POST and link_formset.is_valid():
            for link_form in link_formset:
                guest = link_form.save(commit=False)
                guest.role = "X"
                guest.service = service
                guest.who_add = request.user
                guest.save()
            return HttpResponseRedirect(reverse('service_view', kwargs={'service_id':service.id, 'label': 'Share'}))
        
        #archive service
        if 'arch_ser' in request.POST:
            service.is_active = False
            service.save()
            return redirect('/app/archive/service/' + str(service.id)) 
            
        #delete service
        if 'del_ser' in request.POST:
            service.is_active = False
            service.is_del = True
            service.save()
            #delete permissions
            s_user = ServiceUser.objects.filter(service = service)
            if s_user:
                for s in s_user:
                    s.is_active = False
                    s.save()
            #delete comments
            s_com = ServiceComment.objects.filter(service = service)
            if s_com:
                for s in s_com:
                    s.is_active = False
                    s.save()
            #delete from projects
            s_pro = ServiceProject.objects.filter(service = service)
            if s_pro:
                for s in s_pro:
                    s.is_active = False
                    s.save()
            #delete file format
            s_for = Format.objects.filter(service_in_format = service)
            if s_for:
                for s in s_for:
                    s.is_active = False
                    s.save()
            s_for = Format.objects.filter(service_out_format = service)
            if s_for:
                for s in s_for:
                    s.is_active = False
                    s.save()
            #delete parameters
            s_par = ParamGroup.objects.filter(service_params = service)
            if s_par:
                for s in s_par:
                    s.is_active = False
                    s.save()
            #remove service folder and repo
            service_nm = service.name + "_" + str(service.id)
            shutil.rmtree(settings.BASE_DIR + "/app/static/" + service_nm)
            shutil.rmtree(settings.BASE_DIR + "/app/static/repo/" + service_nm)
            #delete code 
            s_cod = FileCode.objects.filter(service_code = service)
            if s_cod:
                for s in s_cod:
                    s.is_active = False
                    s.save()
                    fl = get_object_or_404(File,file_code = s)
                    fl.is_active = False
                    fl.save()
                    #remove from hard drive
                    os.remove(settings.BASE_DIR + fl.file.url)
            #delete init script
            s_init = FileCode.objects.filter(service_init = service)
            if s_init:
                for s in s_init:
                    s.is_active = False
                    s.save()                    
                    fl = get_object_or_404(File,file_code = s)
                    fl.is_active = False
                    fl.save()
                    #remove from hard drive
                    os.remove(settings.BASE_DIR + fl.file.url)
            return redirect('/app/my_site')
            
        #add service desription
        if 'add_comment' in request.POST and comm.is_valid():
            new_comm = comm.save(commit=False)
            new_comm.service = service
            new_comm.user = self.request.user
            new_comm.save()
            return HttpResponseRedirect('#')
        
        #add new group of parameters
        if  'new_group' in request.POST and new_params.is_valid() and new_group.is_valid():
            new_group = new_group.save(commit=False)
            new_group.user = self.request.user
            new_group.save()
            obj = new_params.cleaned_data['obj_param']
            save_params(new_group, obj, request.user)
            service.default.add(new_group)
            service.save()
            return HttpResponseRedirect(reverse('service_view', kwargs={'service_id':service.id, 'label': 'Parameters'}))
        
        #add new parameter    
        if  'new_params' in request.POST and new_params.is_valid():
            param_group_id = request.POST.get('new_params', False)
            param_group = get_object_or_404(ParamGroup, pk = param_group_id)
            obj = new_params.cleaned_data['obj_param']
            save_params(param_group, obj, request.user)
            return HttpResponseRedirect(reverse('service_view', kwargs={'service_id':service.id, 'label': 'Parameters'}))

        #edit parameter
        if 'edit_param' in request.POST and param_from.is_valid():
            new_param = param_from.save(commit=False)
            old_id = request.POST.get('edit_param', False)
            old_param = get_object_or_404(Param, pk = old_id)
            old_param.is_active = False
            old_param.save()
            param_group_id = request.POST.get('group', False)
            param_group = get_object_or_404(ParamGroup, pk = param_group_id)
            new_param.user = self.request.user
            new_param.par_type = old_param.par_type
            new_param.save()
            param_group.params.add(new_param)
            param_group.save()
            return HttpResponseRedirect(reverse('service_view', kwargs={'service_id':service.id, 'label': 'Parameters'}))
        
        #add description to group    
        if 'new_format_comm' in request.POST and para_comm.is_valid():
            param_group_id = request.POST.get('group', False)
            param_group = get_object_or_404(ParamGroup, pk = param_group_id)
            new_comm = para_comm.save(commit=False)
            new_comm.params = param_group
            new_comm.user = self.request.user
            new_comm.save()
            return HttpResponseRedirect(reverse('service_view', kwargs={'service_id':service.id, 'label': 'Parameters'}))
            
        #edit code
        if 'edit_init' in request.POST and edit_init.is_valid():
            init_id = request.POST.get('edit_init', False)
            init = get_object_or_404(FileCode, pk = init_id)
            text = edit_init.cleaned_data['text']
            text = text.replace("\r\n", "\n")
            ext = File.objects.filter(file_code__name = init.name)
            ext = ext[0].ext
            file = File()
            nr = init.file.count()
            code_name_part = "v" + str(nr + 1)
            code_name = init.name
            file.file.save(code_name, ContentFile(text))
            file.user_name = code_name_part
            file.save()
            creator = FileUser(file = file, user = request.user, who_add = request.user, role = "C")
            creator.save()
            if commit.is_valid():
                comment = commit.cleaned_data['commit']
            else:
                name = init.name
                nr = init.file.count()
                comment = name + "_" + str(nr + 1)
            com = FileComment(file=file, user = request.user, comment = comment)
            com.save()
            update_code(service, file, init, text, comment)
            return HttpResponseRedirect(reverse('service_view', kwargs={'service_id':service.id, 'label': 'Init'}))
            
        #new code - send
        if form_file.is_valid():
            service = get_object_or_404(Service, pk = service_id)
            file = form_file.save()
            red_url = "/app/show_service/" + str(service.id)
            files = [serialize_red(file, red_url)]
            data = {'files': files}
            response = JSONResponse(data, mimetype=response_mimetype(request))
            response['Content-Disposition'] = 'inline; filename=files.json'

            creator = FileUser(file = file, user = request.user, who_add = request.user, role = "C")
            creator.save()
            is_init = request.POST.get('is_init', False)
            if is_init == "False":
                is_init = False
            else:
                is_init = True
            new_repo(file, service, self.request.user, file.cl_name, is_init)
            red = "/app/show_service/" + str(service.id)
            response.status_code = 278
            return redirect(red)
        
        #new code - paste
        if 'is_init' in request.POST and edit_init.is_valid() and commit.is_valid():
            new_name = commit.cleaned_data['commit']
            text = edit_init.cleaned_data['text']
            text.replace("\r\n", "\n")
            #create file
            file = File()
            file.file.save(new_name, ContentFile(text))
            file.save()
            creator = FileUser(file = file, user = request.user, who_add = request.user, role = "C")
            creator.save()
            if 'new_code' in request.POST:
                is_init = False
                label = "Code"
            else:
                is_init = True
                label = "Init"
            new_repo(file, service, self.request.user, new_name, is_init)
            return HttpResponseRedirect(reverse('service_view', kwargs={'service_id':service.id, 'label': label}))
            
        '''
        if in_type.is_valid():
            obj = in_type.cleaned_data['obj_in_s']
            for i in obj.split(" "):
                in_f = Format(name = i, user = request.user)
                in_f.save()
                service.in_format.add(in_f)
                service.save()
        if out_type.is_valid():
            obj = out_type.cleaned_data['obj_out_s']
            for o in obj.split(" "):
                out_f = Format(name = o, user = request.user)
                out_f.save()
                service.out_format.add(out_f)
                service.save()
        '''
        
        #site info
        service = get_object_or_404(Service, pk = service_id)
        services = Service.objects.filter(user_service__user = self.request.user, is_active = True, user_service__role = "C", user_service__is_active = True)
        else_services = Service.objects.filter(user_service__user = self.request.user, user_service__role = "X", is_active = True, user_service__is_active = True)
        my_projects = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = True)
        else_projects = Project.objects.filter(Q(projectuser__who = self.request.user) & Q(is_active = True) & Q(projectuser__isactive = True) & ~Q(projectuser__role = "Cr") &Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "B")))
        my_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "C", is_active = True, file_user_comment__is_active = True)
        else_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "X", is_active = True, file_user_comment__is_active = True)
        archive = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = False)
        projects = Project.objects.filter(Q(projectuser__who = self.request.user) & (Q(projectuser__role = "Aw") | Q(projectuser__role = "Cr"))).distinct()
        creator = get_object_or_404(User, service_user__role = 'C', service_user__service = service)
        in_format = Format.objects.filter(service_in_format = service, is_active=True)
        out_format = Format.objects.filter(service_out_format = service, is_active=True)
        can_use = ServiceUser.objects.filter(service = service, role = "X", is_active = True)
        pro_archive = Project.objects.filter(Q(is_del = False) & Q(projectuser__who = self.request.user) & Q(is_active = False) & Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "Cr") | Q(projectuser__role = "B")))
        file_archive = File.objects.filter(Q(is_del = False) & Q(file_user_comment__user = self.request.user) & Q(Q(file_user_comment__role = "C") | Q(file_user_comment__role = "X")) & Q(is_active = False))
        ser_archive = Service.objects.filter(Q(is_del = False) & Q(user_service__user = self.request.user) & Q(Q(user_service__role = "C") | Q(user_service__role = "X")) & Q(is_active = False))
        init = FileCode.objects.filter(service_init = service, is_active=True)
        code = FileCode.objects.filter(service_code = service, is_active=True)
        params = ParamGroup.objects.filter(service_params = service, is_active=True)
        try:
            old_comm = ServiceComment.objects.filter(service = service).values('service').annotate(max_id=Max('id'))
            comm_id = old_comm[0]['max_id']
            old_comm = ServiceComment.objects.get(pk = comm_id)
        except:
            old_comm = ""
            
        #formset
        LinkFormSet = formset_factory(ServiceUserForm, formset=BaseLinkFormSet2)
        intersect = User.objects.filter(~Q(Q(service_user__service = service) & Q(Q(service_user__role = "X") | Q(service_user__role = "C")) & Q(service_user__is_active = True)))
        link_formset = LinkFormSet(form_kwargs={'queryset':intersect})
        
        return render(request, 'app/show_service.html', {'init_name':commit, 'new_init':edit_init, 'commit':commit, 'init':init, 
                                'new_params' : new_params, 'services':services, 'services':services, 'group_name':new_group,
                                'params' : params, 'out_type':out_type, 'in_type':in_type, 'out_format':out_format, 'in_format':in_format,
                                'old_comm':old_comm, 'comm':comm, 'creator':creator, 'service':service, 'can_use':can_use,
                                'my_projects': my_projects, 'projects':projects, 'code':code, 'archive':archive, 'else_projects':else_projects,
                                'my_file':my_file, 'else_file':else_file, 'link_formset':link_formset, 'else_services':else_services,
                                'pro_archive':pro_archive, 'file_archive':file_archive, 'ser_archive':ser_archive})
                                
        

    def get(self, request, service_id, *args, **kwargs):
        
        #site info
        service = get_object_or_404(Service, pk = service_id)
        services = Service.objects.filter(user_service__user = self.request.user, is_active = True, user_service__role = "C", user_service__is_active = True)
        else_services = Service.objects.filter(user_service__user = self.request.user, user_service__role = "X", is_active = True, user_service__is_active = True)
        my_projects = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = True)
        else_projects = Project.objects.filter(Q(projectuser__who = self.request.user) & Q(is_active = True) & Q(projectuser__isactive = True) & ~Q(projectuser__role = "Cr") &Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "B")))
        my_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "C", is_active = True, file_user_comment__is_active = True)
        else_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "X", is_active = True, file_user_comment__is_active = True)
        archive = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = False)
        projects = Project.objects.filter(Q(projectuser__who = self.request.user) & (Q(projectuser__role = "Aw") | Q(projectuser__role = "Cr"))).distinct()
        creator = get_object_or_404(User, service_user__role = 'C', service_user__service = service)
        in_format = Format.objects.filter(service_in_format = service, is_active=True)
        out_format = Format.objects.filter(service_out_format = service, is_active=True)
        can_use = ServiceUser.objects.filter(service = service, role = "X", is_active = True)
        pro_archive = Project.objects.filter(Q(is_del = False) & Q(projectuser__who = self.request.user) & Q(is_active = False) & Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "Cr") | Q(projectuser__role = "B")))
        file_archive = File.objects.filter(Q(is_del = False) & Q(file_user_comment__user = self.request.user) & Q(Q(file_user_comment__role = "C") | Q(file_user_comment__role = "X")) & Q(is_active = False))
        ser_archive = Service.objects.filter(Q(is_del = False) & Q(user_service__user = self.request.user) & Q(Q(user_service__role = "C") | Q(user_service__role = "X")) & Q(is_active = False))
        init = FileCode.objects.filter(service_init = service, is_active=True)
        code = FileCode.objects.filter(service_code = service, is_active=True)
        params = ParamGroup.objects.filter(service_params = service, is_active=True)
        old_comm = ""
        
        try:
            #remove user permission
            if(request.GET['command'] == "remove_share"):
                remove_user = get_object_or_404(ServiceUser, pk = request.GET.get('userser_id'))
                remove_user.is_active = False;
                remove_user.save()
                return HttpResponse()
            #remove input format
            if(request.GET['command'] == "remove"):
                update_format = get_object_or_404(Format, pk = request.GET.get('com_id'))
                update_format.is_active = False;
                update_format.save()
                return HttpResponse()
            #remove group of parameters
            if(request.GET['command'] == "remove_group"):
                update_group = get_object_or_404(ParamGroup, pk = request.GET.get('pargr_id'))
                update_group.is_active = False;
                update_group.save()
                return HttpResponse()
            #remove parameter
            if(request.GET['command'] == "remove_param"):
                update_param = get_object_or_404(Param, pk = request.GET.get('par_id'))
                update_param.is_active = False;
                update_param.save()
                return HttpResponse()
            #remove code
            if(request.GET['command'] == "remove_init"):
                update_init = get_object_or_404(FileCode, pk = request.GET.get('init_id'))
                update_init.is_active = False
                update_init.save()
                for f in update_init.file:
                    f.is_active = False
                    f.save()
                return HttpResponse()            
        except:
            pass

        #archived service
        if service.is_active == False:
            return render(request, 'app/arch_service.html', {'init':init, 'services':services, 'params' : params, 'out_format':out_format, 
                                    'in_format':in_format, 'old_comm':old_comm, 'creator':creator, 'service':service, 'can_use':can_use,
                                    'my_projects': my_projects, 'projects':projects, 'code':code, 'archive':archive, 'else_projects':else_projects,
                                    'my_file':my_file, 'else_file':else_file, 'else_services':else_services,
                                    'pro_archive':pro_archive, 'file_archive':file_archive, 'ser_archive':ser_archive})
            
        #forms
        in_type = InTypeSmall()
        out_type = OutTypeSmall()
        group_name = ParamGroupNameForm()
        commit = CommitForm()
        new_init = TextForm()
        init_name = CommitForm()
        new_params = Params()
        try:
            old_comm = ServiceComment.objects.filter(service = service).values('service').annotate(max_id=Max('id'))
            comm_id = old_comm[0]['max_id']
            old_comm = ServiceComment.objects.get(pk = comm_id)
            comm = ServiceCommForm(instance = old_comm)
        except:
            comm = ServiceCommForm()
        
        #formset
        LinkFormSet = formset_factory(ServiceUserForm, formset=BaseLinkFormSet2)
        intersect = User.objects.filter(~Q(Q(service_user__service = service) & Q(Q(service_user__role = "X") | Q(service_user__role = "C")) & Q(service_user__is_active = True)))
        link_formset = LinkFormSet(form_kwargs={'queryset':intersect})
        
        return render(request, 'app/show_service.html', {'init_name':init_name, 'new_init':new_init, 'commit':commit, 'init':init, 
                                'group_name':group_name, 'new_params' : new_params, 'services':services, 'services':services, 
                                'params' : params, 'out_type':out_type, 'in_type':in_type, 'out_format':out_format, 'in_format':in_format,
                                'old_comm':old_comm, 'comm':comm, 'creator':creator, 'service':service, 'can_use':can_use,
                                'my_projects': my_projects, 'projects':projects, 'code':code, 'archive':archive, 'else_projects':else_projects,
                                'my_file':my_file, 'else_file':else_file, 'link_formset':link_formset, 'else_services':else_services,
                                'pro_archive':pro_archive, 'file_archive':file_archive, 'ser_archive':ser_archive})
                                
#archive project
def archive(status, project):
    status = ProjectStatus(status = status, project = project)
    status.save()
    project.end_date = datetime.date.today();
    project.is_active = False
    project.save()
    return
   
#generate random string
def id_generator(size=15, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
   
#update project plan
def update_plan(json, parent = None):
    i = 0
    for plan in json[0]:
        if plan:
            i += 1
            plan_edit = get_object_or_404(ProjectComment, pk = plan["id"])
            plan_edit.numer = str(i)
            if parent:
                plan_edit.child = parent
            plan_edit.save()
            if plan["children"][0]:
                update_plan(plan["children"], plan_edit)  

#show div with parameter group in project site
@csrf_exempt
def ShowDivView(request, project_id, *args, **kwargs):
    param_id = request.POST.get('param_id')
    param = get_object_or_404(ParamGroup, pk = param_id)
    return render(request, 'app/my_div.html', {'param':param, 'project_id':project_id})
   
#group elements to show grouped in template
def grouped(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]
         
#check value
def max_value(value, v_min, v_max):
    print("SPRAWDZAM: ", value, " i ", v_min)
    if float(value) < float(v_min):
        value = v_min
    elif float(value) > float(v_max):
        value = v_max
    return value
    
###################  
# PROJECT
###################


class ProjectView(View):
    def post(self, request, project_id, *args, **kwargs):
        project = get_object_or_404(Project, pk = project_id)
        files = File.objects.filter(is_active = True, file_project__project = project)

        #forms
        new_plan = ProjectPlanForm(request.POST)
        new_comment = CommentForm(request.POST)
        edited_comm = ProjectEditCommForm(request.POST)
        new_group = GroupForm(request.POST)
        new_group_desc = GroupDescForm(request.POST)
        form_file = UploadFileForm2(request.POST, request.FILES)
        new_module_com = ModuleCommentForm(request.POST)
        naw_params = ParamForm(request.POST)
        register_file_name = RegisterFileNameForm(request.POST)
        
        #formset
        LinkFormSet = formset_factory(ProjectUserForm, formset=BaseLinkFormSet)
        link_formset = LinkFormSet(request.POST, prefix='link_formset')
        ComFormSet = formset_factory(FileCommentForm2, formset=CommentFormSet)
        comment_formset = ComFormSet(request.POST, prefix='comment_formset')
        FDFormSet = formset_factory(FileDictForm, formset=FileDictFormSet)
        dict_formset = FDFormSet(request.POST, prefix='dict_formset')
        intersect = User.objects.all()        
        ShareFormSet = formset_factory(FileUserForm, formset=BaseLinkFormSet2)
        share_formset = ShareFormSet(request.POST, form_kwargs={'queryset':intersect}, prefix='share_formset')
        param_formset = modelformset_factory(Param, form=ParamForm2)
        param_formset = param_formset( request.POST, form_kwargs={'project_id': project_id}, prefix='param_formset')
    
        #add comment
        if 'add_comment' in request.POST and new_comment.is_valid():
            comment = new_comment.save(commit=False)
            comment.project = project
            comment.comment_add_by = request.user
            comment.save()
            return HttpResponseRedirect(reverse('project_view', kwargs={'project_id':project.id, 'label': "Comments"}))

        #edit comment
        if 'edit_pro_comm' in request.POST and edited_comm.is_valid():
            comment = edited_comm.save(commit=False)
            old_id = request.POST.get('edit_pro_comm', False)
            old_comm = get_object_or_404(ProjectComment, pk = old_id)
            old_comm.is_active = False
            old_comm.save()
            new_comm = ProjectComment(comment = comment.comment, project = old_comm.project, comment_add_by = request.user, show = old_comm.show)
            new_comm.save()
            return HttpResponseRedirect(reverse('project_view', kwargs={'project_id':project.id, 'label': "Comments"}))
            
        #share project
        if 'share' in request.POST and link_formset.is_valid():
            for link_form in link_formset:
                guest = link_form.save(commit=False)
                guest.role = link_form.cleaned_data["role"]
                guest.project = project
                guest.who_add = request.user
                guest.save()
                files = File.objects.filter(is_active = True, file_project__project = project, file_project__is_active = True)
                for f in files:
                    f_user = FileUser(file = f, user = guest.who, who_add = request.user, comment = guest.comment, role = 'X')
                    f_user.save()
            return HttpResponseRedirect(reverse('project_view', kwargs={'project_id':project.id, 'label': "Share"}))
            
        #delete project
        if 'pro_del' in request.POST:
            project.is_active = False
            project.is_del = True
            project.save()
            status = ProjectStatus(project = project, status = "DEL")
            status.save()
            pro_file = Fileproject.objects.filter(project = project)
            if pro_file:
                for pfile in pro_file:
                    fl = get_object_or_404(File,file_project = pfile)
                    pro_number = Fileproject.objects.filter(file = fl).count()
                    if pro_number == 1:
                        fl.is_active = False
                        fl.save()
                        os.remove(settings.BASE_DIR + fl.file.url)
                    pfile.is_active = False
                    pfile.save()
                    new_Fname = str(fl.ad_name) + "_" + str(fl.id)
                    os.unlink(os.path.join(project.path, new_Fname))
            os.rmdir(project.path)
            return redirect('/app/my_site')
            
        #archive project - success
        if "pro_OK" in request.POST:
            archive("OK", project)
            return redirect('/app/archive/project/' + str(project.id)) 

        #archive project - suspend
        if "pro_SUS" in request.POST:
            archive("SUS", project)
            return redirect('/app/archive/project/' + str(project.id)) 

        #archive project - failure
        if "pro_NOK" in request.POST:
            archive("NOK", project)
            return redirect('/app/archive/project/' + str(project.id)) 
            
        #delete file
        if 'deletefile' in request.POST:
            file_remove = request.POST.getlist('choices')
            file_remove = Fileproject.objects.filter(file__id__in = file_remove).update(is_active=False)
            add_to = request.POST.getlist('choices')
            for f in add_to:
                file = get_object_or_404(File, pk = f)
                new_Fname = str(file.id) + "_" + str(file.ad_name)
                os.unlink(os.path.join(project.path, new_Fname))
            return HttpResponseRedirect(reverse('project_view', kwargs={'project_id':project.id, 'label': "Files"}))
            
        #add file to project
        if "add" in request.POST:
            add_to_project = request.POST.getlist('choices')
            projects = request.POST.getlist('project_name')
            for file_to in add_to_project:
                file = get_object_or_404(File, pk = file_to)
                for pro in projects:
                    try:
                        project = get_object_or_404(Project, pk = pro)
                        tmp = Fileproject.objects.get(role = 'In', project = project, file = file, is_active=True)
                    except Fileproject.DoesNotExist:
                        fileproject = Fileproject(role = 'In', project = project, file = file, user = request.user)
                        fileproject.save()
                        tmp, ext = os.path.splitext(file.path)
                        new_Fname = str(file.id) + "_" + str(file.ad_name)
                        os.symlink(settings.BASE_DIR + file.file.url, os.path.join(fileproject.project.path, new_Fname))
            return HttpResponseRedirect(reverse('project_view', kwargs={'project_id':project.id, 'label': "Files"}))
            
        #add comment to file
        if 'add_comment_file' in request.POST and comment_formset.is_valid():
            add_to = request.POST.getlist('choices')
            for file_to in add_to:
                file = get_object_or_404(File, pk = file_to)
                for comment_form in comment_formset:
                    comment = comment_form.save(commit=False)
                    com = FileComment(file = file, user = request.user, show = comment.show, comment = comment.comment)
                    com.save()
            return HttpResponseRedirect(reverse('project_view', kwargs={'project_id':project.id, 'label': "Files"}))
            
        #register new file
        if 'registerfile' in request.POST and register_file_name.is_valid():
            name = register_file_name.cleaned_data["name"]
            path = os.path.join(settings.BASE_DIR, "app/static/register")
            path = os.path.join(path, name)
            my_file = Path(path)
            if my_file.is_file():
                name = basename(path)
                name_tmp, ext = os.path.splitext(name)
                file_id = File.objects.latest('id').id + 1
                j = (file_id // 1000) + 1
                new_path_file = os.path.join('app/static', str(j), str(file_id) + ext)
                copy2(path, new_path_file)
                file = File()
                file.file = new_path_file
                file.path = new_path_file
                file.save()
                file.user_name = str(file.id)
                file.ad_name = name
                file.cl_name = name
                file.ext = ext
                file.save()
                file_pro = Fileproject(role = 'In', project = project, file = file, user = request.user)
                file_pro.save()
                new_Fname = str(file.id) + "_" + str(file.ad_name)

                os.symlink(settings.BASE_DIR + file.file.url, os.path.join(file_pro.project.path, new_Fname))
                creator = FileUser(file = file, user = request.user, who_add = request.user, role = "C")
                creator.save()
                os.remove(path)
            return HttpResponseRedirect(reverse('project_view', kwargs={'project_id':project.id, 'label': "Files"}))
            
        #send file
        if form_file.is_valid():
            file = form_file.save()
            files = [serialize(file)]
            data = {'files': files}
            response = JSONResponse(data, mimetype=response_mimetype(request))
            response['Content-Disposition'] = 'inline; filename=files.json'
            file_pro = Fileproject(role = 'In', project = project, file = file, user = request.user)
            file_pro.save()
            file.user_name = str(file.id)
            file.save()
            tmp, ext = os.path.splitext(file.path)
            new_Fname = str(file.id) + "_" + str(file.ad_name)
            os.symlink(settings.BASE_DIR + file.file.url, os.path.join(file_pro.project.path, new_Fname))
            creator = FileUser(file = file, user = request.user, who_add = request.user, role = "C")
            creator.save()
            return response
        
        #update project plan    
        if 'update_plan' in request.POST and new_plan.is_valid():
            plan = new_plan.save(commit=False)
            plan.project = project
            plan.comment_add_by = request.user
            plan.is_plan = True
            try:
                num = ProjectComment.objects.filter(project = project, is_plan = True, is_active = True).values('project').annotate(max_nr=Max('number'))
                num = num[0]['max_nr']
            except IndexError:
                num = 0
            plan.number = int(num) + 1
            plan.save()
            
        #share file
        if 'share_files' in request.POST and share_formset.is_valid():
            add_to = request.POST.getlist('choices')
            for file_to in add_to:
                file = get_object_or_404(File, pk = file_to)
                for share_form in share_formset:
                    old_guest = share_form.save(commit=False)
                    guest = FileUser(role = "X", file = file, who_add = request.user, comment = old_guest.comment, user = old_guest.user)
                    guest.save()
            return HttpResponseRedirect(reverse('project_view', kwargs={'project_id':project.id, 'label': "Files"}))
        
        #add service    
        if 'new_services' in request.POST:
            add_service = request.POST.getlist('stay')
            for pk in add_service:
                new_service = get_object_or_404(Service, pk = pk)
                new_service = ServiceProject(project = project, service = new_service)
                new_service.save()
            return HttpResponseRedirect(reverse('project_view', kwargs={'project_id':project.id, 'label': "Module"}))
            
        #add module
        if 'new_module' in request.POST or 'save_and_run' in request.POST:
            service_id = request.POST.get('new_module', False)
            if not service_id:
                service_id = request.POST.get('save_and_run', False)
            service = get_object_or_404(Service, pk = service_id)
            module_form = ModuleForm(service, request.POST)
            if module_form.is_valid():
                module = module_form.save(commit=False)
                module.user = request.user
                module.service = service
                module.save()
                module_form.save_m2m()
                module_project = ModuleProject(project = project, module = module)
                module_project.save()
                if new_module_com.is_valid():
                    module_com = new_module_com.save(commit=False)
                    module_com.user = request.user
                    module_com.module = module
                    module_com.save()
                if param_formset.is_valid():
                    par_gr_name = service.name + "_" + str(datetime.date.today())
                    param_group = ParamGroup(name = par_gr_name, user = request.user)
                    param_group.save()
                    for param_form in param_formset:
                        tmp_param = param_form.save(commit=False)
                        if(tmp_param.id != None):
                            def_par = get_object_or_404(Param, pk = tmp_param.id)
                            new_val = tmp_param.value 
                            if def_par.par_type == "N":
                                new_val = max_value(tmp_param.value, def_par.v_min, def_par.v_max)
                            new_param = Param( name=def_par.name, v_min = def_par.v_min, v_max = def_par.v_max, value = new_val, par_type = def_par.par_type, comment = def_par.comment, file = tmp_param.file, user =  request.user)
                            new_param.save()
                            param_group.params.add(new_param)
                            param_group.save()
                    module.param = param_group
                    module.save()
                    if 'save_and_run' in request.POST:
                        path = os.path.join(settings.BASE_DIR, "app/static/tmp_docker")
                        folder_name = id_generator()
                        path = os.path.join(path, folder_name)
                        analysis = Analysis(status = "P", creator = request.user, module = module, path = path)
                        analysis.save()
                        seler = run.delay(module.id, analysis.id, path)
                        seler_id = AsyncResult(seler.task_id)
                        analysis.seler_id = seler_id
                        analysis.save()
                        return redirect('/app/show_analysis/' + str(analysis.id))
               
        #run module
        if 'run_module' in request.POST:
            module_id = request.POST.get('run_module', False)
            module = get_object_or_404(Module, pk = module_id)
            path = os.path.join(settings.BASE_DIR, "app/static/tmp_docker")
            folder_name = id_generator()
            path = os.path.join(path, folder_name)
            analysis = Analysis(status = "P", creator = request.user, module = module, path = path)
            analysis.save()
            seler = run.delay(module_id, analysis.id, path)
            seler_id = AsyncResult(seler.task_id)
            analysis.seler_id = seler_id
            analysis.save()
            return redirect('/app/show_analysis/' + str(analysis.id))        
            
        ''' 
        if 'add_new_group' in request.POST and new_group.is_valid():
            group = new_group.save()
            project = Groupproject(group = group, project =project, user = request.user)
            project.save()
            creator = GroupUser(role = 'C', group = group, user = request.user, who_add = request.user)
            creator.save()
            if new_group_desc.is_valid():
                com = new_group_desc.save(commit=False)
                com.group = group
                com.user = request.user
                com.is_description = True
                com.save()
            add_to = request.POST.getlist('choices')
            for file_to in add_to:
                file = get_object_or_404(File, pk = file_to)
                file_group = Filegroup(group = group, user = request.user, file = file)
                file_group.save()
                       
        if 'add_group' in request.POST:
            add_to_project = request.POST.getlist('choices')
            groups = request.POST.getlist('group_name')
            for file_to in add_to_project:
                file = get_object_or_404(File, pk = file_to)
                for gr in groups:
                    try:
                        group = get_object_or_404(Group, name = gr)
                        file_group = Filegroup.objects.get(group = group, file = file)
                    except Filegroup.DoesNotExist:
                        file_group = Filegroup(group = group, user = request.user, file = file)
                        file_group.save()

        if  'add_ext' in request.POST and dict_formset.is_valid():
            add_to = request.POST.getlist('choices')
            for file_to in add_to:
                file = get_object_or_404(File, pk = file_to)
                for dict_form in dict_formset:
                    tmp_ext = dict_form.save(commit=False)
                    ext = FileDict(file = file, user = request.user, key = tmp_ext.key, value = tmp_ext.value)
                    ext.save()
        '''
        #formset
        LinkFormSet = formset_factory(ProjectUserForm, formset=BaseLinkFormSet)
        link_formset = LinkFormSet(prefix='link_formset')
        FDFormSet = formset_factory(FileDictForm, formset=FileDictFormSet)
        dict_formset = FDFormSet(prefix='dict_formset')
        ComFormSet = formset_factory(FileCommentForm2, formset=CommentFormSet)
        comment_formset = ComFormSet(prefix='comment_formset')
        intersect = User.objects.all()
        ShareFormSet = formset_factory(FileUserForm, formset=BaseLinkFormSet2)
        share_formset = ShareFormSet(form_kwargs={'queryset':intersect}, prefix='share_formset')
        
        #site info
        my_projects = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = True)
        else_projects = Project.objects.filter(Q(projectuser__who = self.request.user) & Q(is_active = True) & Q(projectuser__isactive = True) & ~Q(projectuser__role = "Cr") &Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "B")))
        my_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "C", is_active = True, file_user_comment__is_active = True)
        else_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "X", is_active = True, file_user_comment__is_active = True)
        archive = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = False)
        pro_archive = Project.objects.filter(Q(is_del = False) & Q(projectuser__who = self.request.user) & Q(is_active = False) & Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "Cr") | Q(projectuser__role = "B")))
        file_archive = File.objects.filter(Q(is_del = False) & Q(file_user_comment__user = self.request.user) & Q(Q(file_user_comment__role = "C") | Q(file_user_comment__role = "X")) & Q(is_active = False))
        ser_archive = Service.objects.filter(Q(is_del = False) & Q(user_service__user = self.request.user) & Q(Q(user_service__role = "C") | Q(user_service__role = "X")) & Q(is_active = False))
        can_see_a = ProjectUser.objects.filter(project = project, role = "Ar", isactive = True)
        can_write_a = ProjectUser.objects.filter(project = project, role = "Aw", isactive = True)
        clients = ProjectUser.objects.filter(project = project, role = "C", isactive = True)
        boss = ProjectUser.objects.filter(project = project, role = "B", isactive = True)
        creator = ProjectUser.objects.get(project = project, role = "Cr", isactive = True)
        services = Service.objects.filter(user_service__user = self.request.user, is_active = True, user_service__role = "C", user_service__is_active = True)
        else_services = Service.objects.filter(user_service__user = self.request.user, user_service__role = "X", is_active = True, user_service__is_active = True)
        status = ProjectStatus.objects.filter(project = project).values('project').annotate(max_id=Max('id'))
        status = status[0]['max_id']
        status = ProjectStatus.objects.get(pk = status)
        plan = ProjectComment.objects.filter(project = project, is_plan = True, is_active=True)
        comments = ProjectComment.objects.filter(Q(project = project) & Q(is_active = True) & Q(is_plan = False) & (Q(comment_add_by =  self.request.user) | Q(show = True)))
        files = File.objects.filter(file_project__is_active = True, file_project__project = project)
        c_files = files.count()
        project_files = Project.objects.filter(Q(projectuser__role = "Aw") | Q(projectuser__role = "Cr")).distinct()
        show_groups = Group.objects.filter(group_project__project = project, group_project__is_active = True)
        c_groups = show_groups.count()
        groups = Group.objects.filter(Q(is_active = True) & (Q(user_group__user = self.request.user) & Q(user_group__is_active = True)))
        project_services = Service.objects.filter(Q(user_service__user = self.request.user) & Q(is_active = True) & (Q(project_service__project = project) & Q(project_service__is_active = True)))
        all_services = Service.objects.filter(Q(is_active = True) & (Q(user_service__user = self.request.user) & Q(user_service__is_active = True)) & ~(Q(project_service__project = project) & Q(project_service__is_active = True)))
        all_services = grouped(all_services, 4)
        end = project.end_date
        if not end:
            end = datetime.date.today()
        c_days = end - project.start_date
        
        printf(param_formset)
        return render(request, 'app/project_view.html', {'my_projects': my_projects, 
                'project' : project, 'can_see_a': can_see_a, 'clients': clients, 'boss' : boss, 'can_write_a' : can_write_a,
                'link_formset' : link_formset, 'status' : status, 'creator' : creator, 'plan' : plan, 'new_plan' : new_plan,
                'new_comment' : new_comment, 'comments' : comments, 'form_file': form_file, 'files':files, 'project_files' : project_files,
                'fileform' : form_file, 'comment_formset' : comment_formset, 'dict_formset' : dict_formset, 'share_formset' : share_formset,
                 'new_group' : new_group, 'new_group_desc' : new_group_desc, 'groups' : groups, 'show_groups':show_groups,
                 'services':services, 'c_files' : c_files, 'c_groups' : c_groups, 'c_days' : c_days.days, 'archive':archive,
                 'new_module_com':new_module_com, 'project_services':project_services, 'all_services':all_services,
                 'register_file_name':register_file_name, 'else_projects':else_projects, 'my_file':my_file, 'else_file':else_file,
                 'else_services':else_services, 'pro_archive':pro_archive, 'file_archive':file_archive, 'ser_archive':ser_archive,
                 'module_form2':module_form, 'param_formset2':param_formset})
           
    def get(self, request, project_id, *args, **kwargs):
        project = get_object_or_404(Project, pk = project_id)
        try:
            #remove comment
            if(request.GET['command'] == "remove"):
                update_com = get_object_or_404(ProjectComment, pk = request.GET.get('com_id'))
                update_com.is_active = False;
                update_com.save()
                return HttpResponse()
            #remove permission
            if(request.GET['command'] == "remove_share"):
                update_share = get_object_or_404(ProjectUser, pk = request.GET.get('user_pro_id'))
                update_share.isactive = False;
                update_share.save()
                return HttpResponse()
            #show comment
            if(request.GET['command'] == "show"):
                update_com = get_object_or_404(ProjectComment, pk = request.GET.get('com_id'))
                update_com.show = True;
                update_com.save()
                return HttpResponse()
            #hide comment
            if(request.GET['command'] == "hide"):
                update_com = get_object_or_404(ProjectComment, pk = request.GET.get('com_id'))
                update_com.show = False;
                update_com.save()
                return HttpResponse()
            #remove service
            if(request.GET['command'] == "remove_service"):
                remove_service = get_object_or_404(Service, pk = request.GET.get('service_id'))
                remove_service = get_object_or_404(ServiceProject, service = remove_service, project = project)
                remove_service.is_active = False;
                remove_service.save()
                return HttpResponse()
            #remove module
            if(request.GET['command'] == "remove_module"):
                remove_module = get_object_or_404(Module, pk = request.GET.get('module_id'))
                remove_module.is_active = False
                remove_module.save()
                return HttpResponse()
            #remove plan
            if(request.GET['command'] == "remove_plan"):
                remove_plan = get_object_or_404(ProjectComment, pk = request.GET.get('plan_id'))
                remove_plan.is_active = False
                remove_plan.save()
                return HttpResponse()
            #change plan status - error
            if(request.GET['command'] == "error_plan"):
                remove_plan = get_object_or_404(ProjectComment, pk = request.GET.get('plan_id'))
                remove_plan.p_class = "NOK"
                remove_plan.save()
                remove_plan.save()
                return HttpResponse()
            #change plan status - error
            if(request.GET['command'] == "back_plan"):
                remove_plan = get_object_or_404(ProjectComment, pk = request.GET.get('plan_id'))
                remove_plan.p_class = "P"
                remove_plan.save()
                return HttpResponse()
            #change plan status - success
            if(request.GET['command'] == "success_plan"):
                remove_plan = get_object_or_404(ProjectComment, pk = request.GET.get('plan_id'))
                remove_plan.p_class = "OK"
                remove_plan.save()
                return HttpResponse()
            if(request.GET['command'] == "drop"):
                string = request.GET.get('serialize')
                jsn = json.loads(string)
                update_plan(jsn)
                return HttpResponse()
        except:
            pass

        #site info
        my_projects = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = True)
        else_projects = Project.objects.filter(Q(projectuser__who = self.request.user) & Q(is_active = True) & Q(projectuser__isactive = True) & ~Q(projectuser__role = "Cr") &Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "B")))
        my_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "C", is_active = True, file_user_comment__is_active = True)
        else_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "X", is_active = True, file_user_comment__is_active = True)
        archive = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = False)
        pro_archive = Project.objects.filter(Q(is_del = False) & Q(projectuser__who = self.request.user) & Q(is_active = False) & Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "Cr") | Q(projectuser__role = "B")))
        file_archive = File.objects.filter(Q(is_del = False) & Q(file_user_comment__user = self.request.user) & Q(Q(file_user_comment__role = "C") | Q(file_user_comment__role = "X")) & Q(is_active = False))
        ser_archive = Service.objects.filter(Q(is_del = False) & Q(user_service__user = self.request.user) & Q(Q(user_service__role = "C") | Q(user_service__role = "X")) & Q(is_active = False))
        can_see_a = ProjectUser.objects.filter(project = project, role = "Ar", isactive = True)
        can_write_a = ProjectUser.objects.filter(project = project, role = "Aw", isactive = True)
        clients = ProjectUser.objects.filter(project = project, role = "C", isactive = True)
        boss = ProjectUser.objects.filter(project = project, role = "B", isactive = True)
        creator = ProjectUser.objects.get(project = project, role = "Cr", isactive = True)
        services = Service.objects.filter(user_service__user = self.request.user, is_active = True, user_service__role = "C", user_service__is_active = True)
        else_services = Service.objects.filter(user_service__user = self.request.user, user_service__role = "X", is_active = True, user_service__is_active = True)
        status = ProjectStatus.objects.filter(project = project).values('project').annotate(max_id=Max('id'))
        status = status[0]['max_id']
        status = ProjectStatus.objects.get(pk = status)
        plan = ProjectComment.objects.filter(project = project, is_plan = True, is_active=True)
        comments = ProjectComment.objects.filter(Q(project = project) & Q(is_active = True) & Q(is_plan = False) & (Q(comment_add_by =  self.request.user) | Q(show = True)))
        files = File.objects.filter(file_project__is_active = True, file_project__project = project)
        c_files = files.count()
        project_files = Project.objects.filter(Q(projectuser__role = "Aw") | Q(projectuser__role = "Cr")).distinct()
        show_groups = Group.objects.filter(group_project__project = project, group_project__is_active = True)
        c_groups = show_groups.count()
        groups = Group.objects.filter(Q(is_active = True) & (Q(user_group__user = self.request.user) & Q(user_group__is_active = True)))
        project_services = Service.objects.filter(Q(user_service__user = self.request.user) & Q(is_active = True) & (Q(project_service__project = project) & Q(project_service__is_active = True)))
        all_services = Service.objects.filter(Q(is_active = True) & (Q(user_service__user = self.request.user) & Q(user_service__is_active = True)) & ~(Q(project_service__project = project) & Q(project_service__is_active = True)))
        all_services = grouped(all_services, 4)
        end = project.end_date
        if not end:
            end = datetime.date.today()
        c_days = end - project.start_date
        
        #project archived
        if project.is_active == False and project.is_del == False:
                return render(request, 'app/arch_pro.html', {'my_projects': my_projects, 'project' : project, 'can_see_a': can_see_a,
                        'clients': clients, 'boss' : boss, 'can_write_a' : can_write_a, 'status' : status, 'creator' : creator, 
                        'plan' : plan, 'comments' : comments, 'files':files, 'project_files' : project_files, 'services':services,
                        'c_files' : c_files, 'c_groups' : c_groups, 'c_days' : c_days.days, 'project_services':project_services,
                        'all_services':all_services, 'else_projects':else_projects, 'my_file':my_file, 'else_file':else_file,
                        'else_services':else_services, 'pro_archive':pro_archive, 'file_archive':file_archive, 'ser_archive':ser_archive})
        
        #forms
        form_file = UploadFileForm2()
        new_plan = ProjectPlanForm()
        new_comment = CommentForm()
        fileform = FileDictForm()
        new_group = GroupForm()
        new_group_desc = GroupCommForm()
        register_file_name = RegisterFileNameForm()
        new_module_com = ModuleCommentForm()
        
        #formset
        LinkFormSet = formset_factory(ProjectUserForm, formset=BaseLinkFormSet)
        link_formset = LinkFormSet(prefix='link_formset')
        FDFormSet = formset_factory(FileDictForm, formset=FileDictFormSet)
        dict_formset = FDFormSet(prefix='dict_formset')
        ComFormSet = formset_factory(FileCommentForm2, formset=CommentFormSet)
        comment_formset = ComFormSet(prefix='comment_formset')
        intersect = User.objects.all()
        ShareFormSet = formset_factory(FileUserForm, formset=BaseLinkFormSet2)
        share_formset = ShareFormSet(form_kwargs={'queryset':intersect}, prefix='share_formset')
        
        
        return render(request, 'app/project_view.html', {'my_projects': my_projects, 
                        'project' : project, 'can_see_a': can_see_a, 'clients': clients, 'boss' : boss, 'can_write_a' : can_write_a,
                        'link_formset' : link_formset, 'status' : status, 'creator' : creator, 'plan' : plan, 'new_plan' : new_plan,
                        'new_comment' : new_comment, 'comments' : comments, 'form_file': form_file, 'files':files, 'project_files' : project_files,
                        'fileform' : fileform, 'comment_formset' : comment_formset, 'dict_formset' : dict_formset, 'share_formset' : share_formset,
                         'new_group' : new_group, 'new_group_desc' : new_group_desc, 'groups' : groups, 'show_groups':show_groups,
                         'services':services, 'c_files' : c_files, 'c_groups' : c_groups, 'c_days' : c_days.days, 'archive':archive,
                         'new_module_com':new_module_com, 'project_services':project_services, 'all_services':all_services,
                         'register_file_name':register_file_name, 'else_projects':else_projects, 'my_file':my_file, 'else_file':else_file,
                         'else_services':else_services, 'pro_archive':pro_archive, 'file_archive':file_archive, 'ser_archive':ser_archive})
                         
#upload classes
class PictureCreateView(CreateView):
    model = Picture
    fields = "__all__"
    
    def form_valid(self, form):
        
        self.object = form.save()
        files = [serialize(self.object)]
        data = {'files': files}
        raise Exception(response_mimetype(self.request))
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    def form_invalid(self, form):
        data = json.dumps(form.errors)
        return HttpResponse(content=data, status=400, content_type='application/json')


class jQueryVersionCreateView(PictureCreateView):
    template_name_suffix = '_jquery_form'


class PictureDeleteView(DeleteView):
    model = Picture

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        response = JSONResponse(True, mimetype=response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class PictureListView(ListView):
    model = Picture

    def render_to_response(self, context, **response_kwargs):
        files = [ serialize(p) for p in self.get_queryset() ]
        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

class ProjectViewEnableMixin(object):

    def get_object(self, queryset=None):
        
        if queryset is None:
            queryset = self.get_queryset()
        try:
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise PermissionDenied
        return obj

            
@login_required
def upload_file(request):
    choice = Project.objects.filter(Q(can_read = request.user) | Q(creator = request.user))
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            selected_item = get_object_or_404(Project, name = request.POST.get('name'))
            handle_uploaded_file(request.FILES['file'], selected_item)
            return HttpResponseRedirect('success/')
    else:
        form = UploadFileForm()
    return render(request, 'app/upload.html', {'form': form, 'choice':choice})
        
###################  
# ANALYSIS
###################

class AnalysisView(View):
    
    def post(self, request, analysis_id, *args, **kwargs):
        analysis = get_object_or_404(Analysis, pk = analysis_id)
        return HttpResponseRedirect('#')

    def get(self, request, analysis_id, *args, **kwargs):
        
        #site info
        analysis = get_object_or_404(Analysis, pk = analysis_id)
        services = Service.objects.filter(user_service__user = self.request.user, is_active = True, user_service__role = "C", user_service__is_active = True)
        else_services = Service.objects.filter(user_service__user = self.request.user, user_service__role = "X", is_active = True, user_service__is_active = True)
        my_projects = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = True)
        else_projects = Project.objects.filter(Q(projectuser__who = self.request.user) & Q(is_active = True) & Q(projectuser__isactive = True) & ~Q(projectuser__role = "Cr") &Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "B")))
        my_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "C", is_active = True, file_user_comment__is_active = True)
        else_file = File.objects.filter(file_user_comment__user = self.request.user, file_user_comment__role = "X", is_active = True, file_user_comment__is_active = True)
        archive = Project.objects.filter(projectuser__who = self.request.user, projectuser__role = "Cr", is_active = False)
        pro_archive = Project.objects.filter(Q(is_del = False) & Q(projectuser__who = self.request.user) & Q(is_active = False) & Q(Q(projectuser__role = "Aw") | Q(projectuser__role = "Ar") | Q(projectuser__role = "Cr") | Q(projectuser__role = "B")))
        file_archive = File.objects.filter(Q(is_del = False) & Q(file_user_comment__user = self.request.user) & Q(Q(file_user_comment__role = "C") | Q(file_user_comment__role = "X")) & Q(is_active = False))
        ser_archive = Service.objects.filter(Q(is_del = False) & Q(user_service__user = self.request.user) & Q(Q(user_service__role = "C") | Q(user_service__role = "X")) & Q(is_active = False))
        if analysis.status == "P":
            is_pending = True
        else:
            is_pending = False
        
        return render(request, 'app/show_analysis.html', {'services':services, 'my_projects': my_projects, 'my_file':my_file, 
                'else_file':else_file, 'else_services':else_services, 'analysis':analysis, 'else_projects':else_projects,
                'archive':archive, 'is_pending':is_pending, 'pro_archive':pro_archive, 'file_archive':file_archive, 'ser_archive':ser_archive})

#render analysis content
def AnalysisContentView(request, analysis_id, *args, **kwargs):
        analysis = get_object_or_404(Analysis, pk = analysis_id)
        if analysis.status == "P":
            result = run.AsyncResult(analysis.seler_id)
            is_end = result.ready()
            #analysis is running
            if not is_end:
                pending = True
                return render(request, 'app/content_analysis.html', {'pending':pending})
            #analysis ended
            else:
                res = result.get()
                if res == 0:
                    analysis.status = "OK"
                    analysis.end_date = datetime.date.today();
                    analysis.save()
                else:
                    error = res
                    analysis.status = "Err"
                    analysis.end_date = datetime.date.today();
                    analysis.save()
                    
            #clean after analysis
            path = analysis.path
            
            #conf
            path_t = os.path.join(path, "conf/out/")
            for file_name in glob.glob(path_t + "*.conf"):
                path_file = os.path.join(path_t, file_name)
                name = basename(file_name)
                f = open(path_file)
                myfile = File_dj(f)
                file = File()
                file.file.save(name, content=myfile)
                file.save()
                file.user_name = file.id
                file.save()
                f.close()
                analysis.file_conf.add(file)
                
            #log
            path_t = os.path.join(path, "log/")
            for file_name in glob.glob(path_t + "*.log"):
                path_file = os.path.join(path_t, file_name)
                name = basename(file_name)
                f = open(path_file)
                myfile = File_dj(f)
                file = File()
                file.file.save(name, content=myfile)
                file.save()
                file.user_name = file.id
                file.save()
                f.close()
                analysis.file_log.add(file)
                
            #out
            path_t = os.path.join(path, "output/")
            for file_name in glob.glob(path_t + "*"):
                path_file = os.path.join(path_t, file_name)
                name = basename(file_name)
                name_tmp, ext = os.path.splitext(name)
                file_id = File.objects.latest('id').id + 1
                j = (file_id // 1000) + 1
                new_path_file = os.path.join('app/static', str(j), str(file_id) + ext)
                copy2(path_file, new_path_file)
                file = File()
                file.file = new_path_file
                file.path = new_path_file
                file.save()
                file.user_name = file.id
                file.ad_name = name
                file.cl_name = name
                file.ext = ext
                file.save()
                
                analysis.file_out.add(file)                
            shutil.rmtree(path)

        pending = False
        file_out = File.objects.filter(analysis_fileout = analysis)
        n_out = file_out.count()
        file_log = File.objects.filter(analysis_filelog = analysis)
        n_log = file_log.count()
        file_conf = File.objects.filter(analysis_fileconf = analysis)
        n_conf = file_conf.count()
        return render(request, 'app/content_analysis.html', {'pending':pending, 'analysis':analysis, 'file_out':file_out,
                'file_log':file_log, 'file_conf':file_conf, 'n_out':n_out, 'n_log':n_log, 'n_conf':n_conf})
                                
'''
class GroupView(View):
    
    def post(self, request, group_id, *args, **kwargs):
        # Create the formset, specifying the form and formset we want to use.
        LinkFormSet = formset_factory(GroupUserForm, formset=BaseLinkFormSet2)
        link_formset_group = LinkFormSet(request.POST,  prefix='link_formset_group')
        
        extform = FileDictForm(request.POST)
        
        new_comment = GroupCommForm(request.POST)
        group = get_object_or_404(Group, pk = group_id)
        new_desc = GroupDescForm(request.POST)
        
        ExtFormSet = formset_factory(GroupDictForm, formset=FileDictFormSet)
        ext_formset = ExtFormSet(request.POST, prefix='ext_formset')
        
        ExtFileFormSet = formset_factory(FileDictForm, formset=FileDictFormSet)
        ext_file_formset = ExtFormSet(request.POST, prefix='ext_file_formset')
        
        
        #OK
        if 'update_desc' in request.POST and new_desc.is_valid():
            desc = new_desc.save(commit=False)
            desc.group = group
            desc.user = request.user
            desc.is_description = True
            desc.save()
        #OK
        if 'add_comment' in request.POST and new_comment.is_valid():
            comment = new_comment.save(commit=False)
            comment.group = group
            comment.user = request.user
            comment.save()
        if 'add_ext' in request.POST and ext_formset.is_valid():
            #print(ext_formset)
            for ext_form in ext_formset:
                ext = ext_form.save(commit=False)
                ext.group = group
                ext.user = request.user
                ext.save()
        if 'add_ext_files' in request.POST and ext_file_formset.is_valid():
            for ext_form in ext_file_formset:
                ext = ext_form.save(commit=False)
                add_to = request.POST.getlist('choices')
                for file_to in add_to:
                    file = get_object_or_404(File, pk = file_to)
                    new_ext = FileDict(file = file, user = request.user, key = ext.key, value = ext.value)
                    new_ext.save()
            
        #OK   
        if 'deletefile' in request.POST:
            file_remove = request.POST.getlist('choices')
            file_remove = Filegroup.objects.filter(file__id__in = file_remove).update(is_active=False)
            
        if 'share' in request.POST and link_formset_group.is_valid():
            for link_form in link_formset_group:
                guest = link_form.save(commit=False)
                guest.role = "X"
                guest.group = group
                guest.who_add = request.user
                guest.save()
        if "add_to_project" in request.POST:
            project = get_object_or_404(Project, pk = request.POST.get('project_id'))
            groupproject = Fileproject(project = project, group = group, user = request.user)
            groupproject.save()
            
        #to new project
        return HttpResponseRedirect('#')
   
        
    def get(self, request, group_id, *args, **kwargs):
        group = get_object_or_404(Group, pk = group_id)
        try:
            #OK
            if(request.GET['command'] == "show"):
                update_com = get_object_or_404(GroupComment, pk = request.GET.get('com_id'))
                update_com.show = True;
                update_com.save()
                return HttpResponse()
            #OK
            if(request.GET['command'] == "hide"):
                update_com = get_object_or_404(GroupComment, pk = request.GET.get('com_id'))
                update_com.show = False;
                update_com.save()
                return HttpResponse()
            #OK
            if(request.GET['command'] == "removebutton"):
                update_com = get_object_or_404(GroupComment, pk = request.GET.get('com_id'))
                update_com.is_active = False;
                update_com.save()
                return HttpResponse()
            if(request.GET['command'] == "removeext"):
                update_com = get_object_or_404(GroupDict, pk = request.GET.get('ext_id'))
                update_com.is_active = False;
                update_com.save()
                return HttpResponse()
            #OK
            if(request.GET['command'] == "remove"):
                #print("user: ", request.GET.get('usergroup_id'))
                remove_user = get_object_or_404(GroupUser, group = group, user = request.GET.get('usergroup_id'))
                remove_user.is_active = False;
                remove_user.save()
                return HttpResponse()
            if(request.GET['command'] == "removeproject"):
                pro = get_object_or_404(Project, name = request.GET.get('project_id'))
                update_com = get_object_or_404(Groupproject, project = pro, group = group)
                update_com.is_active = False;
                update_com.save()
                return HttpResponse()
            
        except:
            pass 
        
        creator = get_object_or_404(User, group_user__role = 'C', group_user__group = group)
        description = GroupComment.objects.filter(group = group, is_description = True).values('group').annotate(max_id=Max('id'))
        description = description[0]['max_id']
        description = GroupComment.objects.get(pk = description)
        new_desc = GroupDescForm(instance = description)
        comments = GroupComment.objects.filter(Q(group = group) & Q(is_description = False) & Q(is_active = True) & (Q(user =  self.request.user) | Q(show = True)))
        new_comment = GroupCommForm()
        exts = GroupDict.objects.filter(group = group, is_active = True)
        services = Service.objects.filter(user_service__user = self.request.user, is_active = True, user_service__role = "C", user_service__is_active = True)

        can_use = User.objects.filter(group_user__group = group, group_user__role = "X", group_user__is_active = True)
        projects = Project.objects.filter(Q(project_group__group = group) & Q(project_group__is_active = True) & ( Q(project_group__group__user_group__user = self.request.user) & Q(project_group__group__is_active= True))).distinct()

        # Create the formset, specifying the form and formset we want to use.
        LinkFormSet = formset_factory(GroupUserForm, formset=BaseLinkFormSet2)
        link_formset_group = LinkFormSet(prefix='link_formset_group')
        ExtFormSet = formset_factory(GroupDictForm, formset=FileDictFormSet)
        ext_formset = ExtFormSet(prefix='ext_formset')
        
        ExtFileFormSet = formset_factory(FileDictForm, formset=FileDictFormSet)
        ext_file_formset = ExtFormSet(prefix='ext_file_formset')
        
        files = File.objects.filter(file_group__is_active = True, file_group__group = group)
        #project_files = Project.objects.filter((~Q(group_project__group = group) | (Q(group_project__group = group) & Q(group_project__is_active = False))) & Q( Q(groupuser__user = self.request.user) & (Q(groupuser__role = "X") | Q(groupuser__role = "C")))).distinct()
        return render(request, 'app/group_view.html', {'exts': exts, 'new_comment':new_comment, 'comments': comments, 'projects':projects,
                    'can_use' : can_use, 'creator' : creator, 'link_formset_group' : link_formset_group, 'group' : group, 'description' : description,
                    'services':services, 'new_desc' : new_desc, 'ext_formset' : ext_formset, "files" : files, "ext_file_formset" : ext_file_formset})
'''
