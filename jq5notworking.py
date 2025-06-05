import os
import re
import time
import json
from concurrent.futures import ProcessPoolExecutor

# Constants
FQDN_INPUT_FILE = "fqdn_input.txt"
OUTPUT_JSON = "pools_output.json"
TEST_MODE = False  # Set to True to only run validations without generating JSON

# Optional constant whitelist variable name or list of IPs
whitelist = "CONSTANTS:my_whitelist"
local_subnets = ["100.116.121.0/24", "100.124.121.0/24"]

url_rewrites = [
    {"regex": "100[.]116[.]123[.]240", "replace": "epm.glb.cala.attmx.avayacloud.com"},
    {"regex": "100[.]124[.]123[.]240", "replace": "epmgeo.glb.cala.attmx.avayacloud.com"},
]

header_updates = [
    {"header": "TerminationURL", "regex": "http", "replace": "https"},
]

# Load input
if os.path.exists(FQDN_INPUT_FILE):
    with open(FQDN_INPUT_FILE, "r") as f:
        raw_input = f.read()
else:
    raw_input = """
o.glb.ac.com	12345
o1.glb.ac.com	12346
u.glb.ac.com	12347
    """
    with open(FQDN_INPUT_FILE, "w") as f:
        f.write(raw_input.strip())

# Pre-validation checks
seen = set()
errors = []
host_port_list = []
fqdn_pattern = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(?:\.[A-Za-z]{2,})+$")
port_pattern = re.compile(r"^\d{1,5}$")

for line_no, line in enumerate(raw_input.strip().splitlines(), 1):
    parts = line.strip().split()
    if len(parts) != 2:
        errors.append(f"Line {line_no}: Invalid format")
        continue
    fqdn, port = parts
    parts = fqdn.split(".", 1)
    hostname = parts[0]
    domain = parts[1] if len(parts) > 1 else ""

    if not fqdn_pattern.match(fqdn):
        errors.append(f"Line {line_no}: Invalid FQDN '{fqdn}'")
        continue
    if not port_pattern.match(port) or not (0 < int(port) < 65536):
        errors.append(f"Line {line_no}: Invalid port '{port}'")
        continue

    key = (hostname.lower(), port)
    if key in seen:
        errors.append(f"Line {line_no}: Duplicate hostname '{hostname}' and port '{port}'")
        continue

    seen.add(key)
    host_port_list.append((hostname, domain, port))

if errors:
    print("\n❌ Pre-validation Errors:")
    for e in errors:
        print(" -", e)

if TEST_MODE:
    print("\n✅ Test mode enabled. Skipping JSON generation.")
    exit(0)

start_time = time.time_ns()

# Generate POOLS

def create_pool_entry(hostname, domain, port):
    base_name = hostname.upper()
    pool_name = f"CUSTOMER_{base_name}_{port}"
    escaped_fqdn = f"{hostname}[.]{domain.replace('.', '[.]')}"

    regex_https = f"^https://({escaped_fqdn}):443/"
    regex_http = f"^http://({escaped_fqdn}):443/"

    result = {}
    for protocol, regex in [("HTTPS", regex_https), ("HTTP", regex_http)]:
        pool_key = f"{pool_name}_{protocol}"
        pool_config = {
            "description": f"{pool_name} {protocol} Pool Selection",
            "excludeLog": False,
            "localSubnets": local_subnets,
            "poolName": pool_name,
            "regexUrl": regex,
            "urlQueryStringReplaceEncodeFull": True,
            "urlQueryStringReplace": url_rewrites,
            "responseHeadersUpdate": header_updates,
            "whitelist": f"${{{whitelist}}}" if isinstance(whitelist, str) else whitelist
        }
        result[pool_key] = pool_config
    return result

pools = {}
with ProcessPoolExecutor() as executor:
    results = list(executor.map(lambda hp: create_pool_entry(*hp), host_port_list))
    for r in results:
        pools.update(r)

output = {"POOLS": pools}

# Post-validation checks
try:
    json_bytes = json.dumps(output, indent=2)
    with open(OUTPUT_JSON, "wb") as f:
        f.write(json_bytes)

    end_time = time.time_ns()
    duration = end_time - start_time

    print(f"\n✅ JSON generated successfully: {OUTPUT_JSON}")
    print(f"✔ Completed in {duration:,} nanoseconds ({duration / 1e6:.3f} ms) for {len(host_port_list)} entries")
    print(f"✔ Total lines in JSON file: {json_bytes.count(b'\\n')}")

except Exception as e:
    print("\n❌ Post-validation failed while writing JSON:", e)
 Line 164: Duplicate hostname 'activavxmldsmty02' and port '17501'
 - Line 166: Duplicate hostname 'activavxmldsmty03' and port '17501'
 - Line 168: Duplicate hostname 'activavxmldsmty04' and port '17501'
 - Line 170: Duplicate hostname 'activavxmldsmty05' and port '17501'
 - Line 172: Duplicate hostname 'activavxml502dsmty01' and port '17502'
 - Line 174: Duplicate hostname 'activavxml502dsmty02' and port '17502'
 - Line 212: Duplicate hostname 'unefonvxmldsmty10' and port '17511'
 - Line 190: Duplicate hostname 'renovacionpiasdsmty05' and port '17503'
 - Line 176: Duplicate hostname 'activavxml502dsmty03' and port '17502'
 - Line 214: Duplicate hostname 'unefonvxmldsmty11' and port '17511'
 - Line 216: Duplicate hostname 'unefonvxmldsmty12' and port '17511'
 - Line 178: Duplicate hostname 'activavxml502dsmty04' and port '17502'
 - Line 192: Duplicate hostname 'regtarjetasdsmty13' and port '17506'
 - Line 218: Duplicate hostname 'prepag611dsmty06' and port '17502'
 - Line 180: Duplicate hostname 'activavxml502dsmty05' and port '17502'
 - Line 182: Duplicate hostname 'renovacionpiasdsmty01' and port '17503'
 - Line 220: Duplicate hostname 'prepag611dsmty07' and port '17502'
 - Line 194: Duplicate hostname 'regtarjetasdsmty14' and port '17506'
 - Line 196: Duplicate hostname 'regtarjetasdsmty15' and port '17506'
 - Line 198: Duplicate hostname 'hbvxmldsmty13' and port '17504'
 - Line 200: Duplicate hostname 'hbvxmldsmty14' and port '17504'
 - Line 202: Duplicate hostname 'hbvxmldsmty15' and port '17504'
 - Line 204: Duplicate hostname 'unefonvxmldsmty06' and port '17511'
 - Line 206: Duplicate hostname 'unefonvxmldsmty07' and port '17511'
 - Line 184: Duplicate hostname 'renovacionpiasdsmty02' and port '17503'
 - Line 186: Duplicate hostname 'renovacionpiasdsmty03' and port '17503'
 - Line 188: Duplicate hostname 'renovacionpiasdsmty04' and port '17503'
 - Line 190: Duplicate hostname 'renovacionpiasdsmty05' and port '17503'
 - Line 208: Duplicate hostname 'unefonvxmldsmty08' and port '17511'
 - Line 222: Duplicate hostname 'prepag611dsmty08' and port '17502'
 - Line 192: Duplicate hostname 'regtarjetasdsmty13' and port '17506'
 - Line 194: Duplicate hostname 'regtarjetasdsmty14' and port '17506'
 - Line 224: Duplicate hostname 'prepag611dsmty09' and port '17502'
 - Line 210: Duplicate hostname 'unefonvxmldsmty09' and port '17511'
 - Line 196: Duplicate hostname 'regtarjetasdsmty15' and port '17506'
 - Line 226: Duplicate hostname 'prepag611dsmty10' and port '17502'
 - Line 212: Duplicate hostname 'unefonvxmldsmty10' and port '17511'
 - Line 214: Duplicate hostname 'unefonvxmldsmty11' and port '17511'
 - Line 228: Duplicate hostname 'prepag611dsmty11' and port '17502'
 - Line 230: Duplicate hostname 'prepag611dsmty12' and port '17502'
 - Line 216: Duplicate hostname 'unefonvxmldsmty12' and port '17511'
 - Line 218: Duplicate hostname 'prepag611dsmty06' and port '17502'
 - Line 220: Duplicate hostname 'prepag611dsmty07' and port '17502'
 - Line 222: Duplicate hostname 'prepag611dsmty08' and port '17502'
 - Line 224: Duplicate hostname 'prepag611dsmty09' and port '17502'
 - Line 198: Duplicate hostname 'hbvxmldsmty13' and port '17504'
 - Line 232: Duplicate hostname 'prepag611dsmty13' and port '17505'

❌ Pre-validation Errors: - Line 226: Duplicate hostname 'prepag611dsmty10' and port '17502'
 - Line 228: Duplicate hostname 'prepag611dsmty11' and port '17502'
 - Line 234: Duplicate hostname 'prepag611dsmty14' and port '17505'
 - Line 236: Duplicate hostname 'prepag611dsmty15' and port '17505'
 - Line 238: Duplicate hostname 'saldovxmldsmty13' and port '17501'
 - Line 230: Duplicate hostname 'prepag611dsmty12' and port '17502'
 - Line 232: Duplicate hostname 'prepag611dsmty13' and port '17505'
 - Line 200: Duplicate hostname 'hbvxmldsmty14' and port '17504'
 - Line 240: Duplicate hostname 'saldovxmldsmty14' and port '17501'
 - Line 242: Duplicate hostname 'saldovxmldsmty15' and port '17501'
 - Line 234: Duplicate hostname 'prepag611dsmty14' and port '17505'
 - Line 202: Duplicate hostname 'hbvxmldsmty15' and port '17504'

 - Line 244: Duplicate hostname 'saldovxml502dsmty13' and port '17502'
 - Line 246: Duplicate hostname 'saldovxml502dsmty14' and port '17502'
 - Line 204: Duplicate hostname 'unefonvxmldsmty06' and port '17511'
 - Line 206: Duplicate hostname 'unefonvxmldsmty07' and port '17511'
 - Line 236: Duplicate hostname 'prepag611dsmty15' and port '17505'
 - Line 238: Duplicate hostname 'saldovxmldsmty13' and port '17501'
 - Line 240: Duplicate hostname 'saldovxmldsmty14' and port '17501'
 - Line 242: Duplicate hostname 'saldovxmldsmty15' and port '17501'
 - Line 244: Duplicate hostname 'saldovxml502dsmty13' and port '17502'
 - Line 246: Duplicate hostname 'saldovxml502dsmty14' and port '17502'
 - Line 248: Duplicate hostname 'saldovxml502dsmty15' and port '17502'
 - Line 248: Duplicate hostname 'saldovxml502dsmty15' and port '17502'
 - Line 2: Duplicate hostname 'ochocientosvxmlmty' and port '15070'
 - Line 4: Duplicate hostname 'unefonmtxxvxmlmty' and port '15131'
 - Line 6: Duplicate hostname 'empresarialvxmlmty' and port '15060'
 - Line 8: Duplicate hostname 'hibridovxmlmty' and port '15090'
 - Line 208: Duplicate hostname 'unefonvxmldsmty08' and port '17511'
 - Line 10: Duplicate hostname 'postpagovxmlmty' and port '15126'
 - Line 12: Duplicate hostname 'prepagomtxxvxmlmty' and port '15132'
 - Line 14: Duplicate hostname 'visualvxmlmty' and port '15040'
 - Line 16: Duplicate hostname 'visualmtxxvxmlmty' and port '15133'
 - Line 18: Duplicate hostname 'ciamsvxmlmty' and port '15124'
Traceback (most recent call last):
 - Line 20: Duplicate hostname 'activacionesvxmlmty' and port '15125'
 - Line 22: Duplicate hostname 'renovacionpiasvxmlmty' and port '15120'
 - Line 210: Duplicate hostname 'unefonvxmldsmty09' and port '17511'
 - Line 24: Duplicate hostname 'regtarjetasvxmlmty' and port '15100'
 - Line 26: Duplicate hostname 'hardblockvxmlmty' and port '15110'
 - Line 28: Duplicate hostname 'unefonvxmlmty' and port '15020'
 - Line 30: Duplicate hostname 'prepagovxmlmty' and port '15050'
 - Line 212: Duplicate hostname 'unefonvxmldsmty10' and port '17511'
  File "<string>", line 1, in <module>
    from multiprocessing.spawn import spawn_main; spawn_main(parent_pid=29516, pipe_handle=396)
                                                  ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 - Line 32: Duplicate hostname 'pucvxmlmty' and port '11010'
 - Line 34: Duplicate hostname 'saldovxmlmty' and port '11090'
 - Line 36: Duplicate hostname 'unoochovxmldsmty06' and port '17507'
 - Line 38: Duplicate hostname 'unoochovxmldsmty07' and port '17507'
 - Line 40: Duplicate hostname 'unoochovxmldsmty08' and port '17507'
 - Line 214: Duplicate hostname 'unefonvxmldsmty11' and port '17511'
  File "multiprocessing\spawn.py", line 122, in spawn_main
  File "multiprocessing\spawn.py", line 131, in _main
 - Line 216: Duplicate hostname 'unefonvxmldsmty12' and port '17511'
 - Line 42: Duplicate hostname 'unoochovxmldsmty09' and port '17507'
  File "multiprocessing\spawn.py", line 246, in prepare
  File "multiprocessing\spawn.py", line 297, in _fixup_main_from_path
  File "<frozen runpy>", line 287, in run_path
  File "<frozen runpy>", line 98, in _run_module_code
  File "<frozen runpy>", line 88, in _run_code
 - Line 218: Duplicate hostname 'prepag611dsmty06' and port '17502'
 - Line 220: Duplicate hostname 'prepag611dsmty07' and port '17502'
 - Line 222: Duplicate hostname 'prepag611dsmty08' and port '17502'
 - Line 44: Duplicate hostname 'unoochovxmldsmty10' and port '17507'
  File "C:\Users\ankurv\github.com\anshvermahotmail\TechnimentAnalysis\TechnimentAnalysis\jq5.py", line 110, in <module>
    results = list(executor.map(lambda hp: create_pool_entry(*hp), host_port_list))
                   ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 - Line 224: Duplicate hostname 'prepag611dsmty09' and port '17502'
 - Line 226: Duplicate hostname 'prepag611dsmty10' and port '17502'
 - Line 228: Duplicate hostname 'prepag611dsmty11' and port '17502'
 - Line 230: Duplicate hostname 'prepag611dsmty12' and port '17502'
 - Line 232: Duplicate hostname 'prepag611dsmty13' and port '17505'
 - Line 234: Duplicate hostname 'prepag611dsmty14' and port '17505'
 - Line 46: Duplicate hostname 'unoochovxmldsmty11' and port '17507'
  File "concurrent\futures\process.py", line 832, in map

❌ Pre-validation Errors:
 - Line 48: Duplicate hostname 'unoochovxmldsmty12' and port '17507'
 - Line 50: Duplicate hostname 'unefonmatvxmldsmty06' and port '17515'
 - Line 236: Duplicate hostname 'prepag611dsmty15' and port '17505'
 - Line 238: Duplicate hostname 'saldovxmldsmty13' and port '17501'
  File "concurrent\futures\_base.py", line 600, in map
 - Line 52: Duplicate hostname 'unefonmatvxmldsmty07' and port '17515'
 - Line 54: Duplicate hostname 'unefonmatvxmldsmty08' and port '17515'
 - Line 240: Duplicate hostname 'saldovxmldsmty14' and port '17501'
 - Line 242: Duplicate hostname 'saldovxmldsmty15' and port '17501'
 - Line 244: Duplicate hostname 'saldovxml502dsmty13' and port '17502'
 - Line 246: Duplicate hostname 'saldovxml502dsmty14' and port '17502'
  File "concurrent\futures\process.py", line 803, in submit
 - Line 2: Duplicate hostname 'ochocientosvxmlmty' and port '15070'
