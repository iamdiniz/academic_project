2FA (TOTP) – Implementação
O que foi adicionado

Autenticação em duas etapas (2FA) via aplicativo autenticador (códigos de 6 dígitos).

Aplicável para usuários dos perfis chefe e instituicao.

Como funciona

Usuário faz login com e-mail + senha.

Se o 2FA estiver ativado, será pedido o código de 6 dígitos do app autenticador.

Só após validar o código o login é concluído.

Alterações no código

Dependências: pyotp, qrcode[pil], Pillow adicionadas em requirements.txt.

Banco de dados: criada a tabela two_factor para armazenar segredo do TOTP, usuário e status (ativo/inativo).

Rotas novas:

/2fa/setup → gera QR Code e ativa o 2FA após confirmar um código válido.

/2fa/verify → valida o código no login.

Templates:

2fa_setup.html (ativação).

2fa_verify.html (validação no login).

configuracoes.html (botão “Ativar 2FA”).

Como o usuário ativa

No sistema, acessar Configurações → Ativar 2FA.

Escanear o QR Code no app autenticador (Google Authenticator, Authy etc.).

Digitar o código exibido no app → 2FA ativado.

Nos próximos logins, o sistema sempre pedirá o código além da senha.

Segurança

O segredo TOTP não é exibido em logs.

É importante manter o relógio do servidor sincronizado (NTP).

Recomenda-se limitar tentativas de verificação para evitar ataques de força bruta.