from niimbot_b1 import NiimbotB1Printer, LabelCanvas

ADDRESS = "09:0c:12:66:3b:3d"


def main():
    printer = NiimbotB1Printer(ADDRESS, debug=True)

    try:
        printer.connect()

        canvas = LabelCanvas(width=384, height=240)

        canvas.rect(1, 1, 382, 238, width=2)

        canvas.text(20, 20, "NIIMBOT PYTHON TEST", bold=True)

        canvas.line(20, 55, 130, 55, width=2)
        canvas.line(145, 55, 255, 55, width=2)
        canvas.line(270, 55, 360, 55, width=2)

        canvas.text(20, 80, "ESP32 -> Python BLE", bold=True)
        canvas.text(20, 110, "B1-GC09121929", bold=True)
        canvas.text(20, 150, "Bitmap row OK", bold=True)
        canvas.text(20, 180, "Protocol fixed", bold=True)

        ok = printer.print_image(
            canvas.image,
            density=5,
            copies=1,
            row_delay_s=0.012,
        )

        print("Print result:", ok)

    finally:
        printer.disconnect()


if __name__ == "__main__":
    main()
