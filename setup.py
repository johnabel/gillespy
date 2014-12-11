from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from setuptools.command.bdist_egg import bdist_egg
from setuptools.command.easy_install import easy_install
import os



def stoch_path(command_subclass):
    """
    A decorator for classes subclassing one of the setuptools commands.
    It modifies the run() method so that it prints a friendly greeting.
    """
    orig_run = command_subclass.run
    
    def modified_run(self):
        print "It worked."
        
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
        if success is False:
           raise Exception("StochKit not found, to simulate GillesPy models either StochKit solvers or StochSS must to be installed")
           
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
      
      cmdclass = {'bdist_egg':bdist_egg_new,
                  'install':install_new,
                  'develop':develop_new,
                  'easy_install':easy_install_new}
      
      )
