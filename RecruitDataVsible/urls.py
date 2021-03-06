"""JobDataViewer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.contrib import admin
from RecruitDataVsible import settings
from django.conf.urls import url, include
from django.urls import path
from dataView import views

from django.views import static


urlpatterns = [
    url(r'^$', views.login),
    url(r'^admin/', admin.site.urls),
    url(r'^login/', views.login),
    url(r'^search/', include('haystack.urls')),
    # path('page/index_i.html', views.pageConvert1),

    url(r'^static/(?P<path>.*)$', static.serve,
      {'document_root': settings.STATIC_ROOT}, name='static'),

    path('page/<pageName>',views.pageConvert),
    path('job/getJobsInfo',views.getJobInfos),
    path('job/getSpiderInfo',views.getSpiderInfo),

    url(r'^static/(?P<path>.*)$', static.serve,
      {'document_root': settings.STATIC_ROOT}, name='static'),

    path('job/jobTypeCountOfCity', views.getReplyTypeCountByTime),
    path('job/getEducationAndExperienceOfCity', views.getEducationAndExperienceOfCity),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
