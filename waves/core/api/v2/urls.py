from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from views import jobs, services
from waves.core.views.jobs import JobOutputView, JobInputView

# API router setup
router = routers.DefaultRouter()
# Services URIs configuration
router.register(prefix=r'services',
                viewset=services.ServiceViewSet,
                base_name='waves-services')
# Jobs URIs configuration
router.register(prefix=r'jobs',
                viewset=jobs.JobViewSet,
                base_name='waves-jobs')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^services/(?P<service>[^/.]+)/submissions/(?P<api_name>[^/.]+)/$',
        services.ServiceJobSubmissionView.as_view(), name='waves-services-submissions'),
    url(r'^services/(?P<service>[^/.]+)/submissions/(?P<api_name>[^/.]+)/form/',
        services.ServiceJobSubmissionViewForm.as_view(), name='waves-services-submissions-form'),
    url(r'^jobs/outputs/(?P<slug>[\w-]+)/$', JobOutputView.as_view(), name="waves-job-output"),
    url(r'^jobs/inputs/(?P<slug>[\w-]+)/$', JobInputView.as_view(), name="waves-job-input"),
]
