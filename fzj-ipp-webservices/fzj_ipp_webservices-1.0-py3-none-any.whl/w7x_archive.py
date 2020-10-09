import urllib.request
import json
import numpy

API_HOME = 'http://archive-webapi.ipp-hgw.mpg.de';
_coil_streams = {
        'nonplanar 1' : '/ArchiveDB/raw/W7X/CoDaStationDesc.84/DataModuleDesc.21643_DATASTREAM/0/current_npc1 (AAE10)',
        'nonplanar 2' : '/ArchiveDB/raw/W7X/CoDaStationDesc.84/DataModuleDesc.21643_DATASTREAM/1/current_npc2 (AAE29)',
        'nonplanar 3' : '/ArchiveDB/raw/W7X/CoDaStationDesc.84/DataModuleDesc.21643_DATASTREAM/2/current_npc3 (AAE38)',
        'nonplanar 4' : '/ArchiveDB/raw/W7X/CoDaStationDesc.84/DataModuleDesc.21643_DATASTREAM/3/current_npc4 (AAE47)',
        'nonplanar 5' : '/ArchiveDB/raw/W7X/CoDaStationDesc.84/DataModuleDesc.21643_DATASTREAM/4/current_npc5 (AAE56)',
		
        'planar A'    : '/ArchiveDB/raw/W7X/CoDaStationDesc.84/DataModuleDesc.21643_DATASTREAM/5/current_pca (AAE14)',
        'planar B'    : '/ArchiveDB/raw/W7X/CoDaStationDesc.84/DataModuleDesc.21643_DATASTREAM/6/current_pcb (AAE23)',
		
        'trim 1'      : '/ArchiveDB/raw/W7X/CoDaStationDesc.10082/DataModuleDesc.10084_DATASTREAM/48/AAQ11_ActVal_I',
        'trim 2'      : '/ArchiveDB/raw/W7X/CoDaStationDesc.10082/DataModuleDesc.10084_DATASTREAM/49/AAQ22_ActVal_I',
        'trim 3'      : '/ArchiveDB/raw/W7X/CoDaStationDesc.10082/DataModuleDesc.10084_DATASTREAM/50/AAQ31_ActVal_I',
        'trim 4'      : '/ArchiveDB/raw/W7X/CoDaStationDesc.10082/DataModuleDesc.10084_DATASTREAM/51/AAQ41_ActVal_I',
        'trim 5'      : '/ArchiveDB/raw/W7X/CoDaStationDesc.10082/DataModuleDesc.10084_DATASTREAM/52/AAQ51_ActVal_I',
		
		'sweep 1'     : '/ArchiveDB/codac/W7X/CoDaStationDesc.12/DataModuleDesc.16_DATASTREAM/0/ACM11 _ ACG 38 Module 1 upper',
		'sweep 2'     : '/ArchiveDB/codac/W7X/CoDaStationDesc.12/DataModuleDesc.16_DATASTREAM/1/ACM19 _ ACG 39 Module 1 lower',
		'sweep 3'     : '/ArchiveDB/codac/W7X/CoDaStationDesc.12/DataModuleDesc.16_DATASTREAM/2/ACM21 _ ACG 28 Module 2 upper',
		'sweep 4'     : '/ArchiveDB/codac/W7X/CoDaStationDesc.12/DataModuleDesc.16_DATASTREAM/3/ACM29 _ ACG 29 Module 2 lower',
		'sweep 5'     : '/ArchiveDB/codac/W7X/CoDaStationDesc.12/DataModuleDesc.16_DATASTREAM/4/ACM31 _ ACG 18 Module 3 upper',
		'sweep 6'     : '/ArchiveDB/codac/W7X/CoDaStationDesc.12/DataModuleDesc.16_DATASTREAM/5/ACM39 _ ACG 19 Module 3 lower',
		'sweep 7'     : '/ArchiveDB/codac/W7X/CoDaStationDesc.12/DataModuleDesc.16_DATASTREAM/6/ACM41 _ ACG 48 Module 4 upper',
		'sweep 8'     : '/ArchiveDB/codac/W7X/CoDaStationDesc.12/DataModuleDesc.16_DATASTREAM/7/ACM49 _ ACG 49 Module 4 lower',
		'sweep 9'     : '/ArchiveDB/codac/W7X/CoDaStationDesc.12/DataModuleDesc.16_DATASTREAM/8/ACM51 _ ACG 58 Module 5 upper',
		'sweep 10'    : '/ArchiveDB/codac/W7X/CoDaStationDesc.12/DataModuleDesc.16_DATASTREAM/9/ACM59 _ ACG 59 Module 5 lower',
		
		'I plasma' : '/Test/raw/Minerva1/Minerva.Magnetics15.Iplasma/Iplasma_QXR11CE001x_DATASTREAM/V1/0/Iplasma_for_continous_Rogowski_QXR11CE001x'
};

_coil_streams_iota_corrected = {
		'nonplanar 1' : '/ArchiveDB/raw/W7XAnalysis/Equilibrium/RefEq_PARLOG/V1/parms/coilCurrents_iotaCorrected/[0]',
		'nonplanar 2' : '/ArchiveDB/raw/W7XAnalysis/Equilibrium/RefEq_PARLOG/V1/parms/coilCurrents_iotaCorrected/[1]',
		'nonplanar 3' : '/ArchiveDB/raw/W7XAnalysis/Equilibrium/RefEq_PARLOG/V1/parms/coilCurrents_iotaCorrected/[2]',
		'nonplanar 4' : '/ArchiveDB/raw/W7XAnalysis/Equilibrium/RefEq_PARLOG/V1/parms/coilCurrents_iotaCorrected/[3]',
		'nonplanar 5' : '/ArchiveDB/raw/W7XAnalysis/Equilibrium/RefEq_PARLOG/V1/parms/coilCurrents_iotaCorrected/[4]',
		
		'planar A' :    '/ArchiveDB/raw/W7XAnalysis/Equilibrium/RefEq_PARLOG/V1/parms/coilCurrents_iotaCorrected/[5]',
		'planar B' :    '/ArchiveDB/raw/W7XAnalysis/Equilibrium/RefEq_PARLOG/V1/parms/coilCurrents_iotaCorrected/[6]'
};

def getShotData(shotID):
	infile = urllib.request.urlopen(API_HOME + '/programs.json?from=' + shotID);
	return json.load(infile)['programs'][0];

def getStream(stream, fromval, toval):
        urlstring = API_HOME + _coil_streams[stream] + '/_signal.json?from=' + str(fromval) + '&upto=' + str(toval);
        #print('Reading ' + stream + ' from ' + urlstring.replace(' ', '%20'));
        infile = urllib.request.urlopen(urlstring.replace(' ', '%20'));
        return json.load(infile);

def getStreamAvg(stream, fromval, toval):
        data = getStream(stream, fromval, toval);
        return numpy.average(data['values']);

def getCoilCurrentsFromStreams(shotID, streams):
        shotData = getShotData(shotID);
        
        fromval = shotData['from'];
        toval   = shotData['upto'];

        averages = {};

        for k in streams.keys():
            try:
                averages[k] = getStreamAvg(k, fromval, toval);
            except Exception:
                print('Failed to load ' + k + ', setting to 0');
                averages[k] = 0;
        
        return averages;

def getCoilCurrents(shotID):
	return getCoilCurrentsFromStreams(shotID, _coil_streams);

def getIotaCorrectedCoilCurrents(shotID):
	return getCoilCurrentsFromStreams(shotID, _coil_streams_iota_corrected);