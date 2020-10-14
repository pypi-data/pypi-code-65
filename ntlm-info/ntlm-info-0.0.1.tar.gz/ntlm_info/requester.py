import base64
import requests
from impacket import smb3, smb, ntlm
import logging

from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

logger = logging.getLogger(__name__)


def request_http(url):
    logger.debug("Request HTTP for {}".format(url))
    headers = {
        'Authorization': 'NTLM TlRMTVNTUAABAAAAB4IIAAAAAAAAAAAAAAAAAAAAAAA='
    }

    request = requests.get(url, headers=headers, verify=False)

    if request.status_code not in [401, 302]:
        raise Exception(
            'Expecting response code 401 or 302, received: {}'.format(
                request.status_code))

    try:
        auth_header = request.headers['WWW-Authenticate']
    except KeyError:
        raise Exception(
            "NTLM Challenge response not found (WWW-Authenticate header missing)"
        )

    if 'NTLM' not in auth_header:
        raise Exception(
            'NTLM Challenge response not found (WWW-Authenticate does not contain "NTLM")'
        )

    challenge_message = base64.b64decode(
        auth_header.split(' ')[1].replace(',', ''))

    return challenge_message


def request_SMBv23(host, port=445):
    logger.debug("Request SMB2/3 for {}:{}".format(host, port))

    # start client
    smb_client = smb3.SMB3(host, host, sess_port=port)

    # start: modified from login()
    # https://github.com/SecureAuthCorp/impacket/blob/master/impacket/smb3.py

    session_setup = smb3.SMB2SessionSetup()

    if smb_client.RequireMessageSigning is True:
        session_setup['SecurityMode'] = smb3.SMB2_NEGOTIATE_SIGNING_REQUIRED
    else:
        session_setup['SecurityMode'] = smb3.SMB2_NEGOTIATE_SIGNING_ENABLED

    session_setup['Flags'] = 0

    # NTLMSSP
    blob = smb3.SPNEGO_NegTokenInit()
    blob['MechTypes'] = [
        smb3.TypesMech['NTLMSSP - Microsoft NTLM Security Support Provider']]

    auth = ntlm.getNTLMSSPType1(smb_client._Connection['ClientName'], '',
                                smb_client._Connection['RequireSigning'])
    blob['MechToken'] = auth.getData()

    session_setup['SecurityBufferLength'] = len(blob)
    session_setup['Buffer'] = blob.getData()

    packet = smb_client.SMB_PACKET()
    packet['Command'] = smb3.SMB2_SESSION_SETUP
    packet['Data'] = session_setup

    packet_id = smb_client.sendSMB(packet)

    smb_response = smb_client.recvSMB(packet_id)

    if smb_client._Connection['Dialect'] == smb3.SMB2_DIALECT_311:
        smb_client.__UpdatePreAuthHash(smb_response.rawData)

    # NTLM challenge
    if smb_response.isValidAnswer(smb3.STATUS_MORE_PROCESSING_REQUIRED):
        session_setup_response = smb3.SMB2SessionSetup_Response(
            smb_response['Data'])
        resp_token = smb3.SPNEGO_NegTokenResp(session_setup_response['Buffer'])

        return resp_token['ResponseToken']

    else:
        return None


def request_SMBv1(host, port=445):
    logger.debug("Request SMB1 for {}:{}".format(host, port))

    # start client
    smb_client = smb.SMB(host, host, sess_port=port)

    # start: modified from login_standard()
    # https://github.com/SecureAuthCorp/impacket/blob/master/impacket/smb.py

    session_setup = smb.SMBCommand(smb.SMB.SMB_COM_SESSION_SETUP_ANDX)
    session_setup['Parameters'] = smb.SMBSessionSetupAndX_Extended_Parameters()
    session_setup['Data'] = smb.SMBSessionSetupAndX_Extended_Data()

    session_setup['Parameters']['MaxBufferSize'] = 61440
    session_setup['Parameters']['MaxMpxCount'] = 2
    session_setup['Parameters']['VcNumber'] = 1
    session_setup['Parameters']['SessionKey'] = 0
    session_setup['Parameters']['Capabilities'] = smb.SMB.CAP_EXTENDED_SECURITY | \
        smb.SMB.CAP_USE_NT_ERRORS |  \
        smb.SMB.CAP_UNICODE | \
        smb.SMB.CAP_LARGE_READX | \
        smb.SMB.CAP_LARGE_WRITEX

    # NTLMSSP
    blob = smb.SPNEGO_NegTokenInit()

    blob['MechTypes'] = [
        smb.TypesMech['NTLMSSP - Microsoft NTLM Security Support Provider']]

    auth = ntlm.getNTLMSSPType1(smb_client.get_client_name(), '',
                                smb_client._SignatureRequired, use_ntlmv2=True)
    blob['MechToken'] = auth.getData()

    session_setup['Parameters']['SecurityBlobLength'] = len(blob)
    session_setup['Parameters'].getData()
    session_setup['Data']['SecurityBlob'] = blob.getData()
    session_setup['Data']['NativeOS'] = 'Unix'
    session_setup['Data']['NativeLanMan'] = 'Samba'

    smb_packet = smb.NewSMBPacket()

    if smb_client._SignatureRequired:
        smb_packet['Flags2'] |= smb_packet.SMB.FLAGS2_SMB_SECURITY_SIGNATURE

    smb_packet.addCommand(session_setup)

    smb_client.sendSMB(smb_packet)

    smb_response = smb_client.recvSMB()

    # NTLM challenge
    if smb_response.isValidAnswer(smb.SMB.SMB_COM_SESSION_SETUP_ANDX):

        session_response = smb.SMBCommand(smb_response['Data'][0])
        session_parameters = smb.SMBSessionSetupAndX_Extended_Response_Parameters(
            session_response['Parameters'])
        session_data = smb.SMBSessionSetupAndX_Extended_Response_Data(
            flags=smb_response['Flags2'])
        session_data['SecurityBlobLength'] = session_parameters['SecurityBlobLength']
        session_data.fromString(session_response['Data'])

        resp_token = smb.SPNEGO_NegTokenResp(session_data['SecurityBlob'])

        return resp_token['ResponseToken']

    else:
        return None
