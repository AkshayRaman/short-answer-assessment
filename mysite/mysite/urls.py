from django.conf.urls import patterns, include, url
from django.contrib import admin

from django.views.static import * 
from django.conf import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'studentauth.views.login_user', name='login'),
    url(r'^view_page/$', 'studentauth.views.view_page'),
    url(r'^logout/$', 'studentauth.views.logout_user', name='logout'),
    url(r'^submit/$', 'studentauth.views.submit', name='submit'),
    url(r'^correct/$', 'assessment.views.correct_answers', name='correct'),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
