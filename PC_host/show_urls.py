#!/usr/bin/env python3
"""
Quick script to show all available URLs for WC Control System
"""

import socket
import subprocess
import platform

def get_local_ip():
    """Get local IP address"""
    try:
        # Connect to a remote server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def get_all_ips():
    """Get all network interfaces"""
    ips = []
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if 'IPv4' in line and '192.168' in line:
                    ip = line.split(':')[-1].strip()
                    if ip:
                        ips.append(ip)
        else:
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
            ips = result.stdout.split()
    except:
        pass
    return ips

def main():
    print("🚀 WC Control System - Access URLs")
    print("=" * 50)
    
    # Get IPs
    local_ip = get_local_ip()
    all_ips = get_all_ips()
    
    print("📱 DASHBOARD (PC Analytics Interface):")
    print(f"   • Local:    http://localhost:5000")
    print(f"   • Network:  http://{local_ip}:5000")
    
    if all_ips:
        for ip in all_ips:
            if ip != local_ip and '192.168' in ip:
                print(f"   • Network:  http://{ip}:5000")
    
    print()
    print("📱 SIMPLE UI (Mobile Interface):")
    print(f"   • Local:    http://localhost:5000/simple")
    print(f"   • Network:  http://{local_ip}:5000/simple")
    
    print()
    print("📊 OTHER PAGES:")
    print(f"   • Analytics: http://{local_ip}:5000/analytics")
    print(f"   • Events:    http://{local_ip}:5000/events")
    print(f"   • API:       http://{local_ip}:5000/api/status")
    
    print()
    print("💡 FEATURES:")
    print("   • Dashboard: Quick control (4 cards/row) + Analytics")
    print("   • Simple UI: Mobile 2x2 grid layout")
    print("   • Fixed logo: Bottom-right corner")
    print("   • Mock data: 6 demo nodes available")
    
    print()
    print("🔥 Ready to test the new UI!")

if __name__ == "__main__":
    main()
