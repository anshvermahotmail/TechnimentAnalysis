import json

hostnames = [
"hostname1",
"hostname2",
"hostname3"
]


whitelist = ["fqdn1.sld.tld","fqdn2.sld.tld"]
local_subnets = ["2.3.4.5/24", "3.4.5.6/24"]
url_rewrites = [
    {
        "regex": "1[.]1[.]1[.]2",
        "replace": "e.g.c.a.a.com"
    },
    {
        "regex": "1[.]2[.]1[.]2",
        "replace": "eg.g.c.a.a.com"
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
        pools[f"{pool_name}_{protocol}"] = {
            "description": f"{pool_name} {protocol} Pool Selection",
            "excludeLog": False,
            "localSubnets": local_subnets,
            "poolName": pool_name,
            "regexUrl": regex_https if protocol == "HTTPS" else regex_http,
            "urlQueryStringReplaceEncodeFull": True,
            "urlQueryStringReplace": url_rewrites,
            "responseHeadersUpdate": header_updates,
            "whitelist": whitelist
        }

output = {"POOLS": pools}

with open("pools_output.json", "w") as f:
    json.dump(output, f, indent=2)