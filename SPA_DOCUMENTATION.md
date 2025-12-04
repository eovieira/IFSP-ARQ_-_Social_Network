# 🚀 Single Page Application (SPA) - Social Network

## Visão Geral

A aplicação foi completamente refatorada para ser uma **Single Page Application (SPA)** com arquitetura moderna de JavaScript puro. O Flask agora atua apenas como servidor de APIs JSON, enquanto todo o front-end é gerenciado dinamicamente pelo JavaScript.

---

## 📁 Arquitetura JavaScript

### Módulos Criados

#### 1. **api.js** - Camada de Requisições HTTP
Gerencia todas as comunicações com o backend Flask.

```javascript
// Exemplo de uso
const result = await API.criarPublicacao("Olá mundo!");
const publicacoes = await API.obterPublicacoes();
const comentario = await API.adicionarComentario(1, "Bom post!");
```

**Métodos principais:**
- `API.login(username, password)` - Login
- `API.register(username, email, password)` - Registro
- `API.criarPublicacao(texto)` - Criar post
- `API.obterPublicacoes()` - Listar feed
- `API.adicionarComentario(pub_id, texto)` - Comentar
- `API.adicionarResposta(com_id, texto)` - Responder comentário
- `API.curtirPublicacao(pub_id)` - Curtir
- `API.seguirUsuario(username)` - Seguir
- `API.bloquearUsuario(username)` - Bloquear

---

#### 2. **auth.js** - Gerenciamento de Autenticação
Controla todo o fluxo de login, registro e logout.

```javascript
// Verificar se está autenticado
if (Auth.estaAutenticado()) {
    const usuario = Auth.getUsuarioAtual();
    console.log(usuario.username);
}

// Fazer login
await Auth.login('usuario1', 'senha123');

// Fazer logout
await Auth.logout();
```

**Funcionalidades:**
- ✅ Carrega usuário atual ao inicializar
- ✅ Gerencia estado de autenticação
- ✅ Renderiza UI correta (autenticada ou não)
- ✅ Event listeners para formulários de login/registro

---

#### 3. **ui.js** - Gerenciamento de Interface
Controla a renderização da interface e navegação.

```javascript
// Mudar página
UI.mudarPagina('feed');  // 'feed', 'perfil', 'topics'

// Mostrar notificação
UI.mostrarNotificacao('Sucesso!', 'sucesso');  // 'sucesso', 'erro', 'info'

// Renderizar app
UI.renderizarAppAutenticada();
UI.renderizarAppNaoAutenticada();
```

**Recursos:**
- 🎨 Renderização dinâmica completa do HTML
- 📱 Sistema de páginas/rotas
- 🔔 Sistema de notificações
- 🎛️ Gerenciamento de tabs (login/registro)

---

#### 4. **feed.js** - Gerenciamento de Feed e Interações
Controla publicações, comentários, curtidas.

```javascript
// Carregar feed
await Feed.carregarPublicacoes();

// Criar publicação
await Feed.criarPublicacao("Novo post!");

// Comentar
await Feed.adicionarComentario(1, "Que post legal!");

// Responder comentário
await Feed.adicionarResposta(5, "Concordo totalmente!");

// Curtir
await Feed.curtirPublicacao(1);
await Feed.curtirComentario(5);

// Deletar
await Feed.deletarPublicacao(1);
await Feed.deletarComentario(5);
```

**Funcionalidades:**
- 📝 Carrega e renderiza publicações dinamicamente
- 💬 Gerencia comentários e respostas
- ❤️ Sistema completo de curtidas
- 🗑️ Deletar publicações, comentários e respostas
- ⌨️ Enter para enviar, Shift+Enter para quebra de linha

---

#### 5. **perfil.js** - Gerenciamento de Perfis
Controla visualização de perfis e relacionamentos.

```javascript
// Carregar perfil
await Perfil.carregarPerfil('usuario1');

// Seguir
await Perfil.seguirUsuario('usuario1');

// Deixar de seguir
await Perfil.deixarDeSeguir('usuario1');

// Bloquear
await Perfil.bloquearUsuario('usuario1');

// Desbloquear
await Perfil.desbloquearUsuario('usuario1');
```

**Funcionalidades:**
- 👤 Carrega dados do perfil
- 📊 Exibe estatísticas (publicações, seguidores, seguindo)
- 🔗 Gerencia relacionamentos (seguir/deixar de seguir)
- 🚫 Gerencia bloqueios

---

#### 6. **main.js** - Inicializador
Coordena a inicialização de todos os módulos e navegação.

