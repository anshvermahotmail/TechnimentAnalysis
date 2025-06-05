import json

# 📋 Paste your FQDN-port mappings below
raw_input = """
ochocientosvxmlmty.glb.avayacloud.com	15070
ochocientosvxmlmty.glb.avayacloud.com	15070
unefonmtxxvxmlmty.glb.avayacloud.com	15131
unefonmtxxvxmlmty.glb.avayacloud.com	15131
empresarialvxmlmty.glb.avayacloud.com	15060
empresarialvxmlmty.glb.avayacloud.com	15060
hibridovxmlmty.glb.avayacloud.com	15090
hibridovxmlmty.glb.avayacloud.com	15090
postpagovxmlmty.glb.avayacloud.com	15126
postpagovxmlmty.glb.avayacloud.com	15126
prepagomtxxvxmlmty.glb.avayacloud.com	15132
prepagomtxxvxmlmty.glb.avayacloud.com	15132
visualvxmlmty.glb.avayacloud.com	15040
visualvxmlmty.glb.avayacloud.com	15040
visualmtxxvxmlmty.glb.avayacloud.com	15133
visualmtxxvxmlmty.glb.avayacloud.com	15133
ciamsvxmlmty.glb.avayacloud.com	15124
ciamsvxmlmty.glb.avayacloud.com	15124
activacionesvxmlmty.glb.avayacloud.com	15125
activacionesvxmlmty.glb.avayacloud.com	15125
renovacionpiasvxmlmty.glb.avayacloud.com	15120
renovacionpiasvxmlmty.glb.avayacloud.com	15120
regtarjetasvxmlmty.glb.avayacloud.com	15100
regtarjetasvxmlmty.glb.avayacloud.com	15100
hardblockvxmlmty.glb.avayacloud.com	15110
hardblockvxmlmty.glb.avayacloud.com	15110
unefonvxmlmty.glb.avayacloud.com	15020
unefonvxmlmty.glb.avayacloud.com	15020
prepagovxmlmty.glb.avayacloud.com	15050
prepagovxmlmty.glb.avayacloud.com	15050
pucvxmlmty.glb.avayacloud.com	11010
pucvxmlmty.glb.avayacloud.com	11010
saldovxmlmty.glb.avayacloud.com	11090
saldovxmlmty.glb.avayacloud.com	11090
unoochovxmldsmty06.glb.avayacloud.com	17507
unoochovxmldsmty06.glb.avayacloud.com	17507
unoochovxmldsmty07.glb.avayacloud.com	17507
unoochovxmldsmty07.glb.avayacloud.com	17507
unoochovxmldsmty08.glb.avayacloud.com	17507
unoochovxmldsmty08.glb.avayacloud.com	17507
unoochovxmldsmty09.glb.avayacloud.com	17507
unoochovxmldsmty09.glb.avayacloud.com	17507
unoochovxmldsmty10.glb.avayacloud.com	17507
unoochovxmldsmty10.glb.avayacloud.com	17507
unoochovxmldsmty11.glb.avayacloud.com	17507
unoochovxmldsmty11.glb.avayacloud.com	17507
unoochovxmldsmty12.glb.avayacloud.com	17507
unoochovxmldsmty12.glb.avayacloud.com	17507
unefonmatvxmldsmty06.glb.avayacloud.com	17515
unefonmatvxmldsmty06.glb.avayacloud.com	17515
unefonmatvxmldsmty07.glb.avayacloud.com	17515
unefonmatvxmldsmty07.glb.avayacloud.com	17515
unefonmatvxmldsmty08.glb.avayacloud.com	17515
unefonmatvxmldsmty08.glb.avayacloud.com	17515
unefonmatvxmldsmty09.glb.avayacloud.com	17515
unefonmatvxmldsmty09.glb.avayacloud.com	17515
unefonmatvxmldsmty10.glb.avayacloud.com	17515
unefonmatvxmldsmty10.glb.avayacloud.com	17515
unefonmatvxmldsmty11.glb.avayacloud.com	15515
unefonmatvxmldsmty11.glb.avayacloud.com	15515
unefonmatvxmldsmty12.glb.avayacloud.com	17515
unefonmatvxmldsmty12.glb.avayacloud.com	17515
enterprisedsmty06.glb.avayacloud.com	17506
enterprisedsmty06.glb.avayacloud.com	17506
enterprisedsmty07.glb.avayacloud.com	17506
enterprisedsmty07.glb.avayacloud.com	17506
enterprisedsmty08.glb.avayacloud.com	17506
enterprisedsmty08.glb.avayacloud.com	17506
enterprisedsmty09.glb.avayacloud.com	17506
enterprisedsmty09.glb.avayacloud.com	17506
enterprisedsmty10.glb.avayacloud.com	17506
enterprisedsmty10.glb.avayacloud.com	17506
enterprisedsmty11.glb.avayacloud.com	17506
enterprisedsmty11.glb.avayacloud.com	17506
enterprisedsmty12.glb.avayacloud.com	17506
enterprisedsmty12.glb.avayacloud.com	17506
hibri611dsmty06.glb.avayacloud.com	17504
hibri611dsmty06.glb.avayacloud.com	17504
hibri611dsmty07.glb.avayacloud.com	17504
hibri611dsmty07.glb.avayacloud.com	17504
hibri611dsmty08.glb.avayacloud.com	17504
hibri611dsmty08.glb.avayacloud.com	17504
hibri611dsmty09.glb.avayacloud.com	17504
hibri611dsmty09.glb.avayacloud.com	17504
hibri611dsmty10.glb.avayacloud.com	17504
hibri611dsmty10.glb.avayacloud.com	17504
hibri611dsmty11.glb.avayacloud.com	17504
hibri611dsmty11.glb.avayacloud.com	17504
hibri611dsmty12.glb.avayacloud.com	17504
hibri611dsmty12.glb.avayacloud.com	17504
postpag611dsmty06.glb.avayacloud.com	17501
postpag611dsmty06.glb.avayacloud.com	17501
postpag611dsmty07.glb.avayacloud.com	17501
postpag611dsmty07.glb.avayacloud.com	17501
postpag611dsmty08.glb.avayacloud.com	17501
postpag611dsmty08.glb.avayacloud.com	17501
postpag611dsmty09.glb.avayacloud.com	17501
postpag611dsmty09.glb.avayacloud.com	17501
postpag611dsmty10.glb.avayacloud.com	17501
postpag611dsmty10.glb.avayacloud.com	17501
postpag611dsmty11.glb.avayacloud.com	17501
postpag611dsmty11.glb.avayacloud.com	17501
postpag611dsmty12.glb.avayacloud.com	17501
postpag611dsmty12.glb.avayacloud.com	17501
prepmatvxmldsmty06.glb.avayacloud.com	17516
prepmatvxmldsmty06.glb.avayacloud.com	17516
prepmatvxmldsmty07.glb.avayacloud.com	17516
prepmatvxmldsmty07.glb.avayacloud.com	17516
prepmatvxmldsmty08.glb.avayacloud.com	17516
prepmatvxmldsmty08.glb.avayacloud.com	17516
prepmatvxmldsmty09.glb.avayacloud.com	17516
prepmatvxmldsmty09.glb.avayacloud.com	17516
prepmatvxmldsmty10.glb.avayacloud.com	17516
prepmatvxmldsmty10.glb.avayacloud.com	17516
prepmatvxmldsmty11.glb.avayacloud.com	17516
prepmatvxmldsmty11.glb.avayacloud.com	17516
prepmatvxmldsmty12.glb.avayacloud.com	17516
prepmatvxmldsmty12.glb.avayacloud.com	17516
visualvxmldsmty06.glb.avayacloud.com	17505
visualvxmldsmty06.glb.avayacloud.com	17505
visualvxmldsmty07.glb.avayacloud.com	17505
visualvxmldsmty07.glb.avayacloud.com	17505
visualvxmldsmty08.glb.avayacloud.com	17505
visualvxmldsmty08.glb.avayacloud.com	17505
visualvxmldsmty09.glb.avayacloud.com	17505
visualvxmldsmty09.glb.avayacloud.com	17505
visualvxmldsmty10.glb.avayacloud.com	17505
visualvxmldsmty10.glb.avayacloud.com	17505
visualvxmldsmty11.glb.avayacloud.com	17505
visualvxmldsmty11.glb.avayacloud.com	17505
visualvxmldsmty12.glb.avayacloud.com	17505
visualvxmldsmty12.glb.avayacloud.com	17505
visualmtxxdsmty06.glb.avayacloud.com	17517
visualmtxxdsmty06.glb.avayacloud.com	17517
visualmtxxdsmty07.glb.avayacloud.com	17517
visualmtxxdsmty07.glb.avayacloud.com	17517
visualmtxxdsmty08.glb.avayacloud.com	17517
visualmtxxdsmty08.glb.avayacloud.com	17517
visualmtxxdsmty09.glb.avayacloud.com	17517
visualmtxxdsmty09.glb.avayacloud.com	17517
visualmtxxdsmty10.glb.avayacloud.com	17517
visualmtxxdsmty10.glb.avayacloud.com	17517
visualmtxxdsmty11.glb.avayacloud.com	17517
visualmtxxdsmty11.glb.avayacloud.com	17517
visualmtxxdsmty12.glb.avayacloud.com	17517
visualmtxxdsmty12.glb.avayacloud.com	17517
ciamsvxmldsmty06.glb.avayacloud.com	17508
ciamsvxmldsmty06.glb.avayacloud.com	17508
ciamsvxmldsmty07.glb.avayacloud.com	17508
ciamsvxmldsmty07.glb.avayacloud.com	17508
ciamsvxmldsmty08.glb.avayacloud.com	17508
ciamsvxmldsmty08.glb.avayacloud.com	17508
ciamsvxmldsmty09.glb.avayacloud.com	17508
ciamsvxmldsmty09.glb.avayacloud.com	17508
ciamsvxmldsmty10.glb.avayacloud.com	17508
ciamsvxmldsmty10.glb.avayacloud.com	17508
ciamsvxmldsmty11.glb.avayacloud.com	17508
ciamsvxmldsmty11.glb.avayacloud.com	17508
ciamsvxmldsmty12.glb.avayacloud.com	17508
ciamsvxmldsmty12.glb.avayacloud.com	17508
activavxmldsmty01.glb.avayacloud.com	17501
activavxmldsmty01.glb.avayacloud.com	17501
activavxmldsmty02.glb.avayacloud.com	17501
activavxmldsmty02.glb.avayacloud.com	17501
activavxmldsmty03.glb.avayacloud.com	17501
activavxmldsmty03.glb.avayacloud.com	17501
activavxmldsmty04.glb.avayacloud.com	17501
activavxmldsmty04.glb.avayacloud.com	17501
activavxmldsmty05.glb.avayacloud.com	17501
activavxmldsmty05.glb.avayacloud.com	17501
activavxml502dsmty01.glb.avayacloud.com	17502
activavxml502dsmty01.glb.avayacloud.com	17502
activavxml502dsmty02.glb.avayacloud.com	17502
activavxml502dsmty02.glb.avayacloud.com	17502
activavxml502dsmty03.glb.avayacloud.com	17502
activavxml502dsmty03.glb.avayacloud.com	17502
activavxml502dsmty04.glb.avayacloud.com	17502
activavxml502dsmty04.glb.avayacloud.com	17502
activavxml502dsmty05.glb.avayacloud.com	17502
activavxml502dsmty05.glb.avayacloud.com	17502
renovacionpiasdsmty01.glb.avayacloud.com	17503
renovacionpiasdsmty01.glb.avayacloud.com	17503
renovacionpiasdsmty02.glb.avayacloud.com	17503
renovacionpiasdsmty02.glb.avayacloud.com	17503
renovacionpiasdsmty03.glb.avayacloud.com	17503
renovacionpiasdsmty03.glb.avayacloud.com	17503
renovacionpiasdsmty04.glb.avayacloud.com	17503
renovacionpiasdsmty04.glb.avayacloud.com	17503
renovacionpiasdsmty05.glb.avayacloud.com	17503
renovacionpiasdsmty05.glb.avayacloud.com	17503
regtarjetasdsmty13.glb.avayacloud.com	17506
regtarjetasdsmty13.glb.avayacloud.com	17506
regtarjetasdsmty14.glb.avayacloud.com	17506
regtarjetasdsmty14.glb.avayacloud.com	17506
regtarjetasdsmty15.glb.avayacloud.com	17506
regtarjetasdsmty15.glb.avayacloud.com	17506
hbvxmldsmty13.glb.avayacloud.com	17504
hbvxmldsmty13.glb.avayacloud.com	17504
hbvxmldsmty14.glb.avayacloud.com	17504
hbvxmldsmty14.glb.avayacloud.com	17504
hbvxmldsmty15.glb.avayacloud.com	17504
hbvxmldsmty15.glb.avayacloud.com	17504
unefonvxmldsmty06.glb.avayacloud.com	17511
unefonvxmldsmty06.glb.avayacloud.com	17511
unefonvxmldsmty07.glb.avayacloud.com	17511
unefonvxmldsmty07.glb.avayacloud.com	17511
unefonvxmldsmty08.glb.avayacloud.com	17511
unefonvxmldsmty08.glb.avayacloud.com	17511
unefonvxmldsmty09.glb.avayacloud.com	17511
unefonvxmldsmty09.glb.avayacloud.com	17511
unefonvxmldsmty10.glb.avayacloud.com	17511
unefonvxmldsmty10.glb.avayacloud.com	17511
unefonvxmldsmty11.glb.avayacloud.com	17511
unefonvxmldsmty11.glb.avayacloud.com	17511
unefonvxmldsmty12.glb.avayacloud.com	17511
unefonvxmldsmty12.glb.avayacloud.com	17511
prepag611dsmty06.glb.avayacloud.com	17502
prepag611dsmty06.glb.avayacloud.com	17502
prepag611dsmty07.glb.avayacloud.com	17502
prepag611dsmty07.glb.avayacloud.com	17502
prepag611dsmty08.glb.avayacloud.com	17502
prepag611dsmty08.glb.avayacloud.com	17502
prepag611dsmty09.glb.avayacloud.com	17502
prepag611dsmty09.glb.avayacloud.com	17502
prepag611dsmty10.glb.avayacloud.com	17502
prepag611dsmty10.glb.avayacloud.com	17502
prepag611dsmty11.glb.avayacloud.com	17502
prepag611dsmty11.glb.avayacloud.com	17502
prepag611dsmty12.glb.avayacloud.com	17502
prepag611dsmty12.glb.avayacloud.com	17502
prepag611dsmty13.glb.avayacloud.com	17505
prepag611dsmty13.glb.avayacloud.com	17505
prepag611dsmty14.glb.avayacloud.com	17505
prepag611dsmty14.glb.avayacloud.com	17505
prepag611dsmty15.glb.avayacloud.com	17505
prepag611dsmty15.glb.avayacloud.com	17505
saldovxmldsmty13.glb.avayacloud.com	17501
saldovxmldsmty13.glb.avayacloud.com	17501
saldovxmldsmty14.glb.avayacloud.com	17501
saldovxmldsmty14.glb.avayacloud.com	17501
saldovxmldsmty15.glb.avayacloud.com	17501
saldovxmldsmty15.glb.avayacloud.com	17501
saldovxml502dsmty13.glb.avayacloud.com	17502
saldovxml502dsmty13.glb.avayacloud.com	17502
saldovxml502dsmty14.glb.avayacloud.com	17502
saldovxml502dsmty14.glb.avayacloud.com	17502
saldovxml502dsmty15.glb.avayacloud.com	17502
saldovxml502dsmty15.glb.avayacloud.com	17502
"""

