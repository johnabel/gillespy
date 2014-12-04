""" 
Code based off StochSS internal interface to StochKit, originally by 
A. Hellander. Stand-alone GillesPy module work by J. Abel and B. Drawert.

Version 0.1 on github as of 12-4-2014.
    
"""

# import 3rd party modules
from collections import OrderedDict
import scipy as sp
import numpy as np
import matplotlib.pyplot as plt
import tempfile
import uuid
import subprocess

try:
    import lxml.etree as etree
    no_pretty_print = False
except:
    import xml.etree.ElementTree as etree
    import xml.dom.minidom
    import re
    no_pretty_print = True

try:
    import scipy.io as spio
    isSCIPY = True
except:
    pass

import os
import sys
try:
    import shutil
    import numpy
except:
    pass



class Model(object):
    """
    Representation of a well mixed biochemical model. Contains reactions,
    parameters, species, etc.
    
    """
    
    def __init__(self,name="",volume = None):
        """ Create an empty model. """
        
        # The name that the model is referenced by (should be a String)
        self.name = name
        
        # Optional decription of the model (string)
        self.annotation = ""
        
        # Dictionaries with Species, Reactions and Parameter objects.
        # Species,Reactio and Paramter names are used as keys.
        self.listOfParameters = OrderedDict()
        self.listOfSpecies    = OrderedDict()
        self.listOfReactions  = OrderedDict()
        
        # A well mixed model has an optional volume parameter. This should be a Parameter
        self.volume = volume;

        # This defines the unit system at work for all numbers in the model
        #   It should be a logical error to leave this undefined, subclasses should set it
        self.units = None
        
        # Dict that holds flattended parameters and species for
        # evaluation of expressions in the scope of the model.
        self.namespace = OrderedDict([])

    def updateNamespace(self):
        """ Create a dict with flattened parameter and species objects. """
        for param in self.listOfParameters:
            self.namespace[param]=self.listOfParameters[param].value
        # Dictionary of expressions that can be evaluated in the scope of this model.
        self.expressions = {}

    def getSpecies(self, sname):
        return self.listOfSpecies[sname]
    
    def getAllSpecies(self):
        return self.listOfSpecies

    def addSpecies(self, obj):
        """ 
            Add a species to listOfSpecies. Accepts input either as a single 
            Species object, or as a list of Species objects.
        """
                
        if isinstance(obj, Species):
            if obj.name in self.listOfSpecies:
                raise ModelError("Can't add species. A species with that name alredy exisits.")
            self.listOfSpecies[obj.name] = obj;
        else: # obj is a list of species
            for S in obj:
                if S.name in self.listOfSpecies:
                    raise ModelError("Can't add species. A species with that name alredy exisits.")
                self.listOfSpecies[S.name] = S;
    
    def deleteSpecies(self, obj):
        self.listOfSpecies.pop(obj)        
         
    def deleteAllSpecies(self):
        self.listOfSpecies.clear()

    def setUnits(self, units):
        if units.lower() == 'concentration' or units.lower() == 'population':
            self.units = units.lower()
        else:
            raise Exception("units must be either concentration or population (case insensitive)")

    def getParameter(self,pname):
        try:
            return self.listOfParameters[pname]
        except:
            raise ModelError("No parameter named "+pname)
    def getAllParameters(self):
        return self.listOfParameters
    
    def addParameter(self,params):
        """ 
            Add Paramter(s) to listOfParamters. Input can be either a
            single paramter object or a list of Parameters.
        """
        # TODO, make sure that you don't overwrite an existing parameter??
        if type(params).__name__=='list':
            for p in params:
                self.listOfParameters[p.name] = p
        else:
            if type(params).__name__=='instance':
                self.listOfParameters[params.name] = params
            else:
                raise

    def deleteParameter(self, obj):
        self.listOfParameters.pop(obj)

    def setParameter(self,pname,expression):
        """ Set the expression of an existing paramter. """
        p = self.listOfParameters[pname]
        p.expression = expression
        p.evaluate()
        
    def resolveParameters(self):
        """ Attempt to resolve all parameter expressions to scalar floats. 
        This methods must be called before exporting the model. """
        self.updateNamespace()
        for param in self.listOfParameters:
            try:
                self.listOfParameters[param].evaluate(self.namespace)
            except:
                raise ParameterError("Could not resolve Parameter expression "+ param + "to a scalar value.")
    
    def deleteAllParameters(self):
        self.listOfParameters.clear()

    def addReaction(self,reacs):
        """ Add reactions to model. Input can be single instance, a list
        of instances or a dict with name,instance pairs. """
        
        # TODO, make sure that you cannot overwrite an existing parameter
        param_type = type(reacs).__name__
        if param_type == 'list':
            for r in reacs:
                self.listOfReactions[r.name] = r
        elif param_type == 'dict' or param_type == 'OrderedDict':
            self.listOfReactions = reacs
        elif param_type == 'instance':
                self.listOfReactions[reacs.name] = reacs
        else:
            raise

    def getReaction(self, rname):
        return self.listOfReactions[rname]

    def getAllReactions(self):
        return self.listOfReactions
    
    def deleteReaction(self, obj):
        self.listOfReactions.pop(obj)
        
    def deleteAllReactions(self):
        self.listOfReactions.clear()

    

