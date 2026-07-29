import machine
import utime

class LidarScanner:
    def __init__(self, servo_pin=15, uart_id=0, tx_pin=0, rx_pin=1, baudrate=115200):
        self.pwm = machine.PWM(machine.Pin(servo_pin))
        self.pwm.freq(50)

        self.uart = machine.UART(
            uart_id,
            baudrate=baudrate,
            tx=machine.Pin(tx_pin),
            rx=machine.Pin(rx_pin)
        )
        self.set_angle(0)

    def set_angle(self, degrees):
        degrees = max(0, min(180, degrees))
        duty = int(1638 + (degrees / 180.0) * 6554)
        self.pwm.duty_u16(duty)

    def get_distance(self):
        if self.uart.any() >= 9:
            if self.uart.read(1) == b'\x59':
                if self.uart.read(1) == b'\x59':
                    payload = self.uart.read(7)
                    if payload and len(payload) == 7:
                        return payload[0] + (payload[1] << 8)
        return None

    def scan_sweep(self, start=0, stop=180, step=2, step_delay_ms=30):
        direction = 1 if start < stop else -1
        for angle in range(start, stop + direction, step * direction):
            self.set_angle(angle)
            utime.sleep_ms(step_delay_ms)

            reading = self.get_distance()
            if reading is not None:
                print(f"{angle},{reading}")

    def run_continuous(self):
        while True:
            self.scan_sweep(0, 180, 2)
            self.scan_sweep(180, 0, 2)

if __name__ == "__main__":
    scanner = LidarScanner()
    scanner.run_continuous()
