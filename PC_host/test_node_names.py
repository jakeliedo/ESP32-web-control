#!/usr/bin/env python3
"""
Test script to verify node names and ensure pc_host doesn't appear as a node
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import get_nodes_with_mock_data

def test_node_names():
    """Test that node names are correctly formatted"""
    print("🔍 Testing node names and count...")
    
    nodes = get_nodes_with_mock_data()
    
    print(f"📊 Found {len(nodes)} nodes:")
    
    expected_names = ["Room 1", "Room 2", "Room 3", "Room 4"]
    
    for i, node in enumerate(nodes):
        node_id = node.get('node_id', 'unknown')
        name = node.get('name', 'unknown')
        node_type = node.get('node_type', 'unknown')
        status = node.get('status', 'unknown')
        
        print(f"   {i+1}. {name} ({node_type}) - {status}")
        
        # Check if this is pc_host (should not appear)
        if 'pc_host' in node_id.lower():
            print(f"❌ ERROR: pc_host found in nodes! {node_id}")
            return False
            
        # Check if name format is correct
        if name not in expected_names:
            print(f"⚠️ WARNING: Unexpected name format: '{name}'")
    
    # Check that we have exactly 4 nodes
    if len(nodes) != 4:
        print(f"❌ ERROR: Expected 4 nodes, got {len(nodes)}")
        return False
    
    # Check that names have spaces
    success = True
    for node in nodes:
        name = node.get('name', '')
        if ' ' not in name:
            print(f"❌ ERROR: Node name '{name}' should have spaces")
            success = False
    
    if success:
        print("✅ SUCCESS: All node names are correctly formatted!")
        print("✅ SUCCESS: Exactly 4 nodes found!")
        print("✅ SUCCESS: No pc_host in node list!")
    
    return success

if __name__ == "__main__":
    test_node_names()
