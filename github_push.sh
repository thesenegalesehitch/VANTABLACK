#!/bin/bash

# Afficher la bannière
source .trae/display_banner.sh

# Commit et push automatique vers GitHub
echo "🚀 Préparation du push GitHub..."
git add .

if [ -z "$1" ]; then
    commit_msg="Auto-commit: $(date '+%Y-%m-%d %H:%M:%S')"
else
    commit_msg="$1"
fi

git commit -m "$commit_msg"

echo "📤 Pushing to GitHub..."
if git push origin main; then
    echo "✅ Push vers GitHub réussi: $commit_msg"
else
    echo "⚠️  Push échoué, tentative de pull et merge..."
    git pull origin main --rebase
    git push origin main
    echo "✅ Push après merge réussi: $commit_msg"
fi