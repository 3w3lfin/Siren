from django import template
from django.contrib.auth.models import User
register = template.Library()
from django.shortcuts import render, get_object_or_404 
from ..models import Analysis, ProjectComment, Module, Project, File, ParamsComment, Param
from ..forms import ProjectEditCommForm, ParamForm2, ModuleParamForm, ParamTextForm, ModuleForm, TextForm, ParamCommForm, ParamForm, ProjectPlanForm
from django.db.models.aggregates import Max
from django.forms import modelformset_factory
from django.forms import ModelForm, Textarea, NumberInput,Select

#render upload div
@register.simple_tag
def upload_js():
    return """
<!-- The template to display files available for upload -->
<script id="template-upload" type="text/x-tmpl">
{% for (var i=0, file; file=o.files[i]; i++) { %}
    <tr class="template-upload fade">
        <td>
            <span class="preview"></span>
        </td>
        <td>
            <p class="name">{%=file.name%}</p>
            {% if (file.error) { %}
                <div><span class="label label-important">{%=locale.fileupload.error%}</span> {%=file.error%}</div>
            {% } %}
        </td>
        <td>
            <p class="size">{%=o.formatFileSize(file.size)%}</p>
            {% if (!o.files.error) { %}
                <div class="progress progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><div class="progress-bar progress-bar-success" style="width:0%;"></div></div>
            {% } %}
        </td>
        <td>
            {% if (!o.files.error && !i && !o.options.autoUpload) { %}
                <button class="btn btn-primary start">
                    <i class="glyphicon glyphicon-upload"></i>
                    <span>{%=locale.fileupload.start%}</span>
                </button>
            {% } %}
            {% if (!i) { %}
                <button class="btn btn-warning cancel">
                    <i class="glyphicon glyphicon-ban-circle"></i>
                    <span>{%=locale.fileupload.cancel%}</span>
                </button>
            {% } %}
        </td>
    </tr>
{% } %}
</script>
<!-- The template to display files available for download -->
<script id="template-download" type="text/x-tmpl">
{% for (var i=0, file; file=o.files[i]; i++) { %}
    <tr class="template-download fade">
        <td>
            <span class="preview">
                {% if (file.thumbnailUrl) { %}
                    <a href="{%=file.url%}" title="{%=file.name%}" download="{%=file.name%}" data-gallery><img src="{%=file.thumbnailUrl%}"></a>
                {% } %}
            </span>
        </td>
        <td>
            <p class="name">
                <a href="{%=file.url%}" title="{%=file.name%}" download="{%=file.name%}" {%=file.thumbnailUrl?'data-gallery':''%}>{%=file.name%}</a>
            </p>
            {% if (file.error) { %}
                <div><span class="label label-important">{%=locale.fileupload.error%}</span> {%=file.error%}</div>
            {% } %}
        </td>
        <td>
            <span class="size">{%=o.formatFileSize(file.size)%}</span>
        </td>
        <td>
            <button class="btn btn-danger delete" data-type="{%=file.deleteType%}" data-url="{%=file.deleteUrl%}"{% if (file.deleteWithCredentials) { %} data-xhr-fields='{"withCredentials":true}'{% } %}>
                <i class="glyphicon glyphicon-trash"></i>
                <span>{%=locale.fileupload.destroy%}</span>
            </button>
            <input type="checkbox" name="delete" value="1" class="toggle">
        </td>
    </tr>
{% } %}
</script>
"""

#render plan div
@register.simple_tag
def get_plan_html(plans, ancestor=True):
    html = ""
    for plan in plans:
        #first time only basic comments
        if not (ancestor and plan.child):
            plan_class = plan.get_p_class_display()
            #plan_header = plan.header if plan.header else ""
            if plan.p_class == "P":
                plan_span = """
                    <span onclick="changeClassError({0})" class="{0}_plan1 glyphicon glyphicon-remove glyphicon-right glyphicon-red"></span>
                    <span onclick="changeClassOk({0})" class="{0}_plan1 glyphicon glyphicon-ok glyphicon-right glyphicon-green"></span>
                    <span style="display: none;" onclick="changeClassError({0})" class="{0}_plan2 glyphicon glyphicon-repeat glyphicon-right glyphicon-blue"></span>
                """.format(plan.id)
            else:
                plan_span = """
                    <span style="display: none;" onclick="changeClassError({0})" class="{0}_plan1 glyphicon glyphicon-remove glyphicon-right glyphicon-red"></span>
                    <span style="display: none;" onclick="changeClassOk({0})" class="{0}_plan1 glyphicon glyphicon-ok glyphicon-right glyphicon-green"></span>
                    <span onclick="changeClassError({0})" class="{0}_plan2 glyphicon glyphicon-repeat glyphicon-right glyphicon-blue"></span>
                """.format(plan.id)
                
            html += """
                <li id="plan_{0}" class="placeholder-children col-xs-12" data-id="{0}" data-name="{0}">
                    <div id="{0}" class="panel no_pad col-xs-12 {1}">
                        <div class="panel-heading col-xs-12 ">
                            <div class="panel_left col-xs-12 ">
                                <div class="col-xs-9 top_m"> {3} </div>
                                <div class="col-xs-3">
                                    
                                        <span onclick="removePlan({0})" class="glyphicon glyphicon-right glyphicon-black glyphicon-trash"></span>
                                        {2}
                                    
                                 </div>
                            </div>
                        </div>
                    </div>
                    <div class="left_plan"></div>
                <ol>
            """.format(plan.id, plan_class, plan_span, plan.comment)
            children = ProjectComment.objects.filter(child = plan)
            print(plan.id, plan.child)
            if children: 
                html += get_plan_html(children, False)
            html += "</ol> </li> <ol></ol>"
    return html

