from django.db import models
from django.conf import settings
from django.db import connection
import os
from django.db.models.aggregates import Max
from django.shortcuts import get_object_or_404 
from django.contrib.auth.models import User 

#project 
class Project(models.Model):
    name = models.CharField(max_length = 100)
    start_date = models.DateField(auto_now_add = True, editable = False)
    end_date = models.DateField(blank = True, null = True)
    path = models.FilePathField(editable = False, blank = True, null = True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null = True)
    is_active = models.BooleanField(default=True)
    is_del = models.BooleanField(default=False)

#project status
class ProjectStatus(models.Model):
    STATUS = (
        ('P', 'Pending'),
        ('OK', 'Ended with success'),
        ('SUS', 'Suspended'),
        ('NOK', 'Ended with failure'),
        ('DEL', 'Deleted')
    )
    date = models.DateField(auto_now_add = True, editable = False)
    status = models.CharField(max_length=4, choices=STATUS)
    project = models.ForeignKey(Project, blank = True, null = True)
    
#project comment
class ProjectComment(models.Model):
    CLASS = (
        ('OK', 'panel-success'),
        ('P', 'panel-primary'),
        ('NOK', 'panel-danger')
    )
    comment = models.CharField(max_length = 1500, null = True, blank=True)
    date = models.DateField(auto_now_add = True, null = True, blank=True)
    project = models.ForeignKey(Project, related_name="project")
    comment_add_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="comment_add_by")
    is_plan = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    show = models.BooleanField(default=True)
    number = models.CharField(max_length=40,blank = True, null = True, default="0")
    p_class = models.CharField(max_length=4, choices=CLASS, default='P')
    child = models.ForeignKey('self', related_name="comment_children", blank=True, null = True)
    
#project permission
class ProjectUser(models.Model):
    ROLE = (
        ('C', 'Client'),
        ('Cr', 'Creator'),
        ('Aw', 'Analitic write'),
        ('Ar', 'Analitic read'),
        ('B', 'Boss'),
    )
    comment = models.CharField(max_length = 1500, null = True, blank=True)
    role = models.CharField(max_length=2, choices=ROLE)
    date = models.DateField(auto_now_add = True, null = True, blank=True)
    who = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="who", null = True, blank=True)
    who_add = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="who_add", null = True, blank=True)
    project = models.ForeignKey(Project, related_name="projectuser")
    isactive = models.BooleanField(default=True)
    
    def image(self):
        try:
            img_id = Picture.objects.filter(user = self.who).values('user').annotate(max_id=Max('id'))
            img_id = img_id[0]['max_id']
            img_name = Picture.objects.get(pk = img_id)
            img_name = img_name.name
        except: 
            img_name = "icon-dna.png"
        return img_name

#test class
class Program(models.Model):
    version = models.IntegerField(blank = True, null = True)
    name = models.CharField(max_length = 100, blank = True, null = True)
    
#user additional info
class UserExtension(models.Model):
    first_name = models.CharField(max_length = 100, null = True, blank=True)
    last_name = models.CharField(max_length = 100, null = True, blank=True)
    email = models.EmailField(null = True, blank=True)
    company = models.CharField(max_length = 100, null = True, blank=True)
    department = models.CharField(max_length = 100, null = True, blank=True)
    tel = models.CharField(max_length = 100, null = True, blank=True)
    cell = models.CharField(max_length = 100, null = True, blank=True)
    about = models.CharField(max_length = 1500, null = True, blank=True)
    adress = models.CharField(max_length = 500, null = True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_ext",null = True, blank=True)
    date = models.DateTimeField(auto_now_add = True, null = True, blank=True)

#user description
class UserComment(models.Model): 
     comment = models.CharField(max_length = 1500, null = True, blank=True)
     date = models.DateField(auto_now_add = True, null = True, blank=True)
     about_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user")
     add_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="add_by")

#get file name
def content_file_name(instance, filename):
    try:
        picture_id = Picture.objects.latest('id').id + 1
    except:
        picture_id = 1
    name, ext = os.path.splitext(filename)
    name = str(picture_id) + ext
    instance.name = os.path.join(instance.user.username, name)
    return os.path.join('app/static', instance.user.username, name)
    
