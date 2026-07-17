DEFAULT_SERVICE_UUID = "e7810a71-73ae-499d-8c15-faa9aef0c3f2"

import asyncio
import time
from queue import Queue, Empty

from bleak import BleakClient, BleakScanner

DEFAULT_CHAR_UUID = "bef8d6c9-9c21-4c9e-b632-bd58c1009f9f"


def find_niimbot_b1(timeout_s: float = 5.0, debug: bool = False) -> str | None:
    """
    Scans nearby BLE devices and returns the address of the first likely NIIMBOT B1 printer.
    Pairing is usually not required for this BLE/GATT workflow.
    """

    async def _scan():
        devices = await BleakScanner.discover(timeout=timeout_s)

        candidates = []

        for device in devices:
            address = device.address
            name = device.name or ""

            name_lower = name.lower()

            name_match = "niimbot" in name_lower or "b1" in name_lower

            # Bazı platformlarda advertisement içindeki service uuid'ler
            # her zaman gelmeyebilir. Bu yüzden name_match yeterli.
            service_match = False

            metadata = getattr(device, "metadata", {}) or {}
            uuids = metadata.get("uuids", []) or []

            for uuid in uuids:
                if str(uuid).lower() == DEFAULT_SERVICE_UUID.lower():
                    service_match = True
                    break

            if debug:
                print("BLE:", address, name, uuids)

            if service_match or name_match:
                candidates.append((address, name, service_match, name_match))

        if debug:
            print("NIIMBOT candidates:", candidates)

        if not candidates:
            return None

        # Service UUID match daha güçlü; sonra isim eşleşmesi.
        candidates.sort(key=lambda x: (not x[2], not x[3], x[1]))
        return candidates[0][0]

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_scan())
    finally:
        loop.close()


class BleTransport:
    def __init__(
        self,
        address: str,
        char_uuid: str = DEFAULT_CHAR_UUID,
        debug: bool = False,
    ):
        self.address = address
        self.char_uuid = char_uuid
        self.debug = debug

        self.client: BleakClient | None = None
        self.rx_queue: Queue[bytes] = Queue()

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def connect(self):
        self.loop.run_until_complete(self._connect())

    async def _connect(self):
        self.client = BleakClient(self.address)
        await self.client.connect()

        if self.debug:
            print("Connected:", self.client.is_connected)
            print("\nServices / Characteristics:")
            for service in self.client.services:
                print(service.uuid)
                for char in service.characteristics:
                    print("  ", char.uuid, char.properties)

        await self.client.start_notify(self.char_uuid, self._notification_handler)

        if self.debug:
            print("\nNotify started on:", self.char_uuid)

    def disconnect(self):
        if self.client and self.client.is_connected:
            try:
                self.loop.run_until_complete(self.client.stop_notify(self.char_uuid))
            except Exception as e:
                if self.debug:
                    print("stop_notify error:", e)

            self.loop.run_until_complete(self.client.disconnect())

    def is_connected(self) -> bool:
        return bool(self.client and self.client.is_connected)

    def _notification_handler(self, sender, data: bytearray):
        data = bytes(data)

        if self.debug:
            print("NOTIFY:", self.hex_dump(data))

        self.rx_queue.put(data)

    def write(self, data: bytes, delay_s: float = 0.0):
        if not self.client or not self.client.is_connected:
            raise RuntimeError("BLE client is not connected")

        if self.debug:
            print("WRITE :", self.hex_dump(data))

        self.loop.run_until_complete(
            self.client.write_gatt_char(self.char_uuid, data, response=False)
        )

        if delay_s > 0:
            self.loop.run_until_complete(asyncio.sleep(delay_s))

    def read(self, timeout_s: float = 2.0) -> bytes:
        deadline = time.time() + timeout_s

        while time.time() < deadline:
            try:
                data = self.rx_queue.get_nowait()

                if self.debug:
                    print("READ  :", self.hex_dump(data))

                return data

            except Empty:
                self.loop.run_until_complete(asyncio.sleep(0.02))

        if self.debug:
            print("READ  : timeout")

        return b""

    @staticmethod
    def hex_dump(data: bytes) -> str:
        return " ".join(f"{b:02X}" for b in data)
