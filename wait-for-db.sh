#!/bin/sh

# Espera até que o banco esteja pronto
echo "Aguardando o banco de dados estar pronto..."

while ! nc -z "$1" 3306; do
  sleep 1
done

echo "Banco de dados está pronto. Iniciando a aplicação..."

# Executa o comando passado após o host e porta
shift
exec "$@"
