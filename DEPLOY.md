# 🚀 Guia de Deploy - Barzinhos

## 📋 Pré-requisitos

- Conta no Render.com (para backend)
- Conta no Vercel ou Netlify (para frontend)
- Git configurado
- Node.js 18+ e Python 3.11+

## 🔧 Preparação dos Arquivos

### 1. Backend Flask (Render.com)

Crie um arquivo `render.yaml` na raiz do projeto:

```yaml
services:
  - type: web
    name: barzinhos-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python src/main.py"
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: JWT_SECRET_KEY
        generateValue: true
```

### 2. Frontend React (Vercel)

Crie um arquivo `vercel.json` na pasta frontend:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

## 🌐 Deploy do Backend (Render.com)

### Passo 1: Preparar Repositório
```bash
cd barzinhos_project
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/seu-usuario/barzinhos.git
git push -u origin main
```

### Passo 2: Configurar Render
1. Acesse [render.com](https://render.com)
2. Conecte seu repositório GitHub
3. Selecione "Web Service"
4. Configure:
   - **Name**: barzinhos-api
   - **Environment**: Python 3
   - **Build Command**: `cd backend_flask && pip install -r requirements.txt`
   - **Start Command**: `cd backend_flask && python src/main.py`
   - **Root Directory**: deixe vazio

### Passo 3: Variáveis de Ambiente
No painel do Render, adicione:
- `FLASK_ENV`: production
- `SECRET_KEY`: (gerar chave aleatória)
- `JWT_SECRET_KEY`: (gerar chave aleatória)

### Passo 4: Deploy
- Clique em "Create Web Service"
- Aguarde o deploy (5-10 minutos)
- Anote a URL gerada (ex: https://barzinhos-api.onrender.com)

## 🎨 Deploy do Frontend (Vercel)

### Passo 1: Atualizar Configuração da API
No arquivo `frontend/src/lib/api.js`, atualize:

```javascript
export const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? "https://barzinhos-api.onrender.com" 
  : "http://localhost:5000";
```

### Passo 2: Deploy no Vercel
```bash
cd frontend
npm install -g vercel
vercel login
vercel --prod
```

Ou através da interface web:
1. Acesse [vercel.com](https://vercel.com)
2. Conecte seu repositório
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: frontend
   - **Build Command**: `pnpm run build`
   - **Output Directory**: dist

### Passo 3: Configurar Domínio (Opcional)
- No painel do Vercel, vá em "Domains"
- Adicione seu domínio personalizado
- Configure DNS conforme instruções

## 🔧 Configurações Adicionais

### CORS no Backend
Certifique-se que o backend aceita requisições do frontend:

```python
# Em src/main.py
CORS(app, origins=[
    "https://seu-frontend.vercel.app",
    "https://barzinhos.com.br",
    "http://localhost:5173"  # Para desenvolvimento
])
```

### Banco de Dados (Produção)
Para produção, considere migrar para PostgreSQL:

1. No Render, adicione um PostgreSQL database
2. Atualize a configuração do SQLAlchemy
3. Execute migrações

## 📊 Monitoramento

### Logs do Backend (Render)
- Acesse o dashboard do Render
- Vá em "Logs" para ver logs em tempo real
- Configure alertas para erros

### Analytics do Frontend (Vercel)
- Ative Vercel Analytics
- Configure Google Analytics (opcional)
- Monitore performance e erros

## 🔒 Segurança em Produção

### Backend
- Use HTTPS sempre
- Configure rate limiting
- Valide todos os inputs
- Use variáveis de ambiente para secrets

### Frontend
- Configure CSP headers
- Use HTTPS
- Minimize dados sensíveis no cliente

## 🚀 Automação (CI/CD)

### GitHub Actions
Crie `.github/workflows/deploy.yml`:

```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Render
        run: |
          # Render auto-deploys on push
          echo "Backend deployed automatically"

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        run: |
          # Vercel auto-deploys on push
          echo "Frontend deployed automatically"
```

## 🔄 Atualizações

### Deploy de Atualizações
1. Faça suas alterações
2. Commit e push para o repositório
3. Render e Vercel fazem deploy automático
4. Teste a aplicação em produção

### Rollback
- **Render**: Use o painel para fazer rollback
- **Vercel**: Use `vercel --prod` com commit anterior

## 📞 Troubleshooting

### Problemas Comuns

**Backend não inicia:**
- Verifique logs no Render
- Confirme variáveis de ambiente
- Teste localmente primeiro

**Frontend não conecta com API:**
- Verifique URL da API
- Confirme CORS configurado
- Teste endpoints manualmente

**Banco de dados:**
- Verifique conexão
- Execute migrações se necessário
- Backup antes de mudanças

### Comandos Úteis

```bash
# Testar API localmente
curl https://barzinhos-api.onrender.com/api/health

# Verificar logs do Vercel
vercel logs

# Rebuild no Render
# Use o botão "Manual Deploy" no dashboard
```

## 📈 Otimizações

### Performance
- Configure CDN para imagens
- Use cache para APIs
- Otimize bundle do frontend
- Configure compressão gzip

### SEO
- Configure meta tags
- Adicione sitemap.xml
- Use URLs amigáveis
- Configure Open Graph

---

**🎉 Parabéns! Sua aplicação Barzinhos está no ar!**

Acesse:
- **Frontend**: https://seu-app.vercel.app
- **API**: https://barzinhos-api.onrender.com
- **Admin**: https://seu-app.vercel.app/admin

