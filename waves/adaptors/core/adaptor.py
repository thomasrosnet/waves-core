""" Base class for all JobRunnerAdaptor implementation, define main job workflow expected behaviour """
from __future__ import unicode_literals

import logging

import waves.adaptors.core
from waves.adaptors.exceptions.adaptors import *

logger = logging.getLogger(__name__)


class JobAdaptor(object):
    """
    Abstract JobAdaptor class, declare expected behaviour from any WAVES's JobAdaptor dependent ?
    """
    NOT_AVAILABLE_MESSAGE = "Adaptor is currently not available on platform"
    name = 'Abstract Adaptor name'
    #: Remote command for Job execution
    command = None
    #: Defined remote connector, depending on subclass implementation
    connector = None
    #: Some connector need to parse requested job in order to create a remote job
    parser = None
    #: Each Adaptor need a 'protocol' to communicate with remote job execution
    protocol = 'http'
    #: Host
    host = 'localhost'
    #: Remote status need to be mapped with WAVES expected job status
    _states_map = {}

    def __init__(self, *args, **kwargs):
        """ Initialize a adaptor
        Set _initialized value (True or False) if all non default expected params are set
        :raise: :class:`waves.adaptors.exceptions.adaptors.AdaptorInitError` if wrong parameter given as init values
        :param init_params: a dictionary with expected initialization params (retrieved from init_params property)
        :param kwargs: its possible to force connector and _parser attributes when initialize a Adaptor
        :return: a new JobAdaptor object
        """
        self._connected = False
        self.connector = kwargs.get('connector', self.connector)
        self.parser = kwargs.get('parser', self.parser)
        self.command = kwargs.get('command', self.command)
        self.protocol = kwargs.get('protocol', self.protocol)
        self.host = kwargs.get('host', self.host)
        self._initialized = all(value is not None for init_param, value in self.init_params.items())

    """
    def __str__(self):
        return '.'.join([self.__class__.__module__, self.__class__.__name__])
    """

    def init_value_editable(self, init_param):
        """ By default all fields are editable, override this function for your specific needs in your adaptor """
        return True

    @property
    def init_params(self):
        """ Returns expected (required) 'init_params', with default if set at class level
        :return: A dictionary containing expected init params
        :rtype: dict
        """
        return dict(command=self.command, protocol=self.protocol, host=self.host)

    @property
    def connected(self):
        """ Tells whether current remote adaptor object is connected to calculation infrastructure
        :return: True if actually connected / False either
        :rtype: bool
        """
        return self.connector is not None and self._connected is True

    @property
    def available(self):
        return True

    def connect(self):
        """
        Connect to remote platform adaptor
        :raise: :class:`waves.adaptors.exceptions.adaptors.AdaptorConnectException`
        :return: connector reference or raise an
        """
        if not self._initialized:
            # search missing values
            raise AdaptorNotReady(
                "Missing required parameter(s) for initialization: %s " % [init_param for init_param, value in
                                                                           self.init_params.items() if value is None])
        if not self.connected:
            self._connect()
        return self.connector

    def disconnect(self):
        """ Shut down connection to adaptor. Called after job adaptor execution to disconnect from remote
        :raise: :class:`waves.adaptors.exceptions.adaptors.AdaptorConnectException`
        :return: Nothing
        """
        if self.connected:
            self._disconnect()
        self.connector = None
        self._connected = False

    def prepare_job(self, job):
        """ Job execution preparation process, may store prepared data in a pickled object
        :param job: The job to prepare execution for
        :raise: :class:`waves.adaptors.exceptions.RunnerNotReady` if adaptor is not initialized before call
        :raise: :class:`waves.adaptors.exceptions.JobPrepareException` if error during preparation process
        :raise: :class:`waves.adaptors.exceptions.JobInconsistentStateError` if job status is not 'created'
        """
        try:
            assert (job.status <= waves.adaptors.core.JOB_CREATED)
        except AssertionError:
            raise AdaptorJobStateException(job.status, waves.adaptors.core.JOB_CREATED)
        self.connect()
        self._prepare_job(job)
        job.status = waves.adaptors.core.JOB_PREPARED
        return job

    def run_job(self, job):
        """ Launch a previously 'prepared' job on the remote adaptor class
        :param job: The job to launch execution
        :raise: :class:`waves.adaptors.exceptions.RunnerNotReady` if adaptor is not initialized
        :raise: :class:`waves.adaptors.exceptions.JobRunException` if error during launch
        :raise: :class:`waves.adaptors.exceptions.JobInconsistentStateError` if job status is not 'prepared'
        """
        try:
            assert (job.status == waves.adaptors.core.JOB_PREPARED)
        except AssertionError:
            raise AdaptorJobStateException(job.status, waves.adaptors.core.JOB_PREPARED)
        self.connect()
        self._run_job(job)
        job.status = waves.adaptors.core.JOB_QUEUED
        return job

    def cancel_job(self, job):
        """ Cancel a running job on adaptor class, if possible
        :param job: The job to cancel
        :return: The new job status
        :rtype: int
        :raise: :class:`waves.adaptors.exceptions.JobRunException` if error during launch
        :raise: :class:`waves.adaptors.exceptions.JobInconsistentStateError` if job status is not 'prepared'
        """
        try:
            assert (job.status <= waves.adaptors.core.JOB_SUSPENDED)
        except AssertionError:
            raise AdaptorJobStateException(job.status, waves.adaptors.core.STATUS_MAP[0:5])
        self.connect()
        self._cancel_job(job)
        job.status = waves.adaptors.core.JOB_CANCELLED
        return job

    def job_status(self, job):
        """ Return current WAVES Job status
        :param job: current job
        :return: one of `waves.adaptors.STATUS_MAP`
        """
        self.connect()
        status = self._states_map[self._job_status(job)]
        logger.debug('Current remote state %s mapped to %s', self._job_status(job),
                     waves.adaptors.core.STATUS_MAP.get(status, 'Undefined'))
        job.status = status
        return job

    def job_results(self, job):
        """ If job is done, return results
        :param job: current Job
        :return: a list a JobOutput
        """
        self.connect()
        self._job_results(job)
        return job

    def job_run_details(self, job):
        """ Retrive job run details for job
        :param job: current Job
        :return: JobRunDetails object
        """
        self.connect()
        return self._job_run_details(job)

    def dump_config(self):
        """ Create string representation of current adaptor config"""
        str_dump = 'Dump config for %s \n ' % self.__class__
        str_dump += 'Init params:'
        for key, param in self.init_params.items():
            if key.startswith('crypt'):
                value = "*" * len(param)
            else:
                value = getattr(self, key)
            str_dump += ' - %s : %s ' % (key, value)
        extra_dump = self._dump_config()
        return str_dump + extra_dump

    def _connect(self):
        """ Actually do connect to concrete remote job runner platform,
         :raise: `waves.adaptors.exception.AdaptorConnectException` if error
         :return: an instance of concrete connector implementation """
        raise NotImplementedError()

    def _disconnect(self):
        """ Actually disconnect from remote job runner platform
        :raise: `waves.adaptors.exception.AdaptorConnectException` if error """
        raise NotImplementedError()

    def _prepare_job(self, job):
        """ Actually do preparation for job if needed by concrete adaptor.
        For example:
            - prepare and upload input files to remote host
            - set up parameters according to concrete adaptor needs
        :raise: `waves.adaptors.exception.AdaptorException` if error """
        raise NotImplementedError()

    def _run_job(self, job):
        """ Actually launch job on concrete adaptor
        :raise: `waves.adaptors.exception.AdaptorException` if error """
        raise NotImplementedError()

    def _cancel_job(self, job):
        """ Try to cancel job on concrete adaptor
        :raise: `waves.adaptors.exception.AdaptorException` if error """
        raise NotImplementedError()

    def _job_status(self, job):
        """ Actually retrieve job states on concrete adaptor, return raw value to be mapped with defined in _states_map
        :raise: `waves.adaptors.exception.AdaptorException` if error """
        raise NotImplementedError()

    def _job_results(self, job):
        """ Retrieve job results from concrete adaptor, may include some file download from remote hosts
        Set attribute result_available for job if success
        :raise: `waves.adaptors.exception.AdaptorException` if error
        :return: Boolean True if results are retrieved from remote host, False either
        """
        raise NotImplementedError()

    def _job_run_details(self, job):
        """ Retrieve job run details if possible from concrete adaptor
        :raise: `waves.adaptors.exception.AdaptorException` if error """
        raise NotImplementedError()

    def _dump_config(self):
        """ Return string representation of concrete adaptor configuration
        :return: a String representing configuration """
        return ""

    def test_connection(self):
        self.connect()
        return self.connected

    def connexion_string(self):
        return "%s://%s" % (self.protocol, self.host)

    @property
    def importer(self):
        return None
