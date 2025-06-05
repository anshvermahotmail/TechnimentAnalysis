import json

# Paste raw FQDNs as multiline string (simulating copy-paste from Excel)
raw_fqdn_input = """
hostname.g.a.c
hostname1.g.a.c
hostname2.g.a.c
"""

# Extract just the hostname part (before first dot)
hostnames = [line.strip().split('.')[0] for line in raw_fqdn_input.strip().splitlines() if line.strip()]

# Toggle between variable reference or direct IP/hostname list for whitelist
# whitelist = ["fqdn1.sld.tld", "fqdn2.sld.tld"]
whitelist = "CONSTANTS:vermaa_whitelist"

local_subnets = ["100.116.121.0/24", "100.124.121.0/24"]

url_rewrites = [
    {
        "regex": "100[.]116[.]123[.]240",
        "replace": "epm.glb.cala.attmx.avayacloud.com"
    },
    {
        "regex": "100[.]124[.]123[.]240",
        "replace": "epmgeo.glb.cala.attmx.avayacloud.com"
    }
]


header_updates = [
    {
        "header": "TerminationURL",
        "regex": "http",
        "replace": "https"
    }
]


pools = {}

for host in hostnames:
    base_name = host.upper()
    pool_name = f"CUSTOMER_{base_name}_15070"
    regex_https = f"^https://({host}[.]glb[.]ac[.]com):443/"
    regex_http = f"^http://({host}[.]glb[.]ac[.]com):443/"

    for protocol in ["HTTPS", "HTTP"]:
        pool_key = f"{pool_name}_{protocol}"
        pool_config = {
            "description": f"{pool_name} {protocol} Pool Selection",
            "excludeLog": False,
            "localSubnets": local_subnets,
            "poolName": pool_name,
            "regexUrl": regex_https if protocol == "HTTPS" else regex_http,
            "urlQueryStringReplaceEncodeFull": True,
            "urlQueryStringReplace": url_rewrites,
            "responseHeadersUpdate": header_updates,
        }

        # Handle variable-based or static whitelist
        if isinstance(whitelist, str):
            pool_config["whitelist"] = f"${{{whitelist}}}"
        else:
            pool_config["whitelist"] = whitelist

        pools[pool_key] = pool_config

output = {"POOLS": pools}

with open("pools_output.json", "w") as f:
    json.dump(output, f, indent=2)
