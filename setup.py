from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from setuptools.command.bdist_egg import bdist_egg
from setuptools.command.easy_install import easy_install
import subprocess
import os

SETUP_DIR = os.path.dirname(os.path.abspath(__file__))

def stoch_path(command_subclass):
    """
    A decorator for classes subclassing one of the setuptools commands.
    It modifies the run() method.
    """
    orig_run = command_subclass.run
    
    def modified_run(self):
      
        success=False
        cmd = "echo 'from .gillespy import *' > {0}/gillespy/__init__.py".format(SETUP_DIR)
        cmd += "\necho 'import os' >> {0}/gillespy/__init__.py".format(SETUP_DIR)
        if os.environ.get('STOCHSS_HOME') is not None:
            cmd += "\necho 'os.environ[\"PATH\"] += os.pathsep + \"{0}/StochKit/\"' >> {1}/gillespy/__init__.py".format(os.path.abspath(os.environ['STOCHSS_HOME']),SETUP_DIR)
            cmd += "\necho 'os.environ[\"PATH\"] += os.pathsep + \"{0}/ode/\"' >> {1}/gillespy/__init__.py".format(os.path.abspath(os.environ['STOCHSS_HOME']),SETUP_DIR)            
            success=True
        if os.environ.get('STOCHKIT_HOME') is not None:
            cmd += "\necho 'os.environ[\"PATH\"] += os.pathsep + \"{0}\"' >> {1}/gillespy/__init__.py".format(os.path.abspath(os.environ['STOCHKIT_HOME']),SETUP_DIR)
            success=True
        if os.environ.get('STOCHKIT_ODE_HOME') is not None:
            cmd += "\necho 'os.environ[\"PATH\"] += os.pathsep + \"{0}\"' >> {1}/gillespy/__init__.py".format(os.path.abspath(os.environ['STOCHKIT_ODE_HOME']),SETUP_DIR)
            success=True
        if success is False:
           raise Exception("StochKit not found, to simulate GillesPy models either StochKit solvers or StochSS must to be installed")
        
        try:
            subprocess.check_call(cmd,shell=True)
        except(subprocess.CalledProcessError,OSError) as e:
            print("It didn't work {0}".format(e))
            raise SystemExit
        orig_run(self)
    command_subclass.run = modified_run
    return command_subclass



# update all install classes with our new class
@stoch_path
class develop_new(develop):
    pass

@stoch_path
class install_new(install):
    pass

@stoch_path
class bdist_egg_new(bdist_egg):
    pass

@stoch_path
class easy_install_new(easy_install):
    pass




setup(name = "gillespy",
      version = "1.1",
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
      
      cmdclass = {'bdist_egg':bdist_egg_new,
                  'install':install_new,
                  'develop':develop_new,
                  'easy_install':easy_install_new}
      
      )
