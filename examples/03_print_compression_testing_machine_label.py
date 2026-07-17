from niimbot_b1 import NiimbotB1Printer, product_label

ADDRESS = "09:0c:12:66:3b:3d"


def main():
    printer = NiimbotB1Printer(ADDRESS, debug=True)

    try:
        printer.connect()

        image = product_label(
            product_id="B001",
            product_name="COMPRESSION TESTING MACHINE",
            serial_no="547",
            release="B001CAIV1R6006",
            model_code="B001P032H",
            inspected_by="GOKHAN AREL",
            inspection_date="08.07.2026",
            qr_text="B001P032H|547|B001CAIV1R6006",
        )

        ok = printer.print_image(
            image,
            density=5,
            copies=1,
            row_delay_s=0.012,
        )

        print("Print result:", ok)

    finally:
        printer.disconnect()


if __name__ == "__main__":
    main()
