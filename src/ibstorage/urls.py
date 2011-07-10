
from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views.generic.base import TemplateView

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^{{ project_name }}/', include('{{ project_name }}.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    url(r'^auth/logout/$', 'django.contrib.auth.views.logout', {'next_page':'/'}),
    url(r'^auth/logout/ajax/$', 'storage.views.ajax_logout', name='ajax_logout'),
    url(r'^auth/logged-in/$', TemplateView.as_view(template_name='logged_in.html')),
    url(r'^auth/', include('social_auth.urls')),
    url(r'', include('storage.urls'))
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )

