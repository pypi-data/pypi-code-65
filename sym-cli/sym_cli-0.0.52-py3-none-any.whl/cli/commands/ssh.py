import re
import sys
from datetime import timedelta
from functools import wraps
from typing import Optional, Sequence

import click

from ..decorators import loses_interactivity, require_bins, require_login
from ..helpers.boto import host_to_instance
from ..helpers.global_options import GlobalOptions
from ..helpers.keywords_to_options import keywords_to_options
from ..helpers.options import resource_argument
from ..helpers.ssh import ensure_ssh_key, raw_ssh, start_ssh_session
from .sym import sym

SSH_MAN = """
     ssh [-AaCfGgKkMNnqsTtVvXxYy] [-B bind_interface] [-b bind_address] [-c cipher_spec]
         [-D [bind_address:]port] [-E log_file] [-e escape_char] [-F configfile] [-I pkcs11]
         [-i identity_file] [-J destination] [-L address] [-l login_name] [-m mac_spec] [-O ctl_cmd]
         [-o option] [-p port] [-Q query_option] [-R address] [-S ctl_path] [-W host:port]
         [-w local_tun[:remote_tun]] destination [command]
"""

SSH_OPTS = list(
    map(
        lambda x: x.casefold(),
        {
            "LogLevel",
            "CheckHostIP",
            "ForwardX11Trusted",
            "HostKeyAlias",
            "SetEnv",
            "UpdateHostKeys",
            "ClearAllForwardings",
            "GSSAPIKeyExchange",
            "HashKnownHosts",
            "remote_tun",
            "CertificateFile",
            "Hostname",
            "RemoteForward",
            "PubkeyAuthentication",
            "HostbasedKeyTypes",
            "AddKeysToAgent",
            "NumberOfPasswordPrompts",
            "KbdInteractiveDevices",
            "BatchMode",
            "PubkeyAcceptedKeyTypes",
            "CASignatureAlgorithms",
            "LocalCommand",
            "GSSAPIClientIdentity",
            "UserKnownHostsFile",
            "CanonicalizePermittedCNAMEs",
            "PermitLocalCommand",
            "HostName",
            "VerifyHostKeyDNS",
            "UsePrivilegedPort",
            "Port",
            "AddressFamily",
            "RemoteCommand",
            "HostKeyAlgorithms",
            "ForwardAgent",
            "CanonicalDomains",
            "VisualHostKey",
            "ExitOnForwardFailure",
            "EscapeChar",
            "GSSAPIDelegateCredentials",
            "IdentitiesOnly",
            "RekeyLimit",
            "TunnelDevice",
            "ControlMaster",
            "Ciphers",
            "KbdInteractiveAuthentication",
            "DynamicForward",
            "XAuthLocation",
            "SmartcardDevice",
            "ControlPath",
            "CanonicalizeHostname",
            "RequestTTY",
            "BindAddress",
            "StreamLocalBindUnlink",
            "StreamLocalBindMask",
            "RSAAuthentication",
            "RhostsRSAAuthentication",
            "ConnectionAttempts",
            "LocalForward",
            "PKCS11Provider",
            "PreferredAuthentications",
            "ServerAliveCountMax",
            "TCPKeepAlive",
            "Cipher",
            "local_tun",
            "Host",
            "ForwardX11Timeout",
            "Tunnel",
            "ChallengeResponseAuthentication",
            "GSSAPIKexAlgorithms",
            "HostbasedAuthentication",
            "CanonicalizeFallbackLocal",
            "Protocol",
            "ConnectTimeout",
            "ProxyJump",
            "SendEnv",
            "User",
            "GatewayPorts",
            "MACs",
            "Compression",
            "IPQoS",
            "GlobalKnownHostsFile",
            "ServerAliveInterval",
            "StrictHostKeyChecking",
            "KexAlgorithms",
            "CompressionLevel",
            "IdentityAgent",
            "ProxyUseFdpass",
            "GSSAPIAuthentication",
            "GSSAPIRenewalForcesRekey",
            "GSSAPITrustDns",
            "NoHostAuthenticationForLocalhost",
            "ProxyCommand",
            "PasswordAuthentication",
            "CanonicalizeMaxDots",
            "ControlPersist",
            "GSSAPIServerIdentity",
            "Match",
            "IdentityFile",
            "ForwardX11",
            "FingerprintHash",
        },
    )
)


def parse_ssh_man(ssh_man):
    flags_pattern = re.compile(r"ssh \[-(\w+)\]")
    options_pattern = re.compile(r"\[-(\w) (\S+)\]")

    flags = list(flags_pattern.search(ssh_man)[1])
    options = options_pattern.findall(ssh_man)

    return (flags, options)


def ssh_options(fn):
    flags, options = parse_ssh_man(SSH_MAN)
    for flag in flags:
        fn = click.option(f"-{flag}", flag, is_flag=True)(fn)
    for (option, name) in options:
        fn = click.option(f"-{option}", option, metavar=f"<{name}>", multiple=True)(fn)
    for opt in SSH_OPTS:
        fn = click.option(f"-o{opt}", opt, multiple=True)(fn)
    return fn


def normalize_token(token):
    if token.startswith("o") and len(token) > 1:
        return token.casefold()
    return token


def encode_options(kv):
    k, v = kv
    if k in SSH_OPTS:
        return {"o": [f"{k}={vv}" for vv in v]}
    else:
        return {k: v}


@sym.command(
    short_help="Start a SSH session",
    context_settings={
        "ignore_unknown_options": True,
        "token_normalize_func": normalize_token,
    },
)
@resource_argument
@ssh_options
@click.option("-p", "--port", default=22, type=int, show_default=True)
@click.argument("destination", required=False)
@click.argument("command", nargs=-1, required=False)
@click.make_pass_decorator(GlobalOptions)
@loses_interactivity
@require_bins("aws", "session-manager-plugin", "ssh")
@require_login
def ssh(
    options: GlobalOptions,
    resource: str,
    destination: Optional[str],
    port: int,
    command: Sequence[str],
    **kwargs,
) -> None:
    ssh_args = keywords_to_options(map(encode_options, kwargs.items()))

    if not destination:
        raw_ssh({"p": str(port)}, *ssh_args)

    client = options.create_saml_client(resource)

    client.dprint(f"ssh: args={ssh_args}")

    instance = host_to_instance(client, destination)
    start_ssh_session(client, instance, port, args=ssh_args, command=command, wrap=False)
