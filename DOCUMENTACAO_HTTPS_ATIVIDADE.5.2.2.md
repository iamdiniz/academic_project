## HTTPS e Proteção de Cookies – Relatório Rápido

### Como estava antes (trechos do código)

```python
# app.py
app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False  # True em produção
)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
```

- `app.run` subia apenas em HTTP, sem certificados.
- Nenhum redirecionamento obrigatório para HTTPS.
- Cookies dependiam do padrão do Flask e o CSRF era definido sem `secure`/`httponly`.

### Como está agora (trechos novos)

```python
force_https = os.getenv("FORCE_HTTPS", "false").lower() == "true"
ssl_cert_file = os.getenv("SSL_CERT_FILE")
ssl_key_file = os.getenv("SSL_KEY_FILE")

app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=force_https,
    SESSION_COOKIE_HTTPONLY=True
)

if force_https:
    @app.before_request
    def redirect_to_https():
        proto = request.headers.get("X-Forwarded-Proto", request.scheme)
        if proto != "https":
            return redirect(request.url.replace("http://", "https://", 1), code=301)

@app.after_request
def set_csrf_cookie(response):
    csrf_token_value = generate_csrf()
    response.set_cookie(
        "csrf_token",
        csrf_token_value,
        secure=force_https,
        httponly=True,
        samesite="Lax",
        path="/"
    )
    return response

if __name__ == "__main__":
    ssl_context = None
    if ssl_cert_file and ssl_key_file:
        ssl_context = (ssl_cert_file, ssl_key_file)
    app.run(debug=True, host='0.0.0.0', ssl_context=ssl_context)
```

- Variáveis `FORCE_HTTPS`, `SSL_CERT_FILE` e `SSL_KEY_FILE` ativam TLS quando preenchidas.
- `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY` e o cookie `csrf_token` acompanham o modo seguro.
- Um `before_request` redireciona para HTTPS sempre que necessário.
- `app.run` usa `ssl_context` quando os caminhos dos certificados estão definidos.

### Resumo das melhorias

1. **Suporte a TLS**
   - Novas variáveis `SSL_CERT_FILE` e `SSL_KEY_FILE` permitem subir o Flask já com `ssl_context`. Basta apontar para os caminhos dos certificados.
2. **Redirecionamento automático para HTTPS**
   - Quando `FORCE_HTTPS=true`, todas as requisições HTTP são redirecionadas (código 301) para a versão HTTPS.
3. **Cookies protegidos**
   - `SESSION_COOKIE_SECURE` e `SESSION_COOKIE_HTTPONLY` agora seguem o valor de `FORCE_HTTPS`.
   - O cookie `csrf_token` também recebe `secure` e `httponly`, reduzindo a exposição a roubo via JavaScript.

### Por que isso importa

- TLS impede que senhas e dados sensíveis trafeguem em texto puro, atendendo OWASP e LGPD.
- O redirecionamento elimina acessos acidentais em HTTP e evita ataques de downgrade.
- Cookies marcados como `Secure` e `HttpOnly` dificultam sequestro de sessão e mitigam XSS.

### Como usar rapidamente

```env
# .env
FORCE_HTTPS=true
SSL_CERT_FILE=/caminho/para/cert.pem
SSL_KEY_FILE=/caminho/para/key.pem
```

Execute normalmente (`python app.py` ou via Docker). Se os certificados forem válidos e o tráfego passar por HTTPS, as credenciais dos usuários permanecerão protegidas.