class Species():
    """ Chemical species. """
    
    def __init__(self,name="",initial_value=0):
        # A species has a name (string) and an initial value (positive integer)
        self.name = name
        self.initial_value = initial_value
        assert self.initial_value >= 0, "A species initial value has to be a positive number."


class Parameter():
    """ 
        A parameter can be given as an expression (function) or directly 
        as a value (scalar). If given an expression, it should be 
        understood as evaluable in the namespace of a parent Model.
    """

    def __init__(self,name="",expression=None,value=None):

        self.name = name        
        # We allow expression to be passed in as a non-string type. Invalid strings
        # will be caught below. It is perfectly fine to give a scalar value as the expression.
        # This can then be evaluated in an empty namespace to the scalar value.
        self.expression = expression
        if expression != None:
            self.expression = str(expression)
        
        self.value = value
            
        # self.value is allowed to be None, but not self.expression. self.value
        # might not be evaluable in the namespace of this parameter, but defined
        # in the context of a model or reaction.
        if self.expression == None:
            raise TypeError
    
        if self.value == None:
            self.evaluate()
    
    def evaluate(self,namespace={}):
        """ Evaluate the expression and return the (scalar) value """
        try:
            self.value = (float(eval(self.expression, namespace)))
        except:
            self.value = None
            
    def setExpression(self,expression):
        self.expression = expression
        # We allow expression to be passed in as a non-string type. Invalid strings
        # will be caught below. It is perfectly fine to give a scalar value as the expression.
        # This can then be evaluated in an empty namespace to the scalar value.
        if expression != None:
            self.expression = str(expression)
                    
        if self.expression == None:
            raise TypeError
    
        self.evaluate()

