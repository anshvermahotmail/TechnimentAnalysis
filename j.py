import json

hostnames = [
    "ochocientosvxmlmty",
    "unefonmtxxvxmlmty",
    "empresarialvxmlmty",
    "hibridovxmlmty",
    "postpagovxmlmty",
    "prepagomtxxvxmlmty",
    "visualvxmlmty",
    "visualmtxxvxmlmty",
    "ciamsvxmlmty",
    "activacionesvxmlmty",
    "renovacionpiasvxmlmty",
    "regtarjetasvxmlmty",
    "hardblockvxmlmty",
    "unefonvxmlmty",
    "prepagovxmlmty",
    "pucvxmlmty",
    "saldovxmlmty",
    "unoochovxmldsmty06",
    "unoochovxmldsmty07",
    "unoochovxmldsmty08",
    "unoochovxmldsmty09",
    "unoochovxmldsmty10",
    "unoochovxmldsmty11",
    "unoochovxmldsmty12",
    "unefonmatvxmldsmty06",
    "unefonmatvxmldsmty07",
    "unefonmatvxmldsmty08",
    "unefonmatvxmldsmty09",
    "unefonmatvxmldsmty10",
    "unefonmatvxmldsmty11",
    "unefonmatvxmldsmty12",
    "enterprisedsmty06",
    "enterprisedsmty07",
    "enterprisedsmty08",
    "enterprisedsmty09",
    "enterprisedsmty10",
    "enterprisedsmty11",
    "enterprisedsmty12",
    "hibri611dsmty06",
    "hibri611dsmty07",
    "hibri611dsmty08",
    "hibri611dsmty09",
    "hibri611dsmty10",
    "hibri611dsmty11",
    "hibri611dsmty12",
    "postpag611dsmty06",
    "postpag611dsmty07",
    "postpag611dsmty08",
    "postpag611dsmty09",
    "postpag611dsmty10",
    "postpag611dsmty11",
    "postpag611dsmty12",
    "prepmatvxmldsmty06",
    "prepmatvxmldsmty07",
    "prepmatvxmldsmty08",
    "prepmatvxmldsmty09",
    "prepmatvxmldsmty10",
    "prepmatvxmldsmty11",
    "prepmatvxmldsmty12",
    "visualvxmldsmty06",
    "visualvxmldsmty07",
    "visualvxmldsmty08",
    "visualvxmldsmty09",
    "visualvxmldsmty10",
    "visualvxmldsmty11",
    "visualvxmldsmty12",
    "visualmtxxdsmty06",
    "visualmtxxdsmty07",
    "visualmtxxdsmty08",
    "visualmtxxdsmty09",
    "visualmtxxdsmty10",
    "visualmtxxdsmty11",
    "visualmtxxdsmty12",
    "ciamsvxmldsmty06",
    "ciamsvxmldsmty07",
    "ciamsvxmldsmty08",
    "ciamsvxmldsmty09",
    "ciamsvxmldsmty10",
    "ciamsvxmldsmty11",
    "ciamsvxmldsmty12",
    "activavxmldsmty01",
    "activavxmldsmty02",
    "activavxmldsmty03",
    "activavxmldsmty04",
    "activavxmldsmty05",
    "activavxml502dsmty01",
    "activavxml502dsmty02",
    "activavxml502dsmty03",
    "activavxml502dsmty04",
    "activavxml502dsmty05",
    "renovacionpiasdsmty01",
    "renovacionpiasdsmty02",
    "renovacionpiasdsmty03",
    "renovacionpiasdsmty04",
    "renovacionpiasdsmty05",
    "regtarjetasdsmty13",
    "regtarjetasdsmty14",
    "regtarjetasdsmty15",
    "hbvxmldsmty13",
    "hbvxmldsmty14",
    "hbvxmldsmty15",
    "unefonvxmldsmty06",
    "unefonvxmldsmty07",
    "unefonvxmldsmty08",
    "unefonvxmldsmty09",
    "unefonvxmldsmty10",
    "unefonvxmldsmty11",
    "unefonvxmldsmty12",
    "prepag611dsmty06",
    "prepag611dsmty07",
    "prepag611dsmty08",
    "prepag611dsmty09",
    "prepag611dsmty10",
    "prepag611dsmty11",
    "prepag611dsmty12",
    "prepag611dsmty13",
    "prepag611dsmty14",
    "prepag611dsmty15",
    "saldovxmldsmty13",
    "saldovxmldsmty14",
    "saldovxmldsmty15",
    "saldovxml502dsmty13",
    "saldovxml502dsmty14",
    "saldovxml502dsmty15"
]


whitelist = ["10.55.11.0/24"]
local_subnets = ["100.116.121.0/24", "100.116.121.0/24"]
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
    regex_https = f"^https://({host}[.]glb[.]avayacloud[.]com):443/"
    regex_http = f"^http://({host}[.]glb[.]avayacloud[.]com):443/"
    
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

print("JSON generated and saved to 'pools_output.json'")