Traceback (most recent call last):
 - Line 56: Duplicate hostname 'unefonmatvxmldsmty09' and port '17515'
 - Line 248: Duplicate hostname 'saldovxml502dsmty15' and port '17502'
  File "concurrent\futures\process.py", line 762, in _adjust_process_count
 - Line 4: Duplicate hostname 'unefonmtxxvxmlmty' and port '15131'
 - Line 6: Duplicate hostname 'empresarialvxmlmty' and port '15060'
  File "<string>", line 1, in <module>
    from multiprocessing.spawn import spawn_main; spawn_main(parent_pid=29516, pipe_handle=416)
                                                  ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "concurrent\futures\process.py", line 780, in _spawn_process
 - Line 58: Duplicate hostname 'unefonmatvxmldsmty10' and port '17515'
 - Line 8: Duplicate hostname 'hibridovxmlmty' and port '15090'
  File "multiprocessing\spawn.py", line 122, in spawn_main
  File "multiprocessing\spawn.py", line 131, in _main
  File "multiprocessing\spawn.py", line 246, in prepare
 - Line 10: Duplicate hostname 'postpagovxmlmty' and port '15126'
  File "multiprocessing\process.py", line 121, in start
Traceback (most recent call last):
 - Line 60: Duplicate hostname 'unefonmatvxmldsmty11' and port '15515'
  File "multiprocessing\spawn.py", line 297, in _fixup_main_from_path
 - Line 12: Duplicate hostname 'prepagomtxxvxmlmty' and port '15132'

❌ Pre-validation Errors:  File "multiprocessing\context.py", line 337, in _Popen
 - Line 62: Duplicate hostname 'unefonmatvxmldsmty12' and port '17515'
  File "<frozen runpy>", line 287, in run_path
 - Line 14: Duplicate hostname 'visualvxmlmty' and port '15040'

  File "multiprocessing\popen_spawn_win32.py", line 47, in __init__
  File "multiprocessing\spawn.py", line 164, in get_preparation_data
  File "<frozen runpy>", line 98, in _run_module_code
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\ankurv\github.com\anshvermahotmail\TechnimentAnalysis\TechnimentAnalysis\jq5.py", line 110, in <module>
    results = list(executor.map(lambda hp: create_pool_entry(*hp), host_port_list))
                   ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 - Line 64: Duplicate hostname 'enterprisedsmty06' and port '17506'
 - Line 66: Duplicate hostname 'enterprisedsmty07' and port '17506'
 - Line 16: Duplicate hostname 'visualmtxxvxmlmty' and port '15133'
 - Line 2: Duplicate hostname 'ochocientosvxmlmty' and port '15070'
  File "<string>", line 1, in <module>
    from multiprocessing.spawn import spawn_main; spawn_main(parent_pid=29516, pipe_handle=368)
                                                  ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "concurrent\futures\process.py", line 832, in map
  File "multiprocessing\spawn.py", line 140, in _check_not_importing_main
 - Line 68: Duplicate hostname 'enterprisedsmty08' and port '17506'
 - Line 18: Duplicate hostname 'ciamsvxmlmty' and port '15124'
 - Line 4: Duplicate hostname 'unefonmtxxvxmlmty' and port '15131'
  File "multiprocessing\spawn.py", line 122, in spawn_main
  File "concurrent\futures\_base.py", line 600, in map
RuntimeError:
        An attempt has been made to start a new process before the
        current process has finished its bootstrapping phase.

        This probably means that you are not using fork to start your
        child processes and you have forgotten to use the proper idiom
        in the main module:

            if __name__ == '__main__':
                freeze_support()
                ...

        The "freeze_support()" line can be omitted if the program
        is not going to be frozen to produce an executable.

        To fix this issue, refer to the "Safe importing of main module"
        section in https://docs.python.org/3/library/multiprocessing.html

 - Line 70: Duplicate hostname 'enterprisedsmty09' and port '17506'
 - Line 72: Duplicate hostname 'enterprisedsmty10' and port '17506'
 - Line 74: Duplicate hostname 'enterprisedsmty11' and port '17506'
  File "multiprocessing\spawn.py", line 131, in _main
  File "multiprocessing\spawn.py", line 246, in prepare
 - Line 20: Duplicate hostname 'activacionesvxmlmty' and port '15125'
 - Line 6: Duplicate hostname 'empresarialvxmlmty' and port '15060'
 - Line 8: Duplicate hostname 'hibridovxmlmty' and port '15090'
 - Line 10: Duplicate hostname 'postpagovxmlmty' and port '15126'
 - Line 12: Duplicate hostname 'prepagomtxxvxmlmty' and port '15132'
 - Line 22: Duplicate hostname 'renovacionpiasvxmlmty' and port '15120'
 - Line 76: Duplicate hostname 'enterprisedsmty12' and port '17506'
  File "concurrent\futures\process.py", line 803, in submit
  File "multiprocessing\spawn.py", line 297, in _fixup_main_from_path

❌ Pre-validation Errors:
 - Line 24: Duplicate hostname 'regtarjetasvxmlmty' and port '15100'
 - Line 78: Duplicate hostname 'hibri611dsmty06' and port '17504'
  File "concurrent\futures\process.py", line 762, in _adjust_process_count
  File "<frozen runpy>", line 287, in run_path
 - Line 14: Duplicate hostname 'visualvxmlmty' and port '15040'
 - Line 2: Duplicate hostname 'ochocientosvxmlmty' and port '15070'
 - Line 26: Duplicate hostname 'hardblockvxmlmty' and port '15110'
 - Line 80: Duplicate hostname 'hibri611dsmty07' and port '17504'
  File "concurrent\futures\process.py", line 780, in _spawn_process
  File "<frozen runpy>", line 98, in _run_module_code
 - Line 16: Duplicate hostname 'visualmtxxvxmlmty' and port '15133'
 - Line 4: Duplicate hostname 'unefonmtxxvxmlmty' and port '15131'
 - Line 28: Duplicate hostname 'unefonvxmlmty' and port '15020'
 - Line 82: Duplicate hostname 'hibri611dsmty08' and port '17504'
  File "multiprocessing\process.py", line 121, in start
  File "<frozen runpy>", line 88, in _run_code
 - Line 18: Duplicate hostname 'ciamsvxmlmty' and port '15124'
 - Line 6: Duplicate hostname 'empresarialvxmlmty' and port '15060'
 - Line 30: Duplicate hostname 'prepagovxmlmty' and port '15050'
 - Line 84: Duplicate hostname 'hibri611dsmty09' and port '17504'
  File "multiprocessing\context.py", line 337, in _Popen
  File "C:\Users\ankurv\github.com\anshvermahotmail\TechnimentAnalysis\TechnimentAnalysis\jq5.py", line 110, in <module>
    results = list(executor.map(lambda hp: create_pool_entry(*hp), host_port_list))
                   ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 - Line 20: Duplicate hostname 'activacionesvxmlmty' and port '15125'
 - Line 8: Duplicate hostname 'hibridovxmlmty' and port '15090'
 - Line 32: Duplicate hostname 'pucvxmlmty' and port '11010'
 - Line 86: Duplicate hostname 'hibri611dsmty10' and port '17504'
  File "multiprocessing\popen_spawn_win32.py", line 47, in __init__
  File "concurrent\futures\process.py", line 832, in map
 - Line 22: Duplicate hostname 'renovacionpiasvxmlmty' and port '15120'
 - Line 10: Duplicate hostname 'postpagovxmlmty' and port '15126'
 - Line 34: Duplicate hostname 'saldovxmlmty' and port '11090'
 - Line 88: Duplicate hostname 'hibri611dsmty11' and port '17504'
  File "multiprocessing\spawn.py", line 164, in get_preparation_data
  File "concurrent\futures\_base.py", line 600, in map
 - Line 24: Duplicate hostname 'regtarjetasvxmlmty' and port '15100'
 - Line 12: Duplicate hostname 'prepagomtxxvxmlmty' and port '15132'
 - Line 36: Duplicate hostname 'unoochovxmldsmty06' and port '17507'
 - Line 90: Duplicate hostname 'hibri611dsmty12' and port '17504'
  File "multiprocessing\spawn.py", line 140, in _check_not_importing_main
  File "concurrent\futures\process.py", line 803, in submit
RuntimeError:
        An attempt has been made to start a new process before the
        current process has finished its bootstrapping phase.

        This probably means that you are not using fork to start your
        child processes and you have forgotten to use the proper idiom
        in the main module:

            if __name__ == '__main__':
                freeze_support()
                ...

        The "freeze_support()" line can be omitted if the program
        is not going to be frozen to produce an executable.

        To fix this issue, refer to the "Safe importing of main module"
        section in https://docs.python.org/3/library/multiprocessing.html

 - Line 14: Duplicate hostname 'visualvxmlmty' and port '15040'
 - Line 38: Duplicate hostname 'unoochovxmldsmty07' and port '17507'
 - Line 92: Duplicate hostname 'postpag611dsmty06' and port '17501'
 - Line 94: Duplicate hostname 'postpag611dsmty07' and port '17501'
  File "concurrent\futures\process.py", line 762, in _adjust_process_count
 - Line 16: Duplicate hostname 'visualmtxxvxmlmty' and port '15133'
 - Line 40: Duplicate hostname 'unoochovxmldsmty08' and port '17507'
 - Line 42: Duplicate hostname 'unoochovxmldsmty09' and port '17507'
 - Line 96: Duplicate hostname 'postpag611dsmty08' and port '17501'
 - Line 98: Duplicate hostname 'postpag611dsmty09' and port '17501'
 - Line 100: Duplicate hostname 'postpag611dsmty10' and port '17501'
 - Line 26: Duplicate hostname 'hardblockvxmlmty' and port '15110'
 - Line 44: Duplicate hostname 'unoochovxmldsmty10' and port '17507'
  File "concurrent\futures\process.py", line 780, in _spawn_process
 - Line 18: Duplicate hostname 'ciamsvxmlmty' and port '15124'
 - Line 102: Duplicate hostname 'postpag611dsmty11' and port '17501'
 - Line 28: Duplicate hostname 'unefonvxmlmty' and port '15020'
 - Line 46: Duplicate hostname 'unoochovxmldsmty11' and port '17507'
  File "multiprocessing\process.py", line 121, in start
 - Line 20: Duplicate hostname 'activacionesvxmlmty' and port '15125'
 - Line 104: Duplicate hostname 'postpag611dsmty12' and port '17501'
 - Line 30: Duplicate hostname 'prepagovxmlmty' and port '15050'
 - Line 48: Duplicate hostname 'unoochovxmldsmty12' and port '17507'
  File "multiprocessing\context.py", line 337, in _Popen
 - Line 22: Duplicate hostname 'renovacionpiasvxmlmty' and port '15120'
 - Line 106: Duplicate hostname 'prepmatvxmldsmty06' and port '17516'

❌ Pre-validation Errors: - Line 50: Duplicate hostname 'unefonmatvxmldsmty06' and port '17515'
  File "multiprocessing\popen_spawn_win32.py", line 47, in __init__
 - Line 24: Duplicate hostname 'regtarjetasvxmlmty' and port '15100'
 - Line 108: Duplicate hostname 'prepmatvxmldsmty07' and port '17516'
 - Line 32: Duplicate hostname 'pucvxmlmty' and port '11010'

❌ Pre-validation Errors:
 - Line 52: Duplicate hostname 'unefonmatvxmldsmty07' and port '17515'
  File "multiprocessing\spawn.py", line 164, in get_preparation_data
 - Line 26: Duplicate hostname 'hardblockvxmlmty' and port '15110'
 - Line 110: Duplicate hostname 'prepmatvxmldsmty08' and port '17516'
 - Line 34: Duplicate hostname 'saldovxmlmty' and port '11090'

 - Line 2: Duplicate hostname 'ochocientosvxmlmty' and port '15070'
 - Line 54: Duplicate hostname 'unefonmatvxmldsmty08' and port '17515'
  File "multiprocessing\spawn.py", line 140, in _check_not_importing_main
 - Line 28: Duplicate hostname 'unefonvxmlmty' and port '15020'
 - Line 112: Duplicate hostname 'prepmatvxmldsmty09' and port '17516'
 - Line 36: Duplicate hostname 'unoochovxmldsmty06' and port '17507'
 - Line 2: Duplicate hostname 'ochocientosvxmlmty' and port '15070'
 - Line 4: Duplicate hostname 'unefonmtxxvxmlmty' and port '15131'
 - Line 56: Duplicate hostname 'unefonmatvxmldsmty09' and port '17515'
 - Line 30: Duplicate hostname 'prepagovxmlmty' and port '15050'
