from niimbot_b1 import (
    config_file_path,
    load_config,
    get_saved_printer_address,
    clear_saved_printer_address,
    find_niimbot_b1,
    set_saved_printer_address,
)


def main():
    print("Config file:")
    print(config_file_path())

    print("\nCurrent config:")
    print(load_config())

    print("\nSaved printer address:")
    print(get_saved_printer_address() or "(empty)")

    answer = input("\nScan for NIIMBOT B1 now? [y/N]: ").strip().lower()

    if answer == "y":
        address = find_niimbot_b1(timeout_s=5.0, debug=True)

        if address:
            print("\nFound printer:", address)

            save_answer = input("Save this address? [y/N]: ").strip().lower()
            if save_answer == "y":
                set_saved_printer_address(address)
                print("Saved.")
        else:
            print("\nNo NIIMBOT B1 printer found.")

    answer = input("\nClear saved printer address? [y/N]: ").strip().lower()

    if answer == "y":
        clear_saved_printer_address()
        print("Saved printer address cleared.")

    print("\nFinal config:")
    print(load_config())


if __name__ == "__main__":
    main()
