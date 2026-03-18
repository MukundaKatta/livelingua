"""Basic usage example for livelingua."""
from src.core import Livelingua

def main():
    instance = Livelingua(config={"verbose": True})

    print("=== livelingua Example ===\n")

    # Run primary operation
    result = instance.process(input="example data", mode="demo")
    print(f"Result: {result}")

    # Run multiple operations
    ops = ["process", "analyze", "transform]
    for op in ops:
        r = getattr(instance, op)(source="example")
        print(f"  {op}: {"✓" if r.get("ok") else "✗"}")

    # Check stats
    print(f"\nStats: {instance.get_stats()}")

if __name__ == "__main__":
    main()
