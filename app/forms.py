from django import forms
from django.forms import ModelForm, Textarea, NumberInput,Select
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.forms.formsets import BaseFormSet
from django.shortcuts import get_object_or_404 
from io import StringIO
from .models import (Project, ServiceUser, Module, ModuleComment, ParamGroup, Param, ParamsComment, ServiceComment, Service, GroupUser, 
                    GroupDict, UserExtension, Picture, ProjectUser, ProjectComment, File, FileUser, FileComment, FileDict, Group, 
                    GroupComment)
#user forms
class NewUserForm(ModelForm):  
      
    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = ''
        self.fields['password'].widget = forms.PasswordInput(attrs={'placeholder': ''})
        self.fields['password'].widget.attrs['class'] = 'form-control'
        for key in self.fields:
            self.fields[key].required = True
        
    class Meta:
        model = User
        fields = ["username", "password", "email"]

#project forms
class NewProjectForm(forms.Form):
    name = forms.CharField(label='Project name', max_length=100)
    
class ShareProjectForm(forms.Form):
    user_name = forms.CharField(label='User name', max_length=100)
    project_name = forms.CharField(label='Project name', max_length=100)
    
ROLE = ( 
            ('C', 'client'),
            ('B', 'boss'),
            ('Aw', 'analyst with write permission'),
            #('Ar', 'analyst with read permission')
            )
    
class ProjectUserForm(ModelForm):
    
    role = forms.ChoiceField(choices=ROLE, widget=forms.RadioSelect)
    def __init__(self,*args,**kwargs):
        super (ProjectUserForm,self ).__init__(*args,**kwargs) # populates the post
        self.fields['who'].label_from_instance = lambda obj: "%s" % obj.user_name()
    class Meta:
        model = ProjectUser
        
        fields = ['comment', 'who']
        widgets = {
            'comment': Textarea(attrs={'cols': 40, 'rows': 5}),
        }
        
class ProjectPlanForm(ModelForm):
    class Meta:
        model = ProjectComment
        fields = ['comment']
        widgets = {
            'comment': Textarea(attrs={'cols': 70, 'rows': 5}),
        }
class ProjectEditCommForm(ModelForm):
    class Meta:
        model = ProjectComment
        fields = ['comment']
        widgets = {
            'comment': Textarea(attrs={'cols': 24, 'rows': 7}),
        }
        
class CommentForm(ModelForm):
    
    class Meta:
        model = ProjectComment
        fields = ['comment', 'show']
        widgets = {
            'comment': Textarea(attrs={'cols': 80, 'rows': 10}),
        }

#file forms
class InType(forms.Form):
    obj_in = forms.CharField(label='in types', max_length=1000, widget=forms.Textarea(attrs={'cols': 60, 'rows': 5})) 
    
class InTypeSmall(forms.Form):
    obj_in_s = forms.CharField(label='in types small', max_length=1000, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))

class OutType(forms.Form):
    obj_out = forms.CharField(label='out types', max_length=1000, widget=forms.Textarea(attrs={'cols': 60, 'rows': 5}))
    
class OutTypeSmall(forms.Form):
    obj_out_s = forms.CharField(label='out types small', max_length=1000, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
   
class NameFileForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(NameFileForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].required = True
            
    class Meta:
        model = File
        fields = ['ad_name']
        
class UploadFileForm(forms.Form):
    file = forms.FileField()
    
class UploadFileForm(ModelForm):
    class Meta:
        model = Picture
        fields = ['file', 'slug']
        
class FileUserForm(ModelForm):
    
    def __init__(self,*args,**kwargs):
        queryset = kwargs.pop('queryset')
        super (FileUserForm,self ).__init__(*args,**kwargs) # populates the post
        self.fields['user'].queryset = queryset
        self.fields['user'].label_from_instance = lambda obj: "%s" % obj.user_name()
    class Meta:
        model = FileUser
        
        fields = ['comment', 'user']
        widgets = {
            'comment': Textarea(attrs={'cols': 40, 'rows': 5}),
        }
        
class FileCommentForm(ModelForm):
    
    class Meta:
        model = FileComment
        fields = ['comment', 'show']
        widgets = {
            'comment': Textarea(attrs={'cols': 80, 'rows': 10}),
        }
        
class FileCommentForm2(ModelForm):
    
    class Meta:
        model = FileComment
        fields = ['comment', 'show']
        widgets = {
            'comment': Textarea(attrs={'cols': 45, 'rows': 10}),
        }

class UploadFileForm2(ModelForm):
     
    class Meta:
        model = File
        fields = ['file', 'slug']
        
class FileDictForm(ModelForm):
     
    class Meta:
        model = FileDict
        fields = ['key', 'value']
        
class RegisterFileNameForm(forms.Form):
    name = forms.CharField(label='File name', max_length=100)
        
#service form
class ServiceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].required = True
            
    class Meta:
        model = Service
        fields = ['name']
        
