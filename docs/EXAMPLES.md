# Exemplos de uso

## Plano e diagnóstico

“Use certification-study-simulator. Quero estudar para AWS CLF-C02, com seis horas por semana e exame em quatro semanas. Sou iniciante em AWS. Faça um diagnóstico curto e depois um plano.”

O tutor identifica a data real, confirma o guia, aplica diagnóstico com resposta do aluno e cria o plano. Se faltarem data/tempo, pede somente os campos necessários. O exemplo `student-profile.json` é sintético; substituí-lo pelos dados informados, sem coletar identidade civil.

## Prática guiada

“Quero Guided Practice de cinco questões sobre IAM para CLF-C02. Explique meu erro depois de cada resposta.”

O tutor consulta o objetivo e gera/revisa itens suficientes. Mostra uma questão, recebe a resposta, registra, corrige e explica distratores. O banco de referência não contém cinco itens IAM; não prometer essa quantidade sem criar novos itens.

## Mock Exam

“Faça um Mock Exam de dez questões, dificuldade mista. Só revele o gabarito quando eu disser finalizar.”

O tutor apresenta uma questão por vez. O estudante pode responder `B`, `B,D`, `pular`, `marcar CLF-P003` ou `revisar CLF-P002`. Ao fim, a fila não se entrega automaticamente. `finalizar` congela escolhas e libera relatório. A pontuação esperada na demonstração sintética do motor é 7/10; isso é um fixture de engenharia, não uma promessa de pontuação do usuário.

## Contestação e retomada

“Contesto CLF-P004 por esta razão…” registra a contestação. No mock ativo, não revela análise. Depois da entrega, confere fonte e resolve/anula, preservando relatório anterior.

“Retome a sessão destes arquivos” exige estado e banco congelado. Se só houver o resumo público, preservar respostas; não adivinhar o gabarito. A memória da conversa não é requisito de portabilidade.

## Adaptive Practice

“Use meus relatórios JSON e recomende a próxima sessão.”

O tutor valida, separa versões/modos, indica erros por objetivo, propõe revisões e intercala cenários inéditos. Se houver poucos itens, declara amostra insuficiente para afirmar domínio. Respostas abertas recebem correção estimativa por rubrica e podem ser contestadas.
