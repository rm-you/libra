# Copyright 2012 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys
import setuptools
from setuptools.command.test import test as TestCommand
from libra.openstack.common import setup

requires = setup.parse_requirements()
tests_requires = setup.parse_requirements(['tools/test-requires'])


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        pytest.main(self.test_args)

ci_cmdclass = {}

try:
    from sphinx.setup_command import BuildDoc

    class local_BuildDoc(BuildDoc):
        def run(self):
            builders = ['html', 'man']
            for builder in builders:
                self.builder = builder
                self.finalize_options()
                BuildDoc.run(self)

    class local_BuildDoc_latex(BuildDoc):
        def run(self):
            builders = ['latex']
            for builder in builders:
                self.builder = builder
                self.finalize_options()
                BuildDoc.run(self)

    ci_cmdclass['build_sphinx'] = local_BuildDoc
    ci_cmdclass['build_sphinx_latex'] = local_BuildDoc_latex
except Exception:
    pass

ci_cmdclass['test'] = PyTest

setup_reqs = ['Sphinx']

# Get the version number
execfile('libra/__init__.py')

setuptools.setup(
    name="libra",
    description="Python LBaaS Gearman Worker and Pool Manager",
    version=__version__,
    author="David Shrewsbury <shrewsbury.dave@gmail.com>, \
        Andrew Hutchings <andrew@linuxjedi.co.uk>",
    packages=setuptools.find_packages(exclude=["*.tests"]),
    entry_points={
        'console_scripts': [
            'libra_worker = libra.worker.main:main',
            'libra_pool_mgm = libra.mgm.mgm:main',
            'libra_client = libra.client.client:main',
            'libra_statsd = libra.statsd.main:main',
        ]
    },
    cmdclass=ci_cmdclass,
    tests_require=tests_requires,
    install_requires=requires,
    setup_requires=setup_reqs,
    data_files=[
        ('share/libra/', ['etc/sample_libra.cfg'])
    ]
)
