import json
import re
import os
import time
from concurrent.futures import ThreadPoolExecutor

# 🔧 Configuration
TEST_MODE = False  # Set to True to only run validation (no JSON output)
FQDN_FILE = "fqdn_input.txt"
OUTPUT_JSON = "pools_output.json"

# 🛡️ Constants
whitelist = "CONSTANTS:my_whitelist"
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

fqdn_pattern = re.compile(r"^(?!-)([a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}$")

# 🧾 Default raw input works only if input file not present
raw_input = """
o.glb.ac.com	12345
o1.glb.ac.com	12346
u.glb.ac.com	12347
o.glb.ac.com	12345  # duplicate for test
bad_host	99999
invalid.fqdn	70000
"""

# 🗃️ Load or create input file
if not os.path.exists(FQDN_FILE):
    print(f"📄 Creating {FQDN_FILE} from default raw input...")
    with open(FQDN_FILE, "w") as f:
        f.write(raw_input.strip())
else:
    print(f"📥 Loading FQDNs from existing {FQDN_FILE}...")
    with open(FQDN_FILE, "r") as f:
        raw_input = f.read()

# ⏱️ Start timing in nanoseconds
start_ns = time.perf_counter_ns()

# ✅ Pre-validation
host_port_list = []
errors = []
seen_keys = set()

print("\n🔎 Pre-validation Checks:")
for i, line in enumerate(raw_input.strip().splitlines(), start=1):
    parts = line.strip().split()
    if len(parts) < 2:
        errors.append(f"Line {i}: Invalid format - '{line.strip()}'")
        continue

    fqdn, port = parts[0], parts[1]

    if not fqdn_pattern.match(fqdn):
        errors.append(f"Line {i}: Invalid FQDN - '{fqdn}'")
        continue

    if not port.isdigit() or not (1 <= int(port) <= 65535):
        errors.append(f"Line {i}: Invalid TCP port - '{port}'")
        continue

    hostname = fqdn.split(".")[0].lower()
    domain = ".".join(fqdn.split(".")[1:])
    key = (hostname, port)

    if key in seen_keys:
        errors.append(f"Line {i}: Duplicate hostname '{hostname}' and port '{port}'")
    else:
        seen_keys.add(key)
        host_port_list.append((hostname, domain, port))

# Show validation result
if errors:
    print("⚠️ Issues Found:")
    for err in errors:
        print(" -", err)
else:
    print("✅ All FQDN lines passed pre-validation.")

# 🔧 Build POOLS dictionary
def build_pools(hostname, domain, port):
    base_name = hostname.upper()
    pool_name = f"CUSTOMER_{base_name}_{port}"
    escaped_fqdn = f"{hostname}" + ''.join(f"[.]{part}" for part in domain.split("."))

    result = {}
    for protocol in ["HTTPS", "HTTP"]:
        result[f"{pool_name}_{protocol}"] = {
            "description": f"{pool_name} {protocol} Pool Selection",
            "excludeLog": False,
            "localSubnets": local_subnets,
            "poolName": pool_name,
            "regexUrl": f"^{'https' if protocol == 'HTTPS' else 'http'}://({escaped_fqdn}):443/",
            "urlQueryStringReplaceEncodeFull": True,
            "urlQueryStringReplace": url_rewrites,
            "responseHeadersUpdate": header_updates,
            "whitelist": f"${{{whitelist}}}" if isinstance(whitelist, str) else whitelist
        }
    return result

# 🧵 Concurrent processing if needed
pools = {}
if len(host_port_list) < 20:
    for item in host_port_list:
        pools.update(build_pools(*item))
else:
    with ThreadPoolExecutor() as executor:
        results = executor.map(lambda x: build_pools(*x), host_port_list)
        for pool_dict in results:
            pools.update(pool_dict)

# 📝 Skip JSON generation in test mode
if TEST_MODE:
    print("\n🧪 TEST_MODE is ON — Skipping JSON generation.")
else:
    output = {"POOLS": pools}
    with open(OUTPUT_JSON, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n💾 JSON saved as '{OUTPUT_JSON}'.")

# ✅ Post-validation if JSON was created
if not TEST_MODE:
    print("\n🔎 Post-validation Checks:")
    try:
        with open(OUTPUT_JSON, "r") as f:
            loaded = json.load(f)
            if "POOLS" not in loaded:
                raise ValueError("Missing 'POOLS' key in JSON.")

            total = len(loaded["POOLS"])
            print(f"✅ JSON structure valid. Total pool entries: {total}")
    except Exception as e:
        print(f"❌ Post-validation failed: {e}")

# ⏱️ End time
end_ns = time.perf_counter_ns()
duration_ns = end_ns - start_ns
print(f"\n🕒 Completed in {duration_ns:,} nanoseconds ({duration_ns / 1e6:.3f} ms)")
print(f"🔢 Valid pool mappings processed: {len(host_port_list)}")
