import asyncio
from bleak import BleakScanner, BleakClient

async def scan_devices():
    """Scan for nearby BLE devices and list them."""
    print('''\033[0;34m\t
     ____    ____                  
    | __ )  / ___|  ___ __ _ _ __  
    |  _ \  \___ \ / __/ _` | '_ \ 
    | |_) |  ___) | (_| (_| | | | |
    |____/  |____/ \___\__,_|_| |_|
    
                           by linux
    \033[0m''')
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()
    if not devices:
        print("No BLE devices found.")
    else:
        for i, device in enumerate(devices):
            print(f"{i + 1}: {device.name or 'Unknown'} - {device.address}")
    return devices

async def connect_and_send_payload(device_address, payload, max_retries=3, timeout=10.0):
    """Connect to a BLE device by address, find a writable characteristic, and send the payload."""
    retry_count = 0
    while retry_count < max_retries:
        try:
            async with BleakClient(device_address, timeout=timeout) as client:
                print(f"Connecting to {device_address} (Attempt {retry_count + 1})...")
                if client.is_connected:
                    print("Connected successfully!")
                    services = await client.get_services()

                    # Find the first writable characteristic
                    writable_char = None
                    for service in services:
                        for char in service.characteristics:
                            if "write" in char.properties:
                                writable_char = char.uuid
                                print(f"Found writable characteristic: {writable_char}")
                                break
                        if writable_char:
                            break

                    # If no writable characteristic is found, prompt the user to select
                    if not writable_char:
                        print("No writable characteristic found automatically. Here are available characteristics:")
                        characteristics = [char.uuid for service in services for char in service.characteristics]
                        for i, char_uuid in enumerate(characteristics):
                            print(f"{i + 1}: {char_uuid}")
                        
                        try:
                            char_index = int(input("Select a characteristic by entering its number: ")) - 1
                            writable_char = characteristics[char_index]
                            print(f"Selected characteristic: {writable_char}")
                        except (ValueError, IndexError):
                            print("Invalid selection. Exiting.")
                            return
                    
                    # Send payload to the selected writable characteristic
                    try:
                        await client.write_gatt_char(writable_char, payload.encode())
                        print("Payload sent successfully!")
                        return
                    except Exception as e:
                        print(f"Failed to send payload: {e}")
                        return
                else:
                    print("Failed to connect.")
        except asyncio.TimeoutError:
            print(f"Connection attempt {retry_count + 1} timed out.")
        except Exception as e:
            print(f"Connection attempt {retry_count + 1} failed: {e}")
        
        retry_count += 1
        print("Retrying...")

    print("Max retries reached. Could not connect to the device.")

async def main():
    devices = await scan_devices()
    if not devices:
        print("No devices found. Please try again.")
        return
    
    # Select target device
    try:
        device_index = int(input("Select the device by entering its number: ")) - 1
        if device_index < 0 or device_index >= len(devices):
            print("Invalid selection.")
            return
    except ValueError:
        print("Please enter a valid number. Exiting.")
        return
    
    target_device = devices[device_index]
    print(f"Selected device: {target_device.name or 'Unknown'} - {target_device.address}")

    # Define the payload
    payload = input("Enter the payload to send: ")

    # Connect and send the payload
    await connect_and_send_payload(target_device.address, payload)

# Run the main function
asyncio.run(main())
