"""Command-line entry point for ReflectAI."""
import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="ReflectAI multi-provider reflection agent")
    parser.add_argument("--version", action="store_true", help="show version and exit")
    parser.add_argument("--check-config", action="store_true", help="validate and display provider configuration")
    args = parser.parse_args()
    if args.version:
        from . import __version__
        print(f"ReflectAI {__version__}")
        return 0
    if args.check_config:
        from .config import app_settings, provider_settings
        providers = provider_settings().get("providers", {})
        if not isinstance(providers, dict) or not providers:
            parser.error("config/providers.yaml must contain a non-empty 'providers' mapping")
        print(f"Configuration OK. Enabled providers: {', '.join(k for k, v in providers.items() if isinstance(v, dict) and v.get('enabled')) or 'none'}")
        print(f"Application settings: {app_settings().get('app', {})}")
        return 0
    parser.print_help()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
