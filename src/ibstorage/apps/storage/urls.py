from django.conf.urls.defaults import *
from django.views.generic.base import TemplateView

urlpatterns = patterns('storage.views',
    url(r'^$', TemplateView.as_view(template_name='index.html')),
    url(r'^list-files/$', 'list_files'),
    url(r'^upload/', 'upload')
)