RuntimeError:
        An attempt has been made to start a new process before the
        current process has finished its bootstrapping phase.

        This probably means that you are not using fork to start your
        child processes and you have forgotten to use the proper idiom
        in the main module:

            if __name__ == '__main__':
                freeze_support()
                ...

        The "freeze_support()" line can be omitted if the program
        is not going to be frozen to produce an executable.

        To fix this issue, refer to the "Safe importing of main module"
        section in https://docs.python.org/3/library/multiprocessing.html

 - Line 114: Duplicate hostname 'prepmatvxmldsmty10' and port '17516'
 - Line 38: Duplicate hostname 'unoochovxmldsmty07' and port '17507'
 - Line 4: Duplicate hostname 'unefonmtxxvxmlmty' and port '15131'
 - Line 6: Duplicate hostname 'empresarialvxmlmty' and port '15060'
 - Line 58: Duplicate hostname 'unefonmatvxmldsmty10' and port '17515'
 - Line 32: Duplicate hostname 'pucvxmlmty' and port '11010'
 - Line 116: Duplicate hostname 'prepmatvxmldsmty11' and port '17516'
 - Line 40: Duplicate hostname 'unoochovxmldsmty08' and port '17507'
 - Line 42: Duplicate hostname 'unoochovxmldsmty09' and port '17507'
 - Line 44: Duplicate hostname 'unoochovxmldsmty10' and port '17507'
 - Line 46: Duplicate hostname 'unoochovxmldsmty11' and port '17507'
 - Line 34: Duplicate hostname 'saldovxmlmty' and port '11090'
 - Line 118: Duplicate hostname 'prepmatvxmldsmty12' and port '17516'
 - Line 6: Duplicate hostname 'empresarialvxmlmty' and port '15060'
 - Line 8: Duplicate hostname 'hibridovxmlmty' and port '15090'
 - Line 60: Duplicate hostname 'unefonmatvxmldsmty11' and port '15515'
 - Line 48: Duplicate hostname 'unoochovxmldsmty12' and port '17507'
 - Line 36: Duplicate hostname 'unoochovxmldsmty06' and port '17507'
 - Line 120: Duplicate hostname 'visualvxmldsmty06' and port '17505'
 - Line 8: Duplicate hostname 'hibridovxmlmty' and port '15090'
 - Line 10: Duplicate hostname 'postpagovxmlmty' and port '15126'
 - Line 62: Duplicate hostname 'unefonmatvxmldsmty12' and port '17515'
 - Line 64: Duplicate hostname 'enterprisedsmty06' and port '17506'
 - Line 66: Duplicate hostname 'enterprisedsmty07' and port '17506'
 - Line 68: Duplicate hostname 'enterprisedsmty08' and port '17506'
 - Line 10: Duplicate hostname 'postpagovxmlmty' and port '15126'
 - Line 12: Duplicate hostname 'prepagomtxxvxmlmty' and port '15132'
 - Line 50: Duplicate hostname 'unefonmatvxmldsmty06' and port '17515'
 - Line 38: Duplicate hostname 'unoochovxmldsmty07' and port '17507'
 - Line 122: Duplicate hostname 'visualvxmldsmty07' and port '17505'
 - Line 70: Duplicate hostname 'enterprisedsmty09' and port '17506'
 - Line 124: Duplicate hostname 'visualvxmldsmty08' and port '17505'
 - Line 126: Duplicate hostname 'visualvxmldsmty09' and port '17505'
 - Line 128: Duplicate hostname 'visualvxmldsmty10' and port '17505'
 - Line 130: Duplicate hostname 'visualvxmldsmty11' and port '17505'
 - Line 132: Duplicate hostname 'visualvxmldsmty12' and port '17505'
 - Line 134: Duplicate hostname 'visualmtxxdsmty06' and port '17517'
 - Line 136: Duplicate hostname 'visualmtxxdsmty07' and port '17517'
 - Line 138: Duplicate hostname 'visualmtxxdsmty08' and port '17517'
 - Line 140: Duplicate hostname 'visualmtxxdsmty09' and port '17517'
 - Line 12: Duplicate hostname 'prepagomtxxvxmlmty' and port '15132'
 - Line 72: Duplicate hostname 'enterprisedsmty10' and port '17506'
 - Line 14: Duplicate hostname 'visualvxmlmty' and port '15040'
 - Line 16: Duplicate hostname 'visualmtxxvxmlmty' and port '15133'
 - Line 18: Duplicate hostname 'ciamsvxmlmty' and port '15124'
 - Line 20: Duplicate hostname 'activacionesvxmlmty' and port '15125'
 - Line 22: Duplicate hostname 'renovacionpiasvxmlmty' and port '15120'
 - Line 24: Duplicate hostname 'regtarjetasvxmlmty' and port '15100'
 - Line 26: Duplicate hostname 'hardblockvxmlmty' and port '15110'
 - Line 28: Duplicate hostname 'unefonvxmlmty' and port '15020'
 - Line 142: Duplicate hostname 'visualmtxxdsmty10' and port '17517'
 - Line 74: Duplicate hostname 'enterprisedsmty11' and port '17506'
 - Line 14: Duplicate hostname 'visualvxmlmty' and port '15040'
 - Line 52: Duplicate hostname 'unefonmatvxmldsmty07' and port '17515'
 - Line 40: Duplicate hostname 'unoochovxmldsmty08' and port '17507'
 - Line 30: Duplicate hostname 'prepagovxmlmty' and port '15050'
 - Line 144: Duplicate hostname 'visualmtxxdsmty11' and port '17517'
 - Line 76: Duplicate hostname 'enterprisedsmty12' and port '17506'
 - Line 16: Duplicate hostname 'visualmtxxvxmlmty' and port '15133'
 - Line 54: Duplicate hostname 'unefonmatvxmldsmty08' and port '17515'
 - Line 42: Duplicate hostname 'unoochovxmldsmty09' and port '17507'
 - Line 32: Duplicate hostname 'pucvxmlmty' and port '11010'
 - Line 146: Duplicate hostname 'visualmtxxdsmty12' and port '17517'
 - Line 78: Duplicate hostname 'hibri611dsmty06' and port '17504'
 - Line 18: Duplicate hostname 'ciamsvxmlmty' and port '15124'
 - Line 56: Duplicate hostname 'unefonmatvxmldsmty09' and port '17515'
 - Line 44: Duplicate hostname 'unoochovxmldsmty10' and port '17507'
 - Line 34: Duplicate hostname 'saldovxmlmty' and port '11090'
 - Line 148: Duplicate hostname 'ciamsvxmldsmty06' and port '17508'
 - Line 150: Duplicate hostname 'ciamsvxmldsmty07' and port '17508'
 - Line 20: Duplicate hostname 'activacionesvxmlmty' and port '15125'
 - Line 58: Duplicate hostname 'unefonmatvxmldsmty10' and port '17515'
 - Line 46: Duplicate hostname 'unoochovxmldsmty11' and port '17507'
 - Line 36: Duplicate hostname 'unoochovxmldsmty06' and port '17507'
 - Line 80: Duplicate hostname 'hibri611dsmty07' and port '17504'
 - Line 152: Duplicate hostname 'ciamsvxmldsmty08' and port '17508'
 - Line 22: Duplicate hostname 'renovacionpiasvxmlmty' and port '15120'
 - Line 60: Duplicate hostname 'unefonmatvxmldsmty11' and port '15515'
 - Line 62: Duplicate hostname 'unefonmatvxmldsmty12' and port '17515'
 - Line 64: Duplicate hostname 'enterprisedsmty06' and port '17506'
 - Line 82: Duplicate hostname 'hibri611dsmty08' and port '17504'
 - Line 154: Duplicate hostname 'ciamsvxmldsmty09' and port '17508'
 - Line 24: Duplicate hostname 'regtarjetasvxmlmty' and port '15100'
 - Line 48: Duplicate hostname 'unoochovxmldsmty12' and port '17507'
Traceback (most recent call last):
 - Line 38: Duplicate hostname 'unoochovxmldsmty07' and port '17507'
 - Line 66: Duplicate hostname 'enterprisedsmty07' and port '17506'
 - Line 84: Duplicate hostname 'hibri611dsmty09' and port '17504'
 - Line 156: Duplicate hostname 'ciamsvxmldsmty10' and port '17508'
 - Line 26: Duplicate hostname 'hardblockvxmlmty' and port '15110'
 - Line 50: Duplicate hostname 'unefonmatvxmldsmty06' and port '17515'
 - Line 40: Duplicate hostname 'unoochovxmldsmty08' and port '17507'
 - Line 68: Duplicate hostname 'enterprisedsmty08' and port '17506'
 - Line 86: Duplicate hostname 'hibri611dsmty10' and port '17504'
 - Line 88: Duplicate hostname 'hibri611dsmty11' and port '17504'
 - Line 90: Duplicate hostname 'hibri611dsmty12' and port '17504'
 - Line 52: Duplicate hostname 'unefonmatvxmldsmty07' and port '17515'
 - Line 42: Duplicate hostname 'unoochovxmldsmty09' and port '17507'
 - Line 70: Duplicate hostname 'enterprisedsmty09' and port '17506'
 - Line 158: Duplicate hostname 'ciamsvxmldsmty11' and port '17508'
  File "<string>", line 1, in <module>
    from multiprocessing.spawn import spawn_main; spawn_main(parent_pid=29516, pipe_handle=356)
                                                  ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 - Line 92: Duplicate hostname 'postpag611dsmty06' and port '17501'
 - Line 54: Duplicate hostname 'unefonmatvxmldsmty08' and port '17515'
 - Line 44: Duplicate hostname 'unoochovxmldsmty10' and port '17507'
 - Line 72: Duplicate hostname 'enterprisedsmty10' and port '17506'
 - Line 28: Duplicate hostname 'unefonvxmlmty' and port '15020'
 - Line 160: Duplicate hostname 'ciamsvxmldsmty12' and port '17508'
  File "multiprocessing\spawn.py", line 122, in spawn_main
 - Line 94: Duplicate hostname 'postpag611dsmty07' and port '17501'
 - Line 56: Duplicate hostname 'unefonmatvxmldsmty09' and port '17515'
 - Line 46: Duplicate hostname 'unoochovxmldsmty11' and port '17507'
 - Line 74: Duplicate hostname 'enterprisedsmty11' and port '17506'
 - Line 30: Duplicate hostname 'prepagovxmlmty' and port '15050'
 - Line 162: Duplicate hostname 'activavxmldsmty01' and port '17501'
  File "multiprocessing\spawn.py", line 131, in _main
 - Line 96: Duplicate hostname 'postpag611dsmty08' and port '17501'
 - Line 58: Duplicate hostname 'unefonmatvxmldsmty10' and port '17515'
 - Line 48: Duplicate hostname 'unoochovxmldsmty12' and port '17507'
 - Line 76: Duplicate hostname 'enterprisedsmty12' and port '17506'
 - Line 32: Duplicate hostname 'pucvxmlmty' and port '11010'
 - Line 164: Duplicate hostname 'activavxmldsmty02' and port '17501'
  File "multiprocessing\spawn.py", line 246, in prepare
 - Line 98: Duplicate hostname 'postpag611dsmty09' and port '17501'
 - Line 60: Duplicate hostname 'unefonmatvxmldsmty11' and port '15515'
 - Line 50: Duplicate hostname 'unefonmatvxmldsmty06' and port '17515'

❌ Pre-validation Errors: - Line 78: Duplicate hostname 'hibri611dsmty06' and port '17504'
 - Line 34: Duplicate hostname 'saldovxmlmty' and port '11090'
 - Line 166: Duplicate hostname 'activavxmldsmty03' and port '17501'
  File "multiprocessing\spawn.py", line 297, in _fixup_main_from_path
 - Line 100: Duplicate hostname 'postpag611dsmty10' and port '17501'
 - Line 62: Duplicate hostname 'unefonmatvxmldsmty12' and port '17515'
 - Line 52: Duplicate hostname 'unefonmatvxmldsmty07' and port '17515'

 - Line 80: Duplicate hostname 'hibri611dsmty07' and port '17504'
 - Line 36: Duplicate hostname 'unoochovxmldsmty06' and port '17507'
 - Line 168: Duplicate hostname 'activavxmldsmty04' and port '17501'
  File "<frozen runpy>", line 287, in run_path
 - Line 102: Duplicate hostname 'postpag611dsmty11' and port '17501'
 - Line 64: Duplicate hostname 'enterprisedsmty06' and port '17506'
 - Line 54: Duplicate hostname 'unefonmatvxmldsmty08' and port '17515'
 - Line 2: Duplicate hostname 'ochocientosvxmlmty' and port '15070'
 - Line 82: Duplicate hostname 'hibri611dsmty08' and port '17504'
 - Line 38: Duplicate hostname 'unoochovxmldsmty07' and port '17507'
 - Line 170: Duplicate hostname 'activavxmldsmty05' and port '17501'
  File "<frozen runpy>", line 98, in _run_module_code
 - Line 104: Duplicate hostname 'postpag611dsmty12' and port '17501'
 - Line 66: Duplicate hostname 'enterprisedsmty07' and port '17506'
 - Line 56: Duplicate hostname 'unefonmatvxmldsmty09' and port '17515'
 - Line 4: Duplicate hostname 'unefonmtxxvxmlmty' and port '15131'
 - Line 84: Duplicate hostname 'hibri611dsmty09' and port '17504'
 - Line 40: Duplicate hostname 'unoochovxmldsmty08' and port '17507'
 - Line 172: Duplicate hostname 'activavxml502dsmty01' and port '17502'
  File "<frozen runpy>", line 88, in _run_code
 - Line 106: Duplicate hostname 'prepmatvxmldsmty06' and port '17516'
 - Line 68: Duplicate hostname 'enterprisedsmty08' and port '17506'
 - Line 58: Duplicate hostname 'unefonmatvxmldsmty10' and port '17515'
 - Line 6: Duplicate hostname 'empresarialvxmlmty' and port '15060'
 - Line 86: Duplicate hostname 'hibri611dsmty10' and port '17504'
 - Line 42: Duplicate hostname 'unoochovxmldsmty09' and port '17507'
 - Line 174: Duplicate hostname 'activavxml502dsmty02' and port '17502'
  File "C:\Users\ankurv\github.com\anshvermahotmail\TechnimentAnalysis\TechnimentAnalysis\jq5.py", line 110, in <module>
    results = list(executor.map(lambda hp: create_pool_entry(*hp), host_port_list))
                   ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 - Line 108: Duplicate hostname 'prepmatvxmldsmty07' and port '17516'
 - Line 70: Duplicate hostname 'enterprisedsmty09' and port '17506'
 - Line 60: Duplicate hostname 'unefonmatvxmldsmty11' and port '15515'
 - Line 8: Duplicate hostname 'hibridovxmlmty' and port '15090'
 - Line 88: Duplicate hostname 'hibri611dsmty11' and port '17504'
 - Line 44: Duplicate hostname 'unoochovxmldsmty10' and port '17507'
 - Line 176: Duplicate hostname 'activavxml502dsmty03' and port '17502'
  File "concurrent\futures\process.py", line 832, in map
 - Line 110: Duplicate hostname 'prepmatvxmldsmty08' and port '17516'
 - Line 72: Duplicate hostname 'enterprisedsmty10' and port '17506'
 - Line 62: Duplicate hostname 'unefonmatvxmldsmty12' and port '17515'
 - Line 10: Duplicate hostname 'postpagovxmlmty' and port '15126'
 - Line 90: Duplicate hostname 'hibri611dsmty12' and port '17504'
 - Line 46: Duplicate hostname 'unoochovxmldsmty11' and port '17507'
 - Line 178: Duplicate hostname 'activavxml502dsmty04' and port '17502'
  File "concurrent\futures\_base.py", line 600, in map
 - Line 112: Duplicate hostname 'prepmatvxmldsmty09' and port '17516'
 - Line 74: Duplicate hostname 'enterprisedsmty11' and port '17506'
 - Line 64: Duplicate hostname 'enterprisedsmty06' and port '17506'
 - Line 12: Duplicate hostname 'prepagomtxxvxmlmty' and port '15132'
 - Line 92: Duplicate hostname 'postpag611dsmty06' and port '17501'
 - Line 48: Duplicate hostname 'unoochovxmldsmty12' and port '17507'
 - Line 180: Duplicate hostname 'activavxml502dsmty05' and port '17502'
  File "concurrent\futures\process.py", line 803, in submit
 - Line 114: Duplicate hostname 'prepmatvxmldsmty10' and port '17516'
 - Line 76: Duplicate hostname 'enterprisedsmty12' and port '17506'
 - Line 66: Duplicate hostname 'enterprisedsmty07' and port '17506'
 - Line 14: Duplicate hostname 'visualvxmlmty' and port '15040'
 - Line 94: Duplicate hostname 'postpag611dsmty07' and port '17501'
 - Line 50: Duplicate hostname 'unefonmatvxmldsmty06' and port '17515'
 - Line 182: Duplicate hostname 'renovacionpiasdsmty01' and port '17503'
  File "concurrent\futures\process.py", line 762, in _adjust_process_count
 - Line 116: Duplicate hostname 'prepmatvxmldsmty11' and port '17516'
 - Line 78: Duplicate hostname 'hibri611dsmty06' and port '17504'
 - Line 68: Duplicate hostname 'enterprisedsmty08' and port '17506'
 - Line 16: Duplicate hostname 'visualmtxxvxmlmty' and port '15133'
 - Line 96: Duplicate hostname 'postpag611dsmty08' and port '17501'
 - Line 52: Duplicate hostname 'unefonmatvxmldsmty07' and port '17515'
 - Line 184: Duplicate hostname 'renovacionpiasdsmty02' and port '17503'
  File "concurrent\futures\process.py", line 780, in _spawn_process
 - Line 118: Duplicate hostname 'prepmatvxmldsmty12' and port '17516'
 - Line 80: Duplicate hostname 'hibri611dsmty07' and port '17504'
 - Line 70: Duplicate hostname 'enterprisedsmty09' and port '17506'
 - Line 18: Duplicate hostname 'ciamsvxmlmty' and port '15124'
 - Line 98: Duplicate hostname 'postpag611dsmty09' and port '17501'
 - Line 54: Duplicate hostname 'unefonmatvxmldsmty08' and port '17515'
 - Line 186: Duplicate hostname 'renovacionpiasdsmty03' and port '17503'
  File "multiprocessing\process.py", line 121, in start
 - Line 120: Duplicate hostname 'visualvxmldsmty06' and port '17505'
 - Line 82: Duplicate hostname 'hibri611dsmty08' and port '17504'
 - Line 72: Duplicate hostname 'enterprisedsmty10' and port '17506'
 - Line 20: Duplicate hostname 'activacionesvxmlmty' and port '15125'
 - Line 100: Duplicate hostname 'postpag611dsmty10' and port '17501'
 - Line 56: Duplicate hostname 'unefonmatvxmldsmty09' and port '17515'
 - Line 188: Duplicate hostname 'renovacionpiasdsmty04' and port '17503'
  File "multiprocessing\context.py", line 337, in _Popen
 - Line 122: Duplicate hostname 'visualvxmldsmty07' and port '17505'
 - Line 84: Duplicate hostname 'hibri611dsmty09' and port '17504'
 - Line 74: Duplicate hostname 'enterprisedsmty11' and port '17506'
 - Line 22: Duplicate hostname 'renovacionpiasvxmlmty' and port '15120'
 - Line 102: Duplicate hostname 'postpag611dsmty11' and port '17501'
 - Line 58: Duplicate hostname 'unefonmatvxmldsmty10' and port '17515'
 - Line 190: Duplicate hostname 'renovacionpiasdsmty05' and port '17503'
  File "multiprocessing\popen_spawn_win32.py", line 47, in __init__
 - Line 124: Duplicate hostname 'visualvxmldsmty08' and port '17505'
 - Line 86: Duplicate hostname 'hibri611dsmty10' and port '17504'
 - Line 76: Duplicate hostname 'enterprisedsmty12' and port '17506'
 - Line 24: Duplicate hostname 'regtarjetasvxmlmty' and port '15100'
 - Line 104: Duplicate hostname 'postpag611dsmty12' and port '17501'
 - Line 60: Duplicate hostname 'unefonmatvxmldsmty11' and port '15515'
 - Line 192: Duplicate hostname 'regtarjetasdsmty13' and port '17506'
  File "multiprocessing\spawn.py", line 164, in get_preparation_data
 - Line 126: Duplicate hostname 'visualvxmldsmty09' and port '17505'
 - Line 88: Duplicate hostname 'hibri611dsmty11' and port '17504'
 - Line 78: Duplicate hostname 'hibri611dsmty06' and port '17504'
 - Line 26: Duplicate hostname 'hardblockvxmlmty' and port '15110'
 - Line 106: Duplicate hostname 'prepmatvxmldsmty06' and port '17516'
 - Line 62: Duplicate hostname 'unefonmatvxmldsmty12' and port '17515'
 - Line 194: Duplicate hostname 'regtarjetasdsmty14' and port '17506'
  File "multiprocessing\spawn.py", line 140, in _check_not_importing_main
 - Line 128: Duplicate hostname 'visualvxmldsmty10' and port '17505'
 - Line 90: Duplicate hostname 'hibri611dsmty12' and port '17504'
 - Line 80: Duplicate hostname 'hibri611dsmty07' and port '17504'
 - Line 28: Duplicate hostname 'unefonvxmlmty' and port '15020'
 - Line 108: Duplicate hostname 'prepmatvxmldsmty07' and port '17516'
 - Line 64: Duplicate hostname 'enterprisedsmty06' and port '17506'
 - Line 196: Duplicate hostname 'regtarjetasdsmty15' and port '17506'
