# Credenciais de Teste — SoulNutri

## Usuário Premium (Admin)
- PIN: 2212
- Nome: Joao Manoel (sem acento, sem espaço final)
- is_admin: true
- Acesso: Premium ativo + Painel Admin via botão no dashboard

## Admin (chave direta)
- Chave: 833981109a436c46898a224bda0770c5273d5f2e48da8001
- URL: /admin
- Header: X-Admin-Key

## Fluxo Admin via PIN
1. Login com PIN 2212 no Premium
2. Clicar em "Painel Admin" (visível somente para is_admin=true)
3. Redirecionado para /admin já autenticado

## Nota
- Para designar outros admins: Admin → aba Premium → Buscar usuário → "Tornar Admin"
- Para alterar PIN: Admin → aba Premium → Buscar usuário → botão "🔑 PIN"
