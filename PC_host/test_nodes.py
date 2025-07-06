#!/usr/bin/env python3
"""Test script to verify our node changes"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import get_nodes_with_mock_data

def test_nodes():
    """Test that we get exactly 4 nodes with simplified names"""
    nodes = get_nodes_with_mock_data()
    
    print(f"✅ Total nodes: {len(nodes)}")
    print("📋 Node details:")
    
    for i, node in enumerate(nodes, 1):
        print(f"   {i}. {node['name']} ({node['node_type']}) - {node['status']}")
    
    # Verify we have exactly 4 nodes
    if len(nodes) == 4:
        print("✅ SUCCESS: Exactly 4 nodes found!")
    else:
        print(f"❌ ERROR: Expected 4 nodes, got {len(nodes)}")
    
    # Verify simplified names
    expected_names = ['Room1', 'Room2', 'Room3', 'Room4']
    actual_names = [node['name'] for node in nodes]
    
    if actual_names == expected_names:
        print("✅ SUCCESS: Node names are simplified correctly!")
    else:
        print(f"❌ ERROR: Expected {expected_names}, got {actual_names}")

if __name__ == "__main__":
    test_nodes()