RuntimeError:
        An attempt has been made to start a new process before the
        current process has finished its bootstrapping phase.

        This probably means that you are not using fork to start your
        child processes and you have forgotten to use the proper idiom
        in the main module:

            if __name__ == '__main__':
                freeze_support()
                ...

        The "freeze_support()" line can be omitted if the program
        is not going to be frozen to produce an executable.

        To fix this issue, refer to the "Safe importing of main module"
        section in https://docs.python.org/3/library/multiprocessing.html

 - Line 130: Duplicate hostname 'visualvxmldsmty11' and port '17505'
 - Line 92: Duplicate hostname 'postpag611dsmty06' and port '17501'
 - Line 94: Duplicate hostname 'postpag611dsmty07' and port '17501'
 - Line 30: Duplicate hostname 'prepagovxmlmty' and port '15050'
 - Line 110: Duplicate hostname 'prepmatvxmldsmty08' and port '17516'
 - Line 66: Duplicate hostname 'enterprisedsmty07' and port '17506'
 - Line 198: Duplicate hostname 'hbvxmldsmty13' and port '17504'
 - Line 132: Duplicate hostname 'visualvxmldsmty12' and port '17505'
 - Line 82: Duplicate hostname 'hibri611dsmty08' and port '17504'
 - Line 96: Duplicate hostname 'postpag611dsmty08' and port '17501'
 - Line 32: Duplicate hostname 'pucvxmlmty' and port '11010'
 - Line 112: Duplicate hostname 'prepmatvxmldsmty09' and port '17516'
 - Line 68: Duplicate hostname 'enterprisedsmty08' and port '17506'
 - Line 200: Duplicate hostname 'hbvxmldsmty14' and port '17504'
 - Line 202: Duplicate hostname 'hbvxmldsmty15' and port '17504'
 - Line 84: Duplicate hostname 'hibri611dsmty09' and port '17504'
 - Line 98: Duplicate hostname 'postpag611dsmty09' and port '17501'
 - Line 34: Duplicate hostname 'saldovxmlmty' and port '11090'
 - Line 114: Duplicate hostname 'prepmatvxmldsmty10' and port '17516'
 - Line 70: Duplicate hostname 'enterprisedsmty09' and port '17506'
 - Line 134: Duplicate hostname 'visualmtxxdsmty06' and port '17517'
 - Line 204: Duplicate hostname 'unefonvxmldsmty06' and port '17511'
 - Line 86: Duplicate hostname 'hibri611dsmty10' and port '17504'
 - Line 100: Duplicate hostname 'postpag611dsmty10' and port '17501'
 - Line 36: Duplicate hostname 'unoochovxmldsmty06' and port '17507'
 - Line 116: Duplicate hostname 'prepmatvxmldsmty11' and port '17516'
 - Line 72: Duplicate hostname 'enterprisedsmty10' and port '17506'
 - Line 136: Duplicate hostname 'visualmtxxdsmty07' and port '17517'
 - Line 206: Duplicate hostname 'unefonvxmldsmty07' and port '17511'
 - Line 88: Duplicate hostname 'hibri611dsmty11' and port '17504'
 - Line 102: Duplicate hostname 'postpag611dsmty11' and port '17501'
 - Line 104: Duplicate hostname 'postpag611dsmty12' and port '17501'
 - Line 106: Duplicate hostname 'prepmatvxmldsmty06' and port '17516'
 - Line 108: Duplicate hostname 'prepmatvxmldsmty07' and port '17516'
 - Line 110: Duplicate hostname 'prepmatvxmldsmty08' and port '17516'
 - Line 112: Duplicate hostname 'prepmatvxmldsmty09' and port '17516'
 - Line 114: Duplicate hostname 'prepmatvxmldsmty10' and port '17516'
 - Line 38: Duplicate hostname 'unoochovxmldsmty07' and port '17507'
 - Line 118: Duplicate hostname 'prepmatvxmldsmty12' and port '17516'
 - Line 74: Duplicate hostname 'enterprisedsmty11' and port '17506'
 - Line 138: Duplicate hostname 'visualmtxxdsmty08' and port '17517'
 - Line 208: Duplicate hostname 'unefonvxmldsmty08' and port '17511'
 - Line 90: Duplicate hostname 'hibri611dsmty12' and port '17504'
 - Line 116: Duplicate hostname 'prepmatvxmldsmty11' and port '17516'
 - Line 40: Duplicate hostname 'unoochovxmldsmty08' and port '17507'
 - Line 120: Duplicate hostname 'visualvxmldsmty06' and port '17505'
 - Line 76: Duplicate hostname 'enterprisedsmty12' and port '17506'
 - Line 140: Duplicate hostname 'visualmtxxdsmty09' and port '17517'
 - Line 210: Duplicate hostname 'unefonvxmldsmty09' and port '17511'
 - Line 92: Duplicate hostname 'postpag611dsmty06' and port '17501'
 - Line 118: Duplicate hostname 'prepmatvxmldsmty12' and port '17516'
 - Line 42: Duplicate hostname 'unoochovxmldsmty09' and port '17507'
 - Line 122: Duplicate hostname 'visualvxmldsmty07' and port '17505'
 - Line 78: Duplicate hostname 'hibri611dsmty06' and port '17504'
 - Line 142: Duplicate hostname 'visualmtxxdsmty10' and port '17517'
 - Line 212: Duplicate hostname 'unefonvxmldsmty10' and port '17511'
 - Line 94: Duplicate hostname 'postpag611dsmty07' and port '17501'
 - Line 120: Duplicate hostname 'visualvxmldsmty06' and port '17505'
 - Line 44: Duplicate hostname 'unoochovxmldsmty10' and port '17507'
 - Line 124: Duplicate hostname 'visualvxmldsmty08' and port '17505'
 - Line 80: Duplicate hostname 'hibri611dsmty07' and port '17504'
 - Line 144: Duplicate hostname 'visualmtxxdsmty11' and port '17517'
 - Line 214: Duplicate hostname 'unefonvxmldsmty11' and port '17511'
 - Line 96: Duplicate hostname 'postpag611dsmty08' and port '17501'
 - Line 122: Duplicate hostname 'visualvxmldsmty07' and port '17505'
 - Line 46: Duplicate hostname 'unoochovxmldsmty11' and port '17507'
 - Line 126: Duplicate hostname 'visualvxmldsmty09' and port '17505'
 - Line 82: Duplicate hostname 'hibri611dsmty08' and port '17504'
 - Line 146: Duplicate hostname 'visualmtxxdsmty12' and port '17517'
 - Line 216: Duplicate hostname 'unefonvxmldsmty12' and port '17511'
 - Line 98: Duplicate hostname 'postpag611dsmty09' and port '17501'
 - Line 124: Duplicate hostname 'visualvxmldsmty08' and port '17505'
 - Line 48: Duplicate hostname 'unoochovxmldsmty12' and port '17507'
 - Line 128: Duplicate hostname 'visualvxmldsmty10' and port '17505'
 - Line 84: Duplicate hostname 'hibri611dsmty09' and port '17504'
 - Line 148: Duplicate hostname 'ciamsvxmldsmty06' and port '17508'
 - Line 218: Duplicate hostname 'prepag611dsmty06' and port '17502'
 - Line 100: Duplicate hostname 'postpag611dsmty10' and port '17501'
 - Line 126: Duplicate hostname 'visualvxmldsmty09' and port '17505'
 - Line 50: Duplicate hostname 'unefonmatvxmldsmty06' and port '17515'
 - Line 130: Duplicate hostname 'visualvxmldsmty11' and port '17505'
 - Line 86: Duplicate hostname 'hibri611dsmty10' and port '17504'
 - Line 150: Duplicate hostname 'ciamsvxmldsmty07' and port '17508'
 - Line 220: Duplicate hostname 'prepag611dsmty07' and port '17502'
 - Line 102: Duplicate hostname 'postpag611dsmty11' and port '17501'
 - Line 128: Duplicate hostname 'visualvxmldsmty10' and port '17505'
 - Line 52: Duplicate hostname 'unefonmatvxmldsmty07' and port '17515'
 - Line 132: Duplicate hostname 'visualvxmldsmty12' and port '17505'
 - Line 88: Duplicate hostname 'hibri611dsmty11' and port '17504'
 - Line 152: Duplicate hostname 'ciamsvxmldsmty08' and port '17508'
 - Line 222: Duplicate hostname 'prepag611dsmty08' and port '17502'
 - Line 104: Duplicate hostname 'postpag611dsmty12' and port '17501'
 - Line 130: Duplicate hostname 'visualvxmldsmty11' and port '17505'
 - Line 54: Duplicate hostname 'unefonmatvxmldsmty08' and port '17515'
 - Line 134: Duplicate hostname 'visualmtxxdsmty06' and port '17517'
 - Line 90: Duplicate hostname 'hibri611dsmty12' and port '17504'
 - Line 154: Duplicate hostname 'ciamsvxmldsmty09' and port '17508'
 - Line 224: Duplicate hostname 'prepag611dsmty09' and port '17502'
 - Line 106: Duplicate hostname 'prepmatvxmldsmty06' and port '17516'
 - Line 132: Duplicate hostname 'visualvxmldsmty12' and port '17505'
 - Line 56: Duplicate hostname 'unefonmatvxmldsmty09' and port '17515'
 - Line 136: Duplicate hostname 'visualmtxxdsmty07' and port '17517'
 - Line 92: Duplicate hostname 'postpag611dsmty06' and port '17501'
 - Line 156: Duplicate hostname 'ciamsvxmldsmty10' and port '17508'
 - Line 226: Duplicate hostname 'prepag611dsmty10' and port '17502'
 - Line 108: Duplicate hostname 'prepmatvxmldsmty07' and port '17516'
 - Line 134: Duplicate hostname 'visualmtxxdsmty06' and port '17517'
 - Line 58: Duplicate hostname 'unefonmatvxmldsmty10' and port '17515'
 - Line 138: Duplicate hostname 'visualmtxxdsmty08' and port '17517'
 - Line 94: Duplicate hostname 'postpag611dsmty07' and port '17501'
 - Line 158: Duplicate hostname 'ciamsvxmldsmty11' and port '17508'
 - Line 228: Duplicate hostname 'prepag611dsmty11' and port '17502'
 - Line 110: Duplicate hostname 'prepmatvxmldsmty08' and port '17516'
 - Line 136: Duplicate hostname 'visualmtxxdsmty07' and port '17517'
 - Line 60: Duplicate hostname 'unefonmatvxmldsmty11' and port '15515'
 - Line 140: Duplicate hostname 'visualmtxxdsmty09' and port '17517'
 - Line 96: Duplicate hostname 'postpag611dsmty08' and port '17501'
 - Line 160: Duplicate hostname 'ciamsvxmldsmty12' and port '17508'
 - Line 230: Duplicate hostname 'prepag611dsmty12' and port '17502'
 - Line 232: Duplicate hostname 'prepag611dsmty13' and port '17505'
 - Line 138: Duplicate hostname 'visualmtxxdsmty08' and port '17517'
 - Line 62: Duplicate hostname 'unefonmatvxmldsmty12' and port '17515'
 - Line 142: Duplicate hostname 'visualmtxxdsmty10' and port '17517'
 - Line 98: Duplicate hostname 'postpag611dsmty09' and port '17501'
 - Line 162: Duplicate hostname 'activavxmldsmty01' and port '17501'
 - Line 112: Duplicate hostname 'prepmatvxmldsmty09' and port '17516'
 - Line 234: Duplicate hostname 'prepag611dsmty14' and port '17505'
 - Line 236: Duplicate hostname 'prepag611dsmty15' and port '17505'
 - Line 64: Duplicate hostname 'enterprisedsmty06' and port '17506'
 - Line 66: Duplicate hostname 'enterprisedsmty07' and port '17506'
 - Line 68: Duplicate hostname 'enterprisedsmty08' and port '17506'
 - Line 164: Duplicate hostname 'activavxmldsmty02' and port '17501'
 - Line 166: Duplicate hostname 'activavxmldsmty03' and port '17501'
 - Line 140: Duplicate hostname 'visualmtxxdsmty09' and port '17517'
 - Line 238: Duplicate hostname 'saldovxmldsmty13' and port '17501'
 - Line 144: Duplicate hostname 'visualmtxxdsmty11' and port '17517'
 - Line 100: Duplicate hostname 'postpag611dsmty10' and port '17501'
 - Line 70: Duplicate hostname 'enterprisedsmty09' and port '17506'
 - Line 114: Duplicate hostname 'prepmatvxmldsmty10' and port '17516'
 - Line 168: Duplicate hostname 'activavxmldsmty04' and port '17501'
 - Line 142: Duplicate hostname 'visualmtxxdsmty10' and port '17517'
 - Line 240: Duplicate hostname 'saldovxmldsmty14' and port '17501'
 - Line 146: Duplicate hostname 'visualmtxxdsmty12' and port '17517'
 - Line 102: Duplicate hostname 'postpag611dsmty11' and port '17501'
 - Line 72: Duplicate hostname 'enterprisedsmty10' and port '17506'
 - Line 116: Duplicate hostname 'prepmatvxmldsmty11' and port '17516'
 - Line 170: Duplicate hostname 'activavxmldsmty05' and port '17501'
 - Line 144: Duplicate hostname 'visualmtxxdsmty11' and port '17517'
 - Line 242: Duplicate hostname 'saldovxmldsmty15' and port '17501'
 - Line 148: Duplicate hostname 'ciamsvxmldsmty06' and port '17508'
 - Line 104: Duplicate hostname 'postpag611dsmty12' and port '17501'
 - Line 74: Duplicate hostname 'enterprisedsmty11' and port '17506'
 - Line 118: Duplicate hostname 'prepmatvxmldsmty12' and port '17516'
 - Line 172: Duplicate hostname 'activavxml502dsmty01' and port '17502'
 - Line 146: Duplicate hostname 'visualmtxxdsmty12' and port '17517'
 - Line 244: Duplicate hostname 'saldovxml502dsmty13' and port '17502'
 - Line 150: Duplicate hostname 'ciamsvxmldsmty07' and port '17508'
 - Line 152: Duplicate hostname 'ciamsvxmldsmty08' and port '17508'
 - Line 76: Duplicate hostname 'enterprisedsmty12' and port '17506'
 - Line 120: Duplicate hostname 'visualvxmldsmty06' and port '17505'
 - Line 174: Duplicate hostname 'activavxml502dsmty02' and port '17502'
 - Line 148: Duplicate hostname 'ciamsvxmldsmty06' and port '17508'
 - Line 246: Duplicate hostname 'saldovxml502dsmty14' and port '17502'
 - Line 106: Duplicate hostname 'prepmatvxmldsmty06' and port '17516'
 - Line 154: Duplicate hostname 'ciamsvxmldsmty09' and port '17508'
 - Line 78: Duplicate hostname 'hibri611dsmty06' and port '17504'
 - Line 122: Duplicate hostname 'visualvxmldsmty07' and port '17505'
 - Line 176: Duplicate hostname 'activavxml502dsmty03' and port '17502'
 - Line 150: Duplicate hostname 'ciamsvxmldsmty07' and port '17508'
 - Line 248: Duplicate hostname 'saldovxml502dsmty15' and port '17502'
 - Line 108: Duplicate hostname 'prepmatvxmldsmty07' and port '17516'
 - Line 156: Duplicate hostname 'ciamsvxmldsmty10' and port '17508'
 - Line 80: Duplicate hostname 'hibri611dsmty07' and port '17504'
 - Line 124: Duplicate hostname 'visualvxmldsmty08' and port '17505'
 - Line 178: Duplicate hostname 'activavxml502dsmty04' and port '17502'
 - Line 180: Duplicate hostname 'activavxml502dsmty05' and port '17502'
 - Line 110: Duplicate hostname 'prepmatvxmldsmty08' and port '17516'
 - Line 158: Duplicate hostname 'ciamsvxmldsmty11' and port '17508'
 - Line 82: Duplicate hostname 'hibri611dsmty08' and port '17504'
 - Line 126: Duplicate hostname 'visualvxmldsmty09' and port '17505'
 - Line 152: Duplicate hostname 'ciamsvxmldsmty08' and port '17508'
 - Line 182: Duplicate hostname 'renovacionpiasdsmty01' and port '17503'
 - Line 112: Duplicate hostname 'prepmatvxmldsmty09' and port '17516'
 - Line 160: Duplicate hostname 'ciamsvxmldsmty12' and port '17508'
 - Line 84: Duplicate hostname 'hibri611dsmty09' and port '17504'
 - Line 128: Duplicate hostname 'visualvxmldsmty10' and port '17505'
 - Line 154: Duplicate hostname 'ciamsvxmldsmty09' and port '17508'
 - Line 184: Duplicate hostname 'renovacionpiasdsmty02' and port '17503'
 - Line 114: Duplicate hostname 'prepmatvxmldsmty10' and port '17516'
 - Line 162: Duplicate hostname 'activavxmldsmty01' and port '17501'
 - Line 86: Duplicate hostname 'hibri611dsmty10' and port '17504'
 - Line 130: Duplicate hostname 'visualvxmldsmty11' and port '17505'
 - Line 156: Duplicate hostname 'ciamsvxmldsmty10' and port '17508'
 - Line 186: Duplicate hostname 'renovacionpiasdsmty03' and port '17503'
 - Line 188: Duplicate hostname 'renovacionpiasdsmty04' and port '17503'
 - Line 164: Duplicate hostname 'activavxmldsmty02' and port '17501'
 - Line 88: Duplicate hostname 'hibri611dsmty11' and port '17504'
 - Line 132: Duplicate hostname 'visualvxmldsmty12' and port '17505'
 - Line 158: Duplicate hostname 'ciamsvxmldsmty11' and port '17508'
 - Line 116: Duplicate hostname 'prepmatvxmldsmty11' and port '17516'
 - Line 190: Duplicate hostname 'renovacionpiasdsmty05' and port '17503'
 - Line 166: Duplicate hostname 'activavxmldsmty03' and port '17501'
 - Line 90: Duplicate hostname 'hibri611dsmty12' and port '17504'
 - Line 134: Duplicate hostname 'visualmtxxdsmty06' and port '17517'
 - Line 92: Duplicate hostname 'postpag611dsmty06' and port '17501'
 - Line 118: Duplicate hostname 'prepmatvxmldsmty12' and port '17516'
 - Line 192: Duplicate hostname 'regtarjetasdsmty13' and port '17506'
 - Line 168: Duplicate hostname 'activavxmldsmty04' and port '17501'
 - Line 160: Duplicate hostname 'ciamsvxmldsmty12' and port '17508'
 - Line 162: Duplicate hostname 'activavxmldsmty01' and port '17501'
 - Line 94: Duplicate hostname 'postpag611dsmty07' and port '17501'
 - Line 120: Duplicate hostname 'visualvxmldsmty06' and port '17505'
 - Line 194: Duplicate hostname 'regtarjetasdsmty14' and port '17506'
 - Line 170: Duplicate hostname 'activavxmldsmty05' and port '17501'
 - Line 136: Duplicate hostname 'visualmtxxdsmty07' and port '17517'
 - Line 164: Duplicate hostname 'activavxmldsmty02' and port '17501'
 - Line 96: Duplicate hostname 'postpag611dsmty08' and port '17501'
 - Line 122: Duplicate hostname 'visualvxmldsmty07' and port '17505'
 - Line 196: Duplicate hostname 'regtarjetasdsmty15' and port '17506'
 - Line 172: Duplicate hostname 'activavxml502dsmty01' and port '17502'
 - Line 138: Duplicate hostname 'visualmtxxdsmty08' and port '17517'
 - Line 166: Duplicate hostname 'activavxmldsmty03' and port '17501'
 - Line 98: Duplicate hostname 'postpag611dsmty09' and port '17501'
 - Line 100: Duplicate hostname 'postpag611dsmty10' and port '17501'
 - Line 198: Duplicate hostname 'hbvxmldsmty13' and port '17504'
 - Line 174: Duplicate hostname 'activavxml502dsmty02' and port '17502'
 - Line 140: Duplicate hostname 'visualmtxxdsmty09' and port '17517'
 - Line 168: Duplicate hostname 'activavxmldsmty04' and port '17501'
 - Line 124: Duplicate hostname 'visualvxmldsmty08' and port '17505'
 - Line 102: Duplicate hostname 'postpag611dsmty11' and port '17501'
 - Line 200: Duplicate hostname 'hbvxmldsmty14' and port '17504'
 - Line 176: Duplicate hostname 'activavxml502dsmty03' and port '17502'
 - Line 142: Duplicate hostname 'visualmtxxdsmty10' and port '17517'
 - Line 170: Duplicate hostname 'activavxmldsmty05' and port '17501'
 - Line 126: Duplicate hostname 'visualvxmldsmty09' and port '17505'
 - Line 104: Duplicate hostname 'postpag611dsmty12' and port '17501'
 - Line 202: Duplicate hostname 'hbvxmldsmty15' and port '17504'
 - Line 178: Duplicate hostname 'activavxml502dsmty04' and port '17502'
 - Line 144: Duplicate hostname 'visualmtxxdsmty11' and port '17517'
 - Line 172: Duplicate hostname 'activavxml502dsmty01' and port '17502'
 - Line 128: Duplicate hostname 'visualvxmldsmty10' and port '17505'
 - Line 106: Duplicate hostname 'prepmatvxmldsmty06' and port '17516'
 - Line 108: Duplicate hostname 'prepmatvxmldsmty07' and port '17516'
 - Line 180: Duplicate hostname 'activavxml502dsmty05' and port '17502'
 - Line 146: Duplicate hostname 'visualmtxxdsmty12' and port '17517'
 - Line 182: Duplicate hostname 'renovacionpiasdsmty01' and port '17503'
 - Line 130: Duplicate hostname 'visualvxmldsmty11' and port '17505'
 - Line 204: Duplicate hostname 'unefonvxmldsmty06' and port '17511'
 - Line 110: Duplicate hostname 'prepmatvxmldsmty08' and port '17516'
 - Line 174: Duplicate hostname 'activavxml502dsmty02' and port '17502'
 - Line 148: Duplicate hostname 'ciamsvxmldsmty06' and port '17508'
 - Line 184: Duplicate hostname 'renovacionpiasdsmty02' and port '17503'
 - Line 132: Duplicate hostname 'visualvxmldsmty12' and port '17505'
 - Line 134: Duplicate hostname 'visualmtxxdsmty06' and port '17517'
 - Line 112: Duplicate hostname 'prepmatvxmldsmty09' and port '17516'
 - Line 176: Duplicate hostname 'activavxml502dsmty03' and port '17502'
 - Line 150: Duplicate hostname 'ciamsvxmldsmty07' and port '17508'
 - Line 186: Duplicate hostname 'renovacionpiasdsmty03' and port '17503'
 - Line 206: Duplicate hostname 'unefonvxmldsmty07' and port '17511'
 - Line 136: Duplicate hostname 'visualmtxxdsmty07' and port '17517'
 - Line 114: Duplicate hostname 'prepmatvxmldsmty10' and port '17516'
 - Line 178: Duplicate hostname 'activavxml502dsmty04' and port '17502'
 - Line 152: Duplicate hostname 'ciamsvxmldsmty08' and port '17508'
 - Line 188: Duplicate hostname 'renovacionpiasdsmty04' and port '17503'
 - Line 208: Duplicate hostname 'unefonvxmldsmty08' and port '17511'
 - Line 138: Duplicate hostname 'visualmtxxdsmty08' and port '17517'
 - Line 116: Duplicate hostname 'prepmatvxmldsmty11' and port '17516'
 - Line 180: Duplicate hostname 'activavxml502dsmty05' and port '17502'
 - Line 154: Duplicate hostname 'ciamsvxmldsmty09' and port '17508'
 - Line 190: Duplicate hostname 'renovacionpiasdsmty05' and port '17503'
 - Line 210: Duplicate hostname 'unefonvxmldsmty09' and port '17511'
 - Line 140: Duplicate hostname 'visualmtxxdsmty09' and port '17517'
 - Line 118: Duplicate hostname 'prepmatvxmldsmty12' and port '17516'
 - Line 182: Duplicate hostname 'renovacionpiasdsmty01' and port '17503'
 - Line 156: Duplicate hostname 'ciamsvxmldsmty10' and port '17508'
 - Line 192: Duplicate hostname 'regtarjetasdsmty13' and port '17506'
 - Line 212: Duplicate hostname 'unefonvxmldsmty10' and port '17511'
 - Line 142: Duplicate hostname 'visualmtxxdsmty10' and port '17517'
 - Line 120: Duplicate hostname 'visualvxmldsmty06' and port '17505'
 - Line 184: Duplicate hostname 'renovacionpiasdsmty02' and port '17503'
 - Line 158: Duplicate hostname 'ciamsvxmldsmty11' and port '17508'
 - Line 194: Duplicate hostname 'regtarjetasdsmty14' and port '17506'
 - Line 214: Duplicate hostname 'unefonvxmldsmty11' and port '17511'
 - Line 144: Duplicate hostname 'visualmtxxdsmty11' and port '17517'
 - Line 122: Duplicate hostname 'visualvxmldsmty07' and port '17505'
 - Line 124: Duplicate hostname 'visualvxmldsmty08' and port '17505'
 - Line 160: Duplicate hostname 'ciamsvxmldsmty12' and port '17508'
 - Line 196: Duplicate hostname 'regtarjetasdsmty15' and port '17506'
 - Line 216: Duplicate hostname 'unefonvxmldsmty12' and port '17511'
 - Line 146: Duplicate hostname 'visualmtxxdsmty12' and port '17517'
 - Line 186: Duplicate hostname 'renovacionpiasdsmty03' and port '17503'
 - Line 126: Duplicate hostname 'visualvxmldsmty09' and port '17505'
 - Line 162: Duplicate hostname 'activavxmldsmty01' and port '17501'
 - Line 198: Duplicate hostname 'hbvxmldsmty13' and port '17504'
 - Line 218: Duplicate hostname 'prepag611dsmty06' and port '17502'
 - Line 148: Duplicate hostname 'ciamsvxmldsmty06' and port '17508'
 - Line 188: Duplicate hostname 'renovacionpiasdsmty04' and port '17503'
 - Line 128: Duplicate hostname 'visualvxmldsmty10' and port '17505'
 - Line 164: Duplicate hostname 'activavxmldsmty02' and port '17501'
 - Line 200: Duplicate hostname 'hbvxmldsmty14' and port '17504'
 - Line 220: Duplicate hostname 'prepag611dsmty07' and port '17502'
 - Line 150: Duplicate hostname 'ciamsvxmldsmty07' and port '17508'
 - Line 190: Duplicate hostname 'renovacionpiasdsmty05' and port '17503'
 - Line 130: Duplicate hostname 'visualvxmldsmty11' and port '17505'
 - Line 132: Duplicate hostname 'visualvxmldsmty12' and port '17505'
 - Line 202: Duplicate hostname 'hbvxmldsmty15' and port '17504'
 - Line 222: Duplicate hostname 'prepag611dsmty08' and port '17502'
 - Line 152: Duplicate hostname 'ciamsvxmldsmty08' and port '17508'
 - Line 192: Duplicate hostname 'regtarjetasdsmty13' and port '17506'
 - Line 166: Duplicate hostname 'activavxmldsmty03' and port '17501'
 - Line 134: Duplicate hostname 'visualmtxxdsmty06' and port '17517'
 - Line 204: Duplicate hostname 'unefonvxmldsmty06' and port '17511'
 - Line 224: Duplicate hostname 'prepag611dsmty09' and port '17502'
 - Line 154: Duplicate hostname 'ciamsvxmldsmty09' and port '17508'
 - Line 194: Duplicate hostname 'regtarjetasdsmty14' and port '17506'
 - Line 168: Duplicate hostname 'activavxmldsmty04' and port '17501'
 - Line 136: Duplicate hostname 'visualmtxxdsmty07' and port '17517'
 - Line 206: Duplicate hostname 'unefonvxmldsmty07' and port '17511'
 - Line 226: Duplicate hostname 'prepag611dsmty10' and port '17502'
 - Line 156: Duplicate hostname 'ciamsvxmldsmty10' and port '17508'
 - Line 196: Duplicate hostname 'regtarjetasdsmty15' and port '17506'
 - Line 170: Duplicate hostname 'activavxmldsmty05' and port '17501'
 - Line 138: Duplicate hostname 'visualmtxxdsmty08' and port '17517'
 - Line 208: Duplicate hostname 'unefonvxmldsmty08' and port '17511'
 - Line 228: Duplicate hostname 'prepag611dsmty11' and port '17502'
 - Line 158: Duplicate hostname 'ciamsvxmldsmty11' and port '17508'
 - Line 198: Duplicate hostname 'hbvxmldsmty13' and port '17504'
 - Line 172: Duplicate hostname 'activavxml502dsmty01' and port '17502'
 - Line 140: Duplicate hostname 'visualmtxxdsmty09' and port '17517'
 - Line 210: Duplicate hostname 'unefonvxmldsmty09' and port '17511'
 - Line 230: Duplicate hostname 'prepag611dsmty12' and port '17502'
 - Line 160: Duplicate hostname 'ciamsvxmldsmty12' and port '17508'
 - Line 200: Duplicate hostname 'hbvxmldsmty14' and port '17504'
 - Line 174: Duplicate hostname 'activavxml502dsmty02' and port '17502'
 - Line 142: Duplicate hostname 'visualmtxxdsmty10' and port '17517'
 - Line 212: Duplicate hostname 'unefonvxmldsmty10' and port '17511'
 - Line 232: Duplicate hostname 'prepag611dsmty13' and port '17505'
 - Line 162: Duplicate hostname 'activavxmldsmty01' and port '17501'
 - Line 202: Duplicate hostname 'hbvxmldsmty15' and port '17504'
 - Line 176: Duplicate hostname 'activavxml502dsmty03' and port '17502'
 - Line 144: Duplicate hostname 'visualmtxxdsmty11' and port '17517'
 - Line 214: Duplicate hostname 'unefonvxmldsmty11' and port '17511'
 - Line 234: Duplicate hostname 'prepag611dsmty14' and port '17505'
 - Line 164: Duplicate hostname 'activavxmldsmty02' and port '17501'
 - Line 204: Duplicate hostname 'unefonvxmldsmty06' and port '17511'
 - Line 178: Duplicate hostname 'activavxml502dsmty04' and port '17502'
 - Line 146: Duplicate hostname 'visualmtxxdsmty12' and port '17517'
 - Line 216: Duplicate hostname 'unefonvxmldsmty12' and port '17511'
 - Line 236: Duplicate hostname 'prepag611dsmty15' and port '17505'
 - Line 166: Duplicate hostname 'activavxmldsmty03' and port '17501'
 - Line 206: Duplicate hostname 'unefonvxmldsmty07' and port '17511'
 - Line 180: Duplicate hostname 'activavxml502dsmty05' and port '17502'
 - Line 148: Duplicate hostname 'ciamsvxmldsmty06' and port '17508'
 - Line 218: Duplicate hostname 'prepag611dsmty06' and port '17502'
 - Line 238: Duplicate hostname 'saldovxmldsmty13' and port '17501'
 - Line 168: Duplicate hostname 'activavxmldsmty04' and port '17501'
 - Line 208: Duplicate hostname 'unefonvxmldsmty08' and port '17511'
 - Line 182: Duplicate hostname 'renovacionpiasdsmty01' and port '17503'
 - Line 150: Duplicate hostname 'ciamsvxmldsmty07' and port '17508'
 - Line 220: Duplicate hostname 'prepag611dsmty07' and port '17502'
 - Line 240: Duplicate hostname 'saldovxmldsmty14' and port '17501'
 - Line 170: Duplicate hostname 'activavxmldsmty05' and port '17501'
 - Line 210: Duplicate hostname 'unefonvxmldsmty09' and port '17511'
 - Line 184: Duplicate hostname 'renovacionpiasdsmty02' and port '17503'
 - Line 152: Duplicate hostname 'ciamsvxmldsmty08' and port '17508'
 - Line 222: Duplicate hostname 'prepag611dsmty08' and port '17502'
 - Line 242: Duplicate hostname 'saldovxmldsmty15' and port '17501'
 - Line 172: Duplicate hostname 'activavxml502dsmty01' and port '17502'
 - Line 212: Duplicate hostname 'unefonvxmldsmty10' and port '17511'
 - Line 186: Duplicate hostname 'renovacionpiasdsmty03' and port '17503'
 - Line 154: Duplicate hostname 'ciamsvxmldsmty09' and port '17508'
 - Line 224: Duplicate hostname 'prepag611dsmty09' and port '17502'
 - Line 244: Duplicate hostname 'saldovxml502dsmty13' and port '17502'
 - Line 174: Duplicate hostname 'activavxml502dsmty02' and port '17502'
 - Line 214: Duplicate hostname 'unefonvxmldsmty11' and port '17511'
 - Line 188: Duplicate hostname 'renovacionpiasdsmty04' and port '17503'
 - Line 156: Duplicate hostname 'ciamsvxmldsmty10' and port '17508'
 - Line 226: Duplicate hostname 'prepag611dsmty10' and port '17502'
 - Line 246: Duplicate hostname 'saldovxml502dsmty14' and port '17502'
 - Line 176: Duplicate hostname 'activavxml502dsmty03' and port '17502'
 - Line 216: Duplicate hostname 'unefonvxmldsmty12' and port '17511'
 - Line 190: Duplicate hostname 'renovacionpiasdsmty05' and port '17503'
 - Line 158: Duplicate hostname 'ciamsvxmldsmty11' and port '17508'
 - Line 228: Duplicate hostname 'prepag611dsmty11' and port '17502'
 - Line 248: Duplicate hostname 'saldovxml502dsmty15' and port '17502'
 - Line 178: Duplicate hostname 'activavxml502dsmty04' and port '17502'
 - Line 218: Duplicate hostname 'prepag611dsmty06' and port '17502'
 - Line 192: Duplicate hostname 'regtarjetasdsmty13' and port '17506'
 - Line 160: Duplicate hostname 'ciamsvxmldsmty12' and port '17508'
 - Line 230: Duplicate hostname 'prepag611dsmty12' and port '17502'
 - Line 180: Duplicate hostname 'activavxml502dsmty05' and port '17502'
 - Line 220: Duplicate hostname 'prepag611dsmty07' and port '17502'
 - Line 194: Duplicate hostname 'regtarjetasdsmty14' and port '17506'
 - Line 162: Duplicate hostname 'activavxmldsmty01' and port '17501'
 - Line 232: Duplicate hostname 'prepag611dsmty13' and port '17505'
 - Line 182: Duplicate hostname 'renovacionpiasdsmty01' and port '17503'
 - Line 222: Duplicate hostname 'prepag611dsmty08' and port '17502'
 - Line 196: Duplicate hostname 'regtarjetasdsmty15' and port '17506'
 - Line 164: Duplicate hostname 'activavxmldsmty02' and port '17501'
 - Line 234: Duplicate hostname 'prepag611dsmty14' and port '17505'
 - Line 184: Duplicate hostname 'renovacionpiasdsmty02' and port '17503'
 - Line 224: Duplicate hostname 'prepag611dsmty09' and port '17502'
 - Line 198: Duplicate hostname 'hbvxmldsmty13' and port '17504'
 - Line 166: Duplicate hostname 'activavxmldsmty03' and port '17501'
 - Line 236: Duplicate hostname 'prepag611dsmty15' and port '17505'
 - Line 186: Duplicate hostname 'renovacionpiasdsmty03' and port '17503'
 - Line 226: Duplicate hostname 'prepag611dsmty10' and port '17502'
 - Line 200: Duplicate hostname 'hbvxmldsmty14' and port '17504'
 - Line 168: Duplicate hostname 'activavxmldsmty04' and port '17501'
 - Line 238: Duplicate hostname 'saldovxmldsmty13' and port '17501'