class ServiceCommForm(ModelForm):
    class Meta:
        model = ServiceComment
        fields = ['comment']
        widgets = {
            'comment': Textarea(attrs={'cols': 40, 'rows': 6}),
        }
        
class ServiceUserForm(ModelForm):
    def __init__(self,*args,**kwargs):
        queryset = kwargs.pop('queryset')
        super (ServiceUserForm,self ).__init__(*args,**kwargs) # populates the post
        self.fields['user'].queryset = queryset
        self.fields['user'].label_from_instance = lambda obj: "%s" % obj.user_name()
    class Meta:
        model = ServiceUser
        
        fields = ['comment', 'user']
        widgets = {
            'comment': Textarea(attrs={'cols': 40, 'rows': 5}),
        }

class ParamGroupNameForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ParamGroupNameForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].required = True
    class Meta:
        model = ParamGroup
        fields = ['name']
        
class Params(forms.Form):
    obj_param = forms.CharField(label='parameters', required = True, max_length=1000, widget=forms.Textarea(attrs={'cols': 60, 'rows': 20}))
    
    #validate parameters
    def clean(self):
        cleaned_data = self.cleaned_data
        obj = cleaned_data.get('obj_param', None)
        s = StringIO(obj)
        for line in s:
            p = line.split(";")
            par_type = p[0]
            if par_type != "N" and par_type != "F" and par_type != "O": 
                error_msg = u'Wrong parameter type'
                self._errors['obj_param'] = self.error_class([error_msg])
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
                if v_min != None and float(value) < float(v_min):
                    error_msg = u'Value error: {0} is smaller than {1}'.format(value, v_min)
                    self._errors['obj_param'] = self.error_class([error_msg])
                elif v_max != None and float(value) > float(v_max):
                    error_msg = u'Value error: {0} is greater than {1}!'.format(value, v_max)
                    self._errors['obj_param'] = self.error_class([error_msg])
        return cleaned_data
        
class ParamCommForm(ModelForm):
    
    class Meta:
        model = ParamsComment
        fields = ['comment']
        widgets = {
            'comment': Textarea(attrs={'cols': 66, 'rows': 10}),
        }
        
class ParamForm(ModelForm):
    
    class Meta:
        model = Param
        fields = ['name', 'value', 'v_min', 'v_max', 'comment', 'par_type']
        widgets = {
            'name': Textarea(attrs={'cols': 10, 'rows': 1}),
            'comment': Textarea(attrs={'cols': 15, 'rows': 5}),
            'v_min': NumberInput(attrs={'class': 'small_input'}),
            'v_max': NumberInput(attrs={'class': 'small_input'}),
            'value': NumberInput(attrs={'class': 'small_input'}),
        }
        
class ParamTextForm(ModelForm):
    
    class Meta:
        model = Param
        fields = ['name', 'value', 'comment']
        widgets = {
            'name': Textarea(attrs={'cols': 10, 'rows': 1}),
            'comment': Textarea(attrs={'cols': 15, 'rows': 5}),
            'value': Textarea(attrs={'cols': 10, 'rows': 1}),
        }
        
class TextForm(forms.Form):
    text = forms.CharField(max_length=100000, widget=forms.Textarea(attrs={'cols': 50, 'rows': 20})) 

class CommitForm(forms.Form):
    commit = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'cols': 50, 'rows': 3}))

class ModuleParamForm(ModelForm):
    
    def __init__(self,service,*args,**kwargs):
        super (ModuleParamForm,self ).__init__(*args,**kwargs)
        self.fields['param'].queryset = ParamGroup.objects.filter(is_active = True, service_params=service)
        self.fields['param'].label_from_instance = lambda obj: "%s" % obj.name
        
    class Meta:
        model = Module
        fields = ['param']

        widgets = {
                    'param': Select(attrs={'class':'param_choice', 'onchange':'show_params(this)'}),
                }
                
