#!/usr/bin/env python3
"""
Automated Database Backup System
Cria backups do banco de dados com rotação automática

Versão: 1.0.0
Data: 02/01/2026
"""

import os
import sys
import shutil
import gzip
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import json


class DatabaseBackup:
    def __init__(self, db_path, backup_dir, retention_days=30, compression=True):
        self.db_path = db_path
        self.backup_dir = Path(backup_dir)
        self.retention_days = retention_days
        self.compression = compression
        
        # Criar diretório de backup se não existir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, tag=""):
        """Cria backup do banco de dados"""
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found: {self.db_path}")
            return False
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        tag_suffix = f"_{tag}" if tag else ""
        backup_filename = f"financas.db.backup_{timestamp}{tag_suffix}"
        
        if self.compression:
            backup_filename += ".gz"
        
        backup_path = self.backup_dir / backup_filename
        
        try:
            print(f"🔄 Creating backup: {backup_filename}")
            
            if self.compression:
                # Backup comprimido
                with open(self.db_path, 'rb') as f_in:
                    with gzip.open(backup_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                # Backup simples
                shutil.copy2(self.db_path, backup_path)
            
            # Obter tamanhos
            original_size = os.path.getsize(self.db_path)
            backup_size = os.path.getsize(backup_path)
            
            compression_ratio = (1 - backup_size / original_size) * 100 if self.compression else 0
            
            print(f"✅ Backup created successfully")
            print(f"   Original size: {original_size / 1024 / 1024:.2f} MB")
            print(f"   Backup size: {backup_size / 1024 / 1024:.2f} MB")
            if self.compression:
                print(f"   Compression ratio: {compression_ratio:.1f}%")
            print(f"   Location: {backup_path}")
            
            # Salvar metadata
            metadata = {
                'timestamp': timestamp,
                'tag': tag,
                'original_size': original_size,
                'backup_size': backup_size,
                'compression': self.compression,
                'db_path': str(self.db_path),
                'backup_path': str(backup_path)
            }
            
            metadata_path = backup_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return False
    
    def list_backups(self):
        """Lista todos os backups disponíveis"""
        backups = []
        
        for file in self.backup_dir.glob("financas.db.backup_*"):
            if file.suffix in ['.gz', ''] and not file.suffix == '.json':
                stat = file.stat()
                backups.append({
                    'filename': file.name,
                    'path': str(file),
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_mtime),
                    'age_days': (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
                })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def cleanup_old_backups(self):
        """Remove backups antigos baseado na política de retenção"""
        backups = self.list_backups()
        
        deleted = 0
        freed_space = 0
        
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for backup in backups:
            if backup['created'] < cutoff_date:
                try:
                    Path(backup['path']).unlink()
                    
                    # Remover metadata se existir
                    metadata_path = Path(backup['path']).with_suffix('.json')
                    if metadata_path.exists():
                        metadata_path.unlink()
                    
                    deleted += 1
                    freed_space += backup['size']
                    
                    print(f"🗑️  Deleted old backup: {backup['filename']} (age: {backup['age_days']} days)")
                    
                except Exception as e:
                    print(f"⚠️  Could not delete {backup['filename']}: {e}")
        
        if deleted > 0:
            print(f"\n✅ Cleanup complete:")
            print(f"   Deleted: {deleted} backup(s)")
            print(f"   Freed space: {freed_space / 1024 / 1024:.2f} MB")
        else:
            print("✅ No old backups to clean up")
        
        return deleted
    
    def restore_backup(self, backup_path, target_path=None):
        """Restaura backup do banco de dados"""
        if not os.path.exists(backup_path):
            print(f"❌ Backup not found: {backup_path}")
            return False
        
        target_path = target_path or self.db_path
        
        # Criar backup do banco atual antes de restaurar
        if os.path.exists(target_path):
            print("⚠️  Creating safety backup of current database...")
            safety_backup = f"{target_path}.pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(target_path, safety_backup)
            print(f"   Safety backup: {safety_backup}")
        
        try:
            print(f"🔄 Restoring backup from {backup_path}")
            
            if backup_path.endswith('.gz'):
                # Descomprimir e restaurar
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(target_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                # Restaurar diretamente
                shutil.copy2(backup_path, target_path)
            
            print(f"✅ Database restored successfully to {target_path}")
            
            # Verificar integridade
            print("🔍 Verifying database integrity...")
            conn = sqlite3.connect(target_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            conn.close()
            
            if result == 'ok':
                print("✅ Database integrity check passed")
                return True
            else:
                print(f"⚠️  Database integrity check failed: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Error restoring backup: {e}")
            return False
    
    def print_backup_list(self):
        """Imprime lista formatada de backups"""
        backups = self.list_backups()
        
        if not backups:
            print("No backups found")
            return
        
        print("\n" + "=" * 100)
        print("📦 AVAILABLE BACKUPS")
        print("=" * 100)
        print(f"{'#':<4} {'Filename':<50} {'Size':<12} {'Age':<15} {'Created':<20}")
        print("-" * 100)
        
        for i, backup in enumerate(backups, 1):
            size_mb = backup['size'] / 1024 / 1024
            age = f"{backup['age_days']} days ago" if backup['age_days'] > 0 else "Today"
            created = backup['created'].strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"{i:<4} {backup['filename']:<50} {size_mb:>8.2f} MB  {age:<15} {created:<20}")
        
        print("=" * 100)
        print(f"Total backups: {len(backups)}")
        print(f"Total size: {sum(b['size'] for b in backups) / 1024 / 1024:.2f} MB")
        print("")


def setup_cron_job(backup_script_path, schedule="0 2 * * *"):
    """Configura cron job para backup automático (Linux/Mac)"""
    cron_command = f"{schedule} /usr/bin/python3 {backup_script_path} --auto\n"
    
    print("\n📅 To setup automatic backups, add this to crontab:")
    print("   Run: crontab -e")
    print("   Add line:")
    print(f"   {cron_command}")
    print("\n   Schedule explanation:")
    print("   0 2 * * *  = Every day at 2:00 AM")
    print("   0 */6 * * * = Every 6 hours")
    print("   0 0 * * 0  = Every Sunday at midnight")


def main():
    parser = argparse.ArgumentParser(description='Database Backup System')
    parser.add_argument('--db', default='financas.db', help='Database path')
    parser.add_argument('--backup-dir', default='backups', help='Backup directory')
    parser.add_argument('--retention-days', type=int, default=30, 
                        help='Days to keep backups (default: 30)')
    parser.add_argument('--no-compression', action='store_true', 
                        help='Disable compression')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create a backup')
    backup_parser.add_argument('--tag', default='', help='Tag for backup')
    
    # List command
    subparsers.add_parser('list', help='List available backups')
    
    # Cleanup command
    subparsers.add_parser('cleanup', help='Remove old backups')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore a backup')
    restore_parser.add_argument('backup_file', help='Backup file to restore')
    restore_parser.add_argument('--target', help='Target database path (default: original)')
    
    # Setup cron
    subparsers.add_parser('setup-cron', help='Show cron setup instructions')
    
    # Auto (for cron)
    subparsers.add_parser('auto', help='Automatic backup (for cron)')
    
    args = parser.parse_args()
    
    # Se nenhum comando, mostrar ajuda
    if not args.command:
        parser.print_help()
        return 0
    
    backup_system = DatabaseBackup(
        db_path=args.db,
        backup_dir=args.backup_dir,
        retention_days=args.retention_days,
        compression=not args.no_compression
    )
    
    if args.command == 'backup':
        success = backup_system.create_backup(tag=args.tag)
        return 0 if success else 1
    
    elif args.command == 'list':
        backup_system.print_backup_list()
        return 0
    
    elif args.command == 'cleanup':
        backup_system.cleanup_old_backups()
        return 0
    
    elif args.command == 'restore':
        success = backup_system.restore_backup(
            backup_path=args.backup_file,
            target_path=args.target
        )
        return 0 if success else 1
    
    elif args.command == 'setup-cron':
        script_path = os.path.abspath(__file__)
        setup_cron_job(script_path)
        return 0
    
    elif args.command == 'auto':
        # Backup automático (silencioso em caso de sucesso)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting automatic backup...")
        success = backup_system.create_backup(tag="auto")
        if success:
            backup_system.cleanup_old_backups()
        return 0 if success else 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