class Reaction():
    """ 
        Models a single reaction. A reaction has its own dictinaries of species 
        (reactants and products) and parameters. The reaction's propensity 
        function needs to be evaluable (and result in a non-negative scalar 
        value) in the namespace defined by the union of those dicts.
    """

    def __init__(self, name = "", reactants = {}, products = {}, 
                 propensity_function = None, massaction = False, 
                 rate=None, annotation=None):
        """ 
            Initializes the reaction using short-hand notation. 
            
            Input: name: string that the model is referenced by 
            parameters: a list of parameter instances 
            propensity_function: string with the expression for the reaction's 
                                    propensity
            reactants: List of (species,stoiciometry)
            tuples product: List of (species,stoiciometry) 
            tuples annotation: Description of the reaction (meta)
            
                massaction True,{False}     is the reaction of mass action type
                or not?  rate                        if mass action, rate is a
                paramter instance.
            
            Raises: ReactionError
            
        """
            
        # Metadata
        self.name = name
        self.annotation = ""
        
        # We might use this flag in the future to automatically generate
        # the propensity function if set to True. 
        self.massaction = massaction

        self.propensity_function = propensity_function
        if self.propensity_function !=None and self.massaction:
            errmsg = "Reaction "+self.name +" You cannot set the propensity type to mass-action and simultaneously set a propensity function."
            raise ReactionError(errmsg)
        
        self.reactants = {}
        for r in reactants:
            rtype = type(r).__name__
            if rtype=='instance':
                self.reactants[r.name] = reactants[r]
            else:
                self.reactants[r]=reactants[r]
    
        self.products = {}
        for p in products:
            rtype = type(p).__name__
            if rtype=='instance':
                self.products[p.name] = products[p]
            else:
                self.products[p]=products[p]

        if self.massaction:
            self.type = "mass-action"
            if rate == None:
                raise ReactionError("Reaction : A mass-action propensity has to have a rate.")
            self.marate = rate
            self.createMassAction()
        else:
            self.type = "customized"
                
    def createMassAction(self):
        """ 
            Create a mass action propensity function given
            self.reactants and a single parameter value.
        """
        # We support zeroth, first and second order propensities only.
        # There is no theoretical justification for higher order propensities.
        # Users can still create such propensities if they really want to,
        # but should then use a custom propensity.
        total_stoch=0
        for r in self.reactants:
            total_stoch+=self.reactants[r]
        if total_stoch>2:
            raise ReactionError("Reaction: A mass-action reaction cannot involve more than two of one species or one of two species.")
        # Case EmptySet -> Y
        propensity_function = self.marate.name;
             
        # There are only three ways to get 'total_stoch==2':
        for r in self.reactants:
            # Case 1: 2X -> Y
            if self.reactants[r] == 2:
                propensity_function = "0.5*" +propensity_function+ "*"+r+"*("+r+"-1)"
            else:
            # Case 3: X1, X2 -> Y;
                propensity_function += "*"+r

        self.propensity_function = propensity_function
            
    def setType(self,type):
        if type.lower() not in {'mass-action','customized'}:
            raise ReactionError("Invalid reaction type.")
        self.type = type.lower()

        self.massaction = False if self.type == 'customized' else True
    
    def addReactant(self,S,stoichiometry):
        if stoichiometry <= 0:
            raise ReactionError("Reaction Stoichiometry must be a positive integer.")
        self.reactants[S.name]=stoichiometry

    def addProduct(self,S,stoichiometry):
        self.products[S.name]=stoichiometry

    def Annotate(self,annotation):
        self.annotation = annotation



# Module exceptions
class ModelError(Exception):
    pass

class SpeciesError(ModelError):
    pass

class ReactionError(ModelError):
    pass

class ParameterError(ModelError):
    pass
class SimuliationError(Exception):
    pass





class gillespy_model(Model):
    """ gillespy_model extends a well mixed model with StochKit specific serialization. """
    def __init__(self, *args, **kwargs):
        super(gillespy_model, self).__init__(*args, **kwargs)

        self.units = "population"

    def serialize(self):
        """ Serializes a Model object to valid StochML. """
        self.resolveParameters()
        doc = StochMLDocument().fromModel(self)
        return doc.toString()
        
    def initialize(self, species_names, species_initial, parameter_names, 
                   parameter_values, volume):
        """
        Sets up the species and parameter names and values, as well as volume,
        for a gillespy_model object.
        """
                  
        self.species_names      = species_names
        self.species_initial    = species_initial
        self.parameter_names    = parameter_names
        self.parameter_values   = parameter_values
        self.volume             = volume
        
        # note: we are assuming here that all species values are POPULATION
        # and same for parameter values in terms of population. We would
        # have to convert otherwise.
        
        self.ParamCount = len(self.parameter_names)
        self.SpecCount  = len(self.species_names)
        
        # converts parameter and values to list of parameter objects
        # adds to model
        parameters = []
        for i in xrange(self.ParamCount):
            parameters.append(Parameter(name=parameter_names[i], 
                                        expression=parameter_values[i]))
        self.addParameter(parameters)
       
        # same for species
        species = []
        for i in xrange(self.SpecCount):
            species.append(Species(name=species_names[i],
                                   initial_value = parameter_values[i]))
            
        self.addSpecies(species)

