from django.conf.urls import patterns, url
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views
from .views import (
        jQueryVersionCreateView,
        PictureCreateView, PictureDeleteView, PictureListView, NewProject, FileView
        )
        
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^sign/$', views.SignView.as_view(), name='sign'),
    url(r'^my_site/$', views.MySite.as_view(), name='my site'),
    url(r'^new_project/$', views.NewProject.as_view(), name='new project'),
    url(r'^archive/project/(?P<project_id>[0-9_]+)/$', views.ProjectView.as_view(), name='archive_project'),
    url(r'^archive/file/(?P<file_id>[0-9]+)/$', views.FileView.as_view(), name='archive_file'),
    url(r'^archive/service/(?P<service_id>[0-9]+)/$', views.ServiceView.as_view(), name='archive_service'),
    url(r'^show_file/(?P<file_id>[0-9]+)/$',  views.FileView.as_view(), name='file_view'),
    url(r'^show_file/(?P<file_id>[0-9]+)/(?P<label>[a-zA-Z]+)/$',  views.FileView.as_view(), name='file_view'),
    url(r'^new_service/$', views.NewService.as_view(), name='new service'),
    url(r'^new_service_2/(?P<service_id>[0-9]+)/$', views.NewService2.as_view(), name='new_service_2'),
    url(r'^show_service/(?P<service_id>[0-9]+)/$', views.ServiceView.as_view(), name='service_view'),
    url(r'^show_service/(?P<service_id>[0-9]+)/(?P<label>[a-zA-Z]+)/$', views.ServiceView.as_view(), name='service_view'),
    url(r'^show_project/(?P<project_id>[0-9_]+)/$',  views.ProjectView.as_view(), name='project_view'),
    url(r'^show_project/(?P<project_id>[0-9_]+)/(?P<label>[a-zA-Z]+)/$',  views.ProjectView.as_view(), name='project_view'),
    url(r'^show_project/([0-9_]+)/my_div.html$', views.ShowDivView, name='show_div'),
    url(r'^show_project/(?P<project_id>[0-9_]+)/my_div.html$', views.ShowDivView, name='show_div'),
    url(r'^show_project/(?P<project_id>[0-9_]+)/(?P<label>[a-zA-Z]+)/my_div.html$', views.ShowDivView, name='show_div'),
    url(r'^show_analysis/(?P<analysis_id>[0-9]+)/$',  views.AnalysisView.as_view(), name='analysis_view'),
    url(r'^show_analysis/(?P<analysis_id>[0-9]+)/content_analysis.html$',  views.AnalysisContentView, name='analysis_content_view'),

    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^log_out/$', views.log_out, name='log out'),
    #url(r'^show_group/(?P<group_id>[0-9]+)/$',  views.GroupView.as_view(), name='group_view'),
    url(r'^upload/$', views.upload_file, name='upload'),
    url(r'^show_service/$', views.ServiceView.as_view(), name='service_view'),
    url(r'^show_service/(?P<service_id>[0-9]+)/remove/(?P<delete_id>[0-9]+)/$', views.ServiceView.as_view(), name='service_view'),
    url(r'^show_project/(?P<project_id>[0-9_]+)/remove/(?P<delete_id>[0-9]+)/$', views.ProjectView.as_view(), name='project_view'),
    url(r'^show_project/(?P<project_id>[0-9_]+)/com/(?P<com_id>[0-9]+)/$', views.ProjectView.as_view(), name='project_view'),
    url(r'^change_password/', auth_views.password_change),
    url(r'^change_password/done', auth_views.password_change_done),
    url(r'^new/$', PictureCreateView.as_view(), name='upload-new'),
    url(r'^jquery-ui/$', jQueryVersionCreateView.as_view(), name='upload-jquery'),
    url(r'^delete/(?P<pk>\d+)$', PictureDeleteView.as_view(), name='upload-delete'),
    url(r'^view/$', views.MySite.as_view(), name='upload-view'),
]

urlpatterns += staticfiles_urlpatterns()
