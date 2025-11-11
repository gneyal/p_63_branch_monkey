#!/bin/bash

echo "=== BRANCH MONKEY DEMO ==="
echo ""
echo "1. Current status:"
monkey status
echo ""
echo "---"
echo ""
echo "2. See recent history:"
monkey history -n 5
echo ""
echo "---"
echo ""
echo "3. List checkpoints:"
monkey checkpoints -n 5
echo ""
echo "---"
echo ""
echo "4. List experiments:"
monkey experiments
echo ""
echo "=== TRY THESE NEXT ==="
echo ""
echo "  monkey                    # Launch visual graph"
echo "  monkey save 'message'     # Create checkpoint"
echo "  monkey try-it feature-x   # Start experiment"
echo "  monkey undo               # Go back one step"
