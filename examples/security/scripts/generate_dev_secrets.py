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

# 3) Discover and materialize .env files from .example templates
def expand_template(src_path, dst_path, mapping):
    """Expand a template file by replacing variables with values."""
    if not src_path.exists():
        print(f"⚠️  Warning: Template file {src_path} not found, skipping {dst_path.name}")
        return False
        
    text = src_path.read_text(encoding="utf-8")
    for k, v in mapping.items():
        text = text.replace("${" + k + "}", v)
    write_file(dst_path, text)
    print(f"✅ Generated {dst_path.relative_to(OUTPUT_DIR)}")
    return True

def discover_and_process_env_templates():
    """Discover all .env.*.example files recursively and process them."""
    # Find all .env.*.example files recursively in TEMPLATE_DIR
    env_example_files = list(TEMPLATE_DIR.rglob(".env.*.example"))
    
    if not env_example_files:
        print(f"⚠️  No .env.*.example files found in {TEMPLATE_DIR}")
        return []
    
    print(f"🔍 Found {len(env_example_files)} .env.*.example files:")
    
    generated_files = []
    
    for template_file in sorted(env_example_files):
        # Calculate relative path from TEMPLATE_DIR to maintain directory structure
        rel_path = template_file.relative_to(TEMPLATE_DIR)
        
        # Generate output filename by removing .example suffix
        output_filename = template_file.name.replace(".example", "")
        output_path = OUTPUT_DIR / rel_path.parent / output_filename
        
        print(f"  📄 {rel_path} -> {output_path.relative_to(OUTPUT_DIR)}")
        
        # Determine which variables to use based on the filename
        mapping = {}
        
        # Files that need OAuth credentials
        if any(x in template_file.name for x in [".client.", ".agent.", ".sentinel.", ".oauth2-server."]):
            mapping.update({
                "DEV_CLIENT_ID": client_id,
                "DEV_CLIENT_SECRET": client_secret,
            })
        
        # All files get PKI mapping if available
        mapping.update(pki_mapping)
        
        # Process the template
        if expand_template(template_file, output_path, mapping):
            generated_files.append(output_path.relative_to(OUTPUT_DIR))
    
    return generated_files

# Process all discovered templates
generated_files = discover_and_process_env_templates()

print("✔ Generated dev credentials and files:")
print(f"  - .secrets/oauth2-clients.json")
if generated_files:
    for file_path in generated_files:
        # Show client_id for files that use OAuth credentials
        if any(x in str(file_path) for x in [".client", ".agent", ".sentinel", ".oauth2-server"]):
            print(f"  - {file_path} (client_id={client_id})")
        else:
            print(f"  - {file_path}")
else:
    print("  - No .env files generated (no templates found)")
