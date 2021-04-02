from openRgbTools import *
from time import sleep

# ===================================================
# Main
# ===================================================


def main():
    # Main Loop
    while True:
        # Get client
        while not (client := get_client()):
            sleep(2)
            continue

        # Print devices for the user
        print_devices(client)

        # Load effects from 
        zone_effects = load_effects_from_json(client)

        # Begin effect listeners
        for zone_effect in zone_effects:
            zone_effect.refresh_listener()

        # Check for effects (devices may not be ready yet)
        if not zone_effects:
            sleep(2)

        # Loop through effect frames; If connection lost retry
        while True:
            try:
                for zone_effect in zone_effects:
                    zone_effect.step_effects()
                    zone_effect.update()
            except ConnectionAbortedError:
                break
            sleep(1)


if __name__ == "__main__":
    main()