#picture
class Picture(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null = True)
    file = models.FileField(upload_to=content_file_name)
    slug = models.SlugField(max_length=100, blank=True)
    name = models.CharField(max_length = 100, null = True, blank = True)
    
    date = models.DateField(auto_now_add = True, editable = False)

    def __unicode__(self):
        return self.file.name

    @models.permalink
    def get_absolute_url(self):
        return ('upload-new', )
    
    def save(self, *args, **kwargs):
        self.slug = self.file.name
        super(Picture, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.file.delete(False)
        super(Picture, self).delete(*args, **kwargs)
        
#get user name
def user_name(self):
    ext = UserExtension.objects.filter(user = self).values('user').annotate(max_id=Max('id'))
    ext = ext[0]['max_id']
    user_ext = UserExtension.objects.get(pk = ext)
    try:
        name = user_ext.first_name + " " + user_ext.last_name + " " + user_ext.company + " " + user_ext.department
    except:
        name = self.username
    return name

#get user image
def image(self):
    try:
        img_id = Picture.objects.filter(user = self).values('user').annotate(max_id=Max('id'))
        img_id = img_id[0]['max_id']
        img_name = Picture.objects.get(pk = img_id)
        img_name = img_name.name
    except: 
        img_name = "icon-dna.png"
    return img_name
    
#register functions in User table
User.add_to_class('user_name', user_name)
User.add_to_class('image', image)

#generate new file path
def file_src(instance, filename):
    try:
        file_id = File.objects.latest('id').id + 1
    except:
        file_id = 1
    j = (file_id // 1000) + 1
    name, ext = os.path.splitext(filename)
    name = str(file_id) + ext
    path = os.path.join('app/static', str(j), name)
    instance.path =  path
    instance.user_name = filename
    instance.ad_name = filename
    instance.cl_name = filename
    instance.ext = ext
    return path

#file
class File(models.Model):
    file = models.FileField(upload_to=file_src)
    slug = models.SlugField(max_length=70, blank=True)
    user_name = models.CharField(max_length = 100, null = True, blank = True)
    is_active = models.BooleanField(default=True)
    is_del = models.BooleanField(default=False)
    date = models.DateField(auto_now_add = True, editable = False)
    path = models.FilePathField(editable = False, blank=True, null = True)
    ext = models.CharField(max_length = 100, null = True, blank = True)
    ad_name = models.CharField(max_length = 100, null = True, blank = True)
    cl_name = models.CharField(max_length = 100, null = True, blank = True)
        
    def __unicode__(self):
        return self.file.name

    @models.permalink
    def get_absolute_url(self):
        return ('upload-new', )
    
    def save(self, *args, **kwargs):
        self.slug = self.file.name
        super(File, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_active = False

    def display_text_file(self):
        path = settings.BASE_DIR + self.file.url
        with open(path) as fp:
            return fp.read()
        
    def user_add(self):
        try:
            ext = FileUser.objects.get(file = self, role = "C")
            user_add_name = ext.user
        except:
            user_add_name = "error"
        return user_add_name
        
    def get_commit(self):
        try:
            com = get_object_or_404(FileComment, file = self)
            com = com.comment
        except:
            com = "No comment"
        return com
        
    def code_name(self):
        try:
            fcode = get_object_or_404(FileCode, file = self)
            com = fcode.name + " " + self.user_name
        except:
            com = "Error"
        return com
    

#code
class FileCode(models.Model):
    name = models.CharField(max_length = 100, null = True, blank = True)
    file = models.ManyToManyField(File, related_name="file_code")
    date = models.DateField(auto_now_add = True, editable = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null = True)
    is_active = models.BooleanField(default=True)
    
    def display_text_file(self):
        code = File.objects.filter(file_code=self).latest('id')
        return code.display_text_file()
    
#relation file - project
class Fileproject(models.Model):
    ROLE = (
        ('In', 'In'),
        ('Out', 'Out'),
        ('Tmp', 'Tmp'),

    )
    role = models.CharField(max_length=3, choices=ROLE)
    project = models.ForeignKey(Project, related_name="project_file")
    file = models.ForeignKey(File, related_name="file_project")
    date = models.DateField(auto_now_add = True, editable = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null = True)
    is_active = models.BooleanField(default=True)
    
#file comment
class FileComment(models.Model):
    file = models.ForeignKey(File, related_name="file_comment")
    date = models.DateField(auto_now_add = True, editable = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null = True)
    is_active = models.BooleanField(default=True)
    comment = models.CharField(max_length = 1500, null = True, blank=True)
    show = models.BooleanField(default=True)

#file additional info
class FileDict(models.Model):
    file = models.ForeignKey(File, related_name="file_dict")
    date = models.DateField(auto_now_add = True, editable = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null = True)
    is_active = models.BooleanField(default=True)
    key = models.CharField(max_length = 100, null = True, blank = True)
    value = models.CharField(max_length = 100, null = True, blank = True)
    
#file permission
class FileUser(models.Model):
    ROLE = (
        ('C', 'Creator'),
        ('X', 'Analitic exec'),

    )
    file = models.ForeignKey(File, related_name="file_user_comment")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="file_user")
    who_add = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="who_add_file", null = True, blank=True)
    role = models.CharField(max_length=2, choices=ROLE)
    comment = models.CharField(max_length = 1500, null = True, blank=True)
    date = models.DateField(auto_now_add = True, editable = False)
    is_active = models.BooleanField(default=True)

#Group
class Group(models.Model):
    name = models.CharField(max_length = 100, null = True, blank = True)
    is_active = models.BooleanField(default=True)
    date = models.DateField(auto_now_add = True, editable = False)

#relation group - project
class Groupproject(models.Model):
    project = models.ForeignKey(Project, related_name="project_group")
    group = models.ForeignKey(Group, related_name="group_project")
    date = models.DateField(auto_now_add = True, editable = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null = True)
    is_active = models.BooleanField(default=True)
    
#relation file - group
class Filegroup(models.Model):
    group = models.ForeignKey(Group, related_name="group_file")
    file = models.ForeignKey(File, related_name="file_group")
    date = models.DateField(auto_now_add = True, editable = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null = True)
    is_active = models.BooleanField(default=True)
    
#group comment
class GroupComment(models.Model):
    group = models.ForeignKey(Group, related_name="group_comment")
    date = models.DateField(auto_now_add = True, editable = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null = True)
    is_active = models.BooleanField(default=True)
    comment = models.CharField(max_length = 1500, null = True, blank=True)
    show = models.BooleanField(default=True)
    is_description = models.BooleanField(default=False)
    
#group additional info
class GroupDict(models.Model):
    group = models.ForeignKey(Group, related_name="group_dict")
    date = models.DateField(auto_now_add = True, editable = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null = True)
    is_active = models.BooleanField(default=True)
    key = models.CharField(max_length = 100, null = True, blank = True)
    value = models.CharField(max_length = 100, null = True, blank = True)
    
#group permission
class GroupUser(models.Model):
    ROLE = (
        ('C', 'Creator'),
        ('X', 'Analitic exec'),

    )
    group = models.ForeignKey(Group, related_name="user_group")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="group_user")
    who_add = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="who_add_group", null = True, blank=True)
    role = models.CharField(max_length=2, choices=ROLE)
    comment = models.CharField(max_length = 1500, null = True, blank=True)
    date = models.DateField(auto_now_add = True, editable = False)
    is_active = models.BooleanField(default=True)

