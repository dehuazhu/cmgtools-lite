import PhysicsTools.HeppyCore.framework.config as cfg
from CMGTools.Production import eostools
from CMGTools.Production.dataset import createDataset, createMyDataset
import re
from pdb import set_trace

class ComponentCreator(object):
    def makeMCComponent(self,name,dataset,user,pattern,xSec=1,useAAA=False,unsafe=False,fracNegWeights=None):
        
         component = cfg.MCComponent(
             dataset=dataset,
             name = name,
             files = self.getFiles(dataset,user,pattern,useAAA=useAAA,unsafe=unsafe),
             xSection = xSec,
             nGenEvents = 1,
             triggers = [],
             effCorrFactor = 1,
         )
         component.splitFactor = 100
         component.fracNegWeights = fracNegWeights
         component.dataset_entries = self.getPrimaryDatasetEntries(dataset,user,pattern,useAAA=useAAA)
         return component

    def makePrivateMCComponent(self,name,dataset,files,xSec=1, prefix="auto"):
         if len(files) == 0:
            raise RuntimeError, "Trying to make a component %s with no files" % name
         dprefix = dataset +"/" if files[0][0] != "/" else ""
         if prefix == "auto":
            if (dprefix+files[0]).startswith("/store"): prefix = "root://eoscms.cern.ch//eos/cms"
            else: prefix = ""
         # prefix filenames with dataset unless they start with "/"
         component = cfg.MCComponent(
             dataset=dataset,
             name = name,
             files = [''.join([prefix,dprefix,f]) for f in files],
             xSection = xSec,
             nGenEvents = 1,
             triggers = [],
             effCorrFactor = 1,
         )
         component.splitFactor = 100

         return component
    
    def makePrivateDataComponent(self,name,dataset,files,json,xSec=1):
         if len(files) == 0:
            raise RuntimeError, "Trying to make a component %s with no files" % name
         dprefix = dataset +"/" if files[0][0] != "/" else ""
         component = cfg.DataComponent(
             name = name,
             files = ['root://eoscms.cern.ch//eos/cms%s%s' % (dprefix,f) for f in files],
             intLumi=1,
             triggers = [],
             json=json
         )
         component.splitFactor = 100

         return component

    def makeMyPrivateMCComponent(self,name,dataset,user,pattern,dbsInstance, xSec=1,useAAA=False):
#        set_trace()
        component = cfg.MCComponent(
            dataset=dataset,
            name = name,
            files = self.getMyFiles(dataset, user, pattern, dbsInstance, useAAA=useAAA),
            xSection = xSec,
            nGenEvents = 1,
            triggers = [],
            effCorrFactor = 1,
        )
        component.splitFactor = 100
        component.dataset_entries = self.getMyPrimaryDatasetEntries(dataset,user,pattern,dbsInstance,useAAA=useAAA) # same number as -query="events dataset=..."
        return component

    def getMyPrimaryDatasetEntries(self, dataset, user, pattern, dbsInstance, useAAA=False):
        # print 'getting files for', dataset,user,pattern
#        ds = createMyDataset(user, dataset, pattern, dbsInstance, True)
        ds = createDataset(user, dataset, pattern, True, None, None, None, False, dbsInstance)
        return ds.primaryDatasetEntries

    def getMyFiles(self, dataset, user, pattern, dbsInstance, useAAA=False):
        # print 'getting files for', dataset,user,pattern
