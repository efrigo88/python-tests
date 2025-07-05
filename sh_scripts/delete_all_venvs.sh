#!/bin/bash

# Find all .venv directories
venv_dirs=$(find . -type d -name ".venv")

# Check if any were found
if [ -z "$venv_dirs" ]; then
  echo "No .venv directories found."
  exit 0
fi

# Show the found directories
echo "The following .venv directories were found:"
echo "$venv_dirs"
echo

# Ask for confirmation
read -p "Do you want to delete all of them? (y/N): " confirm
if [[ "$confirm" =~ ^[Yy]$ ]]; then
  # Delete the directories
  echo "$venv_dirs" | xargs rm -rf
  echo "✅ All .venv directories deleted successfully."
else
  echo "❌ Operation cancelled. No directories were deleted."
fi
