import random  # For generating random values
from shared.shared_variables import shared_queue_1


# Dummy function for moisture
def get_moisture():
    return (
        "detected HIGH i.e. moisture"
        if random.choice([True, False])
        else "detected LOW i.e. no moisture"
    )


# Dummy function for current
def current(thread_id, stop_event):
    print("Current running Thread ID: ", thread_id)
    while not stop_event.is_set():
        try:
            LDR_value = random.randint(0, 1023)  # Simulate LDR value
            pot_value = random.randint(0, 1023)  # Simulate potentiometer value

            result = {"LDR": LDR_value, "pot": pot_value}
            shared_queue_1.put(result)
        except KeyboardInterrupt:
            print("Keyboard Interrupted")
            stop_event.set()
            break


# Dummy function for ultrasonic
async def ultrasonic():
    distance = random.uniform(0, 200)  # Simulate distance measurement
    condition = distance < 120
    print(distance)
    print(condition)
    return condition


# Dummy function for registering card
async def register_card():
    return random.randint(100000, 999999)  # Simulate RFID card ID


# Dummy function for light control
def light(state):
    if state is True:
        return "Light ON"
    else:
        return "Light OFF"
