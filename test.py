# import asyncio
# from bleak import BleakClient

# DADDRESS = "50:20:65:C7:02:89"
# UUID = "78563412-7856-3412-7856-3412-78563412"

# async def send_hello_infinito0():
#     client = BleakClient(DADDRESS)
#     try:
#         await client.connect()
#         if client.is_connected:
#             print("Connected to BLE device.")
#             message = b"12345678901234567890"
#             await client.write_gatt_char(UUID, message)
#             print(f"Sent message: {message}")
#             print("Connection still active. Perform more actions or keep it open.")
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
        
#         pass  

# asyncio.run(send_hello_infInito0())
import asyncio
from bleak import BleakClient
async def send_message(client, message, characteristic_uuid):
    message_bytes = message.encode('utf-8')
    await client.write_gatt_char(characteristic_uuid, message_bytes)
    print(f"Message sent: {message}")
async def main():
    device_address = "50:20:65:C7:02:89"
    characteristic_uuid = "78563412-7856-3412-7856-3412-78563412"
    async with BleakClient(device_address) as client:
        if client.is_connected:
            print(f"Successfully connected to {device_address}")
            while True:
                message = input("Enter the message to send (or type 'exit' to quit): ")
                if message.lower() == 'exit':
                    break
                await send_message(client, message, characteristic_uuid)
                
            print("Connection will remain open after this.")
        else:
            print(f"Failed to connect to {device_address}")

if __name__ == "__main__":
    asyncio.run(main())








