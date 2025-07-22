# Links Diretos para Deploy

## 1. Token do Fly.io

### Opção A - Pelo Dashboard (Recomendado)
1. **Login no Fly.io**: https://fly.io/dashboard
2. **Tokens**: https://fly.io/user/personal_access_tokens
3. Clique em **"Create token"**
4. Nome: `github-actions-deploy`
5. Copie o token gerado

### Opção B - Pelo Terminal
```bash
fly auth token
```

## 2. GitHub Repository Secrets

### Criar novo repositório primeiro:
1. **Criar repo**: https://github.com/new
   - Nome sugerido: `dashboard-estoque-v2`
   - Privado ou Público (sua escolha)
   - NÃO inicialize com README

### Adicionar o Secret:
Após criar o repositório, use este link direto:
```
https://github.com/SEU_USUARIO/dashboard-estoque-v2/settings/secrets/actions/new
```

Substitua `SEU_USUARIO` pelo seu usuário do GitHub.

Ou navegue manualmente:
1. Settings → Secrets and variables → Actions → New repository secret
2. Nome: `FLY_API_TOKEN`
3. Value: Cole o token do Fly.io

## 3. Configurar Git Local

Como descobrimos que seu email é `rodrigo@phoenixinjecao.com.br`, vamos configurar o repositório:

```bash
# No diretório dashboard-v2
cd /Users/rodrigo/Documents/DashboardNovo/dashboard-v2

# Remover remote antigo (se existir)
git remote remove origin

# Adicionar novo remote (substitua SEU_USUARIO)
git remote add origin https://github.com/SEU_USUARIO/dashboard-estoque-v2.git

# Push inicial
git push -u origin main
```

## 4. Verificar Deploy

Após o push, acompanhe o deploy em:
```
https://github.com/SEU_USUARIO/dashboard-estoque-v2/actions
```

## Resumo dos Passos:

1. ✅ Obter token Fly.io: https://fly.io/user/personal_access_tokens
2. ✅ Criar repo GitHub: https://github.com/new
3. ✅ Adicionar secret: `https://github.com/SEU_USUARIO/dashboard-estoque-v2/settings/secrets/actions/new`
4. ✅ Push código: `git push -u origin main`
5. ✅ Acessar dashboard: https://dashboard-estoque-v2.fly.dev/estoque

## Possíveis Usuários GitHub

Baseado no email `rodrigo@phoenixinjecao.com.br`, possíveis usuários:
- rodrigo
- rodrigophoenix
- phoenixinjecao
- rphoenix

Para descobrir seu usuário exato, acesse: https://github.com e veja no canto superior direito.