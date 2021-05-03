from open_rgb_tools import *
from battle_queue import *
from time import sleep

# ===================================================
# Main
# ===================================================


def main():
    # Main Loop
    while True:
        # Get client
        if not (client := get_client()):
            sleep(2)
            continue

        # Print devices for the user
        print_devices(client)

        # Load effects from JSON
        zone_effects = load_effects_from_json(client)

        # Begin effect listeners
        for zone_effect in zone_effects:
            zone_effect.refresh_listener()

        # Check for effects (devices may not be ready yet)
        if not zone_effects:
            sleep(2)

        # Get queue of timed effects
        queue = BattleQueue()
        for zone_effect in zone_effects:
            queue += zone_effect.get_effect_queue()

        # Initial run for all effects
        queue.activate()

        while zone_effects:
            # Run the queue
            try:
                # Update all zones (This is inefficient, we should only update zone which change somehow)
                for zone_effect in zone_effects:
                    zone_effect.update()

                # Wait for and run the next step of the queue
                sleep(queue.get_next_duration()/1000)
                queue.run_next(run_consecutive=True)

            # If the connection is lost, restart the main loop and try to get a new one
            except ConnectionAbortedError:
                break


if __name__ == "__main__":
    main()
