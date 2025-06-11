import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "wotson_config.yaml"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def validate_config(config):
    """Validates that the essential configuration keys are present."""
    REQUIRED_KEYS = {
        "agent": ["id", "base_url", "docs_url", "poll_interval", "urgency_threshold"],
        "paths": ["data_root", "logs"],
        "whatsapp": ["webhook_port", "session_file"],
        "services": ["whatsapp_mcp_server", "analysis_mcp_server"],
        "tech_manager_id": None,
        "admin_ids": None,
    }

    for key, sub_keys in REQUIRED_KEYS.items():
        if key not in config:
            raise ValueError(f"Missing required configuration section: '{key}'")
        if sub_keys:
            for sub_key in sub_keys:
                if sub_key not in config[key]:
                    raise ValueError(f"Missing required configuration key: '{sub_key}' in section '{key}'")

CONFIG = load_config()
validate_config(CONFIG) 