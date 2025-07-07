#!/bin/bash
# Simple Git Push Script for WC Control System

echo "=== WC Control System - Git Push Helper ==="
echo ""

# Navigate to project directory
cd "B:\Python\MicroPython\ESP_WC_System"

# Show current status
echo "Current branch: $(git branch --show-current)"
echo ""
echo "Repository status:"
git status --short
echo ""

# Show last commit
echo "Last commit:"
git log --oneline -1
echo ""

# Options for user
echo "Choose an action:"
echo "1. Push existing commits to remote (recommended)"
echo "2. Add all changes and commit with new message"
echo "3. Reset cache files and push clean"
echo "4. Check what files are ready to commit"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Pushing existing commits to remote repository..."
        git push origin Analytic-UI
        if [ $? -eq 0 ]; then
            echo "✅ Successfully pushed to remote!"
        else
            echo "❌ Failed to push. Check your network connection and repository access."
        fi
        ;;
    2)
        echo ""
        read -p "Enter your commit message: " commit_msg
        if [ -z "$commit_msg" ]; then
            commit_msg="Update ESP32 WC Control System - $(date '+%Y-%m-%d %H:%M')"
        fi
        
        git add .
        git commit -m "$commit_msg"
        git push origin Analytic-UI
        
        if [ $? -eq 0 ]; then
            echo "✅ Successfully committed and pushed!"
        else
            echo "❌ Failed to push. Check for conflicts or network issues."
        fi
        ;;
    3)
        echo ""
        echo "Resetting cache and database files..."
        git reset HEAD PC_host/__pycache__/* 2>/dev/null
        git reset HEAD PC_host/data/*.db 2>/dev/null
        git checkout -- PC_host/__pycache__/* 2>/dev/null
        git checkout -- PC_host/data/*.db 2>/dev/null
        
        echo "Pushing clean repository..."
        git push origin Analytic-UI
        
        if [ $? -eq 0 ]; then
            echo "✅ Successfully pushed clean repository!"
        else
            echo "❌ Failed to push."
        fi
        ;;
    4)
        echo ""
        echo "Files staged for commit:"
        git diff --cached --name-only
        echo ""
        echo "Files modified but not staged:"
        git diff --name-only
        echo ""
        echo "Untracked files:"
        git ls-files --others --exclude-standard
        ;;
    *)
        echo "Invalid choice. Exiting."
        ;;
esac

echo ""
echo "=== Final Status ==="
git status --short
