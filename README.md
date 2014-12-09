GillesPy
========
GillesPy is a python interface to StochKit stochastic simulation software.  It is part of the StochSS project, see http://www.stochss.org for more details.

Installation (with StochSS)
===========================
If you have StochSS installed, set the environment variable STOCHSS_HOME to the location.  Then run 'sudo python setup.py install'.

For example (on OSX), if you have StochSS 1.4.1 installed in your Applications directory, then you would:
```
  export STOCHSS_HOME=/Applications/StochSS-1.4.1/StochSSserver.app/Contents/Resources/
  sudo python setup.py install
```
On a linux Ubuntu system, with StochSS 1.4.1 install in your home directory:
```
  export STOCHSS_HOME=$HOME/stochss.linux.1.4.1/
  sudo python setup.py install
```

Installation (without StochSS)
==============================
If you do not have StochSS installed, you will need to download StochKit (http://sourceforge.net/projects/stochkit/) and the StochKit-ODE package from StochSS.
Then set the environement variables STOCHKIT_HOME and STOCHKIT_ODE_HOME before you run the setup.py script as above.

If you want to simulation GillesPy models deterministically, you need to download the ode package from StochSS
```
  TODO: complete instructions on how to do this
```
