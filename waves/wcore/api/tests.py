from __future__ import unicode_literals

import logging
import random
import string

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from waves.wcore.adaptors.const import JobStatus
from waves.wcore.models import Job, get_service_model, Runner
from waves.wcore.models.const import ParamType
from waves.wcore.tests.base import BaseTestCase

Service = get_service_model()

logger = logging.getLogger(__name__)


class BaseAPITestCase(APITestCase, BaseTestCase):
    fixtures = ['waves/wcore/tests/fixtures/users.json', 'waves/wcore/tests/fixtures/services.json']

    def create_job_inputs_for_submission(self, submission_data):
        submission = submission_data or {}
        job_inputs_params = {}
        i = 0
        for name in submission['inputs']:
            logger.info('name %s ', name)
            submission_input = submission['inputs'][name]
            if submission_input['type'] == ParamType.TYPE_FILE:
                i += 1
                job_input_data = self.create_test_file(name, i)
                job_inputs_params[name] = job_input_data
                logger.debug('file input %s', job_input_data)
            elif submission_input['type'] == ParamType.TYPE_INT:
                job_input_data = int(random.randint(0, 199))
                job_inputs_params[name] = job_input_data
                logger.debug('number input%s', job_input_data)
            elif submission_input['type'] == ParamType.TYPE_DECIMAL:
                job_input_data = int(random.randint(0, 199))
                job_inputs_params[name] = job_input_data
                logger.debug('number input%s', job_input_data)
            elif submission_input['type'] == ParamType.TYPE_BOOLEAN:
                job_input_data = random.randrange(100) < 50
                job_inputs_params[name] = job_input_data
            elif submission_input['type'] == ParamType.TYPE_TEXT:
                job_input_data = ''.join(random.sample(string.letters, 15))
                job_inputs_params[name] = job_input_data
                logger.debug('text input %s', job_input_data)
            elif submission_input['type'] == ParamType.TYPE_LIST:
                job_input_data = ''.join(random.sample(string.letters, 15))
                job_inputs_params[name] = job_input_data
            else:
                job_input_data = ''.join(random.sample(string.letters, 15))
                logger.warn('default ???? %s %s', job_input_data, submission_input['type'])
                job_inputs_params[name] = job_input_data
        logger.debug('Job inputs data %s', job_inputs_params)
        return job_inputs_params


