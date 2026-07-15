import time

from gpiozero import InputDevice, OutputDevice
from loguru import logger


class DHT11Error(Exception):
    """Raised when a DHT11 reading fails."""


class DHT11:
    """A class to interface with the DHT11 temperature and humidity sensor."""
    MAX_DELAY_COUNT = 100
    MAX_WAIT_COUNT = 100000
    BIT_1_DELAY_COUNT = 10
    BITS_LEN = 40

    def __init__(self, pin: int, *, pull_up: bool = False) -> None:
        """Initializes the DHT11 sensor."""
        self._pin = pin
        self._pull_up = pull_up

    def read_data(self, *, retries: int = 3, retry_interval: float = 2.0) -> tuple[float, float]:
        """Reads temperature and humidity data from the DHT11 sensor.

        Returns:
            tuple[float, float]: A tuple containing humidity and temperature values.

        Raises:
            DHT11Error: If no valid reading could be obtained within ``retries``.
        """
        last_error: DHT11Error | None = None
        for _ in range(retries):
            try:
                return self._read_once()
            except DHT11Error as e:
                last_error = e
                time.sleep(retry_interval)
        msg = f"failed to read after {retries} attempts"
        raise DHT11Error(msg) from last_error

    def _read_once(self) -> tuple[float, float]:
        bits = ""

        # -------------- send start --------------
        gpio = OutputDevice(self._pin)
        gpio.off()
        time.sleep(0.02)
        gpio.close()

        gpio = InputDevice(self._pin, pull_up=self._pull_up)
        try:
            # -------------- wait response --------------
            if not self._wait_while(gpio, 1):
                msg = "no response from sensor"
                raise DHT11Error(msg)

            # -------------- read data --------------
            for _ in range(self.BITS_LEN):
                if not self._wait_while(gpio, 0):
                    msg = "timeout waiting for bit start"
                    raise DHT11Error(msg)

                delay_count = 0
                while gpio.value == 1:
                    delay_count += 1
                    if delay_count > self.MAX_DELAY_COUNT:
                        break
                bits += "1" if delay_count > self.BIT_1_DELAY_COUNT else "0"
        finally:
            gpio.close()

        humidity_integer = int(bits[0:8], 2)
        humidity_decimal = int(bits[8:16], 2)
        temperature_integer = int(bits[16:24], 2)
        temperature_decimal = int(bits[24:32], 2)
        check_sum = int(bits[32:40], 2)

        if check_sum != humidity_integer + humidity_decimal + temperature_integer + temperature_decimal:
            msg = "checksum mismatch"
            raise DHT11Error(msg)

        humidity = humidity_integer + humidity_decimal / 10
        temperature = temperature_integer + temperature_decimal / 10
        return humidity, temperature

    def _wait_while(self, gpio: InputDevice, level: int) -> bool:
        count = 0
        while gpio.value == level:
            count += 1
            if count > self.MAX_WAIT_COUNT:
                return False
        return True


if __name__ == "__main__":
    dht11 = DHT11(14)
    while True:
        try:
            humidity, temperature = dht11.read_data()
            logger.info(f"{time.time():.3f}  temperature:{temperature}°C  humidity: {humidity}%")
        except DHT11Error as e:
            logger.warning(f"read failed: {e}")
        time.sleep(2)