class StochMLDocument():
    """ Serializiation and deserialization of a gillespy_model to/from 
        the native StochKit2 XML format. """
    
    def __init__(self):
        # The root element
        self.document = etree.Element("Model")
    
    @classmethod
    def fromModel(cls,model):
        """ Creates an StochKit XML document from an exisiting gillespy_model object.
            This method assumes that all the parameters in the model are already resolved
            to scalar floats (see Model.resolveParamters). 
                
            Note, this method is intended to be used interanally by the models 'serialization' 
            function, which performs additional operations and tests on the model prior to 
            writing out the XML file. You should NOT do 
            
            document = StochMLDocument.fromModel(model)
            print document.toString()
            
            you SHOULD do
            
            print model.serialize()            
            
        """
        
        # Description
        md = cls()
        
        d = etree.Element('Description') 

        #
        if model.units.lower() == "concentration":
            d.set('units', model.units.lower())

        d.text = model.annotation
        md.document.append(d)
        
        # Number of Reactions
        nr = etree.Element('NumberOfReactions')
        nr.text = str(len(model.listOfReactions))
        md.document.append(nr)
        
        # Number of Species
        ns = etree.Element('NumberOfSpecies')
        ns.text = str(len(model.listOfSpecies))
        md.document.append(ns)
        
        # Species
        spec = etree.Element('SpeciesList')
        for sname in model.listOfSpecies:
            spec.append(md.SpeciestoElement(model.listOfSpecies[sname]))
        md.document.append(spec)
                
        # Parameters
        params = etree.Element('ParametersList')
        for pname in model.listOfParameters:
            params.append(md.ParametertoElement(model.listOfParameters[pname]))

        #if model.volume != None and model.units == "population":
        #    params.append(md.ParametertoElement(model.volume))

        md.document.append(params)
        
        # Reactions
        reacs = etree.Element('ReactionsList')
        for rname in model.listOfReactions:
            reacs.append(md.ReactionToElement(model.listOfReactions[rname]))
        md.document.append(reacs)
        
        return md
    
    
    @classmethod
    def fromFile(cls,filepath):
        """ Intializes the document from an exisiting native StochKit XML file read from disk. """
        tree = etree.parse(filepath)
        root = tree.getroot()
        md = cls()
        md.document = root
        return md

    @classmethod
    def fromString(cls,string):
        """ Intializes the document from an exisiting native StochKit XML file read from disk. """
        root = etree.fromstring(string)
        
        md = cls()
        md.document = root
        return md

    def toModel(self,name):
        """ Instantiates a gillespy_model object from a StochMLDocument. """
        
        # Empty model
        model = gillespy_model(name=name)
        root = self.document
        
        # Try to set name from document
        if model.name is "":
            name = root.find('Name')
            if name.text is None:
                raise
            else:
                model.name = name.text
        
        # Set annotiation
        ann = root.find('Description')
        if ann is not None:
            units = ann.get('units')

            if units:
                units = units.strip().lower()

            if units == "concentration":
                model.units = "concentration"
            elif units == "population":
                model.units = "population"
            else: # Default 
                model.units = "population"

            if ann.text is None:
                model.annotation = ""
            else:
                model.annotation = ann.text

        # Set units
        units = root.find('Units')
        if units is not None:
            if units.text.strip().lower() == "concentration":
                model.units = "concentration"
            elif units.text.strip().lower() == "population":
                model.units = "population"
            else: # Default 
                model.units = "population"
    
        # Create parameters
        for px in root.iter('Parameter'):
            name = px.find('Id').text
            expr = px.find('Expression').text
            if name.lower() == 'volume':
                model.volume = Parameter(name, expression = expr)
            else:
                p = Parameter(name,expression=expr)
                # Try to evaluate the expression in the empty namespace (if the expr is a scalar value)
                p.evaluate()
                model.addParameter(p)
        
        # Create species
        for spec in root.iter('Species'):
            name = spec.find('Id').text
            val  = spec.find('InitialPopulation').text
            s = Species(name,initial_value = float(val))
            model.addSpecies([s])
        
        # The namespace_propensity for evaluating the propensity function for reactions must
        # contain all the species and parameters.
        namespace_propensity = OrderedDict()
        all_species = model.getAllSpecies()
        all_parameters = model.getAllParameters()
        
        for param in all_species:
            namespace_propensity[param] = all_species[param].initial_value
        
        for param in all_parameters:
            namespace_propensity[param] = all_parameters[param].value
        
        # Create reactions
        for reac in root.iter('Reaction'):
            try:
                name = reac.find('Id').text
            except:
                raise InvalidStochMLError("Reaction has no name.")
            
            reaction  = Reaction(name=name,reactants={},products={})
                
            # Type may be 'mass-action','customized'
            try:
                type = reac.find('Type').text
            except:
                raise InvalidStochMLError("No reaction type specified.")
                    
            reactants  = reac.find('Reactants')
            try:
                for ss in reactants.iter('SpeciesReference'):
                    specname = ss.get('id')
                    # The stochiometry should be an integer value, but some
                    # exising StoxhKit models have them as floats. This is why we
                    # need the slightly odd conversion below. 
                    stoch = int(float(ss.get('stoichiometry')))
                    # Select a reference to species with name specname
                    sref = model.listOfSpecies[specname]
                    try:
                        # The sref list should only contain one element if the XML file is valid.
                        reaction.reactants[specname] = stoch
                    except Exception,e:
                        StochMLImportError(e)
            except:
                # Yes, this is correct. 'reactants' can be None
                pass

            products  = reac.find('Products')
            try:
                for ss in products.iter('SpeciesReference'):
                    specname = ss.get('id')
                    stoch = int(float(ss.get('stoichiometry')))
                    sref = model.listOfSpecies[specname]
                    try:
                        # The sref list should only contain one element if the XML file is valid.
                        reaction.products[specname] = stoch
                    except Exception,e:
                        raise StochMLImportError(e)
            except:
                # Yes, this is correct. 'products' can be None
                pass
                            
            if type == 'mass-action':
                reaction.massaction = True
                reaction.type = 'mass-action'
                # If it is mass-action, a parameter reference is needed.
                # This has to be a reference to a species instance. We explicitly
                # disallow a scalar value to be passed as the paramtete.  
                try:
                    ratename=reac.find('Rate').text
                    try:
                        reaction.marate = model.listOfParameters[ratename]
                    except KeyError, k:
                        # No paramter name is given. This is a valid use case in StochKit.
                        # We generate a name for the paramter, and create a new parameter instance.
                        # The parameter's value should now be found in 'ratename'.
                        generated_rate_name = "Reaction_" + name + "_rate_constant";
                        p = Parameter(name=generated_rate_name, expression=ratename);
                        # Try to evaluate the parameter to set its value
                        p.evaluate()
                        model.addParameter(p)
                        reaction.marate = model.listOfParameters[generated_rate_name]

                    reaction.createMassAction()
                except Exception, e:
                    raise
            elif type == 'customized':
                try:
                    propfunc = reac.find('PropensityFunction').text
                except Exception,e:
                    raise InvalidStochMLError("Found a customized propensity function, but no expression was given."+e)
                reaction.propensity_function = propfunc
            else:
                raise InvalidStochMLError("Unsupported or no reaction type given for reaction" + name)

            model.addReaction(reaction)
        
        return model
    
    def toString(self):
        """ Returns  the document as a string. """
        try:
            return etree.tostring(self.document, pretty_print=True)
        except:
            # Hack to print pretty xml without pretty-print (requires the lxml module).
            doc = etree.tostring(self.document)
            xmldoc = xml.dom.minidom.parseString(doc)
            uglyXml = xmldoc.toprettyxml(indent='  ')
            text_re = re.compile(">\n\s+([^<>\s].*?)\n\s+</", re.DOTALL)
            prettyXml = text_re.sub(">\g<1></", uglyXml)
            return prettyXml
    
    def SpeciestoElement(self,S):
        e = etree.Element('Species')
        idElement = etree.Element('Id')
        idElement.text = S.name
        e.append(idElement)
        
        if hasattr(S, 'description'):
            descriptionElement = etree.Element('Description')
            descriptionElement.text = S.description
            e.append(descriptionElement)
        
        initialPopulationElement = etree.Element('InitialPopulation')
        initialPopulationElement.text = str(S.initial_value)
        e.append(initialPopulationElement)
        
        return e
    
    def ParametertoElement(self,P):
        e = etree.Element('Parameter')
        idElement = etree.Element('Id')
        idElement.text = P.name
        e.append(idElement)
        expressionElement = etree.Element('Expression')
        expressionElement.text = str(P.value)
        e.append(expressionElement)
        return e
    
    def ReactionToElement(self,R):
        e = etree.Element('Reaction')
        
        idElement = etree.Element('Id')
        idElement.text = R.name
        e.append(idElement)
        
        try:
            descriptionElement = etree.Element('Description')
            descriptionElement.text = self.annotation
            e.append(descriptionElement)
        except:
            pass
        
        try:
            typeElement = etree.Element('Type')
            typeElement.text = R.type
            e.append(typeElement)
        except:
            pass
    
        # StochKit2 wants a rate for mass-action propensites
        if R.massaction:
            try:
                rateElement = etree.Element('Rate')
                # A mass-action reactions should only have one parameter
                rateElement.text = R.marate.name
                e.append(rateElement)
            except:
                pass

        else:
            #try:
            functionElement = etree.Element('PropensityFunction')
            functionElement.text = R.propensity_function
            e.append(functionElement)
            #except:
            #    pass

        reactants = etree.Element('Reactants')

        for reactant, stoichiometry in R.reactants.items():
            srElement = etree.Element('SpeciesReference')
            srElement.set('id', reactant)
            srElement.set('stoichiometry', str(stoichiometry))
            reactants.append(srElement)

        e.append(reactants)

        products = etree.Element('Products')
        for product, stoichiometry in R.products.items():
            srElement = etree.Element('SpeciesReference')
            srElement.set('id', product)
            srElement.set('stoichiometry', str(stoichiometry))
            products.append(srElement)
        e.append(products)

        return e


