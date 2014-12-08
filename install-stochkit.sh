#!/bin/bash

# Attempt to install StochKit 2.0.8
#
# Install it in the user's home folder by default, to override
# Updated from StochSS to GillesPy by JHA
#
#

echo "Current installation directory is:"
PRELIM_PATH="`( cd  && pwd )`/"  # absolutized and normalized
echo $PRELIM_PATH

read -p "If you wish to change this, please enter a directory in which to install StochKit2 solvers: " MY_PATH

if [ -z "$MY_PATH"]; then
    #set installation directory to default
    echo "Default path selected."
    MY_PATH=$PRELIM_PATH
fi

#MY_PATH="`dirname \"$0\"`"

echo "The installation directory will be: $MY_PATH"

GILLESPY_HOME=$MY_PATH
GILLESPY_HOME="`( cd \"$GILLESPY_HOME\" && pwd )`"

STOCHKIT_VERSION=StochKit2.0.10
STOCHKIT_PREFIX=$GILLESPY_HOME
export STOCHKIT_HOME="$STOCHKIT_PREFIX/$STOCHKIT_VERSION"
ODE_VERSION="ode-1.0.1"
export STOCHKIT_ODE="$GILLESPY_HOME/$ODE_VERSION"

# Check that the dependencies are satisfied
echo -n "Are dependencies satisfied?... "

count=$(dpkg-query -l gcc g++ make libxml2-dev curl git | grep '^[a-z]i' | wc -l)

if [ $count != 6 ]; then
    echo "No"
    read -p "Do you want me to try to use sudo to install required package(s) (make, gcc, g++, libxml2-dev, curl, git)? (y/n): " answer

    if [ $? != 0 ]; then
        exit -1
    fi

    if [ "$answer" == 'y' ] || [ "$answer" == 'yes' ]; then
        echo "Running 'sudo apt-get install make gcc g++ libxml2-dev curl git'"
        sudo apt-get install make gcc g++ libxml2-dev curl git

        if [ $? != 0 ]; then
            exit -1
        fi
    fi
else
    echo "Yes"
fi

echo -n "Testing if StochKit2 built... "

rundir=$(mktemp -d /tmp/tmp.XXXXXX)
rm -r "$rundir"

if "$STOCHKIT_HOME/ssa" -m "$STOCHKIT_HOME/models/examples/dimer_decay.xml" -r 1 -t 1 -i 1 --out-dir "$rundir" >& /dev/null; then
    echo "Yes"
    echo "$STOCHKIT_VERSION found in $STOCHKIT_HOME"
else
    echo "No"

    echo "Installing in $GILLESPY_HOME/$STOCHKIT_VERSION"

    echo "Cleaning up anything already there..."
    rm -rf "$STOCHKIT_PREFIX/$STOCHKIT_VERSION"

    if [ ! -e "$STOCHKIT_PREFIX/$STOCHKIT_VERSION.tgz" ]; then
	echo "Downloading $STOCHKIT_VERSION..."
	curl -o "$STOCHKIT_PREFIX/$STOCHKIT_VERSION.tgz" -L "http://sourceforge.net/projects/stochkit/files/StochKit2/$STOCHKIT_VERSION/$STOCHKIT_VERSION.tgz"
    fi

    echo "Building StochKit"
    echo " Logging stdout in $GILLESPY_HOME/stdout.log and "
    echo " stderr in $GILLESPY_HOME/stderr.log "
    echo " * This process will take approximately 5 minutes to complete."
    wd=`pwd`
    cd "$STOCHKIT_PREFIX"
    tar -xzf "$STOCHKIT_VERSION.tgz"
    tmpdir=$(mktemp -d /tmp/tmp.XXXXXX)
    mv "$STOCHKIT_HOME" "$tmpdir/"
    cd "$tmpdir/$STOCHKIT_VERSION"
    STOCHKIT_HOME_R=$STOCHKIT_HOME
    export STOCHKIT_HOME="$(pwd -P)"
    ./install.sh 1>"$GILLESPY_HOME/stdout.log" 2>"$GILLESPY_HOME/stderr.log"
    export STOCHKIT_HOME=$STOCHKIT_HOME_R
    cd $wd
    mv "$tmpdir/$STOCHKIT_VERSION" "$STOCHKIT_HOME"
    rm -r "$tmpdir"

