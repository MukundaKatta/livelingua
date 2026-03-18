"""CLI for livelingua."""
import sys, json, argparse
from .core import Livelingua

def main():
    parser = argparse.ArgumentParser(description="LiveLingua — AI Meeting Translator. Real-time multilingual meeting translation and transcription.")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = Livelingua()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.process(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"livelingua v0.1.0 — LiveLingua — AI Meeting Translator. Real-time multilingual meeting translation and transcription.")

if __name__ == "__main__":
    main()
