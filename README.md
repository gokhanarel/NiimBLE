# NiimBLE

Python BLE library for NIIMBOT B1 label printer.

This project provides a simple Python interface for printing bitmap labels on the NIIMBOT B1 thermal label printer using BLE/GATT.

## Features

- NIIMBOT B1 BLE connection
- Automatic printer discovery
- Saved printer address configuration
- Heartbeat and device serial query
- Bitmap label printing
- QR code support
- Product label template
- Linux and Windows compatible font handling
- Suitable for integration into desktop applications such as `afpWin.exe`

## Tested Printer

- Model: NIIMBOT B1
- Example device name: `B1-GC09121929`
- Example BLE address: `09:0c:12:66:3b:3d`

## BLE UUIDs

```text
Service UUID:
e7810a71-73ae-499d-8c15-faa9aef0c3f2

Characteristic UUID:
bef8d6c9-9c21-4c9e-b632-bd58c1009f9f
```

## Installation

Create and activate virtual environment on Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies and editable package:

```bash
python -m pip install -e .
```

If QR code support is missing:

```bash
python -m pip install "qrcode[pil]"
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

## Project Structure

```text
NiimBLE/
  niimbot_b1/
    __init__.py
    transport.py
    printer.py
    canvas.py
    font_utils.py
    templates.py
    config.py
  examples/
    01_heartbeat.py
    02_print_test_label.py
    03_print_compression_testing_machine_label.py
    04_print_product_label.py
    05_print_product_label_direct.py
    06_print_product_label_saved_or_auto.py
    07_config_demo.py
    08_force_scan_and_print.py
  pyproject.toml
  README.md
  LICENSE
```

## Quick Test

```bash
python examples/01_heartbeat.py
```

Expected result:

```text
Connected: True
Heartbeat OK
Device serial: GC09121929
```

## Print Product Label

```python
from niimbot_b1 import NiimbotB1Printer

printer = NiimbotB1Printer.connect_saved_or_auto(
    timeout_s=5.0,
    debug=True,
    save_found=True,
)

try:
    ok = printer.print_product_label(
        product_id="B001",
        product_name="COMPRESSION TESTING MACHINE",
        serial_no="547",
        release="B001CAIV1R6006",
        stock_code="B001P032H",
        inspected_by="GOKHAN AREL",
        inspection_date="08.07.2026",
        order_no="",
        density=5,
    )

    print("Print result:", ok)

finally:
    printer.disconnect()
```

## Product Label Fields

The default product label supports:

```text
product_id
product_name
serial_no
release
stock_code
inspected_by
inspection_date
order_no
qr_text
```

`order_no` is optional. If empty, the label uses the compact default layout.

## QR Code

If `qr_text` is not provided, the template automatically generates a compact QR payload:

```text
product_id|stock_code|serial_no|release
```

If `order_no` is provided:

```text
product_id|stock_code|serial_no|release|order_no
```

You can also provide your own QR content:

```python
from niimbot_b1 import product_label

image = product_label(
    product_id="B001",
    product_name="COMPRESSION TESTING MACHINE",
    serial_no="547",
    release="B001CAIV1R6006",
    stock_code="B001P032H",
    inspected_by="GOKHAN AREL",
    inspection_date="08.07.2026",
    qr_text="B001P032H|547|B001CAIV1R6006",
)
```

## Printer Discovery and Config

The library can automatically find a nearby NIIMBOT B1 printer.

First use:

```python
printer = NiimbotB1Printer.connect_saved_or_auto(debug=True)
```

Behavior:

```text
1. Try saved printer address.
2. If not available or connection fails, scan for NIIMBOT B1.
3. Save found address.
4. Use saved address next time for faster connection.
```

Config file locations:

Linux:

```text
~/.config/niimbot_b1/config.json
```

Windows:

```text
%APPDATA%\NiimBotB1\config.json
```

Example config:

```json
{
    "printer_address": "09:0c:12:66:3b:3d",
    "density": 5,
    "row_delay_s": 0.012
}
```

## Force Rescan

```python
printer = NiimbotB1Printer.connect_saved_or_auto(
    debug=True,
    force_scan=True,
    save_found=True,
)
```

Useful for a "Find Printer Again" button in desktop applications.

## Protocol Notes

NIIMBOT B1 frame format:

```text
55 55 CMD LEN DATA XOR AA AA
```

Connect packet has a special prefix:

```text
03 55 55 C1 00 C1 AA AA
```

Bitmap row command:

```text
CMD = 0x85

Payload:
rowNumber(u16 BE)
0x00
blackPixels LSB
blackPixels MSB
repeatCount
rowData[48]
```

Important B1 settings:

```text
page_color = 0
repeatCount = 1
density = 5
row_delay_s = 0.012
width = 384 px
row_bytes = 48
```

Correct print sequence:

```text
Connect
SetDensity
SetLabelType
PrintStart
PageStart
SetPageSize
BitmapRow x N
PageEnd
Wait PrintStatus 100/100 and busy=0
PrintEnd
```

`PrintEnd` must not be sent immediately after `PageEnd`. The printer should report done first.

## Font Handling

The library searches fonts in this order:

```text
1. Bundled fonts inside niimbot_b1/fonts/
2. Linux system fonts
3. Windows system fonts
4. PIL default font fallback
```

For consistent output on Windows and Linux, bundle the preferred font with the application.

## PyInstaller Notes

When packaging with PyInstaller, include bundled fonts if used.

Linux/macOS style:

```bash
pyinstaller afpWin.py --add-data "niimbot_b1/fonts:niimbot_b1/fonts"
```

Windows style:

```bash
pyinstaller afpWin.py --add-data "niimbot_b1/fonts;niimbot_b1/fonts"
```

## Example Scripts

Heartbeat:

```bash
python examples/01_heartbeat.py
```

Basic test label:

```bash
python examples/02_print_test_label.py
```

Compression testing machine label:

```bash
python examples/03_print_compression_testing_machine_label.py
```

Product label:

```bash
python examples/04_print_product_label.py
```

Direct product label print:

```bash
python examples/05_print_product_label_direct.py
```

Saved or auto printer:

```bash
python examples/06_print_product_label_saved_or_auto.py
```

Config demo:

```bash
python examples/07_config_demo.py
```

Force scan and print:

```bash
python examples/08_force_scan_and_print.py
```

## pyproject.toml Example

```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "niimbot-b1"
version = "0.1.0"
description = "Python BLE library for NIIMBOT B1 label printer"
requires-python = ">=3.10"
dependencies = [
    "bleak",
    "Pillow",
    "qrcode[pil]",
]

[tool.setuptools]
packages = ["niimbot_b1"]
```

## Acknowledgements

This library was developed by Gökhan Arel with assistance from ChatGPT by OpenAI.

Special thanks to the open-source Python ecosystem, especially Bleak, Pillow, and qrcode.

## License

This project is licensed under the MIT License.

See the [LICENSE](LICENSE) file for details.
