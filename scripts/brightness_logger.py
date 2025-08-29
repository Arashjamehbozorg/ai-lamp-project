import csv
from datetime import datetime
from pathlib import Path
import asyncio
from zoneinfo import ZoneInfo

from kasa import Discover, Module   # << use Discover + Module (modern API)

BULB_IP = "192.168.2.140"  # <-- your bulb IP
csv_path = Path("../logs/brightness_log.csv")
csv_path.parent.mkdir(parents=True, exist_ok=True)

# Create header if missing
if not csv_path.exists():
    with csv_path.open("w", newline="") as f:
        csv.writer(f).writerow(["local_timestamp", "brightness", "is_on"])

BERLIN = ZoneInfo("Europe/Berlin")

async def get_light_module(ip):
    """
    Discover the device at IP, connect, and return its Light module.
    Raises a clear error if no Light module is present.
    """
    dev = await Discover.discover_single(ip)
    if dev is None:
        raise RuntimeError(f"No Kasa device found at {ip}")

    # Try connecting with host parameter first
    try:
        await dev.connect(host=ip)
    except Exception as e:
        # If that fails, try without parameters (device might already be connected)
        print(f"Warning: connect(host=ip) failed ({e}), trying without parameters...")
        try:
            await dev.connect()
        except Exception as e2:
            print(f"Warning: connect() also failed ({e2}), proceeding with update...")
    
    await dev.update()      # pull latest datapoints

    # dev.modules is a dict keyed by Module enum (preferred) or strings
    modules = dev.modules

    # First, try by enum
    light = modules.get(Module.Light)
    if light is None:
        # Fallback: try by name / capability (handles version differences)
        for _, mod in modules.items():
            if getattr(mod, "name", "").lower() == "light" or hasattr(mod, "brightness"):
                light = mod
                break

    if light is None:
        raise RuntimeError(f"Device at {ip} has no Light module. Found modules: {list(modules.keys())}")

    return dev, light

async def main():
    print("Fully-async change-only brightness logger (new API). Ctrl+C to stop.")
    dev, light = await get_light_module(BULB_IP)

    last_brightness = None
    last_is_on = None

    while True:
        try:
            # Refresh state
            await dev.update()

            # Read from Light module only (avoid Energy etc.)
            brightness = getattr(light, "brightness", None)
            # Try different ways to get the on/off state
            is_on = getattr(light, "is_on", None)
            if is_on is None:
                # Fallback to state attribute
                state = getattr(light, "state", None)
                if state is not None:
                    # Extract light_on from LightState object
                    is_on = getattr(state, "light_on", None)
                    if is_on is None:
                        # Another fallback - check if brightness > 0
                        is_on = brightness is not None and brightness > 0
                else:
                    # Last fallback - check if brightness > 0
                    is_on = brightness is not None and brightness > 0

            if brightness is None:
                # Give a helpful error if API shape differs
                raise RuntimeError(
                    f"Light module missing brightness attribute. "
                    f"Available attrs: {[attr for attr in dir(light) if not attr.startswith('_')]}"
                )

            # Write only when something changed
            if brightness != last_brightness or is_on != last_is_on:
                ts = datetime.now(BERLIN).strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{ts}] brightness={brightness} is_on={is_on}")
                with csv_path.open("a", newline="") as f:
                    csv.writer(f).writerow([ts, brightness, is_on])
                last_brightness, last_is_on = brightness, is_on

        except Exception as e:
            print(f"Warning: {e}")

        await asyncio.sleep(3)  # non-blocking pause

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Stopped.")