# Como executar?

1 - Em seu terminal builde a imagem de preferencia com o nome: 'educ'.
    Faça isso com o comando: docker build -t educ .

2 - Suba o compose com o comando: docker compose up

3 - ALTER TABLE alunos ADD COLUMN indicado_por INT NULL;

4 - ALTER DATABASE educ_invest CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE alunos CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE instituicao_de_ensino CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;