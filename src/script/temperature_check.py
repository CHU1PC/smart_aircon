import argparse
import sys
import time
from pathlib import Path

from loguru import logger

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from temperature import DHT11, DHT11Error  # noqa: E402

TEMP_MIN, TEMP_MAX = 0.0, 50.0
HUMIDITY_MIN, HUMIDITY_MAX = 20.0, 90.0


def check(pin: int, count: int, interval: float) -> bool:
    """Reads the DHT11 ``count`` times and reports whether it is working.

    A run passes when at least 60% of reads succeed and return values within
    the DHT11 datasheet ranges (temperature 0-50°C, humidity 20-90%).
    """
    sensor = DHT11(pin)
    ok = 0

    for i in range(1, count + 1):
        try:
            humidity, temperature = sensor.read_data()
        except DHT11Error as e:
            logger.error(f"[{i}/{count}] read failed: {e}")
            time.sleep(interval)
            continue

        in_range = TEMP_MIN <= temperature <= TEMP_MAX and HUMIDITY_MIN <= humidity <= HUMIDITY_MAX
        if in_range:
            ok += 1
            logger.success(f"[{i}/{count}] temperature: {temperature}°C  humidity: {humidity}%")
        else:
            logger.warning(
                f"[{i}/{count}] out of range — temperature: {temperature}°C  humidity: {humidity}%"
            )
        time.sleep(interval)

    rate = ok / count
    passed = rate >= 0.6
    logger.info(f"result: {ok}/{count} valid reads ({rate:.0%}) -> {'PASS' if passed else 'FAIL'}")
    return passed


def main() -> None:
    """Parses arguments and runs the DHT11 diagnostic."""
    parser = argparse.ArgumentParser(description="Check whether a DHT11 sensor is working.")
    parser.add_argument("--pin", type=int, default=14, help="GPIO pin (BCM) the DHT11 data line is on")
    parser.add_argument("--count", type=int, default=5, help="number of reads to attempt")
    parser.add_argument("--interval", type=float, default=2.0, help="seconds between reads")
    args = parser.parse_args()

    passed = check(args.pin, args.count, args.interval)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
