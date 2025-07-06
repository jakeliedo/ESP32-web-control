#!/usr/bin/env python3
"""
Quick test script to verify the new UI changes
"""

import webbrowser
import time
import threading

def open_pages():
    """Open different pages in browser for testing"""
    time.sleep(3)  # Wait for Flask to start
    
    print("\n🌐 Opening pages for testing...")
    
    # Open main dashboard
    webbrowser.open('http://localhost:5000/')
    print("✅ Dashboard opened")
    
    time.sleep(2)
    
    # Open mobile simple UI
    webbrowser.open('http://localhost:5000/simple')
    print("✅ Mobile Simple UI opened")
    
    time.sleep(2)
    
    # Open analytics
    webbrowser.open('http://localhost:5000/analytics')
    print("✅ Analytics page opened")

if __name__ == "__main__":
    print("🚀 WC Control System - UI Test")
    print("=" * 40)
    print("Testing new features:")
    print("  • PC Dashboard with Control Cards")
    print("  • Mobile-optimized Simple UI")
    print("  • Fixed logo positioning")
    print("  • Updated navigation")
    print()
    
    # Start browser opening in background
    threading.Thread(target=open_pages, daemon=True).start()
    
    print("⏳ Browser pages will open automatically...")
    print("💡 Check both interfaces:")
    print("   - PC Dashboard: Row of control cards + analytics")
    print("   - Mobile UI: 2x2 grid layout")
    print("   - Fixed logo at bottom-right on both")
    print()
    
    input("Press Enter to continue...")
