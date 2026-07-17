from niimbot_b1 import NiimbotB1Printer

ADDRESS = "09:0c:12:66:3b:3d"


def main():
    printer = NiimbotB1Printer(ADDRESS, debug=True)

    try:
        printer.connect()

        print("\nHeartbeat:")
        print(printer.heartbeat())

        print("\nDevice serial:")
        print(printer.get_device_serial())

    finally:
        printer.disconnect()


if __name__ == "__main__":
    main()
