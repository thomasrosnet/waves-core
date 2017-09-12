from __future__ import unicode_literals

from uuid import UUID

import swapper
from django.urls import reverse
from django.views import generic

from waves.wcore.forms.services import ServiceSubmissionForm
from waves.wcore.views.services import SubmissionFormView
from waves.wcore.models import Submission, Job

Service = swapper.load_model("wcore", "Service")


class ServiceListView(generic.ListView):
    template_name = "waves/services/services_list.html"
    model = Service
    context_object_name = 'available_services'

    def get_queryset(self):
        return Service.objects.all().prefetch_related('submissions')


class ServiceDetailView(generic.DetailView):
    model = Service
    template_name = 'waves/services/service_details.html'
    context_object_name = 'service'
    queryset = Service.objects.all().prefetch_related('submissions')
    object = None

    def get_context_data(self, **kwargs):
        context = super(ServiceDetailView, self).get_context_data(**kwargs)
        return context

    def get_object(self, queryset=None):
        obj = super(ServiceDetailView, self).get_object(queryset)
        self.object = obj
        if not obj.available_for_user(self.request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied()
        return obj


class JobSubmissionView(ServiceDetailView, SubmissionFormView):
    model = Service
    template_name = 'waves/services/service_form.html'
    form_class = ServiceSubmissionForm

    def get_template_names(self):
        return super(JobSubmissionView, self).get_template_names()

    def get_submissions(self):
        return self.get_object().submissions_web

    def __init__(self, **kwargs):
        super(JobSubmissionView, self).__init__(**kwargs)
        self.job = None
        self.user = None
        self.selected_submission = None

    def get(self, request, *args, **kwargs):
        self.user = self.request.user
        self.selected_submission = self._get_selected_submission()
        return super(JobSubmissionView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('wfront:job_details', kwargs={'slug': self.job.slug})

    def _get_selected_submission(self):
        slug = self.request.POST.get('slug', None)
        if slug is None:
            return self.get_object().default_submission  # Submission.objects.get(default=True, service=)
        else:
            submission = Submission.objects.get(slug=UUID(slug))
            return Submission.objects.get(slug=UUID(slug))


class JobView(generic.DetailView):
    """ Job Detail view """
    model = Job
    slug_field = 'slug'
    template_name = 'waves/jobs/job_detail.html'
    context_object_name = 'job'


class JobListView(generic.ListView):
    """ Job List view (for user) """
    model = Job
    template_name = 'waves/jobs/job_list.html'
    context_object_name = 'job_list'
    paginate_by = 10

    def get_queryset(self):
        """ Retrieve user job """
        return Job.objects.get_user_job(user=self.request.user)