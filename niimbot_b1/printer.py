import math
import struct
import time
from PIL import Image
from .transport import BleTransport, find_niimbot_b1
from .config import get_saved_printer_address, set_saved_printer_address


class NiimbotB1Printer:
    FRAME_HEAD = 0x55
    FRAME_TAIL = 0xAA

    CMD_PRINT_START = 0x01
    CMD_PAGE_START = 0x03
    CMD_SET_PAGE_SIZE = 0x13
    CMD_SET_DENSITY = 0x21
    CMD_SET_LABEL_TYPE = 0x23
    CMD_BITMAP_ROW = 0x85
    CMD_PRINT_STATUS = 0xA3
    CMD_CONNECT = 0xC1
    CMD_PAGE_END = 0xE3
    CMD_PRINT_END = 0xF3

    RESPONSE_OFFSET_DEFAULT = 1

    LABEL_TYPE_GAP = 1

    PRINT_WIDTH_PX = 384
    ROW_BYTES = 48

    def __init__(
        self,
        address: str,
        debug: bool = False,
    ):
        self.address = address
        self.debug = debug
        self.transport = BleTransport(address, debug=debug)
        self._packet_buffer = bytearray()

    @classmethod
    def auto_connect(
        cls,
        timeout_s: float = 5.0,
        debug: bool = False,
    ):
        address = find_niimbot_b1(timeout_s=timeout_s, debug=debug)

        if address is None:
            raise RuntimeError("No NIIMBOT B1 printer found nearby")

        printer = cls(address, debug=debug)
        printer.connect()
        return printer

    @classmethod
    def connect_saved_or_auto(
        cls,
        timeout_s: float = 5.0,
        debug: bool = False,
        save_found: bool = True,
        force_scan: bool = False,
    ):
        saved_address = get_saved_printer_address()

        if saved_address and not force_scan:
            if debug:
                print("Trying saved printer address:", saved_address)

            try:
                printer = cls(saved_address, debug=debug)
                printer.connect()

                if debug:
                    print("Connected to saved printer:", saved_address)

                return printer

            except Exception as exc:
                if debug:
                    print("Saved printer connection failed:", exc)

        if debug:
            print("Scanning for NIIMBOT B1 printer...")

        address = find_niimbot_b1(timeout_s=timeout_s, debug=debug)

        if address is None:
            raise RuntimeError("No NIIMBOT B1 printer found nearby")

        if debug:
            print("Found NIIMBOT B1 printer:", address)

        printer = cls(address, debug=debug)
        printer.connect()

        if save_found:
            set_saved_printer_address(address)

            if debug:
                print("Saved printer address:", address)

        return printer

    def connect(self):
        self.transport.connect()

    def disconnect(self):
        self.transport.disconnect()

    def is_connected(self) -> bool:
        return self.transport.is_connected()

    # ------------------------------------------------------------
    # Low level packet helpers
    # ------------------------------------------------------------

    def _calc_xor(self, cmd: int, data: bytes) -> int:
        x = cmd ^ len(data)

        for b in data:
            x ^= b

        return x & 0xFF

    def _make_frame(self, cmd: int, data: bytes = b"") -> bytes:
        if len(data) > 255:
            raise ValueError("Niimbot frame data too long")

        checksum = self._calc_xor(cmd, data)

        return (
            bytes([self.FRAME_HEAD, self.FRAME_HEAD, cmd, len(data)])
            + data
            + bytes([checksum, self.FRAME_TAIL, self.FRAME_TAIL])
        )

    def _send_raw(self, data: bytes, delay_s: float = 0.0):
        self.transport.write(data, delay_s=delay_s)

    def _send_command(self, cmd: int, data: bytes = b"", delay_s: float = 0.0):
        frame = self._make_frame(cmd, data)
        self._send_raw(frame, delay_s=delay_s)

    def _recv_packets(self, timeout_s: float = 2.0) -> list[tuple[int, bytes]]:
        packets: list[tuple[int, bytes]] = []

        incoming = self.transport.read(timeout_s=timeout_s)
        if incoming:
            self._packet_buffer.extend(incoming)

        while len(self._packet_buffer) >= 7:
            # Frame: 55 55 CMD LEN DATA XOR AA AA
            if (
                self._packet_buffer[0] != self.FRAME_HEAD
                or self._packet_buffer[1] != self.FRAME_HEAD
            ):
                del self._packet_buffer[0]
                continue

            cmd = self._packet_buffer[2]
            payload_len = self._packet_buffer[3]
            frame_len = payload_len + 7

            if len(self._packet_buffer) < frame_len:
                break

            frame = bytes(self._packet_buffer[:frame_len])
            del self._packet_buffer[:frame_len]

            if frame[-2] != self.FRAME_TAIL or frame[-1] != self.FRAME_TAIL:
                continue

            payload = frame[4 : 4 + payload_len]
            checksum = frame[4 + payload_len]
            expected = self._calc_xor(cmd, payload)

            if checksum != expected and self.debug:
                print(
                    "WARNING checksum mismatch:",
                    f"cmd=0x{cmd:02X}",
                    f"got=0x{checksum:02X}",
                    f"expected=0x{expected:02X}",
                )

            packets.append((cmd, payload))

        return packets

    def _transceive(
        self,
        cmd: int,
        data: bytes = b"",
        response_cmd: int | None = None,
        timeout_s: float = 2.0,
        tries: int = 6,
    ) -> bytes | None:
        if response_cmd is None:
            response_cmd = cmd + self.RESPONSE_OFFSET_DEFAULT

        self._send_command(cmd, data)

        for _ in range(tries):
            packets = self._recv_packets(timeout_s=timeout_s)

            for rx_cmd, payload in packets:
                if rx_cmd == response_cmd:
                    return payload

            time.sleep(0.05)

        return None

    # ------------------------------------------------------------
    # B1 specific commands
    # ------------------------------------------------------------

    def connect_printer(self):
        # B1 special connect packet:
        # 03 55 55 C1 00 C1 AA AA
        cmd = self.CMD_CONNECT
        data = b""
        frame = bytes(
            [
                0x03,
                self.FRAME_HEAD,
                self.FRAME_HEAD,
                cmd,
                0x00,
                self._calc_xor(cmd, data),
                self.FRAME_TAIL,
                self.FRAME_TAIL,
            ]
        )

        self._send_raw(frame)
        time.sleep(0.08)

    def set_density(self, density: int = 5) -> bool:
        density = max(1, min(5, int(density)))
        payload = self._transceive(
            self.CMD_SET_DENSITY,
            bytes([density]),
            response_cmd=0x31,
        )
        return bool(payload and payload[0])

    def set_label_type(self, label_type: int = LABEL_TYPE_GAP) -> bool:
        payload = self._transceive(
            self.CMD_SET_LABEL_TYPE,
            bytes([label_type]),
            response_cmd=0x33,
        )
        return bool(payload and payload[0])

    def start_print(self, total_pages: int = 1, page_color: int = 0) -> bool:
        # totalPages(u16 BE), 0, 0, 0, 0, pageColor
        data = struct.pack(">HBBBBB", total_pages, 0, 0, 0, 0, page_color)
        payload = self._transceive(
            self.CMD_PRINT_START,
            data,
            response_cmd=0x02,
        )
        return bool(payload and payload[0])

    def start_page(self) -> bool:
        payload = self._transceive(
            self.CMD_PAGE_START,
            b"\x01",
            response_cmd=0x04,
        )
        return bool(payload and payload[0])

    def set_page_size(
        self, rows: int, cols: int = PRINT_WIDTH_PX, copies: int = 1
    ) -> bool:
        data = struct.pack(">HHH", rows, cols, copies)
        payload = self._transceive(
            self.CMD_SET_PAGE_SIZE,
            data,
            response_cmd=0x14,
        )
        return bool(payload and payload[0])

    def end_page(self) -> bool:
        payload = self._transceive(
            self.CMD_PAGE_END,
            b"\x01",
            response_cmd=0xE4,
        )
        return bool(payload and payload[0])

    def end_print(self) -> bool:
        payload = self._transceive(
            self.CMD_PRINT_END,
            b"\x01",
            response_cmd=0xF4,
        )
        return bool(payload and payload[0])

    def print_status(self) -> dict | None:
        payload = self._transceive(
            self.CMD_PRINT_STATUS,
            b"\x01",
            response_cmd=0xB3,
            timeout_s=1.0,
            tries=3,
        )

        if payload is None:
            return None

        result = {
            "raw": payload,
            "progress_a": None,
            "progress_b": None,
            "busy": None,
        }

        if len(payload) >= 8:
            result["progress_a"] = payload[2]
            result["progress_b"] = payload[3]
            result["busy"] = payload[7]

        return result

    def wait_until_print_done(
        self,
        timeout_s: float = 10.0,
        poll_interval_s: float = 0.3,
    ) -> bool:
        start = time.time()

        while time.time() - start < timeout_s:
            status = self.print_status()

            if self.debug:
                print("PRINT STATUS:", status)

            if (
                status
                and status.get("progress_a", 0) >= 100
                and status.get("progress_b", 0) >= 100
                and status.get("busy") == 0
            ):
                return True

            time.sleep(poll_interval_s)

        return False

    # ------------------------------------------------------------
    # Image encoding
    # ------------------------------------------------------------

    def _encode_rows(self, image: Image.Image, repeat_count: int = 1):
        img = image.convert("1")

        cols = img.width
        rows = img.height
        row_bytes = math.ceil(cols / 8)

        if cols != self.PRINT_WIDTH_PX:
            raise ValueError(f"B1 width must be {self.PRINT_WIDTH_PX}px. Got: {cols}")

        if row_bytes != self.ROW_BYTES:
            raise ValueError(f"B1 row_bytes must be {self.ROW_BYTES}. Got: {row_bytes}")

        repeat_count = max(1, min(1, int(repeat_count)))

        for y in range(rows):
            row_data = bytearray(row_bytes)

            for x in range(cols):
                pix = img.getpixel((x, y))

                # PIL mode '1': 0 = black, 255 = white.
                # B1 expects black pixel as bit 1.
                if pix == 0:
                    byte_index = x // 8
                    bit_index = 7 - (x % 8)
                    row_data[byte_index] |= 1 << bit_index

            black_pixels = sum(byte.bit_count() for byte in row_data)

            # B1 row format:
            # rowNumber(u16 BE), 0, blackPixels LSB, blackPixels MSB, repeatCount, rowData[48]
            payload = bytes(
                [
                    (y >> 8) & 0xFF,
                    y & 0xFF,
                    0x00,
                    black_pixels & 0xFF,
                    (black_pixels >> 8) & 0xFF,
                    repeat_count,
                ]
            ) + bytes(row_data)

            if self.debug and y < 5:
                print(
                    "ROW",
                    y,
                    "black_pixels=",
                    black_pixels,
                    "payload_header=",
                    payload[:6].hex(" ").upper(),
                    "data=",
                    payload[6:14].hex(" ").upper(),
                )

            yield payload

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------

    def print_image(
        self,
        image: Image.Image,
        density: int = 5,
        copies: int = 1,
        row_delay_s: float = 0.012,
        wait_done_timeout_s: float = 10.0,
    ) -> bool:
        if image.width != self.PRINT_WIDTH_PX:
            raise ValueError(f"Image width must be {self.PRINT_WIDTH_PX}px")

        rows = image.height

        self.connect_printer()
        time.sleep(0.08)

        if not self.set_density(density):
            return False
        time.sleep(0.03)

        if not self.set_label_type(self.LABEL_TYPE_GAP):
            return False
        time.sleep(0.03)

        if not self.start_print(total_pages=1, page_color=0):
            return False
        time.sleep(0.08)

        if not self.start_page():
            return False
        time.sleep(0.03)

        if not self.set_page_size(rows=rows, cols=self.PRINT_WIDTH_PX, copies=copies):
            return False
        time.sleep(0.05)

        for row_payload in self._encode_rows(image, repeat_count=1):
            self._send_command(self.CMD_BITMAP_ROW, row_payload)
            time.sleep(row_delay_s)

        time.sleep(0.05)

        if not self.end_page():
            return False

        time.sleep(0.3)

        if not self.wait_until_print_done(
            timeout_s=wait_done_timeout_s, poll_interval_s=0.3
        ):
            if self.debug:
                print("WARNING: print status did not report done")
            return False

        return self.end_print()

    def print_product_label(
        self,
        product_id: str,
        product_name: str,
        serial_no: str,
        release: str,
        stock_code: str,
        inspected_by: str,
        inspection_date: str,
        qr_text: str | None = None,
        order_no: str | None = None,
        density: int = 5,
        copies: int = 1,
        row_delay_s: float = 0.012,
        wait_done_timeout_s: float = 10.0,
    ) -> bool:
        from .templates import product_label

        image = product_label(
            product_id=product_id,
            product_name=product_name,
            serial_no=serial_no,
            release=release,
            stock_code=stock_code,
            inspected_by=inspected_by,
            inspection_date=inspection_date,
            qr_text=qr_text,
            order_no=order_no,
        )

        return self.print_image(
            image,
            density=density,
            copies=copies,
            row_delay_s=row_delay_s,
            wait_done_timeout_s=wait_done_timeout_s,
        )

    def heartbeat(self) -> dict | None:
        payload = self._transceive(0xDC, b"\x01", response_cmd=0xDD)

        if payload is None:
            return None

        result = {
            "raw": payload,
            "closingstate": None,
            "powerlevel": None,
            "paperstate": None,
            "rfidreadstate": None,
        }

        if len(payload) == 13:
            result["closingstate"] = payload[9]
            result["powerlevel"] = payload[10]
            result["paperstate"] = payload[11]
            result["rfidreadstate"] = payload[12]
        elif len(payload) == 20:
            result["paperstate"] = payload[18]
            result["rfidreadstate"] = payload[19]
        elif len(payload) == 19:
            result["closingstate"] = payload[15]
            result["powerlevel"] = payload[16]
            result["paperstate"] = payload[17]
            result["rfidreadstate"] = payload[18]

        return result

    def get_device_serial(self) -> str | None:
        payload = self._transceive(0x40, b"\x0b", response_cmd=0x4B)

        if payload is None:
            return None

        return payload.decode(errors="ignore")
