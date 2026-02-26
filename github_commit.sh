#!/bin/bash

# Afficher la bannière
source .trae/display_banner.sh

# Commit interactif
echo "📝 Commit interactif Vantablack"
echo ""

read -p "💬 Message de commit: " commit_message

if [ -z "$commit_message" ]; then
    commit_message="Auto-commit: $(date '+%Y-%m-%d %H:%M:%S')"
fi

git add .
git commit -m "$commit_message"

echo ""
echo "✅ Commit effectué: $commit_message"
echo "📊 Utilisez './github_push.sh' pour pousser vers GitHub"