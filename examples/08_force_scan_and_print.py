from niimbot_b1 import NiimbotB1Printer


def main():
    printer = NiimbotB1Printer.connect_saved_or_auto(
        timeout_s=5.0,
        debug=True,
        save_found=True,
        force_scan=True,
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


if __name__ == "__main__":
    main()
