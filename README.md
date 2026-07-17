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
- Suitable for integration into desktop applications.

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