class StochKitTrajectory():
    """
        A StochKitTrajectory is a numpy ndarray.
        The first column is the time points in the timeseries,
        followed by species copy numbers.
    """
    
    def __init__(self,data=None,id=None):
        
        # String identifier
        self.id = id
    
        # Matrix with copy number data.
        self.data = data
        [self.tlen,self.ns] = np.shape(data);

class StochKitEnsemble():
    """ 
        A stochKit ensemble is a collection of StochKitTrajectories,
        all sharing a common set of metadata (generated from the same model instance).
    """
    
    def __init__(self,id=None,trajectories=None,parentmodel=None):
        # String identifier
        self.id = id;
        # Trajectory data
        self.trajectories = trajectories
        # Metadata
        self.parentmodel = parentmodel
        dims = np.shape(self.trajectories)
        self.number_of_trajectories = dims[0]
        self.tlen = dims[1]
        self.number_of_species = dims[2]
    
    def addTrajectory(self,trajectory):
        self.trajectories.append(trajectory)
    
    def dump(self, filename, type="mat"):
        """ 
            Serialize to a binary data file in a matrix format.
            Supported formats are HDF5 (requires h5py), .MAT (for Matlab V. <= 7.2, requires SciPy). 
            Matlab V > 7.3 uses HDF5 as it's base format for .mat files. 
        """
        
        if type == "mat":
            # Write to Matlab format.
            filename = filename
            # Build a struct that contains some metadata and the trajectories
            ensemble = {'trajectories':self.trajectories,'species_names':self.parentmodel.listOfSpecies,'model_parameters':self.parentmodel.listOfParameters,'number_of_species':self.number_of_species,'number_of_trajectories':self.number_of_trajectories}
            spio.savemat(filename,{self.id:ensemble},oned_as="column")
        elif type == "hdf5":
            print "Not supported yet."