# ✅ Optional constant whitelist variable name or list of IPs
whitelist = "CONSTANTS:vermaa_whitelist"  # or use a list like ["1.2.3.4/24"]

# 📦 Extract (hostname, domain, port)
host_port_list = []
for line in raw_input.strip().splitlines():
    parts = line.strip().split()
    if len(parts) == 2:
        fqdn, port = parts
        fqdn_parts = fqdn.split(".")
        if len(fqdn_parts) >= 2:
            hostname = fqdn_parts[0]
            domain = ".".join(fqdn_parts[1:])
            host_port_list.append((hostname, domain, port))

# Deduplicate based on hostname and port (case-insensitive)
seen = set()
unique_host_port_list = []

for hostname, domain, port in host_port_list:
    key = (hostname.lower(), port)
    if key not in seen:
        seen.add(key)
        unique_host_port_list.append((hostname, domain, port))

# Replace original list with deduplicated version
host_port_list = unique_host_port_list


# 🧾 Other constants
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



# ⚙️ Generate POOLS
pools = {}

for hostname, domain, port in host_port_list:
    base_name = hostname.upper()
    pool_name = f"CUSTOMER_{base_name}_{port}"

    # Use [.] instead of \. in regex
    escaped_fqdn = f"{hostname}" + ''.join(f"[.]{part}" for part in domain.split("."))

    regex_https = f"^https://({escaped_fqdn}):443/"
    regex_http = f"^http://({escaped_fqdn}):443/"

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

        # 🔄 Dynamic whitelist
        pool_config["whitelist"] = f"${{{whitelist}}}" if isinstance(whitelist, str) else whitelist

        pools[pool_key] = pool_config

# 📝 Output JSON
output = {"POOLS": pools}

with open("pools_output.json", "w") as f:
    json.dump(output, f, indent=2)