#        ds = createMyDataset(user, dataset, pattern, dbsInstance, True )
        ds = createDataset(user, dataset, pattern, True, None, None, None, False, dbsInstance)
        files = ds.listOfGoodFiles()
        mapping = 'root://eoscms.cern.ch//eos/cms%s'
        if useAAA: mapping = 'root://cms-xrd-global.cern.ch/%s'
        return [ mapping % f for f in files]

    def getFilesFromEOS(self,name,dataset,path,pattern=".*root"):
        from CMGTools.Production.dataset import getDatasetFromCache, writeDatasetToCache
        if "%" in path: path = path % dataset;
        try:
            files = getDatasetFromCache('EOS%{path}%{pattern}.pck'.format(path = path.replace('/','_'), pattern = pattern))
        except IOError:
            files = [ 'root://eoscms.cern.ch/'+x for x in eostools.listFiles('/eos/cms'+path) if re.match(pattern,x) ] 
            if len(files) == 0:
                raise RuntimeError, "ERROR making component %s: no files found under %s matching '%s'" % (name,path,pattern)
            writeDatasetToCache('EOS%{path}%{pattern}.pck'.format(path = path.replace('/','_'), pattern = pattern), files)
        return files

    def makeMCComponentFromEOS(self,name,dataset,path,pattern=".*root",xSec=1):
        component = cfg.MCComponent(
            dataset=dataset,
            name = name,
            files = self.getFilesFromEOS(name,dataset,path,pattern),
            xSection = xSec,
            nGenEvents = 1,
            triggers = [],
            effCorrFactor = 1,
        )
        component.splitFactor = 100
        return component

    def getFilesFromPSI(self,name,dataset,path,pattern=".*root"):
        from CMGTools.Production.dataset import getDatasetFromCache, writeDatasetToCache
        if "%" in path: path = path % dataset;
        try:
            files = getDatasetFromCache('PSI%{path}%{pattern}.pck'.format(path = path.replace('/','_'), pattern = pattern))
        except IOError:
            files = [ 'root://t3se01.psi.ch//'+x.replace("/pnfs/psi.ch/cms/trivcat/","") for x in eostools.listFiles('/pnfs/psi.ch/cms/trivcat/'+path) if re.match(pattern,x) ] 
            if len(files) == 0:
                raise RuntimeError, "ERROR making component %s: no files found under %s matching '%s'" % (name,path,pattern)
            writeDatasetToCache('PSI%{path}%{pattern}.pck'.format(path = path.replace('/','_'), pattern = pattern), files)
        return files
    def makeMCComponentFromPSI(self,name,dataset,path,pattern=".*root",xSec=1):
        component = cfg.MCComponent(
            dataset=dataset,
            name = name,
            files = self.getFilesFromPSI(name,dataset,path,pattern),
            xSection = xSec,
            nGenEvents = 1,
            triggers = [],
            effCorrFactor = 1,
        )  
        component.splitFactor = 100
        return component

    def getFilesFromIC(self, dataset, user, pattern):
        # print 'getting files for', dataset,user,pattern
        ds = datasetToSource( user, dataset, pattern, True )
        files = ds.fileNames
        mapping = 'root://gfe02.grid.hep.ph.ic.ac.uk/pnfs/hep.ph.ic.ac.uk/data/cms%s'
        return [ mapping % f for f in files]

    def makeMCComponentFromIC(self,name,dataset,path,pattern=".*root",xSec=1):
        component = cfg.MCComponent(
            dataset=dataset,
            name = name,
            files = self.getFilesFromIC(dataset,path,pattern),
            xSection = xSec,
            nGenEvents = 1,
            triggers = [],
            effCorrFactor = 1,
        )
        component.splitFactor = 100
        return component

    def getFilesFromLocal(self,name,dataset,path,pattern=".*root"):
        from CMGTools.Production.dataset import getDatasetFromCache, writeDatasetToCache
        if "%" in path: path = path % dataset;
        try:
            files = getDatasetFromCache('Local%{path}%{pattern}.pck'.format(path = path.replace('/','_'), pattern = pattern))
        except IOError:
            files = [ x for x in eostools.listFiles(path,True) if re.match(pattern,x) ] 
            if len(files) == 0:
                raise RuntimeError, "ERROR making component %s: no files found under %s matching '%s'" % (name,path,pattern)
            writeDatasetToCache('Local%{path}%{pattern}.pck'.format(path = path.replace('/','_'), pattern = pattern), files)
        return files

    def makeMCComponentFromLocal(self,name,dataset,path,pattern=".*root",xSec=1):
        component = cfg.MCComponent(
            dataset=dataset,
            name = name,
            files = self.getFilesFromLocal(name,dataset,path,pattern),
            xSection = xSec,
            nGenEvents = 1,
            triggers = [],
            effCorrFactor = 1,
        )
        component.splitFactor = 100
        return component

    def makeDataComponent(self,name,dataset,user,pattern,json=None,run_range=None,triggers=[],vetoTriggers=[],useAAA=False,jsonFilter=False):
        component = cfg.DataComponent(
            #dataset = dataset,
            name = name,
            files = self.getFiles(dataset,user,pattern,run_range=run_range,useAAA=useAAA,json=(json if jsonFilter else None)),
            intLumi = 1,
            triggers = triggers,
            json = (json if jsonFilter else None)
            )
        component.json = json
        component.vetoTriggers = vetoTriggers
        component.dataset_entries = self.getPrimaryDatasetEntries(dataset,user,pattern,run_range=run_range)
        component.dataset = dataset
        component.run_range = run_range
        component.splitFactor = 100
        return component

    def getFiles(self, dataset, user, pattern, useAAA=False, run_range=None, json=None, unsafe = False):
        # print 'getting files for', dataset,user,pattern
        ds = createDataset( user, dataset, pattern, readcache=True, run_range=run_range, json=json, unsafe = unsafe )
        files = ds.listOfGoodFiles()
        mapping = 'root://eoscms.cern.ch//eos/cms%s'
        if useAAA: mapping = 'root://cms-xrd-global.cern.ch/%s'
        return [ mapping % f for f in files]

    def getPrimaryDatasetEntries(self, dataset, user, pattern, useAAA=False, run_range=None):
        # print 'getting files for', dataset,user,pattern
        ds = createDataset( user, dataset, pattern, True, run_range=run_range )
        return ds.primaryDatasetEntries

    def getSkimEfficiency(self,dataset,user):
        from CMGTools.Production.datasetInformation import DatasetInformation
        info=DatasetInformation(dataset,user,'',False,False,'','','')
        fraction=info.dataset_details['PrimaryDatasetFraction']
        if fraction<0.001:
            print 'ERROR FRACTION IS ONLY ',fraction
        return fraction 
        

def testSamples(mcSamples, allowAAA=False):
   from subprocess import check_output, CalledProcessError
   from CMGTools.Production.changeComponentAccessMode import convertFile
   for X in mcSamples:
        print X.name, len(X.files)
        try:
            print "\tSample is accessible? ",("events" in check_output(["edmFileUtil","--ls",X.files[0]]))
        except CalledProcessError:
            fail = True
            if allowAAA:
                try:
                    newfile = convertFile(X.files[0], "root://cms-xrd-global.cern.ch/%s")
                    if newfile != X.files[0]:
                        if "events" in check_output(["edmFileUtil","--ls",newfile]):
                            print "yes, but only via AAA"
                            fail = False
                except:
                    pass
            if fail: print "\tERROR trying to access ",X.files[0]