class ParamForm2(ModelForm):
    
    def __init__(self, *args,**kwargs):
        project = get_object_or_404(Project, pk = kwargs.pop('project_id'))
        super (ParamForm2,self ).__init__(*args,**kwargs)
        param = self.instance
        if param != None and param.value:
            ext = "." + param.value
            self.fields['file'].queryset = File.objects.filter(is_active = True, file_project__is_active = True, file_project__project = project, ext = ext)
        else:
            self.fields['file'].queryset = File.objects.filter(is_active = True, file_project__is_active = True, file_project__project = project)
        self.fields['file'].label_from_instance = lambda obj: "%s" % obj.ad_name
        
        if param.par_type == "O":
            self.fields['value'] = forms.CharField()
            
    class Meta:
        model = Param
        fields = ['name', 'value', 'v_min', 'v_max', 'comment', 'file', 'par_type']
        widgets = {
            'value': NumberInput(attrs={'class': 'small_input'}),
        }
        
class ModuleCommentForm(ModelForm):
    
    class Meta:
        model = ModuleComment
        fields = ['comment']
        widgets = {
            'comment': Textarea(attrs={'cols': 50, 'rows': 5}),
        }

#module form
class ModuleForm(ModelForm):
    def __init__(self,service,*args,**kwargs):
        super (ModuleForm,self ).__init__(*args,**kwargs)
        self.fields['init'].queryset = File.objects.filter(is_active = True, file_code__is_active = True, file_code__service_init__name = service.name)
        self.fields['init'].label_from_instance = lambda obj: "%s" % obj.code_name()
        self.fields['code'].queryset = File.objects.filter(is_active = True, file_code__is_active = True, file_code__service_code__name = service.name)
        intt = File.objects.filter(is_active = True, file_code__is_active = True, file_code__service_init__name = service.name)
        tmp = File.objects.filter(is_active = True, file_code__is_active = True, file_code__service_code__name = service.name)
        self.fields['code'].label_from_instance = lambda obj: "%s" % obj.code_name()
        for key in self.fields:
            self.fields[key].required = True
        
    class Meta:
        model = Module
        fields = ['name', 'init', 'code']

#comment forms
class CommentForm(forms.Form):
    text = forms.CharField(label='comment', max_length=10000)

#analysis forms
class NewAnalysisForm(forms.Form):
    program = forms.CharField(label='Program name', max_length=100)
    file = forms.CharField(label='File name', max_length=100)
    
#currently not used
class EditUserExtForm(ModelForm):
    class Meta:
        model = UserExtension
        fields = ['first_name', 'last_name', 'email', 'about', 'department', 'company', 'tel', 'cell']
        widgets = {
            'about': Textarea(attrs={'cols': 45, 'rows': 5}),
        }
        
class GroupForm(ModelForm):
    
    class Meta:
        model = Group
        fields = ['name']

class GroupDictForm(ModelForm):
    
    class Meta:
        model = GroupDict
        fields = ['key', 'value']
        
class GroupDescForm(ModelForm):
    
    class Meta:
        model = GroupComment
        fields = ['comment']
        
class GroupCommForm(ModelForm):
    
    class Meta:
        model = GroupComment
        fields = ['comment', 'show']
        labels = {
            'show': "Show comment to others",
        }
        
class GroupUserForm(ModelForm):
    
    def __init__(self,*args,**kwargs):
        super (GroupUserForm,self ).__init__(*args,**kwargs) # populates the post
        self.fields['user'].label_from_instance = lambda obj: "%s" % obj.user_name()
    class Meta:
        model = GroupUser
        
        fields = ['comment', 'user']

#formsets
class BaseLinkFormSet2(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
    
        comment = []
        user = []
    
        for form in self.forms:
            print("FORMA: ", form)
            if form.cleaned_data:
                comment = form.cleaned_data['comment']
                user = form.cleaned_data['user']
                
class BaseLinkFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
    
        comment = []
        who = []
        role = []
    
        for form in self.forms:
            if form.cleaned_data:
                comment = form.cleaned_data['comment']
                who = form.cleaned_data['who']
                role = form.cleaned_data['role']
    
class CommentFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
    
        comment = []
        show = []
    
        for form in self.forms:
            if form.cleaned_data:
                comment = form.cleaned_data['comment']
                show = form.cleaned_data['show']
            
class FileDictFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
    
        key = []
        value = []
    
        for form in self.forms:
            if form.cleaned_data:
                key = form.cleaned_data['key']
                value = form.cleaned_data['value'] 
