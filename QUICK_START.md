# 📱 Guia Rápido - Social Network SPA

## 🚀 Quick Start

### 1. Iniciar a Aplicação
```bash
cd /workspaces/IFSP-ARQ_-_Social_Network/socialnetwork
python run.py
```

### 2. Acessar
```
http://localhost:5000
```

---

## 👤 Credenciais de Teste

| Usuário | Senha |
|---------|-------|
| superadministrador | admin123 |
| usuario1 | senha123 |
| usuario2 | senha123 |
| usuario3 | senha123 |

---

## 🎯 Recursos Disponíveis

### 📝 Feed
- ✅ Criar publicação
- ✅ Ver publicações do feed
- ✅ Comentar em publicações
- ✅ Responder comentários
- ✅ Curtir publicações, comentários e respostas
- ✅ Deletar próprios posts/comentários

### 👥 Perfis
- ✅ Ver perfil de outros usuários
- ✅ Ver publicações do perfil
- ✅ Seguir/deixar de seguir
- ✅ Bloquear/desbloquear
- ✅ Ver estatísticas (seguidores, seguindo)

### ⚙️ Navegação
- ✅ Menu superior com links
- ✅ Navegação por URL com hash (#feed, #perfil/usuario1)
- ✅ Autenticação integrada
- ✅ Logout

---

## 🔧 Arquitetura Interna

### Front-end (JavaScript)
```
static/js/
├── api.js       → Comunicação com servidor
├── auth.js      → Login/Logout
├── ui.js        → Renderização de interface
├── feed.js      → Posts e comentários
├── perfil.js    → Perfis e relacionamentos
└── main.js      → Inicializador
```

### Back-end (Flask)
```
routes/
├── auth.py              → Login, registro, logout
├── feed.py              → Feed de publicações
├── interacoes.py        → Curtidas, comentários
├── perfil.py            → Perfis, seguir, bloquear
└── comentarios_json.py  → Endpoints JSON
```

### Dados (JSON)
```
instance/
├── usuarios.json        → Usuários
├── publicacoes.json     → Posts
├── comentarios.json     → Comentários
├── respostas.json       → Respostas
├── curtidas.json        → Curtidas
├── seguir.json          → Seguimentos
└── bloquear.json        → Bloqueios
```

---

## 📊 Fluxo de Dados

```
Usuário → JavaScript → API JSON → Flask → JSON Files
                        ↓
                      Response
                        ↓
                    JavaScript
                        ↓
                      DOM Update
```

---

## 🎨 Interface

### Tema
- **Cores**: Azul (#007bff), Cinza, Branco
- **Fonte**: System fonts (Segoe UI, Roboto, etc)
- **Responsivo**: Adapta para mobile, tablet, desktop
- **Componentes**: Botões, formulários, cards, notificações

### Páginas
1. **Login/Registro** - Formulários de autenticação
2. **Feed** - Timeline com publicações
3. **Perfil** - Visualizar perfil de usuários
4. **Topics** - Em desenvolvimento

---

## 🔐 Segurança

- ✅ Senhas com hash SHA256
- ✅ Validação de autenticação em todas as rotas
- ✅ Verificação de permissões (pode deletar próprio post)
- ✅ Bloqueio de usuários para privacidade
- ✅ HTTPS recomendado em produção

---

## 💡 Casos de Uso

### Caso 1: Criar e Comentar um Post
```
1. Fazer login
2. Digitar texto no campo "O que está pensando?"
3. Clicar "Publicar"
4. Ver post no feed
5. Clicar "Comentar"
6. Digitar comentário
7. Pressionar Enter ou clicar enviar
8. Ver comentário aparecer em tempo real
```

### Caso 2: Seguir um Usuário
```
1. Clicar em qualquer nome de usuário (link azul)
2. Ir para perfil do usuário
3. Clicar botão "Seguir"
4. Botão muda para "Deixar de seguir"
5. Posts deste usuário aparecem no topo do feed
```

### Caso 3: Bloquear um Usuário
```
1. Ir para perfil do usuário
2. Clicar botão "Bloquear"
3. Posts dele não aparecem no seu feed
4. Ele não pode ver seus posts
5. Clicar "Desbloquear" para remover bloqueio
```

---

## 🐛 Troubleshooting

### "Não consegui fazer login"
- ✓ Verifique usuário e senha
- ✓ Tente com: usuario1 / senha123
- ✓ Verifique se Flask está rodando (porta 5000)

### "Posts não aparecem no feed"
- ✓ Faça refresh da página (F5)
- ✓ Clique em "Feed" no menu
- ✓ Crie uma nova publicação

### "Não consigo comentar"
- ✓ Verifique se está logado
- ✓ Clique no ícone de comentário primeiro
- ✓ Tente pressionar Enter ou clicar no botão

### "A aplicação carregou em branco"
- ✓ Abra o console (F12)
- ✓ Procure por erros vermelhos
- ✓ Tente fazer refresh (Ctrl+Shift+R)

---

## 📚 APIs Disponíveis

Todas as requisições usam `Content-Type: application/json`

### Autenticação
```
POST /login
POST /registrar
POST /logout
GET /usuario_atual_json
```

### Publicações
```
POST /adicionar_publicacao
GET /publicacoes_json
DELETE /deletar/publicacao/{id}
```

### Comentários
```
POST /comentar/publicacao/{id}
POST /responder/comentario/{id}
DELETE /deletar/comentario/{id}
GET /comentarios/{id}
```

### Curtidas
```
POST /curtir/publicacao/{id}
POST /descurtir/publicacao/{id}
POST /curtir/comentario/{id}
POST /descurtir/comentario/{id}
```

### Relacionamentos
```
POST /seguir_ajax/{username}
POST /deixar_de_seguir_ajax/{username}
POST /bloquear_ajax/{username}
POST /desbloquear_ajax/{username}
```

### Perfis
```
GET /perfil_json/{username}
GET /perfil/{username}/publicacoes_json
```

---

## 📱 Dispositivos Suportados

- ✅ Desktop (Chrome, Firefox, Safari, Edge)
- ✅ Tablet (iPad, Android Tablet)
- ✅ Mobile (iPhone, Android Phone)

---

## 🎓 O que foi Implementado

### Versão 1.0 - SQL → JSON
- Migração de SQLAlchemy para JSON puro
- Todas as funcionalidades mantidas
- Dados persistem em arquivos JSON

### Versão 2.0 - HTML → SPA (Atual)
- Conversão para Single Page Application
- JavaScript gerencia toda a interface
- Flask é apenas um servidor de APIs
- Navegação sem recarregar página
- Experiência 100% dinâmica

---

## 🚀 Próximos Passos Possíveis

- [ ] Adicionar notificações em tempo real (WebSocket)
- [ ] Implementar busca de usuários/posts
- [ ] Adicionar likes/reações animadas
- [ ] Implementar timeline em tempo real
- [ ] Adicionar imagens/mídia em posts
- [ ] Sistema de mensagens privadas
- [ ] Implementar hashtags
- [ ] Analytics e estatísticas

---

## 📞 Suporte

Para problemas ou dúvidas, consulte:
1. `SPA_DOCUMENTATION.md` - Documentação técnica completa
2. Console do navegador (F12) - Erros JavaScript
3. Terminal Flask - Logs de servidor

---

**Versão:** 2.0 SPA Edition  
**Data:** 04 de Dezembro de 2025  
**Status:** ✅ Totalmente Funcional