class StochKitOutputCollection():
    """ 
        A collection of StochKit Ensembles, not necessarily generated
        from a common model instance (i.e. they do not necessarly have the same metadata).
        This datastructure can be useful to store e.g. data from parameter sweeps, 
        or simply an ensemble of ensembles.
        
        AH: Something like a PyTables object would be very useful here, if working
        in a Python environment. 
        
    """

    def __init__(self,collection=[]):
        self.collection = collection

    def addEnsemble(self,ensemble):
        self.collection.append(ensemble)


def simulate(model, t=20, number_of_trajectories=10, 
        increment=0.05, seed=None, stochkit_home=None, algorithm='ssa', job_id=None):
    """ 
    Call out and run StochKit. Collect the results. 
    """
    
    # We write all StochKit input and output files to a temporary folder
    prefix_basedir = tempfile.mkdtemp()
    prefix_outdir = os.path.join(prefix_basedir, 'output')
    os.mkdir(os.path.join(prefix_basedir, 'output'))
    
    if job_id is None:
        job_id = str(uuid.uuid4())
    
    # Write a temporary StochKit2 input file.
    if isinstance(model, gillespy_model):
        outfile =  os.path.join(prefix_basedir, "temp_input_"+job_id+".xml")
        mfhandle = open(outfile, 'w')
        document = StochMLDocument.fromModel(model)

    # If the model is a gillespy_model instance, we serialize it to XML,
    # and if it is an XML file, we just make a copy.
    if isinstance(model, gillespy_model):
        document = model.serialize()
        mfhandle.write(document)
        mfhandle.close()
    elif isinstance(model, str):
        outfile = model

    # Assemble argument list for StochKit
    ensemblename = job_id
    
    print "directories = os.listdir({0})".format(prefix_outdir),os.listdir(prefix_outdir)
    directories = os.listdir(prefix_outdir)
    
    
    outdir = prefix_outdir+'/'+ensemblename
    print 'outdir',outdir
        
    realizations = number_of_trajectories
    if increment == None:
        increment = t/10;

    if seed is None:
        seed = 0

    # Algorithm, SSA or Tau-leaping?
    executable = None
    if stochkit_home is not None:
        if os.path.isfile(os.path.join(stochkit_home, algorithm)):
            executable = os.path.join(stochkit_home, algorithm)
        else:
            raise SimuliationError("stochkit executable '{0}' not found stochkit_home={1}".format(algorithm, stochkit_home))
    elif os.environ.get('STOCHKIT_HOME') is not None:
        if os.path.isfile(os.path.join(os.environ.get('STOCHKIT_HOME'), algorithm)):
            executable = os.path.join(os.environ.get('STOCHKIT_HOME'), algorithm)
    if executable is None:
        # try to find the executable in the path
        if os.environ.get('PATH') is not None:
            for dir in os.environ.get('PATH').split(':'):
                if os.path.isfile(os.path.join(dir, algorithm)):
                    executable = os.path.join(dir, algorithm)
                    break
    if executable is None:
        raise SimuliationError("stochkit executable '{0}' not found.  Make sure it is your path, or set STOCHKIT_HOME envronment variable'".format(algorithm))



    # Assemble the argument list
    args = ''
    args+='--model '
    args+=outfile
    args+=' --out-dir '+outdir
    args+=' -t '
    args+=str(t)
    num_output_points = str(int(float(t/increment)))
    args+=' -i ' + num_output_points
    args+=' --realizations '
    args+=str(realizations)
    print 'directories',directories
    if ensemblename in directories:
        print 'Ensemble '+ensemblename+' already existed, using --force.'
        args+=' --force'
    
    # Only use on processor per StochKit job. 
    args+= ' -p 1'
  
    # We keep all the trajectories by default.
    args+=' --keep-trajectories'

    args+=' --seed '
    args+=str(seed)

    # If we are using local mode, shell out and run StochKit (SSA or Tau-leaping)
    cmd = executable+' '+args

    # Execute
    try:
        print cmd
        handle = subprocess.Popen(cmd.split(' '))
        return_code = handle.wait()
        if return_code != 0:
            raise SimuliationError("Solver execution failed: '{0}'".format(cmd))
    except OSError as e:
        raise SimuliationError("Solver execution failed: {0}\n{1}".format(cmd, e))
    
    # Collect all the output data
    files = os.listdir(outdir + '/stats')
       
    trajectories = []
    files = os.listdir(outdir + '/trajectories')
    
    for filename in files:
        if 'trajectory' in filename:
            trajectories.append(numpy.loadtxt(outdir + '/trajectories/' + filename))
        else:
            raise SimuliationError("Couldn't identify file '{0}' found in output folder".format(filename))

    # Clean up
    #shutil.rmtree(prefix_basedir)

    return trajectories

