# ESP32 Node Deployment Script
# This script helps you upload code to each ESP32 node

import os
import shutil
import time

def deploy_node(room_name, node_folder, com_port="COM3"):
    """
    Deploy code to a specific ESP32 node
    
    Args:
        room_name: Name of the room (e.g., "Room1", "Room2")
        node_folder: Path to the node folder (e.g., "room1", "room2")
        com_port: Serial port of the ESP32 (e.g., "COM3", "COM4")
    """
    
    print(f"\n=== Deploying {room_name} Node ===")
    
    # Check if node folder exists
    if not os.path.exists(node_folder):
        print(f"Error: Node folder '{node_folder}' not found!")
        return False
    
    # Check if main.py exists
    main_py_path = os.path.join(node_folder, "main.py")
    if not os.path.exists(main_py_path):
        print(f"Error: main.py not found in '{node_folder}'!")
        return False
    
    print(f"Found main.py for {room_name}")
    print(f"Deploying to {com_port}...")
    
    # Here you would use your preferred tool to upload to ESP32
    # Examples:
    
    # Using ampy (if installed):
    # os.system(f"ampy --port {com_port} put {main_py_path}")
    # os.system(f"ampy --port {com_port} put lib/umqtt /lib/umqtt")
    
    # Using Thonny (manual):
    print(f"Manual steps for {room_name}:")
    print(f"1. Open Thonny IDE")
    print(f"2. Connect to ESP32 on {com_port}")
    print(f"3. Upload {main_py_path}")
    print(f"4. Upload lib/umqtt folder to /lib/umqtt")
    print(f"5. Reset the ESP32")
    
    return True

def main():
    """Main deployment function"""
    
    print("ESP32 WC Control System - Node Deployment")
    print("=" * 50)
    
    # Node configurations
    nodes = [
        {"name": "Room1 (Male WC)", "folder": "room1", "port": "COM3"},
        {"name": "Room2 (Male WC)", "folder": "room2", "port": "COM4"},
        {"name": "Room3 (Female WC)", "folder": "room3", "port": "COM5"},
        {"name": "Room4 (Female WC)", "folder": "room4", "port": "COM6"},
    ]
    
    print("Available nodes:")
    for i, node in enumerate(nodes, 1):
        print(f"{i}. {node['name']} -> {node['folder']} ({node['port']})")
    
    print("\nOptions:")
    print("0. Deploy all nodes")
    print("1-4. Deploy specific node")
    print("q. Quit")
    
    choice = input("\nEnter your choice: ").strip().lower()
    
    if choice == 'q':
        print("Deployment cancelled.")
        return
    
    elif choice == '0':
        # Deploy all nodes
        print("\nDeploying all nodes...")
        for node in nodes:
            deploy_node(node['name'], node['folder'], node['port'])
            input(f"Press Enter when {node['name']} deployment is complete...")
    
    elif choice in ['1', '2', '3', '4']:
        # Deploy specific node
        node_index = int(choice) - 1
        node = nodes[node_index]
        deploy_node(node['name'], node['folder'], node['port'])
    
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
