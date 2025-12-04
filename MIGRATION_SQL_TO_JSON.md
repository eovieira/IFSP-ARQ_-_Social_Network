# Migração de SQL para JSON

Este documento descreve a migração da aplicação de um banco de dados SQL (SQLite com SQLAlchemy) para armazenamento em arquivos JSON.

## O que mudou?

### Antes (SQL)
- Banco de dados: SQLite (`database.db`)
- ORM: Flask-SQLAlchemy
- Persistência: Transações SQL
- Arquitetura: Models com ORM

### Depois (JSON)
- Armazenamento: Arquivos JSON
- Gerenciamento: Classe `JSONDatabase`
- Persistência: Leitura/escrita de arquivos
- Arquitetura: Models com métodos estáticos

## Estrutura de Dados JSON

Os dados são armazenados em arquivos JSON individuais na pasta `instance/`:

```
instance/
├── usuarios.json          # Dados dos usuários
├── publicacoes.json       # Posts/publicações
├── comentarios.json       # Comentários em publicações
├── respostas.json         # Respostas em comentários
├── curtidas.json          # Likes em posts/comentários/respostas
├── seguir.json            # Relacionamentos de seguimento
└── bloquear.json          # Relacionamentos de bloqueio
```

### Exemplo: usuarios.json
```json
[
  {
    "id": 1,
    "username": "superadministrador",
    "nome": "Administrador",
    "senha": "hash_da_senha",
    "cargo": "Administrador",
    "foto_perfil": null
  },
  {
    "id": 2,
    "username": "usuario1",
    "nome": "Usuário Um",
    "senha": "hash_da_senha",
    "cargo": "Usuário",
    "foto_perfil": "user_2_perfil.png"
  }
]
```

## Migrando de SQL

### Se você tinha dados em SQL:

1. **Faça backup do banco antigo:**
   ```bash
   cp instance/database.db instance/database.db.backup
   ```

2. **Execute o script de migração:**
   ```bash
   python migrate_sql_to_json.py
   ```

3. **O script irá:**
   - Detectar se você tem um banco SQL antigo
   - Criar os arquivos JSON necessários
   - Criar usuários de exemplo para teste

### Se você está começando do zero:

1. **Execute o script de migração:**
   ```bash
   python migrate_sql_to_json.py
   ```

2. **Isso criará:**
   - Arquivos JSON vazios em `instance/`
   - Um usuário admin padrão: `superadministrador` / `admin123`
   - Usuários de teste

## Usando a Aplicação

### Iniciando a aplicação:
```bash
cd socialnetwork
python run.py
```

### Acessar em:
```
http://localhost:5000
```

### Usuários padrão (se criados via script):
- **Usuário**: `superadministrador`
- **Senha**: `admin123`

## Camadas de Abstração

### 1. Banco de Dados (`db.py`)
```python
from db import db

# Operações básicas
db.get_usuario_by_id(1)
db.save_usuario(usuario_dict)
db.get_publicacoes_by_usuario(user_id)
```

### 2. Modelos (`models.py`)
```python
from models import Usuario, Publicacao, Comentario

# Operações OOP
usuario = Usuario.query_by_id(1)
usuario.nome = "Novo Nome"
usuario.save()

pub = Publicacao.create(texto="...", usuario_id=1)
comentario = pub.comentar(usuario, "texto")
```

### 3. Rotas
As rotas usam os modelos de forma transparente.

## Vantagens do JSON

✅ **Simplicidade**: Sem dependência de banco de dados externo
✅ **Portabilidade**: Arquivos JSON são facilmente transportáveis
✅ **Debugging**: Dados em texto puro, fácil de visualizar
✅ **Sem setup**: Não precisa instalar/configurar PostgreSQL, MySQL, etc
✅ **Sincronização**: Fácil de sincronizar entre máquinas

## Desvantagens (considere para produção)

⚠️ **Performance**: Não é escalável para milhões de registros
⚠️ **Concorrência**: Lock baseado em arquivo pode ter contenção
⚠️ **Queries**: Sem índices, todas as buscas são O(n)
⚠️ **Transações**: Sem suporte a transações ACID nativas

> **Para produção**: Considere usar PostgreSQL, MongoDB ou outro banco real

## Estrutura de Código Importante

### Classe JSONDatabase (db.py)
Gerencia leitura/escrita de arquivos JSON com lock para segurança de thread.

### Métodos principais:
- `get_usuario_by_id(id)`
- `save_usuario(dict)`
- `get_publicacoes_by_usuario(user_id)`
- `save_comentario(dict)`
- etc.

### Modelos (models.py)
Encapsulam a lógica de negócio com métodos estáticos para queries.

Exemplo:
```python
class Usuario(UserMixin):
    @staticmethod
    def create(username, nome, senha, cargo):
        # Cria novo usuário
    
    @staticmethod
    def query_by_id(user_id):
        # Busca por ID
    
    def save(self):
        # Salva mudanças
```

## Troubleshooting

### Erro: "Arquivo não encontrado"
- Verifique se a pasta `instance/` existe
- Execute `python migrate_sql_to_json.py`

### Erro: "Permissão negada"
- Verifique permissões da pasta `instance/`
- No Linux: `chmod 755 instance/`

### Dados não salvam
- Verifique espaço em disco
- Verifique permissões de escrita em `instance/`

### Performance lenta
- Para mais de 10k registros, considere migrar para um banco real
- Use `pypy` para melhor performance

## Próximos Passos (Opcional)

Se em futuro quiser migrar para um banco de dados real:

1. **PostgreSQL com SQLAlchemy** (recomendado)
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://...'
   ```

2. **MongoDB com MongoEngine**
   - Melhor para dados não-estruturados

3. **Supabase/Firebase**
   - Para hosting em cloud

---

**Documentação gerada em**: Dezembro 2024
**Versão**: 1.0
