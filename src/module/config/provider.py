import yaml
from pathlib import Path

class ConfigProvider:
    def __init__(self, config_path: Path = None):
        default_path = Path(__file__).parent.parent.parent.parent/ "resource" / "config" / "settings.yaml"
        self.config_path = config_path or default_path.resolve()
        print(f"[ConfigLoader] Using config file: {self.config_path}")

        self.config = self._load()

    def _load(self):
        if not self.config_path.exists():
            print(f"[ConfigLoader] ❌ File does not exist at: {self.config_path}")
            return None
        try:
            with open(self.config_path, "r") as f:
                raw = f.read()
                data = yaml.safe_load(raw)
                return data
        except Exception as e:
            print(f"[ConfigLoader] ❌ Failed to load YAML: {e}")
            return None

    def get(self, dotted_key: str, default=None):
        if not self.config:
            return default

        keys = dotted_key.split(".")
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
        return value if value is not None else default


    def all(self):
        return self.config

    def set(self, dotted_key: str, value):
        if not self.config:
            return
        keys = dotted_key.split(".")
        cfg = self.config
        for k in keys[:-1]:
            cfg = cfg.setdefault(k, {})
        cfg[keys[-1]] = value

        with open(self.config_path, "w") as f:
            yaml.safe_dump(self.config, f)