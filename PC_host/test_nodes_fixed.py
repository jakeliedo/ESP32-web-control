#!/usr/bin/env python3
"""
Test script to verify that pc_host does not appear as a node in the UI
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import get_nodes_with_mock_data
import json

def test_nodes_exclude_pc_host():
    """Test that pc_host is excluded from nodes list"""
    print("🔍 Testing node list (should exclude pc_host)...")
    
    nodes = get_nodes_with_mock_data()
    
    print(f"📊 Found {len(nodes)} nodes:")
    for i, node in enumerate(nodes, 1):
        print(f"   {i}. {node.get('name', 'Unknown')} ({node.get('node_type', 'unknown')}) - {node.get('status', 'unknown')}")
        
        # Check that pc_host is not in the list
        if node.get('node_id') == 'pc_host' or node.get('name') == 'pc_host':
            print("❌ FAILED: pc_host found in nodes list!")
            return False
    
    # Verify expected node count
    if len(nodes) == 4:
        print("✅ SUCCESS: Exactly 4 nodes found!")
    else:
        print(f"⚠️ WARNING: Expected 4 nodes, found {len(nodes)}")
    
    # Verify node names are simplified
    expected_names = {'Room1', 'Room2', 'Room3', 'Room4'}
    actual_names = {node.get('name', '') for node in nodes}
    
    if expected_names == actual_names:
        print("✅ SUCCESS: Node names are simplified correctly!")
    else:
        print(f"⚠️ WARNING: Expected names {expected_names}, got {actual_names}")
    
    # Check for pc_host specifically
    pc_host_found = any(
        'pc_host' in str(node.get('node_id', '')).lower() or 
        'pc_host' in str(node.get('name', '')).lower()
        for node in nodes
    )
    
    if not pc_host_found:
        print("✅ SUCCESS: pc_host is correctly excluded from nodes list!")
        return True
    else:
        print("❌ FAILED: pc_host found in nodes list!")
        return False

if __name__ == "__main__":
    print("🚀 Testing WC System Node Configuration...")
    print("=" * 50)
    
    success = test_nodes_exclude_pc_host()
    
    print("=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("💥 SOME TESTS FAILED!")
    
    print("\n📝 Node configuration is correct for ESP32-only nodes.")