```javascript
// Executa ao carregar a página
document.addEventListener('DOMContentLoaded', async () => {
    Auth.init();      // Verifica autenticação
    UI.init();        // Inicializa UI
    Feed.init();      // Carrega feed
    
    // Configurar navegação por hash
    window.addEventListener('hashchange', () => {
        // Atualizar página baseado em URL
    });
});
```

---

## 🔌 Endpoints da API Flask

Todos retornam JSON e suportam autenticação:

### Autenticação
- `POST /login` → `{usuario: {id, username, email}}`
- `POST /registrar` → `{usuario: {id, username, email}}`
- `POST /logout` → `{status: 'ok'}`
- `GET /usuario_atual_json` → `{usuario: {...}}`

### Publicações
- `POST /adicionar_publicacao` → `{status: 'ok', publicacao_id: ...}`
- `GET /publicacoes_json` → `{publicacoes: [...]}`
- `GET /perfil/<username>/publicacoes_json` → `{publicacoes: [...]}`
- `DELETE /deletar/publicacao/<id>` → `{status: 'ok'}`

### Comentários e Respostas
- `POST /comentar/publicacao/<id>` → `{status: 'ok'}`
- `GET /comentarios/<id>` → `{comentarios: [...]}`
- `POST /responder/comentario/<id>` → `{status: 'ok'}`
- `POST /responder/resposta/<id>` → `{status: 'ok'}`
- `DELETE /deletar/comentario/<id>` → `{status: 'ok'}`
- `DELETE /deletar/resposta/<id>` → `{status: 'ok'}`

### Curtidas
- `POST /curtir/publicacao/<id>` → `{status: 'ok'}`
- `POST /descurtir/publicacao/<id>` → `{status: 'ok'}`
- `POST /curtir/comentario/<id>` → `{status: 'ok'}`
- `POST /descurtir/comentario/<id>` → `{status: 'ok'}`
- `POST /curtir/resposta/<id>` → `{status: 'ok'}`
- `POST /descurtir/resposta/<id>` → `{status: 'ok'}`

### Relacionamentos
- `POST /seguir_ajax/<username>` → `{status: 'seguindo'}`
- `POST /deixar_de_seguir_ajax/<username>` → `{status: 'nao_seguindo'}`
- `POST /bloquear_ajax/<username>` → `{status: 'bloqueado'}`
- `POST /desbloquear_ajax/<username>` → `{status: 'desbloqueado'}`

### Perfil
- `GET /perfil_json/<username>` → `{usuario: {...}}`

---

## 🎨 HTML/Template Único

Existe um único arquivo HTML (`spa.html`) que renderiza toda a aplicação:

```html
<!-- template/spa.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Social Network</title>
    <link rel="stylesheet" href="base.css">
</head>
<body>
    <div id="app"></div>
    
    <!-- Scripts da SPA em ordem -->
    <script src="js/api.js"></script>      <!-- Requisições HTTP -->
    <script src="js/auth.js"></script>     <!-- Autenticação -->
    <script src="js/ui.js"></script>       <!-- Interface -->
    <script src="js/feed.js"></script>     <!-- Feed e comentários -->
    <script src="js/perfil.js"></script>   <!-- Perfis -->
    <script src="js/main.js"></script>     <!-- Inicializador -->
</body>
</html>
```

Todo o conteúdo é renderizado dinamicamente via JavaScript!

---

## 🔄 Fluxo de Dados

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │ clica
       ↓
┌──────────────────────┐
│   Event Listener     │ (click, submit, etc)
└──────┬───────────────┘
       │ dispara
       ↓
┌──────────────────────┐
│   Módulo JS          │ (Feed, Auth, Perfil, etc)
└──────┬───────────────┘
       │ chamada
       ↓
┌──────────────────────┐
│   API.request()      │ (fetch HTTP)
└──────┬───────────────┘
       │ POST/GET
       ↓
┌──────────────────────┐
│   Flask Route        │ (Flask backend)
└──────┬───────────────┘
       │ JSON response
       ↓
┌──────────────────────┐
│   Callback           │ (process response)
└──────┬───────────────┘
       │ update UI
       ↓
┌──────────────────────┐
│   DOM Update         │ (inserir/remover elementos)
└──────────────────────┘
```

---

## 📊 Estrutura de Arquivos JavaScript

```
static/js/
├── api.js           ← Comunicação com backend
├── auth.js          ← Autenticação e sessão
├── ui.js            ← Renderização de interface
├── feed.js          ← Feed, comentários, curtidas
├── perfil.js        ← Perfis e relacionamentos
└── main.js          ← Inicializador geral