class WavesAPIV1TestCase(BaseAPITestCase):
    def test_api_root(self):
        api_root = self.client.get(reverse('wapi:v1:api-root'))
        self.assertEqual(api_root.status_code, status.HTTP_200_OK)
        logger.debug('Results: %s ', api_root.data)
        self.assertIn('services', api_root.data.keys())
        self.assertIn('jobs', api_root.data.keys())
        tool_list = self.client.get(api_root.data['services'], format='json')
        self.assertIsNotNone(tool_list.data)
        logger.debug('Tools list length %s' % len(tool_list.data))
        logger.debug(tool_list.data)
        for service in tool_list.data:
            self.assertIn('url', service.keys())
            logger.debug('ServiceTool url: %s', service['url'])
            tool_details = self.client.get(service['url'], format='json')
            logger.debug('ServiceTool: %s', tool_details.data['name'])
            self.assertIsNotNone(tool_details.data['default_submission_uri'])

    def test_create_job_api(self):
        """
        Ensure for any service, we can create a job according to retrieved parameters
        """
        import random
        import string
        logger.debug('Retrieving service-list from ' + reverse('wapi:v2:waves-services-list'))
        logger.debug('1 %s service loaded ' % Service.objects.count())
        expected_jobs = 0
        for service in Service.objects.all():
            logger.debug("'%s' (%s) is available with %s submission(s)" % (
                service.name, service.get_status_display(), service.submissions_api.count()))
            expected_jobs += service.submissions_api.count()
        tool_list = self.client.get(reverse('wapi:v1:waves-services-list'), format="json")
        self.assertEqual(tool_list.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(tool_list)
        logger.debug(tool_list.data)
        for servicetool in tool_list.data:
            logger.debug('Creating job submission for %s %s', servicetool['name'], str(servicetool['version']))
            # for each servicetool retrieve inputs
            self.assertIsNotNone(servicetool['url'])
            detail = self.client.get(servicetool['url'])
            # logger.debug('Details data: %s', detail)
            tool_data = detail.data
            self.assertTrue('submissions' in tool_data)
            i = 0
            input_datas = {}
            submissions = tool_data.get('submissions')
            logger.debug(submissions)
            for submission in submissions:
                for job_input in submission['inputs']:
                    if job_input['type'] == ParamType.TYPE_FILE:
                        i += 1
                        input_data = self.create_test_file(job_input['name'], i)
                        logger.debug('file input %s', input_data)
                    elif job_input['type'] == ParamType.TYPE_INT:
                        input_data = int(random.randint(0, 199))
                        logger.debug('number input%s', input_data)
                    elif job_input['type'] == ParamType.TYPE_DECIMAL:
                        input_data = int(random.randint(0, 199))
                        logger.debug('number input%s', input_data)
                    elif job_input['type'] == ParamType.TYPE_BOOLEAN:
                        input_data = random.randrange(100) < 50
                    elif job_input['type'] == ParamType.TYPE_TEXT:
                        input_data = ''.join(random.sample(string.letters, 15))
                        logger.debug('text input %s', input_data)
                    elif job_input['type'] == ParamType.TYPE_LIST:
                        input_data = ''.join(random.sample(string.letters, 15))
                    else:
                        input_data = ''.join(random.sample(string.letters, 15))
                        logger.warn('default ???? %s %s', input_data, job_input['type'])
                    input_datas[job_input['name']] = input_data

                logger.debug('Data posted %s', input_datas)
                logger.debug('To => %s', submission['submission_uri'])
                self.login("api_user")
                response = self.client.post(submission['submission_uri'],
                                            data=input_datas,
                                            format='multipart')
                logger.debug(response)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                job = Job.objects.all().order_by('-created').first()
                logger.debug(job)
        for job in Job.objects.all():
            logger.debug('Job %s ', job)
            self.assertEqual(job.status, JobStatus.JOB_CREATED)
            self.assertEqual(job.job_history.count(), 1)
            self.assertIsNotNone(job.job_inputs)
            self.assertIsNotNone(job.outputs)
            self.assertGreaterEqual(job.outputs.count(), 2)
        self.assertEqual(expected_jobs, Job.objects.count())

    def test_update_job(self):
        pass

    def test_delete_job(self):
        pass

    def test_job_error(self):
        pass

    def test_get_status(self):
        pass


class WavesAPIV2TestCase(BaseAPITestCase):
    def test_api_root(self):
        api_root = self.client.get(reverse('wapi:v2:api-root'))
        self.assertEqual(api_root.status_code, status.HTTP_200_OK)
        logger.debug('Results: %s ', api_root.data)
        self.assertIn('services', api_root.data.keys())
        self.assertIn('jobs', api_root.data.keys())
        tool_list = self.client.get(api_root.data['services'], format='json')
        self.assertIsNotNone(tool_list.data)
        logger.debug(tool_list.data)
        for service in tool_list.data:
            self.assertIn('url', service.keys())
            logger.debug('ServiceTool url: %s', service['url'])
            tool_details = self.client.get(service['url'], format='json')
            logger.debug('ServiceTool: %s', tool_details.data['name'])
            self.assertIsNotNone(tool_details.data['submissions'])

    def test_create_job_api(self):
        """
        Ensure for any service, we can create a job according to retrieved parameters
        """
        logger.debug('Retrieving service-list from ' + reverse('wapi:v2:waves-services-list'))
        logger.debug('1 %s service loaded ' % Service.objects.count())
        expected_jobs = 0
        for service in Service.objects.all():
            logger.debug("'%s' (%s) is available with %s submission(s)" % (
                service.name, service.get_status_display(), service.submissions_api.count()))
            expected_jobs += service.submissions_api.count()
        tool_list = self.client.get(reverse('wapi:v2:waves-services-list'), format="json")
        self.assertEqual(tool_list.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(tool_list)
        logger.debug(tool_list.data)
        for servicetool in tool_list.data:
            logger.debug('Creating job submission for %s %s', servicetool['name'], str(servicetool['version']))
            # for each servicetool retrieve inputs
            self.assertIsNotNone(servicetool['url'])
            detail = self.client.get(servicetool['url'])
            # logger.debug('Details data: %s', detail)
            tool_data = detail.data
            self.assertTrue('submissions' in tool_data)
            submissions = tool_data.get('submissions')
            logger.debug(submissions)
            for submission in submissions:
                submission_url = submission['url']
                submission_srv = self.client.get(submission_url)
                self.assertEqual(submission_srv.status_code, status.HTTP_200_OK)
                submission_data = submission_srv.data
                logger.debug(submission_srv.data)
                job_inputs_params = self.create_job_inputs_for_submission(submission_data)
                logger.debug('Submit To => %s', submission_data['jobs'])
                response = self.client.post(submission_data['jobs'],
                                            data=job_inputs_params,
                                            format='multipart')
                logger.debug(response)
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
                self.login('api_user')
                response = self.client.post(submission_data['jobs'],
                                            data=job_inputs_params,
                                            format='multipart')
                logger.debug(response)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                job = Job.objects.get(slug=response.data['slug'])
                self.assertEqual(job.email_to, 'wavesapi@waves.wcore.fr')
                logger.debug(job)
        for job in Job.objects.all():
            logger.debug('Job %s ', job)
            self.assertEqual(job.status, JobStatus.JOB_CREATED)
            self.assertEqual(job.job_history.count(), 1)
            self.assertIsNotNone(job.job_inputs)
            self.assertIsNotNone(job.outputs)
            self.assertGreaterEqual(job.outputs.count(), 2)
        self.assertEqual(expected_jobs, Job.objects.count())

    def test_cancel_job(self):
        """
        Test job cancel service
        """
        runner = Runner.objects.create(name="Mock Runner",
                                       clazz='waves.wcore.adaptors.mocks.MockJobRunnerAdaptor')

        sample_job = self.create_random_job(runner=runner, user=self.users['api_user'])
        test_cancel = self.client.post(reverse('wapi:v2:waves-jobs-cancel', kwargs={'unique_id': sample_job.slug}))
        self.assertEqual(test_cancel.status_code, status.HTTP_401_UNAUTHORIZED)
        self.login("api_user")
        test_cancel = self.client.post(reverse('wapi:v2:waves-jobs-cancel', kwargs={'unique_id': sample_job.slug}))
        self.assertEqual(test_cancel.status_code, status.HTTP_202_ACCEPTED)
        db_job = Job.objects.get(slug=sample_job.slug)
        self.assertEqual(db_job.status, JobStatus.JOB_CANCELLED)
        test_cancel = self.client.put(reverse('wapi:v2:waves-jobs-cancel', kwargs={'unique_id': sample_job.slug}))
        self.assertEqual(test_cancel.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_job(self):
        runner = Runner.objects.create(name="Mock Runner",
                                       clazz='waves.wcore.adaptors.mocks.MockJobRunnerAdaptor')

        sample_job = self.create_random_job(service=self.create_random_service(runner), user=self.users['api_user'])
        test_delete = self.client.delete(reverse('wapi:v2:waves-jobs-detail', kwargs={'unique_id': sample_job.slug}))
        self.assertEqual(test_delete.status_code, status.HTTP_401_UNAUTHORIZED)
        self.login('api_user')
        test_delete = self.client.delete(reverse('wapi:v2:waves-jobs-detail', kwargs={'unique_id': sample_job.slug}))
        self.assertEqual(test_delete.status_code, status.HTTP_204_NO_CONTENT)

    def test_missing_params(self):
        tool_list = self.client.get(reverse('wapi:v2:waves-services-list'), format="json")
        service_tool = tool_list.data[0]
        default_submission = self.client.get(service_tool['submissions'][0]['url'])
        job_params = self.create_job_inputs_for_submission(default_submission.data)
        job_params.pop('input_file')
        self.login("api_user")
        response = self.client.post(default_submission.data['jobs'],
                                    data=job_params,
                                    format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print response
        self.assertDictContainsSubset(response.data, {u'input_file': [u'File Input (:input_file:) is required field']})

    def test_token_auth(self):

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.users['api_user'].waves_user.key)
        response = self.client.get(reverse("wapi:v2:waves-jobs-list"))
        self.assertEqual(response.status_code, 200)

    def test_api_key_auth(self):
        response = self.client.get(reverse("wapi:v2:waves-jobs-list") + "?api_key=" + self.users['api_user'].waves_user.key)
        self.assertEqual(response.status_code, 200)