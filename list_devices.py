from braket.aws import AwsDevice

try:
    # Get all available devices
    devices = AwsDevice.get_devices()
    
    print("Available Amazon Braket devices:")
    print("=" * 50)
    
    for device in devices:
        print(f"Name: {device.name}")
        print(f"ARN: {device.arn}")
        print(f"Type: {device.type}")
        print(f"Status: {device.status}")
        print("-" * 30)
        
except Exception as e:
    print(f"Error listing devices: {e}") 