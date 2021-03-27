from openRgbTools import *
from time import sleep

# ===================================================
# Main
# ===================================================


def main():
    # Main Loop
    while True:
        # Get Client and load effects from JSON
        client = get_client()
        print_devices(client)
        effects = load_effects_from_json(client)

        # Loop through effect frames; If connection lost retry
        while True:
            try:
                for effect in effects:
                    next(effect)
            except ConnectionAbortedError:
                break
            sleep(1)


if __name__ == "__main__":
    main()