Traceback (most recent call last):
 - Line 188: Duplicate hostname 'renovacionpiasdsmty04' and port '17503'
 - Line 228: Duplicate hostname 'prepag611dsmty11' and port '17502'
 - Line 202: Duplicate hostname 'hbvxmldsmty15' and port '17504'
 - Line 170: Duplicate hostname 'activavxmldsmty05' and port '17501'
 - Line 240: Duplicate hostname 'saldovxmldsmty14' and port '17501'
 - Line 190: Duplicate hostname 'renovacionpiasdsmty05' and port '17503'
 - Line 230: Duplicate hostname 'prepag611dsmty12' and port '17502'
 - Line 204: Duplicate hostname 'unefonvxmldsmty06' and port '17511'
 - Line 172: Duplicate hostname 'activavxml502dsmty01' and port '17502'
 - Line 242: Duplicate hostname 'saldovxmldsmty15' and port '17501'
 - Line 192: Duplicate hostname 'regtarjetasdsmty13' and port '17506'
 - Line 232: Duplicate hostname 'prepag611dsmty13' and port '17505'

❌ Pre-validation Errors: - Line 174: Duplicate hostname 'activavxml502dsmty02' and port '17502'
 - Line 244: Duplicate hostname 'saldovxml502dsmty13' and port '17502'
 - Line 246: Duplicate hostname 'saldovxml502dsmty14' and port '17502'
 - Line 206: Duplicate hostname 'unefonvxmldsmty07' and port '17511'
 - Line 234: Duplicate hostname 'prepag611dsmty14' and port '17505'

 - Line 176: Duplicate hostname 'activavxml502dsmty03' and port '17502'
 - Line 194: Duplicate hostname 'regtarjetasdsmty14' and port '17506'
  File "<string>", line 1, in <module>
    from multiprocessing.spawn import spawn_main; spawn_main(parent_pid=29516, pipe_handle=444)
                                                  ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 - Line 248: Duplicate hostname 'saldovxml502dsmty15' and port '17502'
 - Line 208: Duplicate hostname 'unefonvxmldsmty08' and port '17511'
 - Line 236: Duplicate hostname 'prepag611dsmty15' and port '17505'
 - Line 2: Duplicate hostname 'ochocientosvxmlmty' and port '15070'
 - Line 178: Duplicate hostname 'activavxml502dsmty04' and port '17502'
 - Line 196: Duplicate hostname 'regtarjetasdsmty15' and port '17506'
  File "multiprocessing\spawn.py", line 122, in spawn_main
 - Line 210: Duplicate hostname 'unefonvxmldsmty09' and port '17511'
 - Line 238: Duplicate hostname 'saldovxmldsmty13' and port '17501'
 - Line 4: Duplicate hostname 'unefonmtxxvxmlmty' and port '15131'
 - Line 180: Duplicate hostname 'activavxml502dsmty05' and port '17502'
 - Line 198: Duplicate hostname 'hbvxmldsmty13' and port '17504'
  File "multiprocessing\spawn.py", line 131, in _main
 - Line 212: Duplicate hostname 'unefonvxmldsmty10' and port '17511'
 - Line 240: Duplicate hostname 'saldovxmldsmty14' and port '17501'
 - Line 6: Duplicate hostname 'empresarialvxmlmty' and port '15060'
 - Line 182: Duplicate hostname 'renovacionpiasdsmty01' and port '17503'
 - Line 200: Duplicate hostname 'hbvxmldsmty14' and port '17504'
  File "multiprocessing\spawn.py", line 246, in prepare
 - Line 214: Duplicate hostname 'unefonvxmldsmty11' and port '17511'
 - Line 242: Duplicate hostname 'saldovxmldsmty15' and port '17501'
 - Line 8: Duplicate hostname 'hibridovxmlmty' and port '15090'
 - Line 184: Duplicate hostname 'renovacionpiasdsmty02' and port '17503'
 - Line 202: Duplicate hostname 'hbvxmldsmty15' and port '17504'
  File "multiprocessing\spawn.py", line 297, in _fixup_main_from_path
 - Line 216: Duplicate hostname 'unefonvxmldsmty12' and port '17511'
 - Line 244: Duplicate hostname 'saldovxml502dsmty13' and port '17502'
 - Line 10: Duplicate hostname 'postpagovxmlmty' and port '15126'
 - Line 186: Duplicate hostname 'renovacionpiasdsmty03' and port '17503'
 - Line 204: Duplicate hostname 'unefonvxmldsmty06' and port '17511'
  File "<frozen runpy>", line 287, in run_path
 - Line 218: Duplicate hostname 'prepag611dsmty06' and port '17502'
 - Line 246: Duplicate hostname 'saldovxml502dsmty14' and port '17502'
 - Line 12: Duplicate hostname 'prepagomtxxvxmlmty' and port '15132'
 - Line 188: Duplicate hostname 'renovacionpiasdsmty04' and port '17503'
 - Line 206: Duplicate hostname 'unefonvxmldsmty07' and port '17511'
  File "<frozen runpy>", line 98, in _run_module_code
 - Line 220: Duplicate hostname 'prepag611dsmty07' and port '17502'
 - Line 248: Duplicate hostname 'saldovxml502dsmty15' and port '17502'
 - Line 14: Duplicate hostname 'visualvxmlmty' and port '15040'
 - Line 190: Duplicate hostname 'renovacionpiasdsmty05' and port '17503'
 - Line 192: Duplicate hostname 'regtarjetasdsmty13' and port '17506'
  File "<frozen runpy>", line 88, in _run_code
 - Line 222: Duplicate hostname 'prepag611dsmty08' and port '17502'
 - Line 16: Duplicate hostname 'visualmtxxvxmlmty' and port '15133'
 - Line 208: Duplicate hostname 'unefonvxmldsmty08' and port '17511'
 - Line 194: Duplicate hostname 'regtarjetasdsmty14' and port '17506'
 - Line 196: Duplicate hostname 'regtarjetasdsmty15' and port '17506'
 - Line 224: Duplicate hostname 'prepag611dsmty09' and port '17502'
 - Line 18: Duplicate hostname 'ciamsvxmlmty' and port '15124'
 - Line 210: Duplicate hostname 'unefonvxmldsmty09' and port '17511'
  File "C:\Users\ankurv\github.com\anshvermahotmail\TechnimentAnalysis\TechnimentAnalysis\jq5.py", line 110, in <module>
    results = list(executor.map(lambda hp: create_pool_entry(*hp), host_port_list))
                   ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 - Line 198: Duplicate hostname 'hbvxmldsmty13' and port '17504'
 - Line 226: Duplicate hostname 'prepag611dsmty10' and port '17502'
 - Line 20: Duplicate hostname 'activacionesvxmlmty' and port '15125'
 - Line 212: Duplicate hostname 'unefonvxmldsmty10' and port '17511'
  File "concurrent\futures\process.py", line 832, in map
 - Line 200: Duplicate hostname 'hbvxmldsmty14' and port '17504'
 - Line 228: Duplicate hostname 'prepag611dsmty11' and port '17502'
 - Line 22: Duplicate hostname 'renovacionpiasvxmlmty' and port '15120'
 - Line 214: Duplicate hostname 'unefonvxmldsmty11' and port '17511'
  File "concurrent\futures\_base.py", line 600, in map
 - Line 202: Duplicate hostname 'hbvxmldsmty15' and port '17504'
 - Line 230: Duplicate hostname 'prepag611dsmty12' and port '17502'
 - Line 24: Duplicate hostname 'regtarjetasvxmlmty' and port '15100'
 - Line 216: Duplicate hostname 'unefonvxmldsmty12' and port '17511'
  File "concurrent\futures\process.py", line 803, in submit
 - Line 204: Duplicate hostname 'unefonvxmldsmty06' and port '17511'
 - Line 232: Duplicate hostname 'prepag611dsmty13' and port '17505'
 - Line 26: Duplicate hostname 'hardblockvxmlmty' and port '15110'
 - Line 218: Duplicate hostname 'prepag611dsmty06' and port '17502'
  File "concurrent\futures\process.py", line 762, in _adjust_process_count
 - Line 206: Duplicate hostname 'unefonvxmldsmty07' and port '17511'
 - Line 234: Duplicate hostname 'prepag611dsmty14' and port '17505'
 - Line 28: Duplicate hostname 'unefonvxmlmty' and port '15020'
 - Line 220: Duplicate hostname 'prepag611dsmty07' and port '17502'
  File "concurrent\futures\process.py", line 780, in _spawn_process
 - Line 208: Duplicate hostname 'unefonvxmldsmty08' and port '17511'
 - Line 236: Duplicate hostname 'prepag611dsmty15' and port '17505'
 - Line 238: Duplicate hostname 'saldovxmldsmty13' and port '17501'
 - Line 222: Duplicate hostname 'prepag611dsmty08' and port '17502'
  File "multiprocessing\process.py", line 121, in start
 - Line 210: Duplicate hostname 'unefonvxmldsmty09' and port '17511'
 - Line 30: Duplicate hostname 'prepagovxmlmty' and port '15050'
 - Line 240: Duplicate hostname 'saldovxmldsmty14' and port '17501'
 - Line 224: Duplicate hostname 'prepag611dsmty09' and port '17502'
  File "multiprocessing\context.py", line 337, in _Popen
 - Line 212: Duplicate hostname 'unefonvxmldsmty10' and port '17511'
 - Line 32: Duplicate hostname 'pucvxmlmty' and port '11010'
 - Line 242: Duplicate hostname 'saldovxmldsmty15' and port '17501'
 - Line 226: Duplicate hostname 'prepag611dsmty10' and port '17502'
  File "multiprocessing\popen_spawn_win32.py", line 47, in __init__
 - Line 214: Duplicate hostname 'unefonvxmldsmty11' and port '17511'
 - Line 34: Duplicate hostname 'saldovxmlmty' and port '11090'
 - Line 244: Duplicate hostname 'saldovxml502dsmty13' and port '17502'
 - Line 228: Duplicate hostname 'prepag611dsmty11' and port '17502'
  File "multiprocessing\spawn.py", line 164, in get_preparation_data
 - Line 216: Duplicate hostname 'unefonvxmldsmty12' and port '17511'
 - Line 36: Duplicate hostname 'unoochovxmldsmty06' and port '17507'
 - Line 246: Duplicate hostname 'saldovxml502dsmty14' and port '17502'
 - Line 230: Duplicate hostname 'prepag611dsmty12' and port '17502'
  File "multiprocessing\spawn.py", line 140, in _check_not_importing_main
 - Line 218: Duplicate hostname 'prepag611dsmty06' and port '17502'
 - Line 38: Duplicate hostname 'unoochovxmldsmty07' and port '17507'
 - Line 248: Duplicate hostname 'saldovxml502dsmty15' and port '17502'
 - Line 232: Duplicate hostname 'prepag611dsmty13' and port '17505'
 - Line 220: Duplicate hostname 'prepag611dsmty07' and port '17502'