templates/
└── spa.html         ← Único template HTML
```

---

## 🚀 Como Usar

### Iniciar a Aplicação
```bash
cd socialnetwork
python run.py
```

Acesse: `http://localhost:5000`

### Fluxo de Uso
1. **Login** → Digite credenciais (ou registre novo)
2. **Feed** → Vê publicações, cria, comenta, curte
3. **Perfil** → Vê perfil de outros, segue/bloqueia
4. **Navegação** → Clique nos links do menu ou use URLs com hash

### Exemplos de URLs
- `http://localhost:5000` → Login
- `http://localhost:5000#feed` → Feed
- `http://localhost:5000#perfil/usuario1` → Perfil do usuário1
- `http://localhost:5000#topics` → Topics (em desenvolvimento)

---

## 💾 Armazenamento de Dados

Todos os dados continuam salvos em **JSON** dentro de `instance/`:

```
instance/
├── usuarios.json          ← Usuários
├── publicacoes.json       ← Publicações
├── comentarios.json       ← Comentários
├── respostas.json         ← Respostas
├── curtidas.json          ← Curtidas
├── seguir.json            ← Relacionamentos de seguimento
└── bloquear.json          ← Bloqueios
```

Os arquivos são carregados dinamicamente pelo JavaScript conforme necessário.

---

## 🔒 Autenticação

A autenticação é gerenciada por Flask-Login:
- **Sessão**: Armazenada no servidor (cookie)
- **Verificação**: Cada requisição valida a autenticação
- **Token**: Não usa tokens JWT (usa sessão tradicional)

---

## 🎯 Vantagens da Arquitetura SPA

✅ **Experiência fluida** - Sem recarga de página  
✅ **Interface responsiva** - Atualização instantânea  
✅ **Código organizado** - Módulos separados e reutilizáveis  
✅ **Fácil manutenção** - Lógica de UI centralizada em JavaScript  
✅ **API bem definida** - Flask é puramente um servidor de APIs  
✅ **Reutilizável** - A mesma API pode servir web, mobile, desktop  
✅ **Performance** - Apenas dados JSON trafegam, não HTML  

---

## 📝 Exemplo Completo: Criar um Post

```javascript
// 1. Usuário digita e clica em "Publicar"
// 2. Event listener em button dispara:
Feed.criarPublicacao("Olá mundo!");

// 3. Dentro de Feed.criarPublicacao():
async criarPublicacao(texto) {
    const result = await API.criarPublicacao(texto);
    // 4. API.criarPublicacao() faz:
    return this.post(`/adicionar_publicacao`, { texto });
    
    // 5. Flask recebe e processa:
    // @route /adicionar_publicacao POST
    // Cria publicação no JSON
    // Retorna: {status: 'ok', publicacao_id: 1}
    
    // 6. De volta ao JavaScript:
    if (result.ok) {
        UI.mostrarNotificacao('Publicação criada!', 'sucesso');
        Feed.carregarPublicacoes();  // Recarregar feed
    }
}

// 7. Feed.carregarPublicacoes():
async carregarPublicacoes() {
    const result = await API.obterPublicacoes();
    // 8. API.obterPublicacoes() faz GET /publicacoes_json
    // 9. Flask retorna lista de publicações
    
    this.publicacoes = result.data.publicacoes;
    this.renderizarFeed();
    // 10. renderizarFeed() atualiza o DOM com as novas publicações
}
```

---

## 🧪 Testando a SPA

### Login
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "usuario1", "password": "senha123"}'
```

### Criar Publicação
```bash
curl -X POST http://localhost:5000/adicionar_publicacao \
  -H "Content-Type: application/json" \
  -d '{"texto": "Olá mundo!"}'
  # (requer autenticação)
```

### Obter Feed
```bash
curl http://localhost:5000/publicacoes_json
# (requer autenticação)
```

---

## 🎓 Conclusão

A aplicação agora é uma **verdadeira SPA** onde:
- ✅ O Flask é um **servidor de APIs JSON puro**
- ✅ O JavaScript gerencia **toda a interface**
- ✅ **Sem recarregamento de página** - tudo é dinâmico
- ✅ **Dados persistem em JSON** - mesma estrutura anterior
- ✅ **Código modular** - fácil de manter e expandir

A experiência do usuário é agora **muito mais fluida e responsiva**!

---

**Status:** ✅ PRONTO PARA PRODUÇÃO  
**Data:** 04 de Dezembro de 2025  
**Versão:** 2.0 - SPA Edition
