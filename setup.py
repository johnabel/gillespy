import setuptools
from setuptools import setup
from setuptools.command.install import install
import setuptools.command.bdist_egg
import os
import sys
import subprocess

SETUP_DIR = os.path.dirname(os.path.abspath(__file__))


#class Do_bdist_egg(setuptools.command.bdist_egg):
#    def run(self):
#        self.run_command('build_gillespy')
#        setuptools.command.bdist_egg.run(self)

class Install(install):
    def do_egg_install(self):
        self.run_command('build_gillespy')
        install.do_egg_install(self)

    def run(self):
        self.run_command('build_gillespy')
        install.run(self)

class GillesPyBuild(setuptools.Command):
    description = 'Configure GillesPy to find solvers'

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print "GillesPyBuild.run()"
        success=False
        cmd = "echo 'from .gillespy import *' > gillespy/__init__.py"
        cmd += "\necho 'import os' >> gillespy/__init__.py"
        if os.environ.get('STOCHSS_HOME') is not None:
            cmd += "\necho 'os.environ[\"PATH\"] += os.pathsep + \"{0}/StochKit/\"' >> gillespy/__init__.py".format(os.environ['STOCHSS_HOME'])
            cmd += "\necho 'os.environ[\"PATH\"] += os.pathsep + \"{0}/ode/\"' >> gillespy/__init__.py".format(os.environ['STOCHSS_HOME'])
            success=True
        if os.environ.get('STOCHKIT_HOME') is not None:
            cmd += "\necho 'os.environ[\"PATH\"] += os.pathsep + \"{0}\"' >> gillespy/__init__.py".format(os.environ['STOCHKIT_HOME'])
            success=True
        if os.environ.get('STOCHKIT_ODE_HOME') is not None:
            cmd += "\necho 'os.environ[\"PATH\"] += os.pathsep + \"{0}\"' >> gillespy/__init__.py".format(os.environ['STOCHKIT_ODE_HOME'])
            success=True
        print cmd
        try:
            subprocess.check_call(cmd, shell=True)
        except (subprocess.CalledProcessError, OSError) as e:
            sys.stderr.write('Problems setting path to solvers in GillesPy: {0}'.format(e))
            raise SystemExit
        if success is False:
           raise Exception("StochKit not found, to simulate GillesPy models either StochKit solvers or StochSS must to be installed")
        



setup(name = "gillespy",
      version = "0.1",
      packages = ['gillespy'],
      description = 'Python interface to the Gillespie StochKit2 solvers',
      
      install_requires = ["numpy",
                          "matplotlib",
                          "scipy"],
      
      author = "John H. Abel, Brian Drawert, Andreas Hellander",
      author_email = ["jhabel01@gmail.com", "briandrawert@gmail.com", "andreas.hellander@gmail.com"],
      license = "GPL",
      keywords = "gillespy, gillespie algorithm, stochkit, stochastic simulation",

      url = "http://www.github.com/JohnAbel/GillesPy", # we don't really yet have one

      download_url = "https://github.com/JohnAbel/GillesPy/tarball/master/",
      
      cmdclass = {
         #'build' : Do_build,
         #'bdist_egg' : Do_bdist_egg,
         'build_gillespy': GillesPyBuild,
         'install':Install
      }
      
      )