RuntimeError:
        An attempt has been made to start a new process before the
        current process has finished its bootstrapping phase.

        This probably means that you are not using fork to start your
        child processes and you have forgotten to use the proper idiom
        in the main module:

            if __name__ == '__main__':
                freeze_support()
                ...

        The "freeze_support()" line can be omitted if the program
        is not going to be frozen to produce an executable.

        To fix this issue, refer to the "Safe importing of main module"
        section in https://docs.python.org/3/library/multiprocessing.html

 - Line 40: Duplicate hostname 'unoochovxmldsmty08' and port '17507'
 - Line 234: Duplicate hostname 'prepag611dsmty14' and port '17505'
 - Line 236: Duplicate hostname 'prepag611dsmty15' and port '17505'
 - Line 42: Duplicate hostname 'unoochovxmldsmty09' and port '17507'
 - Line 222: Duplicate hostname 'prepag611dsmty08' and port '17502'
 - Line 238: Duplicate hostname 'saldovxmldsmty13' and port '17501'
 - Line 44: Duplicate hostname 'unoochovxmldsmty10' and port '17507'
 - Line 224: Duplicate hostname 'prepag611dsmty09' and port '17502'
 - Line 240: Duplicate hostname 'saldovxmldsmty14' and port '17501'
 - Line 46: Duplicate hostname 'unoochovxmldsmty11' and port '17507'
 - Line 226: Duplicate hostname 'prepag611dsmty10' and port '17502'
 - Line 242: Duplicate hostname 'saldovxmldsmty15' and port '17501'
 - Line 48: Duplicate hostname 'unoochovxmldsmty12' and port '17507'
 - Line 228: Duplicate hostname 'prepag611dsmty11' and port '17502'
 - Line 244: Duplicate hostname 'saldovxml502dsmty13' and port '17502'
 - Line 50: Duplicate hostname 'unefonmatvxmldsmty06' and port '17515'
 - Line 230: Duplicate hostname 'prepag611dsmty12' and port '17502'
 - Line 246: Duplicate hostname 'saldovxml502dsmty14' and port '17502'
 - Line 52: Duplicate hostname 'unefonmatvxmldsmty07' and port '17515'
 - Line 232: Duplicate hostname 'prepag611dsmty13' and port '17505'
 - Line 248: Duplicate hostname 'saldovxml502dsmty15' and port '17502'
 - Line 54: Duplicate hostname 'unefonmatvxmldsmty08' and port '17515'
 - Line 234: Duplicate hostname 'prepag611dsmty14' and port '17505'
 - Line 56: Duplicate hostname 'unefonmatvxmldsmty09' and port '17515'
 - Line 236: Duplicate hostname 'prepag611dsmty15' and port '17505'
 - Line 58: Duplicate hostname 'unefonmatvxmldsmty10' and port '17515'
 - Line 238: Duplicate hostname 'saldovxmldsmty13' and port '17501'
 - Line 60: Duplicate hostname 'unefonmatvxmldsmty11' and port '15515'
 - Line 240: Duplicate hostname 'saldovxmldsmty14' and port '17501'
 - Line 62: Duplicate hostname 'unefonmatvxmldsmty12' and port '17515'
 - Line 242: Duplicate hostname 'saldovxmldsmty15' and port '17501'
 - Line 64: Duplicate hostname 'enterprisedsmty06' and port '17506'
 - Line 244: Duplicate hostname 'saldovxml502dsmty13' and port '17502'
 - Line 66: Duplicate hostname 'enterprisedsmty07' and port '17506'
 - Line 246: Duplicate hostname 'saldovxml502dsmty14' and port '17502'
 - Line 248: Duplicate hostname 'saldovxml502dsmty15' and port '17502'
 - Line 68: Duplicate hostname 'enterprisedsmty08' and port '17506'
 - Line 70: Duplicate hostname 'enterprisedsmty09' and port '17506'
 - Line 72: Duplicate hostname 'enterprisedsmty10' and port '17506'
 - Line 74: Duplicate hostname 'enterprisedsmty11' and port '17506'
 - Line 76: Duplicate hostname 'enterprisedsmty12' and port '17506'
 - Line 78: Duplicate hostname 'hibri611dsmty06' and port '17504'
 - Line 80: Duplicate hostname 'hibri611dsmty07' and port '17504'
 - Line 82: Duplicate hostname 'hibri611dsmty08' and port '17504'
 - Line 84: Duplicate hostname 'hibri611dsmty09' and port '17504'
 - Line 86: Duplicate hostname 'hibri611dsmty10' and port '17504'
 - Line 88: Duplicate hostname 'hibri611dsmty11' and port '17504'
 - Line 90: Duplicate hostname 'hibri611dsmty12' and port '17504'
 - Line 92: Duplicate hostname 'postpag611dsmty06' and port '17501'
 - Line 94: Duplicate hostname 'postpag611dsmty07' and port '17501'
 - Line 96: Duplicate hostname 'postpag611dsmty08' and port '17501'
 - Line 98: Duplicate hostname 'postpag611dsmty09' and port '17501'
 - Line 100: Duplicate hostname 'postpag611dsmty10' and port '17501'
 - Line 102: Duplicate hostname 'postpag611dsmty11' and port '17501'
 - Line 104: Duplicate hostname 'postpag611dsmty12' and port '17501'
 - Line 106: Duplicate hostname 'prepmatvxmldsmty06' and port '17516'
 - Line 108: Duplicate hostname 'prepmatvxmldsmty07' and port '17516'
 - Line 110: Duplicate hostname 'prepmatvxmldsmty08' and port '17516'
 - Line 112: Duplicate hostname 'prepmatvxmldsmty09' and port '17516'
 - Line 114: Duplicate hostname 'prepmatvxmldsmty10' and port '17516'
 - Line 116: Duplicate hostname 'prepmatvxmldsmty11' and port '17516'
 - Line 118: Duplicate hostname 'prepmatvxmldsmty12' and port '17516'
 - Line 120: Duplicate hostname 'visualvxmldsmty06' and port '17505'
 - Line 122: Duplicate hostname 'visualvxmldsmty07' and port '17505'
 - Line 124: Duplicate hostname 'visualvxmldsmty08' and port '17505'
 - Line 126: Duplicate hostname 'visualvxmldsmty09' and port '17505'
 - Line 128: Duplicate hostname 'visualvxmldsmty10' and port '17505'
 - Line 130: Duplicate hostname 'visualvxmldsmty11' and port '17505'
 - Line 132: Duplicate hostname 'visualvxmldsmty12' and port '17505'
 - Line 134: Duplicate hostname 'visualmtxxdsmty06' and port '17517'
 - Line 136: Duplicate hostname 'visualmtxxdsmty07' and port '17517'
 - Line 138: Duplicate hostname 'visualmtxxdsmty08' and port '17517'
 - Line 140: Duplicate hostname 'visualmtxxdsmty09' and port '17517'
 - Line 142: Duplicate hostname 'visualmtxxdsmty10' and port '17517'
 - Line 144: Duplicate hostname 'visualmtxxdsmty11' and port '17517'
 - Line 146: Duplicate hostname 'visualmtxxdsmty12' and port '17517'
 - Line 148: Duplicate hostname 'ciamsvxmldsmty06' and port '17508'
 - Line 150: Duplicate hostname 'ciamsvxmldsmty07' and port '17508'
 - Line 152: Duplicate hostname 'ciamsvxmldsmty08' and port '17508'
 - Line 154: Duplicate hostname 'ciamsvxmldsmty09' and port '17508'
 - Line 156: Duplicate hostname 'ciamsvxmldsmty10' and port '17508'
 - Line 158: Duplicate hostname 'ciamsvxmldsmty11' and port '17508'
 - Line 160: Duplicate hostname 'ciamsvxmldsmty12' and port '17508'
 - Line 162: Duplicate hostname 'activavxmldsmty01' and port '17501'
 - Line 164: Duplicate hostname 'activavxmldsmty02' and port '17501'
 - Line 166: Duplicate hostname 'activavxmldsmty03' and port '17501'
 - Line 168: Duplicate hostname 'activavxmldsmty04' and port '17501'
 - Line 170: Duplicate hostname 'activavxmldsmty05' and port '17501'
 - Line 172: Duplicate hostname 'activavxml502dsmty01' and port '17502'
 - Line 174: Duplicate hostname 'activavxml502dsmty02' and port '17502'
 - Line 176: Duplicate hostname 'activavxml502dsmty03' and port '17502'
 - Line 178: Duplicate hostname 'activavxml502dsmty04' and port '17502'
 - Line 180: Duplicate hostname 'activavxml502dsmty05' and port '17502'
 - Line 182: Duplicate hostname 'renovacionpiasdsmty01' and port '17503'
 - Line 184: Duplicate hostname 'renovacionpiasdsmty02' and port '17503'
 - Line 186: Duplicate hostname 'renovacionpiasdsmty03' and port '17503'
 - Line 188: Duplicate hostname 'renovacionpiasdsmty04' and port '17503'
 - Line 190: Duplicate hostname 'renovacionpiasdsmty05' and port '17503'
 - Line 192: Duplicate hostname 'regtarjetasdsmty13' and port '17506'
 - Line 194: Duplicate hostname 'regtarjetasdsmty14' and port '17506'
 - Line 196: Duplicate hostname 'regtarjetasdsmty15' and port '17506'
 - Line 198: Duplicate hostname 'hbvxmldsmty13' and port '17504'
 - Line 200: Duplicate hostname 'hbvxmldsmty14' and port '17504'
 - Line 202: Duplicate hostname 'hbvxmldsmty15' and port '17504'
 - Line 204: Duplicate hostname 'unefonvxmldsmty06' and port '17511'
 - Line 206: Duplicate hostname 'unefonvxmldsmty07' and port '17511'
 - Line 208: Duplicate hostname 'unefonvxmldsmty08' and port '17511'
 - Line 210: Duplicate hostname 'unefonvxmldsmty09' and port '17511'
 - Line 212: Duplicate hostname 'unefonvxmldsmty10' and port '17511'
 - Line 214: Duplicate hostname 'unefonvxmldsmty11' and port '17511'
 - Line 216: Duplicate hostname 'unefonvxmldsmty12' and port '17511'
 - Line 218: Duplicate hostname 'prepag611dsmty06' and port '17502'
 - Line 220: Duplicate hostname 'prepag611dsmty07' and port '17502'
 - Line 222: Duplicate hostname 'prepag611dsmty08' and port '17502'
