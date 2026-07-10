# 🚀 Instruções de Deploy — MSBD-360

## ✅ Status Atual

- **Backend (Render)**: ✅ Já está no ar
  - URL: `https://msbd360-api.onrender.com`
  - Health check: `/health` retorna `{"status":"ok","app":"MSBD-360"}`

- **Frontend (Vercel)**: ⏳ Pronto para deploy

- **Banco de dados (Supabase)**: ✅ Configurado
  - URL: `fhcfomhlvysjngwacqas.supabase.co`
  - Tabelas: Criadas automaticamente no primeiro startup do backend

---

## 📱 Deploy do Frontend no Vercel

### Passo 1: Acesse o Vercel
1. Abra https://vercel.com/dashboard
2. Faça login com sua conta GitHub (clique em "Continue with GitHub")
3. Autorize o Vercel a acessar seus repositórios

### Passo 2: Crie um novo projeto
1. Clique em "Add New..." → "Project"
2. Procure por `MSBD-360-Building-Health-Assessment` ou cole a URL:
   ```
   https://github.com/Julio-Costa-Braga/MSBD-360-Building-Health-Assessment
   ```
3. Clique em "Import"

### Passo 3: Configure o projeto
Na página de configuração:

**Root Directory:**
```
frontend
```

**Framework Preset:** 
```
Vite
```

**Build Command:** 
```
npm run build
```

**Output Directory:**
```
dist
```

### Passo 4: Configure variáveis de ambiente
Clique em "Environment Variables" e adicione:

| KEY | VALUE |
|-----|-------|
| `VITE_API_URL` | `https://msbd360-api.onrender.com/api/v1` |

### Passo 5: Deploy
Clique em "Deploy"

Aguarde 2-3 minutos e seu frontend estará no ar! 🎉

---

## 🔗 URLs Finais

Após o deploy, você terá:

- **Frontend**: `https://seu-projeto.vercel.app`
- **Backend API**: `https://msbd360-api.onrender.com`
- **Docs da API**: `https://msbd360-api.onrender.com/docs`

---

## 🐛 Troubleshooting

### Frontend não consegue conectar à API
**Solução:** Verifique se a variável `VITE_API_URL` está configurada no Vercel com o endereço correto do Render.

### Backend retorna erro de database
**Solução:** Verifique se a variável `DATABASE_URL` está configurada corretamente no Render com a senha correta do Supabase.

### Rebuild no Vercel
Se precisar fazer um novo deploy:
1. Vá ao Vercel Dashboard
2. Selecione o projeto MSBD-360
3. Clique em "Deployments"
4. Escolha a deployment desejada e clique "Redeploy"

---

## 📝 Credenciais Importantes

Guarde esses valores em um lugar seguro:

- **Supabase URL**: `https://fhcfomhlvysjngwacqas.supabase.co`
- **Render Backend**: `https://msbd360-api.onrender.com`
- **Vercel Frontend**: `https://seu-projeto.vercel.app` (será informado após deploy)

---

## ✨ Próximos passos

Após o deploy estar completo:

1. ✅ Testar a aplicação completa em produção
2. ✅ Configurar domínio customizado (opcional)
3. ✅ Habilitar HTTPS (automático no Vercel)
4. ✅ Monitorar logs em Render e Vercel

Boa sorte! 🚀