#parameters
class Param(models.Model):
    name = models.CharField(max_length = 100, null = True, blank = True)
    v_min = models.FloatField(null = True, blank = True)
    v_max = models.FloatField(null = True, blank = True)
    value = models.CharField(max_length = 100, null = True, blank = True)
    par_type = models.CharField(max_length = 1, null = True, blank = True)
    comment = models.CharField(max_length = 100, null = True, blank = True)
    file = models.ForeignKey(File, related_name="param_file", null = True, blank = True)
    date = models.DateField(auto_now_add = True, editable = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null = True)
    is_active = models.BooleanField(default=True)
  
#group of parameters
class ParamGroup(models.Model):
    name = models.CharField(max_length = 100, null = True, blank = True)
    date = models.DateField(auto_now_add = True, editable = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null = True)
    params = models.ManyToManyField(Param, related_name="params")
    is_active = models.BooleanField(default=True)
    
    def get_comm(self):
        try:
            old_comm = ParamsComment.objects.filter(params = self).values('params').annotate(max_id=Max('id'))
            comm_id = old_comm[0]['max_id']
            param_comm = ParamsComment.objects.get(pk = comm_id)
            param_comm = param_comm.comment
        except:
            param_comm = "no description"
        return param_comm
        
    def get_params(self):
        try:
            d_params = Param.objects.filter(params = self, is_active = True)
        except:
            d_params = "no parameters"
        return d_params

#parameters comment
class ParamsComment(models.Model):
    params = models.ForeignKey(ParamGroup, related_name="params_comment")
    date = models.DateField(auto_now_add = True, editable = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null = True)
    is_active = models.BooleanField(default=True)
    comment = models.CharField(max_length = 1500, null = True, blank=True)
    
#file format
class Format(models.Model):
    name = models.CharField(max_length = 100, null = True, blank = True)
    is_active = models.BooleanField(default=True)
    date = models.DateField(auto_now_add = True, editable = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null = True)
    