# Exceptions
class StochMLImportError(Exception):
    pass

class InvalidStochMLError(Exception):
    pass


#
#
#




if __name__ == '__main__':
    """
    Here, as a test case, we run a simple two-state oscillator (Novak & Tyson 
    2008) as an example of a stochastic reaction system.
    """
        
    # =============================================
    # Define model species, initial values, parameters, and volume
    # =============================================    
    
    # stochastic volume parameter, omega
    omega = 150
    
    # parameter names consists of a list of strings    
    parameter_names = ['P','kt','kd','a0','a1','a2','kdx']
    
    # Parameter values consists of a list or numpy array of floats.
    # These have been converted to be in population, rather than concentration
    # units. For example, a concentration unit of 0.5mol/(L*s) is multiplied 
    # by a volume unit (omega), to get a population/s rate constant.
    parameter_values = np.array([2., 20., 1., 0.005, 0.05, 0.1, 1.])
    
    # Species names
    species_names = ['X','Y']
    
    # Initial values of each species (concentration converted to pop.)
    species_initial = (np.array([ 0.65609071,  0.85088331])*omega).astype(int)
    
    # To set up the model, first create an empty model object. Then, add 
    # species and parameters as was set up above.
    tyson_model = gillespy_model(name = "tyson-2-state")    
    tyson_model.initialize(species_names, species_initial,
                           parameter_names, parameter_values, omega)
    
    
    # =============================================  
    # Define the reactions within the model
    # =============================================  
    
    # creation of X:
    rxn1 = Reaction(name = 'X production',
                    reactants = {},
                    products = {'X':1},
                    propensity_function = '150*1/(1+(Y*Y/((150*150))))')
    
    # degradadation of X:
    rxn2 = Reaction(name = 'X degradation',
                reactants = {'X':1},
                products = {},
                propensity_function = 'kdx*X')
    
    # creation of Y:
    rxn3 = Reaction(name = 'Y production',
                reactants = {},
                products = {'Y':1},
                propensity_function = 'X*kt')
    
    # degradation of Y:
    rxn4 = Reaction(name = 'Y degradation',
                reactants = {'Y':1},
                products = {},
                propensity_function = 'kd*Y')
        
    # nonlinear Y term:
    rxn5 = Reaction(name = 'Y nonlin',
                reactants = {'Y':1},
                products = {},
                propensity_function = 'Y/(a0 + a1*(Y/150) + a2*Y*Y/(150*150))')
    
    reactions = [rxn1,rxn2,rxn3,rxn4,rxn5]
    tyson_model.addReaction(reactions)
    
    # returns trajectories from the tyson model
    tyson_trajectories = simulate(tyson_model)
    
    # plot just the first trajectory, 0, in both time and phase space:
    from matplotlib import gridspec
    
    plt.figure(figsize=(3.5*2*3/4,2.62*3/4))
    gs = gridspec.GridSpec(1,2)
    
    
    ax0 = plt.subplot(gs[0,0])
    ax0.plot(tyson_trajectories[0][:,0], tyson_trajectories[0][:,1], label='X')
    ax0.plot(tyson_trajectories[0][:,0], tyson_trajectories[0][:,2], label='Y')
    ax0.legend()
    ax0.set_xlabel('Time')
    ax0.set_ylabel('Species Count')
    ax0.set_title('Time Series Oscillation')
    
    ax1 = plt.subplot(gs[0,1])
    ax1.plot(tyson_trajectories[1][:,1], tyson_trajectories[0][:,2], 'k')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_title('Phase-Space Plot')
    
    plt.tight_layout()
    plt.show()

    
    
    
    
    
    
    
    
    
    
    
    
    