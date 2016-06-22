import os
from django.conf.urls import patterns, include, url
#from django.contrib import admin
from django_saga_simple_task_manager import settings
from django_saga_simple_task_manager import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'django_saga_simple_task_manager.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),
    # Static files
    url(r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(settings.STATIC_ROOT,'js')}),
    url(r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(settings.STATIC_ROOT,'css')}),
    # Tasks
    url(r'^$', views.IndexView.as_view(), name='tasks'),
    url(r'^tasks/$', views.IndexView.as_view(), name='tasks'),
    url(r'^tasks/(?P<taskId>.*)$', views.task_status, name='task_status'),
    # Submit task
    url(r'^submit/$', views.submit_task, name='submit'),
)