# Test that StochKit was installed successfully by running it on a sample model
    if "$STOCHKIT_HOME/ssa" -m "$STOCHKIT_HOME/models/examples/dimer_decay.xml" -r 1 -t 1 -i 1 --out-dir "$rundir" >& /dev/null; then
	echo "Success!"
    else
	echo "Failed"
	echo "$STOCHKIT_VERSION failed to install. Consult logs above for errors, and the StochKit documentation for help on building StochKit for your platform. Rename successful build folder to $STOCHKIT_HOME"	
	exit -1
    fi
fi

echo -n "Testing if StochKit2 ODE built... "

rm -r "$rundir"
if "$STOCHKIT_ODE/ode" -m "$STOCHKIT_HOME/models/examples/dimer_decay.xml" -t 1 -i 1 --out-dir "$rundir" >& /dev/null; then
    echo "Yes"
    echo "ode found in $STOCHKIT_ODE"
else
    echo "No"

    echo "Installing in $GILLESPY_HOME/$ODE_VERSION"

    echo "Cleaning up anything already there..."
    rm -rf "$GILLESPY_HOME/ode"

    stdout="$GILLESPY_HOME/stdout.log"
    stderr="$GILLESPY_HOME/stderr.log"
    echo "Building StochKit ODE"
    echo " Logging stdout in $GILLESPY_HOME/stdout.log and "
    echo " stderr in $GILLESPY_HOME/stderr.log "
    echo " * This process should take about a minute to complete, please be patient *"
    wd=`pwd`
    tmpdir=$(mktemp -d /tmp/tmp.XXXXXX)
    tar -xzf "$STOCHKIT_ODE.tgz"
    mv "$STOCHKIT_ODE" "$tmpdir"
    cd "$tmpdir/$ODE_VERSION/cvodes"
    tar -xzf "cvodes-2.7.0.tar.gz"
    cd "cvodes-2.7.0"
    ./configure --prefix="$PWD/cvodes" 1>"$stdout" 2>"$stderr"
    if [ $? != 0 ]; then
	echo "Failed"
	echo "StochKit ODE failed to install. Consult logs above for errors, and the StochKit documentation for help on building StochKit for your platform. Rename successful build folder to $STOCHKIT_ODE"
        exit -1
    fi
    make 1>"$stdout" 2>"$stderr"
    if [ $? != 0 ]; then
	echo "Failed"
	echo "StochKit ODE failed to install. Consult logs above for errors, and the StochKit documentation for help on building StochKit for your platform. Rename successful build folder to $STOCHKIT_ODE"
        exit -1
    fi
    make install 1>"$stdout" 2>"$stderr"
    if [ $? != 0 ]; then
	echo "Failed"
	echo "StochKit ODE failed to install. Consult logs above for errors, and the StochKit documentation for help on building StochKit for your platform. Rename successful build folder to $STOCHKIT_ODE"
        exit -1
    fi
    cd ../../
    STOCHKIT_ODE_R=$STOCHKIT_ODE
    export STOCHKIT_ODE="$(pwd -P)"
    make 1>"$stdout" 2>"$stderr"
    if [ $? != 0 ]; then
	echo "Failed"
	echo "StochKit ODE failed to install. Consult logs above for errors, and the StochKit documentation for help on building StochKit for your platform. Rename successful build folder to $STOCHKIT_ODE"
        exit -1
    fi
    export STOCHKIT_ODE="$STOCHKIT_ODE_R"
    cd ../
    cd $wd
    mv "$tmpdir/$ODE_VERSION" "$STOCHKIT_ODE"

# Test that StochKit was installed successfully by running it on a sample model
    if "$STOCHKIT_ODE/ode" -m "$STOCHKIT_HOME/models/examples/dimer_decay.xml" -t 1 -i 1 --out-dir "$rundir" >& /dev/null; then
	echo "Success!"
    else
	echo "Failed"
	echo "StochKit ODE failed to install. Consult logs above for errors, and the StochKit documentation for help on building StochKit for your platform. Rename successful build folder to $STOCHKIT_ODE"
	exit -1
    fi
fi

rm -r "$rundir"

echo "Configuring the GillesPy to use $STOCHKIT_HOME for StochKit... "

ln -s "$STOCHKIT_ODE" ode
ln -s "$STOCHKIT_HOME" StochKit

# Write STOCHKIT_HOME to the appropriate config file
echo "$STOCHKIT_HOME" > "$GILLESPY_HOME/conf/config"
echo -n "$STOCHKIT_ODE" >> "$GILLESPY_HOME/conf/config"
echo "Done!"

# here, give the STOCHKIT_HOME as the path adjustment for running this in python

exec python "$GILLESPY_HOME/launchapp.py" $0
