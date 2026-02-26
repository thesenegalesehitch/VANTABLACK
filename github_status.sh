#!/bin/bash

# Afficher la bannière
source .trae/display_banner.sh

# Status GitHub
echo "📊 Status du dépôt GitHub"
echo ""

echo "🔍 Status local:"
git status
echo ""

echo "📜 Historique récent (5 derniers commits):"
git log --oneline -5
echo ""

echo "🌐 Branches distantes:"
git branch -r
echo ""

echo "💡 Prochaines actions:"
echo "• ./github_commit.sh - Commit interactif"
echo "• ./github_push.sh 'message' - Commit et push automatique"
echo "• git pull origin main - Mettre à jour depuis GitHub"