from django.conf.urls.defaults import *

from storage.views import IndexView

urlpatterns = patterns('storage.views',
    url(r'^$', IndexView.as_view()),
    url(r'^list-files/(?:(?P<page_num>\d+)/)?$', 'list_files', name='list_files'),
    url(r'^upload/$', 'upload'),
    url(r'^file/(?P<id>\d+)/$', 'fileinfo'),
    url(r'^share/(?P<id>\d+)/$', 'share'),
    url(r'^publish/(?P<id>\d+)/$', 'change_publish'),
    url(r'^delete/(?P<id>\d+)/$', 'delete')
)