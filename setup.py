#!/usr/bin/env python

from setuptools import setup, find_packages
import os
import subprocess


def make_version():
    """Generates a version number using `git describe`.
    Returns:
      version number of the form "3.1.1.dev127+g413ed61".
    """
    def _minimal_ext_cmd(cmd):
        """Run a command in a subprocess.
        Args:
          cmd: list of the command
        Returns:
          output from the command
        """
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            value = os.environ.get(k)
            if value is not None:
                env[k] = value
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               env=env).communicate()[0]
        return out

    version = 'unknown'

    if os.path.exists('.git'):
        try:
            out = _minimal_ext_cmd(['git',
                                    'describe',
                                    '--tags',
                                    '--match',
                                    'v*'])
            out = out.decode("utf-8")
            version = out.strip().split("-")
            if len(version) > 1:
                version, dev, sha = version
                version = "%s.dev%s+%s" % (version[1:], dev, sha)
            else:
                version = version[0][1:]
        except OSError:
            import warnings
            warnings.warn("Could not run ``git describe``")
    elif os.path.exists('corrdb.egg-info'):
        from corrdb import get_version
        version = get_version()

    return version

setup(name='contracts',
    decription='A contracting library for cross-tools/services interoperability',
    version=make_version(),
    author='CoRR and Maestro Teams',
    author_email='faical.congo@nist.gov',
    url='https://github.com/usnistgov/contracts',
    license='MIT License',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
      'console_scripts': [
          'cnt-transform = contracts.transform:main',
          'cnt-archive = contracts.archive:main'
      ]
    },
    test_suite='nose.collector',
    tests_require=['nose'],
    install_requires=[
      'PyYAML',
      'six',
      'enum34',
      ],
    classifiers=[
      'Development Status :: 1 - Alpha',
      'Intended Audience :: Developers',
      'Programming Language :: Python',
      ],
    )