# service
class Service(models.Model):
    name = models.CharField(max_length = 100, null = True, blank = True)
    is_active = models.BooleanField(default=True)
    is_del = models.BooleanField(default=False)
    date = models.DateField(auto_now_add = True, editable = False)
    init = models.ManyToManyField(FileCode, related_name="service_init")
    code = models.ManyToManyField(FileCode, related_name="service_code")
    default = models.ManyToManyField(ParamGroup, related_name="service_params")
    in_format = models.ManyToManyField(Format, related_name="service_in_format")
    out_format = models.ManyToManyField(Format, related_name="service_out_format")

#relation service - project
class ServiceProject(models.Model):
    project = models.ForeignKey(Project, related_name="service_pro")
    service = models.ForeignKey(Service, related_name="project_service")
    is_active = models.BooleanField(default=True)
    date = models.DateField(auto_now_add = True, editable = False)
    
#service comment
class ServiceComment(models.Model):
    service = models.ForeignKey(Service, related_name="service_comment")
    date = models.DateField(auto_now_add = True, editable = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null = True)
    is_active = models.BooleanField(default=True)
    comment = models.CharField(max_length = 1500, null = True, blank=True)
    
#service permission
class ServiceUser(models.Model):
    ROLE = (
        ('C', 'Creator'),
        ('X', 'Analitic exec'),
    )
    service = models.ForeignKey(Service, related_name="user_service")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="service_user")
    who_add = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="who_add_service", null = True, blank=True)
    role = models.CharField(max_length=2, choices=ROLE)
    comment = models.CharField(max_length = 1500, null = True, blank=True)
    date = models.DateField(auto_now_add = True, editable = False)
    is_active = models.BooleanField(default=True)
 
#module
class Module(models.Model):
    name = models.CharField(max_length = 100, null = True, blank = True)
    service = models.ForeignKey(Service, related_name="module_service", null = True, blank = True)
    init = models.ForeignKey(File, related_name="module_init", blank=True, null = True)
    code = models.ManyToManyField(File, related_name="module_code")
    param = models.ForeignKey(ParamGroup, related_name="module_params", blank=True, null = True)
    date = models.DateField(auto_now_add = True, editable = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null = True)
    is_active = models.BooleanField(default=True)

    def get_comm(self):
        try:
            old_comm = ModuleComment.objects.filter(module = self).values('module').annotate(max_id=Max('id'))
            comm_id = old_comm[0]['max_id']
            mod_comm = ModuleComment.objects.get(pk = comm_id)
            mod_comm = mod_comm.comment
        except:
            mod_comm = "no description"
        return mod_comm

#relation module - project
class ModuleProject(models.Model):
    project = models.ForeignKey(Project, related_name="module_pro")
    module = models.ForeignKey(Module, related_name="project_module")
    is_active = models.BooleanField(default=True)
    date = models.DateField(auto_now_add = True, editable = False)

#module comment
class ModuleComment(models.Model):
    module = models.ForeignKey(Module, related_name="module_comment")
    date = models.DateField(auto_now_add = True, editable = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null = True)
    is_active = models.BooleanField(default=True)
    comment = models.CharField(max_length = 1500, null = True, blank=True)
    
#docker
class Docker(models.Model):
    name = models.CharField(max_length = 100, null = True, blank = True)
    image_id = models.CharField(max_length = 12, null = True, blank = True)
    date = models.DateField(auto_now_add = True, editable = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null = True)

#docker comment
class DockerComment(models.Model):
    params = models.ForeignKey(Docker, related_name="docker_comment")
    date = models.DateField(auto_now_add = True, editable = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null = True)
    is_active = models.BooleanField(default=True)
    comment = models.CharField(max_length = 1500, null = True, blank=True)
    show = models.BooleanField(default=True)
    is_description = models.BooleanField(default=False)
    
#analysis
class Analysis(models.Model):
    STATUS = (
        ('OK', 'Success'),
        ('Err', 'Error'),
        ('P', 'Pending'),
    )
    start_date = models.DateField(auto_now_add = True, editable = False)
    end_date = models.DateField(editable = False, blank = True, null = True)
    status = models.CharField(max_length = 5, choices=STATUS)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name="analysis_user")
    module = models.ForeignKey(Module, blank=True, null=True, related_name="analysis_module")
    seler_id = models.CharField(editable = True, max_length = 150, null = True, blank=True)
    file_out = models.ManyToManyField(File, related_name="analysis_fileout")
    file_log = models.ManyToManyField(File, related_name="analysis_filelog")
    file_conf = models.ManyToManyField(File, related_name="analysis_fileconf")
    path = models.FilePathField(editable = True, blank = True, null = True)
