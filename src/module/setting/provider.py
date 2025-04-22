class SettingProvider:
    def __init__(self, config_provider):
        self.config_provider = config_provider

    def get_all(self) -> dict:
        """Gibt alle Einstellungen unter settings zurück."""
        return self.config_provider.get("settings", {})

    def get(self, key: str, default=None):
        """Liest eine einzelne Einstellung unter settings."""
        return self.config_provider.get(f"settings.{key}", default)

    def set(self, key: str, value):
        """Setzt eine einzelne Einstellung unter settings."""
        self.config_provider.set(f"settings.{key}", value)