Traceback (most recent call last):
 - Line 224: Duplicate hostname 'prepag611dsmty09' and port '17502'
 - Line 226: Duplicate hostname 'prepag611dsmty10' and port '17502'
 - Line 228: Duplicate hostname 'prepag611dsmty11' and port '17502'
 - Line 230: Duplicate hostname 'prepag611dsmty12' and port '17502'
 - Line 232: Duplicate hostname 'prepag611dsmty13' and port '17505'
 - Line 234: Duplicate hostname 'prepag611dsmty14' and port '17505'
  File "<string>", line 1, in <module>
    from multiprocessing.spawn import spawn_main; spawn_main(parent_pid=29516, pipe_handle=548)
                                                  ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 - Line 236: Duplicate hostname 'prepag611dsmty15' and port '17505'
  File "multiprocessing\spawn.py", line 122, in spawn_main
 - Line 238: Duplicate hostname 'saldovxmldsmty13' and port '17501'
  File "multiprocessing\spawn.py", line 131, in _main
 - Line 240: Duplicate hostname 'saldovxmldsmty14' and port '17501'
  File "multiprocessing\spawn.py", line 246, in prepare
 - Line 242: Duplicate hostname 'saldovxmldsmty15' and port '17501'
 - Line 244: Duplicate hostname 'saldovxml502dsmty13' and port '17502'
  File "multiprocessing\spawn.py", line 297, in _fixup_main_from_path
 - Line 246: Duplicate hostname 'saldovxml502dsmty14' and port '17502'
  File "<frozen runpy>", line 287, in run_path
 - Line 248: Duplicate hostname 'saldovxml502dsmty15' and port '17502'
  File "<frozen runpy>", line 98, in _run_module_code
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\ankurv\github.com\anshvermahotmail\TechnimentAnalysis\TechnimentAnalysis\jq5.py", line 110, in <module>
    results = list(executor.map(lambda hp: create_pool_entry(*hp), host_port_list))
                   ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "concurrent\futures\process.py", line 832, in map
  File "concurrent\futures\_base.py", line 600, in map
  File "concurrent\futures\process.py", line 803, in submit
  File "concurrent\futures\process.py", line 762, in _adjust_process_count
  File "concurrent\futures\process.py", line 780, in _spawn_process
  File "multiprocessing\process.py", line 121, in start
  File "multiprocessing\context.py", line 337, in _Popen
  File "multiprocessing\popen_spawn_win32.py", line 47, in __init__
  File "multiprocessing\spawn.py", line 164, in get_preparation_data
  File "multiprocessing\spawn.py", line 140, in _check_not_importing_main
