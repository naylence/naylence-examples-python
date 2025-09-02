#!/usr/bin/env python3
import secrets, string, json, shutil, pathlib, sys

# Determine the root directory based on where the script is called from
# If called from a subdirectory, use the security directory as root
# If called directly, use the parent directory of the script
if len(sys.argv) > 1 and sys.argv[1] == "--from-subdir":
    # Called from a subdirectory (e.g., gated/), use current working directory for templates and output
    ROOT = pathlib.Path(__file__).resolve().parents[1]  # security directory
    TEMPLATE_DIR = pathlib.Path.cwd()  # current working directory (e.g., gated/)
    OUTPUT_DIR = pathlib.Path.cwd()  # output to current directory
    print(f"📁 Running from subdirectory, using security directory as root: {ROOT}")
    print(f"📁 Looking for templates in: {TEMPLATE_DIR}")
    print(f"📁 Generating files in: {OUTPUT_DIR}")
else:
    # Default behavior - use security directory as root
    ROOT = pathlib.Path(__file__).resolve().parents[1]
    TEMPLATE_DIR = ROOT
    OUTPUT_DIR = ROOT
    print(f"📁 Using security directory as root: {ROOT}")

SECRETS_DIR = ROOT / ".secrets"
SECRETS_DIR.mkdir(exist_ok=True)
print(f"📂 Secrets directory: {SECRETS_DIR}")

def rand_id(prefix):
    alphabet = string.ascii_lowercase + string.digits
    return f"{prefix}-{''.join(secrets.choice(alphabet) for _ in range(12))}"

def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# 1) Generate dev OAuth clients (agent + client)
client_id = rand_id("client")
client_secret = rand_id("s")

# Optional: if your dev OAuth server reads a JSON file for clients:
# (adapt to your server’s expected format)
dev_clients = {
    "clients": [
        {"client_id": client_id, "client_secret": client_secret, "audience": "fame.fabric"},
    ]
}
write_file(SECRETS_DIR / "oauth2-clients.json", json.dumps(dev_clients, indent=2))

# 2) Check for PKI files and prepare PKI variables
pki_dir = OUTPUT_DIR / "pki"
pki_mapping = {}
if pki_dir.exists():
    pki_mapping["PKI_ROOT_CA_CERT"] = str((pki_dir / "root-ca.crt").absolute())
    pki_mapping["PKI_ROOT_CA_KEY"] = str((pki_dir / "root-ca.key").absolute())
    pki_mapping["PKI_INTERMEDIATE_CA_CERT"] = str((pki_dir / "intermediate-ca.crt").absolute())
    pki_mapping["PKI_INTERMEDIATE_CA_KEY"] = str((pki_dir / "intermediate-ca.key").absolute())
    pki_mapping["PKI_INTERMEDIATE_CHAIN"] = str((pki_dir / "intermediate-chain.crt").absolute())
    pki_mapping["PKI_COMPLETE_CHAIN"] = str((pki_dir / "complete-chain.crt").absolute())
    print(f"📋 Found PKI directory: {pki_dir}")
else:
    print(f"⚠️  No PKI directory found at {pki_dir}, PKI variables will be empty")

# 3) Materialize .env files from the .example templates
def expand_template(example_name, out_name, mapping):
    src = TEMPLATE_DIR / example_name
    dst = OUTPUT_DIR / out_name
    
    if not src.exists():
        print(f"⚠️  Warning: Template file {src} not found, skipping {out_name}")
        return
        
    text = src.read_text(encoding="utf-8")
    for k, v in mapping.items():
        text = text.replace("${" + k + "}", v)
    write_file(dst, text)
    print(f"✅ Generated {out_name}")

expand_template(".env.client.example", ".env.client", {
    "DEV_CLIENT_ID": client_id,
    "DEV_CLIENT_SECRET": client_secret,
    **pki_mapping,
})
expand_template(".env.agent.example", ".env.agent", {
    "DEV_CLIENT_ID": client_id,
    "DEV_CLIENT_SECRET": client_secret,
    **pki_mapping,
})
expand_template(".env.oauth2-server.example", ".env.oauth2-server", {
    "DEV_CLIENT_ID": client_id,
    "DEV_CLIENT_SECRET": client_secret,
    **pki_mapping,
})
expand_template(".env.ca.example", ".env.ca", {
    **pki_mapping,
})
expand_template(".env.welcome.example", ".env.welcome", {
    **pki_mapping,
})
# sentinel has no secrets to inject; just copy template if not present
dst = OUTPUT_DIR / ".env.sentinel"
if not dst.exists():
    template_src = TEMPLATE_DIR / ".env.sentinel.example"
    if template_src.exists():
        shutil.copyfile(template_src, dst)
        print(f"✅ Generated .env.sentinel")
    else:
        print(f"⚠️  Warning: Template file {template_src} not found, skipping .env.sentinel")

print("✔ Generated dev credentials and .env files:")
print(f"  - .env.client (client_id={client_id})")
print(f"  - .env.agent  (client_id={client_id})")
print(f"  - .env.sentinel")
print(f"  - .secrets/oauth2-clients.json")
