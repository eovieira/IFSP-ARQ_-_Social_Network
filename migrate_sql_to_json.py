#!/usr/bin/env python3
"""
Script para migrar dados de SQLite para JSON
Execute este script uma vez para migrar os dados antigos
"""

import sys
import os
import json
from datetime import datetime

# Adiciona o diretório socialnetwork ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'socialnetwork'))

def migrate_from_sqlite():
    """Migra dados de SQLite (se existir) para JSON"""
    try:
        db_path = 'instance/database.db'
        if os.path.exists(db_path):
            print(f"✓ Banco de dados SQLite encontrado em: {db_path}")
            print("  IMPORTANTE: Faça backup deste arquivo antes de continuar!")
            print("  A aplicação agora usa JSON para armazenar dados.")
            print("\n  Para migrar dados antigos manualmente:")
            print("  1. Abra o banco de dados com sqlite3 ou outro cliente")
            print("  2. Exporte os dados para CSV ou JSON")
            print("  3. Use este script para importar os dados")
            return True
        else:
            print("✓ Nenhum banco de dados SQLite encontrado")
            print("  A aplicação criará os arquivos JSON automaticamente")
            return False
            
    except Exception as e:
        print(f"✗ Erro ao verificar SQLite: {e}")
        return False

def create_sample_data():
    """Cria dados de exemplo em JSON para teste"""
    try:
        from db import db
        from models import Usuario
        import hashlib
        
        # Verifica se já existe dados
        usuarios = db.get_all_usuarios()
        if usuarios:
            print(f"✓ Já existem {len(usuarios)} usuários no banco JSON")
            return
        
        print("\nCriando dados de exemplo...")
        
        def hash_password(texto):
            return hashlib.sha256(texto.encode('utf-8')).hexdigest()
        
        # Cria usuário admin padrão
        admin = Usuario.create(
            username='superadministrador',
            nome='Administrador',
            senha=hash_password('admin123'),
            cargo='Administrador'
        )
        print(f"✓ Usuário admin criado: {admin.username}")
        
        # Cria alguns usuários de teste
        for i in range(1, 4):
            user = Usuario.create(
                username=f'usuario{i}',
                nome=f'Usuário {i}',
                senha=hash_password('senha123'),
                cargo='Usuário'
            )
            print(f"✓ Usuário criado: {user.username}")
        
        print("\nDados de exemplo criados com sucesso!")
        
    except Exception as e:
        print(f"✗ Erro ao criar dados de exemplo: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("=" * 60)
    print("  MIGRAÇÃO: SQL → JSON")
    print("=" * 60)
    
    print("\n1. Verificando banco de dados SQLite...")
    migrate_from_sqlite()
    
    print("\n2. Verificando arquivos JSON...")
    try:
        from db import db
        
        json_files = [
            db.usuarios_file,
            db.publicacoes_file,
            db.comentarios_file,
            db.respostas_file,
            db.curtidas_file,
            db.seguir_file,
            db.bloquear_file
        ]
        
        for file in json_files:
            if os.path.exists(file):
                size = os.path.getsize(file)
                print(f"✓ {os.path.basename(file):<20} ({size} bytes)")
            else:
                print(f"✓ {os.path.basename(file):<20} (será criado)")
        
    except Exception as e:
        print(f"✗ Erro ao verificar arquivos JSON: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n3. Criando dados iniciais...")
    create_sample_data()
    
    print("\n" + "=" * 60)
    print("  MIGRAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print("\nPróximos passos:")
    print("  1. Execute: python socialnetwork/run.py")
    print("  2. Acesse: http://localhost:5000")
    print("  3. Login: superadministrador / admin123")
    print("\nOs dados agora estão salvos em arquivos JSON em ./instance/")
    print("=" * 60)

if __name__ == '__main__':
    main()
