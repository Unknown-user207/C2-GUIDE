#!/bin/bash
# Backup memory and context

BACKUP_DIR="backups/$(date +%Y-%m-%d)"
mkdir -p $BACKUP_DIR
cp guide_memory.db $BACKUP_DIR/
cp project_context.json $BACKUP_DIR/
echo "✅ Backup saved to $BACKUP_DIR"