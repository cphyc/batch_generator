import subprocess
from distutils.spawn import find_executable
from six import add_metaclass

from os import path
from .log import logger

BACKENDS = dict()


def detect_backend():
    # TODO: support multiple backends?
    for name, backend in BACKENDS.items():
        if name:
            return name

    logger.error('No backend found!')


class BackendRegistry(type):
    """
    This is a base class that on instantiation registers the file
    backend into the list. Used as a metaclass.
    """
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        if cls.name is not None and cls.on_system():
            BACKENDS[cls.name] = cls
        return cls


@add_metaclass(BackendRegistry)
class BaseBackend(object):
    """
    Base class to define backends.
    """
    name = None  # This is the name of backend (qsub, slurm, ...)

    def __init__(self, params):
        '''This takes a params argument that contains the software parameters.

        This function is only called for internal purposes. Use it to
        e.g. override the location of some binary files, ...
        '''
        self.params = params

    @classmethod
    def on_system(cls):
        '''Return true if the backend works on the system.'''
        raise NotImplementedError

    def submit(self, fname):
        '''Customize to submit a file. This should return the id of the job.'''
        raise NotImplementedError

    def job_status(self, job_id):
        '''Return the status of a job.'''
        raise NotImplementedError

    def status(self):
        '''Return the status of the whole queue.'''
        raise NotImplementedError


class QsubBackend(BaseBackend):
    '''
    A backend for the qsub submission system.
    '''

    name = 'qsub'

    @classmethod
    def on_system(cls):
        logger.debug('Detected backend %s' % cls.name)
        return find_executable('qsub') is not None

    def submit(self, fname):
        if not path.exists(fname):
            logger.error('File does not exist.')
            raise FileNotFoundError('%s does not exist')
        result = subprocess.run(['qsub', fname], stdout=subprocess.PIPE)
        if result.returncode != 0:
            logger.error('qsub returned %s', result.returncode)
            raise RuntimeError

        job_id = result.stdout.decode('utf-8').replace('\n', '')

        return job_id

    def job_status(self, job_id):
        cmd = ['qsub', '%s' % job_id]
        subprocess.run(cmd)

    def status(self, user=None):
        cmd = ['qstat', '-a']
        if user:
            cmd.extend(['-u', user])

        subprocess.run(cmd)


class SlurmBackend(BaseBackend):
    '''
    A backend for the slurm submission system.
    '''

    name = 'slurm'

    @classmethod
    def on_system(cls):
        logger.debug('Detected backend %s' % cls.name)
        return find_executable('sbatch') is not None

    def submit(self, fname):
        if not path.exists(fname):
            logger.error('File does not exist.')
            raise FileNotFoundError('%s does not exist')
        result = subprocess.run(['sbatch', fname], stdout=subprocess.PIPE)
        if result.returncode != 0:
            logger.error('sbatch returned %s', result.returncode)
            raise RuntimeError

        job_id = result.stdout.decode('utf-8').replace('\n', '')

        return job_id

    def job_status(self, job_id):
        cmd = ['squeue', '%s' % job_id]
        subprocess.run(cmd)

    def status(self, user=None):
        cmd = ['squeue']
        if user:
            cmd.extend(['-u', user])

        subprocess.run(cmd)