#get people who can see file
@register.simple_tag
def get_obj(file):
    obj = User.objects.filter(file_user__file = file, file_user__role = 'X', file_user__is_active = True)
    if not obj:
        return None
    else:
        analysts = ""
        for entry in obj:
            analysts += " "
            analysts += entry.username
        return analysts

#get files belonging group
@register.simple_tag
def get_files(group):
    obj = File.objects.filter(file_group__group = group, file_group__is_active = True)
    if not obj:
        return None
    else:
        files = ""
        for entry in obj:
            files += " "
            files += entry.user_name + entry.ext
        return files

#get creator of group
@register.simple_tag
def get_creator(group):
    obj = get_object_or_404(User, group_user__group = group, group_user__role = 'C', group_user__is_active = True)
    
    if not obj:
        return None
    else:
        return obj.username

#get people who can see group
@register.simple_tag
def get_group_analysts(group):
    obj = User.objects.filter(group_user__group = group, group_user__role = 'X', group_user__is_active = True)
    
    if not obj:
        return None
    else:
        analysts = ""
        for entry in obj:
            analysts += " "
            analysts += entry.username
        return analysts

#get comment form
@register.simple_tag
def get_comm_form(comm):
    try:
        old_comm = ParamsComment.objects.filter(params = comm).values('params').annotate(max_id=Max('id'))
        comm_id = old_comm[0]['max_id']
        param_comm = ParamsComment.objects.get(pk = comm_id)
        param_comm_from = ParamCommForm(instance = param_comm)
    except:
        param_comm_from = ParamCommForm()

    return param_comm_from

#get module comment form
@register.simple_tag
def get_module_form(mod):
    try:
        old_comm = ModuleComment.objects.filter(module = mod).values('module').annotate(max_id=Max('id'))
        comm_id = old_comm[0]['max_id']
        old_comm = ModuleComment.objects.get(pk = comm_id)
        new_module_com = ModuleCommentForm(instance = old_comm)
    except:
        new_module_com = ModuleCommentForm()

    return new_module_com
 
#get module form
@register.simple_tag
def get_init_module_form(service):
    new_module = ModuleForm(service)
    return new_module
 
#get project comment form
@register.simple_tag
def get_pro_comment(com):
    edit_comm = ProjectEditCommForm(instance = com)
    return edit_comm

#get module parameters form
@register.simple_tag
def get_param_module_form(service):
    new_module = ModuleParamForm(service)
    return new_module
    
#get parameter form
@register.simple_tag
def get_param_form(param):
    if param.par_type == "N":
        param_form = ParamForm(instance = param)
    else:
        param_form = ParamTextForm(instance = param)
    return param_form

@register.simple_tag
def get_param_limit_form(param, project_name):
    print(".")

#get parameters formset
@register.simple_tag
def get_param_limit_formset(param_group, project_id):
    param_formset = modelformset_factory(Param, form=ParamForm2)
    param_formset = param_formset(form_kwargs={'project_id': project_id}, queryset=Param.objects.filter(is_active=True, params__name = param_group.name), prefix='param_formset')
    ile = param_formset.total_form_count()
    return param_formset

#get init script form
@register.simple_tag
def get_init_form(init):
    text = init.display_text_file()
    form = TextForm(initial={'text': text})
    return form

#get module analysis 
@register.simple_tag
def get_service(module_id):
    module =  get_object_or_404(Module, pk = module_id)
    analysis = Analysis.objects.filter(module = module)
    return analysis
    
#get service modules
@register.simple_tag
def get_modules(service, project):
    modules = Module.objects.filter(service = service, is_active = True, project_module__project = project)
    return modules
    
#sort data
@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)

#set global context
@register.simple_tag(takes_context=True)
def set_global_context(context, key, value):
    """
    Sets a value to the global template context, so it can
    be accessible across blocks.

    Note that the block where the global context variable is set must appear
    before the other blocks using the variable IN THE BASE TEMPLATE.  The order
    of the blocks in the extending template is not important. 

    Usage::
        {% extends 'base.html' %}

        {% block first %}
            {% set_global_context 'foo' 'bar' %}
        {% endblock %}

        {% block second %}
            {{ foo }}
        {% endblock %}
    """
    print("set ", key, " ", value)
    print(context)
    context.dicts[0][key] = value
    return ''
