from setuptools import setup
from setuptools.command.install import install
import os
import pdb

class Install(install):
    def do_egg_install(self):
<<<<<<< HEAD
        cmd = "echo -e 'import os' >> gillespy/__init__.py"
        if os.environ.get('STOCHSS_HOME') is not None:
            cmd += "\necho -e 'os.environ[\'PATH\'] += os.pathsep + \'{0}\'' >> gillespy/__init__.py".format(os.environ['STOCHSS_HOME'])
        if os.environ.get('STOCHKIT_HOME') is not None:
            cmd += "\necho -e 'os.environ[\'PATH\'] += os.pathsep + \'{0}\'' >> gillespy/__init__.py".format(os.environ['STOCHKIT_HOME'])
        if os.environ.get('STOCHKIT_ODE_HOME') is not None:
            cmd += "\necho -e 'os.environ[\'PATH\'] += os.pathsep + \'{0}\'' >> gillespy/__init__.py".format(os.environ['STOCHKIT_ODE_HOME'])
=======
        cmd = "echo 'import os' > gillespy/__init__.py'\n"
        success = False
        if os.envion.get('STOCHSS_HOME') is not None:
            success = True
            cmd += "echo 'os.environ[\'PATH\'] += os.pathsep + {0}' > gillespy/__init__.py\n".format(os.environ['STOCHSS_HOME'])
        if os.envion.get('STOCHKIT_HOME') is not None:
            success = True
            cmd += "echo 'os.environ[\'PATH\'] += os.pathsep + {0}' > gillespy/__init__.py\n".format(os.environ['STOCHKIT_HOME'])
        if os.envion.get('STOCHKIT_ODE_HOME') is not None:
            success = True
            cmd += "echo 'os.environ[\'PATH\'] += os.pathsep + {0}' > gillespy/__init__.py\n".format(os.environ['STOCHKIT_ODE_HOME'])
>>>>>>> 5f4ab0a6b9d862caeca32d32263bc8ecd2c78faf
        print cmd
        if not success:
            raise Exception("StochKit not found, to simulation GillesPy models either StochSS or StochKit needs to be installed")
        self.run_command(cmd)

        install.do_egg_install(self)



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
      
      cmdclass = {'install':Install}
      
      )
