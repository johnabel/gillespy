
# coding: utf-8

# In[1]:

import sys
sys.path[:0] = ['..']
import gillespy


# In[2]:

import os
import urllib2
import tempfile
#sbml_file = 'http://www.ebi.ac.uk/biomodels-main/download?mid=BIOMD0000000010'
#sbml_file = 'http://www.ebi.ac.uk/biomodels-main/download?mid=BIOMD0000000017'
sbml_file = 'http://www.ebi.ac.uk/biomodels-main/download?mid=BIOMD0000000028'
response = urllib2.urlopen(sbml_file)
tmp = tempfile.NamedTemporaryFile(delete = False)
tmp.write(response.read())
tmp.close()
######

sbml_model, errors = gillespy.import_SBML(tmp.name)
print os.linesep.join([error for error, code in errors])
print "-----"
os.remove(tmp.name)
######


# In[3]:

dresults = sbml_model.run(solver=gillespy.StochKitODESolver,stochkit_home="/Applications/StochSS-1.6/StochSSserver.app/Contents/Resources/ode/", debug=True)


# In[4]:

ns = len(sbml_model.listOfSpecies)
plt.figure(figsize=(15,4*int(ceil(ns/5.0))))
for n,s in enumerate(sbml_model.listOfSpecies):
    plt.subplot(int(ceil(ns/5.0)),5,n+1)
    plt.plot(dresults[0][:,0],dresults[0][:,n+1])
    plt.title(s)


# In[5]:

sbml_model.name


# In[6]:

for r in sbml_model.listOfReactions:
    print "{0}\t{1}".format(r,sbml_model.listOfReactions[r].propensity_function)


# In[39]:

new_rxns = []
for rname in sbml_model.listOfReactions:
    r = sbml_model.listOfReactions[rname]
    #print r.propensity_function
    rxns = r.propensity_function.replace('cell * ','').replace('(','').replace(')','').split('-')
    #print rxns, r.reactants, r.products
    r1 = gillespy.Reaction(name=r.name,  reactants=r.reactants, 
                           products=r.products,
                           propensity_function = rxns[0])
    new_rxns.append(r1)
    if len(rxns) > 1:
        r2 = gillespy.Reaction(name=r.name+'__reverse',  
                               reactants=r.products, 
                               products=r.reactants,
                               propensity_function = rxns[1])
    
        new_rxns.append(r2)
    
    
print new_rxns


# In[8]:

for s in sbml_model.listOfSpecies:
    print s,sbml_model.listOfSpecies[s].initial_value


# In[78]:

r = model.listOfReactions['reaction_0000001']
print r.propensity_function
print r.propensity_function.replace('(','').replace(')','').split()


# In[9]:

sbml_model.listOfReactions


# In[42]:

'''If we assume the volume is 1.0, we can use the existing propensity 
functions when we convert to a stochastic model.'''
class Markevich2004_MAPK_phosphoRandomElementary(gillespy.Model):
    def __init__(self, concentration_model):
        gillespy.Model.__init__(self, name="Markevich2004_MAPK_phosphoRandomElementary")
        
        for s in concentration_model.listOfSpecies:
            self.add_species(gillespy.Species(name=s, initial_value=int(concentration_model.listOfSpecies[s].initial_value)))
            
        for p in concentration_model.listOfParameters:
            self.add_parameter(concentration_model.listOfParameters[p])
            
        #for r in concentration_model.listOfReactions:
        #    self.add_reaction(concentration_model.listOfReactions[r])
        new_rxns = []
        for rname in concentration_model.listOfReactions:
            r = concentration_model.listOfReactions[rname]
            #print r.propensity_function
            rxns = r.propensity_function.replace('cell * ','').replace('(','').replace(')','').split('-')
            #print rxns, r.reactants, r.products
            r1 = gillespy.Reaction(name=r.name,  reactants=r.reactants, 
                                   products=r.products,
                                   propensity_function = rxns[0])
            new_rxns.append(r1)
            if len(rxns) > 1:
                r2 = gillespy.Reaction(name=r.name+'__reverse',  
                                       reactants=r.products, 
                                       products=r.reactants,
                                       propensity_function = rxns[1])

                new_rxns.append(r2)
        self.add_reaction(new_rxns)


# In[43]:

stoch_model = Markevich2004_MAPK_phosphoRandomElementary(sbml_model)
sresults = stoch_model.run(stochkit_home="/Applications/StochSS-1.6/StochSSserver.app/Contents/Resources/StochKit/", debug=True)


# In[44]:

ns = len(stoch_model.listOfSpecies)
plt.figure(figsize=(15,4*int(ceil(ns/5.0))))
for n,s in enumerate(stoch_model.listOfSpecies):
    plt.subplot(int(ceil(ns/5.0)),5,n+1)
    plt.plot(stoch_model.tspan,sresults[0][:,n])
    plt.title(s)

