#!/bin/sh

# Usa variáveis de ambiente ou parâmetros
HOST=${DB_HOST:-$1}
PORT=${DB_PORT:-3306}

echo "Aguardando o banco de dados estar pronto em $HOST:$PORT..."

while ! nc -z "$HOST" "$PORT"; do
  sleep 1
done

echo "Banco de dados está pronto. Iniciando a aplicação..."

# Executa o comando passado após o host e porta
shift
exec "$@"