RuntimeError:
        An attempt has been made to start a new process before the
        current process has finished its bootstrapping phase.

        This probably means that you are not using fork to start your
        child processes and you have forgotten to use the proper idiom
        in the main module:

            if __name__ == '__main__':
                freeze_support()
                ...

        The "freeze_support()" line can be omitted if the program
        is not going to be frozen to produce an executable.

        To fix this issue, refer to the "Safe importing of main module"
        section in https://docs.python.org/3/library/multiprocessing.html

Traceback (most recent call last):
  File "<string>", line 1, in <module>
    from multiprocessing.spawn import spawn_main; spawn_main(parent_pid=29516, pipe_handle=544)
                                                  ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "multiprocessing\spawn.py", line 122, in spawn_main
  File "multiprocessing\spawn.py", line 131, in _main
  File "multiprocessing\spawn.py", line 246, in prepare
  File "multiprocessing\spawn.py", line 297, in _fixup_main_from_path
  File "<frozen runpy>", line 287, in run_path
Traceback (most recent call last):
  File "<frozen runpy>", line 98, in _run_module_code
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\ankurv\github.com\anshvermahotmail\TechnimentAnalysis\TechnimentAnalysis\jq5.py", line 110, in <module>
    results = list(executor.map(lambda hp: create_pool_entry(*hp), host_port_list))
                   ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "concurrent\futures\process.py", line 832, in map
  File "concurrent\futures\_base.py", line 600, in map
  File "concurrent\futures\process.py", line 803, in submit
  File "<string>", line 1, in <module>
    from multiprocessing.spawn import spawn_main; spawn_main(parent_pid=29516, pipe_handle=400)
                                                  ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "concurrent\futures\process.py", line 762, in _adjust_process_count
  File "multiprocessing\spawn.py", line 122, in spawn_main
  File "concurrent\futures\process.py", line 780, in _spawn_process
  File "multiprocessing\spawn.py", line 131, in _main
  File "multiprocessing\process.py", line 121, in start
  File "multiprocessing\spawn.py", line 246, in prepare
  File "multiprocessing\context.py", line 337, in _Popen
  File "multiprocessing\spawn.py", line 297, in _fixup_main_from_path
  File "multiprocessing\popen_spawn_win32.py", line 47, in __init__
  File "multiprocessing\spawn.py", line 164, in get_preparation_data
  File "<frozen runpy>", line 287, in run_path
  File "multiprocessing\spawn.py", line 140, in _check_not_importing_main
  File "<frozen runpy>", line 98, in _run_module_code
  File "<frozen runpy>", line 88, in _run_code
RuntimeError:
        An attempt has been made to start a new process before the
        current process has finished its bootstrapping phase.

        This probably means that you are not using fork to start your
        child processes and you have forgotten to use the proper idiom
        in the main module:

            if __name__ == '__main__':
                freeze_support()
                ...

        The "freeze_support()" line can be omitted if the program
        is not going to be frozen to produce an executable.

        To fix this issue, refer to the "Safe importing of main module"
        section in https://docs.python.org/3/library/multiprocessing.html

  File "C:\Users\ankurv\github.com\anshvermahotmail\TechnimentAnalysis\TechnimentAnalysis\jq5.py", line 110, in <module>
    results = list(executor.map(lambda hp: create_pool_entry(*hp), host_port_list))
                   ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "concurrent\futures\process.py", line 832, in map
  File "concurrent\futures\_base.py", line 600, in map
  File "concurrent\futures\process.py", line 803, in submit
  File "concurrent\futures\process.py", line 762, in _adjust_process_count
  File "concurrent\futures\process.py", line 780, in _spawn_process
  File "multiprocessing\process.py", line 121, in start
  File "multiprocessing\context.py", line 337, in _Popen
  File "multiprocessing\popen_spawn_win32.py", line 47, in __init__
  File "multiprocessing\spawn.py", line 164, in get_preparation_data
  File "multiprocessing\spawn.py", line 140, in _check_not_importing_main
RuntimeError:
        An attempt has been made to start a new process before the
        current process has finished its bootstrapping phase.

        This probably means that you are not using fork to start your
        child processes and you have forgotten to use the proper idiom
        in the main module:

            if __name__ == '__main__':
                freeze_support()
                ...

        The "freeze_support()" line can be omitted if the program
        is not going to be frozen to produce an executable.

        To fix this issue, refer to the "Safe importing of main module"
        section in https://docs.python.org/3/library/multiprocessing.html

Traceback (most recent call last):
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    from multiprocessing.spawn import spawn_main; spawn_main(parent_pid=29516, pipe_handle=608)
                                                  ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "multiprocessing\spawn.py", line 122, in spawn_main
  File "multiprocessing\spawn.py", line 131, in _main
  File "multiprocessing\spawn.py", line 246, in prepare
  File "multiprocessing\spawn.py", line 297, in _fixup_main_from_path
  File "<frozen runpy>", line 287, in run_path
  File "<frozen runpy>", line 98, in _run_module_code
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\ankurv\github.com\anshvermahotmail\TechnimentAnalysis\TechnimentAnalysis\jq5.py", line 110, in <module>
    results = list(executor.map(lambda hp: create_pool_entry(*hp), host_port_list))
                   ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "concurrent\futures\process.py", line 832, in map
  File "concurrent\futures\_base.py", line 600, in map
  File "concurrent\futures\process.py", line 803, in submit
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    from multiprocessing.spawn import spawn_main; spawn_main(parent_pid=29516, pipe_handle=604)
                                                  ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "concurrent\futures\process.py", line 762, in _adjust_process_count
  File "multiprocessing\spawn.py", line 122, in spawn_main
  File "concurrent\futures\process.py", line 780, in _spawn_process
  File "multiprocessing\spawn.py", line 131, in _main
  File "multiprocessing\process.py", line 121, in start
  File "multiprocessing\spawn.py", line 246, in prepare
  File "multiprocessing\context.py", line 337, in _Popen
  File "multiprocessing\popen_spawn_win32.py", line 47, in __init__
  File "multiprocessing\spawn.py", line 297, in _fixup_main_from_path
  File "<string>", line 1, in <module>
    from multiprocessing.spawn import spawn_main; spawn_main(parent_pid=29516, pipe_handle=580)
                                                  ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "multiprocessing\spawn.py", line 164, in get_preparation_data
  File "<frozen runpy>", line 287, in run_path
  File "multiprocessing\spawn.py", line 122, in spawn_main
  File "multiprocessing\spawn.py", line 140, in _check_not_importing_main
  File "<frozen runpy>", line 98, in _run_module_code
  File "multiprocessing\spawn.py", line 131, in _main
RuntimeError:
        An attempt has been made to start a new process before the
        current process has finished its bootstrapping phase.

        This probably means that you are not using fork to start your
        child processes and you have forgotten to use the proper idiom
        in the main module:

            if __name__ == '__main__':
                freeze_support()
                ...

        The "freeze_support()" line can be omitted if the program
        is not going to be frozen to produce an executable.

        To fix this issue, refer to the "Safe importing of main module"
        section in https://docs.python.org/3/library/multiprocessing.html

  File "<frozen runpy>", line 88, in _run_code
  File "multiprocessing\spawn.py", line 246, in prepare
  File "C:\Users\ankurv\github.com\anshvermahotmail\TechnimentAnalysis\TechnimentAnalysis\jq5.py", line 110, in <module>
    results = list(executor.map(lambda hp: create_pool_entry(*hp), host_port_list))
                   ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "multiprocessing\spawn.py", line 297, in _fixup_main_from_path
  File "concurrent\futures\process.py", line 832, in map
  File "<frozen runpy>", line 287, in run_path
  File "concurrent\futures\_base.py", line 600, in map
  File "concurrent\futures\process.py", line 803, in submit
  File "<frozen runpy>", line 98, in _run_module_code
  File "concurrent\futures\process.py", line 762, in _adjust_process_count
  File "<frozen runpy>", line 88, in _run_code
  File "concurrent\futures\process.py", line 780, in _spawn_process
  File "C:\Users\ankurv\github.com\anshvermahotmail\TechnimentAnalysis\TechnimentAnalysis\jq5.py", line 110, in <module>
    results = list(executor.map(lambda hp: create_pool_entry(*hp), host_port_list))
                   ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "concurrent\futures\process.py", line 832, in map
  File "multiprocessing\process.py", line 121, in start
  File "concurrent\futures\_base.py", line 600, in map
  File "multiprocessing\context.py", line 337, in _Popen
  File "concurrent\futures\process.py", line 803, in submit
  File "multiprocessing\popen_spawn_win32.py", line 47, in __init__
  File "concurrent\futures\process.py", line 762, in _adjust_process_count
  File "multiprocessing\spawn.py", line 164, in get_preparation_data
  File "concurrent\futures\process.py", line 780, in _spawn_process
  File "multiprocessing\spawn.py", line 140, in _check_not_importing_main
  File "multiprocessing\process.py", line 121, in start
  File "multiprocessing\context.py", line 337, in _Popen
RuntimeError:
        An attempt has been made to start a new process before the
        current process has finished its bootstrapping phase.

        This probably means that you are not using fork to start your
        child processes and you have forgotten to use the proper idiom
        in the main module:

            if __name__ == '__main__':
                freeze_support()
                ...

        The "freeze_support()" line can be omitted if the program
        is not going to be frozen to produce an executable.

        To fix this issue, refer to the "Safe importing of main module"
        section in https://docs.python.org/3/library/multiprocessing.html

  File "multiprocessing\popen_spawn_win32.py", line 47, in __init__
  File "multiprocessing\spawn.py", line 164, in get_preparation_data
  File "multiprocessing\spawn.py", line 140, in _check_not_importing_main
RuntimeError:
        An attempt has been made to start a new process before the
        current process has finished its bootstrapping phase.

        This probably means that you are not using fork to start your
        child processes and you have forgotten to use the proper idiom
        in the main module:

            if __name__ == '__main__':
                freeze_support()
                ...

        The "freeze_support()" line can be omitted if the program
        is not going to be frozen to produce an executable.

        To fix this issue, refer to the "Safe importing of main module"
        section in https://docs.python.org/3/library/multiprocessing.html

Traceback (most recent call last):
  File "<string>", line 1, in <module>
    from multiprocessing.spawn import spawn_main; spawn_main(parent_pid=29516, pipe_handle=628)
                                                  ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "multiprocessing\spawn.py", line 122, in spawn_main
  File "multiprocessing\spawn.py", line 131, in _main
  File "multiprocessing\spawn.py", line 246, in prepare
  File "multiprocessing\spawn.py", line 297, in _fixup_main_from_path
  File "<frozen runpy>", line 287, in run_path
  File "<frozen runpy>", line 98, in _run_module_code
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\ankurv\github.com\anshvermahotmail\TechnimentAnalysis\TechnimentAnalysis\jq5.py", line 110, in <module>
    results = list(executor.map(lambda hp: create_pool_entry(*hp), host_port_list))
                   ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "concurrent\futures\process.py", line 832, in map
  File "concurrent\futures\_base.py", line 600, in map
  File "concurrent\futures\process.py", line 803, in submit
  File "concurrent\futures\process.py", line 762, in _adjust_process_count
  File "concurrent\futures\process.py", line 780, in _spawn_process
  File "multiprocessing\process.py", line 121, in start
  File "multiprocessing\context.py", line 337, in _Popen
  File "multiprocessing\popen_spawn_win32.py", line 47, in __init__
  File "multiprocessing\spawn.py", line 164, in get_preparation_data
  File "multiprocessing\spawn.py", line 140, in _check_not_importing_main
RuntimeError:
        An attempt has been made to start a new process before the
        current process has finished its bootstrapping phase.

        This probably means that you are not using fork to start your
        child processes and you have forgotten to use the proper idiom
        in the main module:

            if __name__ == '__main__':
                freeze_support()
                ...

        The "freeze_support()" line can be omitted if the program
        is not going to be frozen to produce an executable.

        To fix this issue, refer to the "Safe importing of main module"
        section in https://docs.python.org/3/library/multiprocessing.html

concurrent.futures.process._RemoteTraceback:
"""
AttributeError: module '__main__' has no attribute '<lambda>'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "multiprocessing\queues.py", line 262, in _feed
  File "multiprocessing\reduction.py", line 51, in dumps
_pickle.PicklingError: Can't pickle <function <lambda> at 0x000001F041CF7530>: it's not found as __main__.<lambda>
when serializing tuple item 0
when serializing tuple item 1
when serializing functools.partial reconstructor arguments
when serializing functools.partial object
when serializing dict item 'fn'
when serializing concurrent.futures.process._CallItem state
when serializing concurrent.futures.process._CallItem object
"""

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\ankurv\github.com\anshvermahotmail\TechnimentAnalysis\TechnimentAnalysis\jq5.py", line 110, in <module>
    results = list(executor.map(lambda hp: create_pool_entry(*hp), host_port_list))
  File "concurrent\futures\process.py", line 617, in _chain_from_iterable_of_lists
  File "concurrent\futures\_base.py", line 611, in result_iterator
  File "concurrent\futures\_base.py", line 309, in _result_or_cancel
  File "concurrent\futures\_base.py", line 441, in result
  File "concurrent\futures\_base.py", line 393, in __get_result
  File "multiprocessing\queues.py", line 262, in _feed
  File "multiprocessing\reduction.py", line 51, in dumps
_pickle.PicklingError: Can't pickle <function <lambda> at 0x000001F041CF7530>: it's not found as __main__.<lambda>
when serializing tuple item 0
when serializing tuple item 1
when serializing functools.partial reconstructor arguments
when serializing functools.partial object
when serializing dict item 'fn'
when serializing concurrent.futures.process._CallItem state
when serializing concurrent.futures.process._CallItem object