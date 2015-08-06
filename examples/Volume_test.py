import sys
sys.path[:0] = ['..']
import gillespy
import time
import numpy

class Simple1(gillespy.Model):
    """
    This is a simple example for mass-action degradation of species S.
    """

    def __init__(self, parameter_values=None,volume=1.0):

        # Initialize the model.
        gillespy.Model.__init__(self, name="simple1", volume=volume)
        
        # Parameters
        k1 = gillespy.Parameter(name='k1', expression=0.03)
        self.add_parameter(k1)
        
        # Species
        r1 = gillespy.Species(name='r1', initial_value=100)
        self.add_species(r1)
        r2 = gillespy.Species(name='r2', initial_value=100)
        self.add_species(r2)
        
        
        # Reactions
        rxn1 = gillespy.Reaction(
                name = 'r1d',
                reactants = {r1:2},
                products = {},
                rate = k1 )
                
        self.add_reaction(rxn1)
        
        rxn2 = gillespy.Reaction(
                name = 'r2d',
                reactants = {r2:2},
                products = {},
                propensity_function = 'k1/2 * r2*(r2-1)/vol' )
                
        self.add_reaction(rxn2)
        self.timespan(numpy.linspace(0,100,101))

simple_1 = Simple1(volume=1)
simple_10 = Simple1(volume=10)
num_trajectories = 1

tick = time.time()
simple_1trajectories = simple_1.run(number_of_trajectories = num_trajectories, stochkit_home="/Applications/StochSS-1.6/StochSSserver.app/Contents/Resources/StochKit/")
print 'vol=1\t',time.time() - tick

tick = time.time()
simple_10trajectories = simple_10.run(number_of_trajectories = num_trajectories, stochkit_home="/Applications/StochSS-1.6/StochSSserver.app/Contents/Resources/StochKit/")
print 'vol=10\t',time.time() - tick


print simple_10.serialize()

from matplotlib import gridspec

gs = gridspec.GridSpec(1,1)

plt.figure()
ax0 = plt.subplot(gs[0,0])

# extract time values
t = np.array(simple_1trajectories[0][:,0]) 

# extract just the trajectories for S into a numpy array

#plot mean
ax0.plot(t,simple_1trajectories[0][:,1],'k--',label='ma')
ax0.plot(t,simple_1trajectories[0][:,2],'g+',label='custom')

ax0.legend()
ax0.set_xlabel('Time')
ax0.set_ylabel('Species r Count')

plt.tight_layout()
plt.show()

gs = gridspec.GridSpec(1,1)

plt.figure()
ax0 = plt.subplot(gs[0,0])

# extract time values
t = np.array(simple_10trajectories[0][:,0]) 

# extract just the trajectories for S into a numpy array

#plot mean
ax0.plot(t,simple_10trajectories[0][:,1],'k--',label='ma')
ax0.plot(t,simple_10trajectories[0][:,2],'g+',label='custom')

ax0.legend()
ax0.set_xlabel('Time')
ax0.set_ylabel('Species r Count')

plt.tight_layout()
plt.show()


