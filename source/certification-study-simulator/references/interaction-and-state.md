# Interação e estado explícito

Estado principal: `in_progress` → `submitted` ou `abandoned`. No primeiro, aceitar respostas e navegação. No segundo, congelar respostas e permitir revisão do gabarito por contestação e avaliação de rubrica. O terceiro encerra a tentativa sem resultado pontuado.

| Ação do estudante | Ação de estado | Retorno |
|---|---|---|
| B ou B,D | answer, IDs normalizados | Registro e próxima questão; feedback só fora de mock |
| pular | answer com null | Questão fica pendente |
| revisar QID | goto | Enunciado e escolha atual, sem gabarito |
| avançar | next | Próxima posição, sem inventar resposta |
| marcar QID | flag | Alterna marca de revisão |
| contestar QID | challenge | Registra razão; adia análise no mock |
| finalizar | submit | Congela e permite correção |
| abandonar | abandon | Preserva tentativa sem resultado final |

No final da fila, não chamar `submit` automaticamente. Mostrar pendências e esperar entrega. Resposta em revisão atualiza apenas o item identificado. Não interpretar “sim” como B nem aceitar duas letras em single-choice. Perguntar quando houver ambiguidade.

## Capacidade de interface

O contrato universal é conversacional. Ler as capacidades realmente expostas pelo host, sem instalar integrações. Uma interface de preferência não é necessariamente uma interface de avaliação. No ambiente de desenvolvimento observado, o widget `ask_user_input` é destinado à coleta de preferências; `request_user_input` tem restrições de modo/quantidade e recomenda uma opção. Nenhum deles foi validado aqui como transporte de respostas de exame sem pistas. Portanto, o quiz usa texto; o onboarding pode usar seleções de preferências se o host explicitamente permitir.

Se um host oferecer um componente apropriado para quiz, confirmar: retorno dos IDs selecionados; suporte a todos os distratores e múltipla seleção; ausência de alternativa recomendada; vínculo com session_id, question_id e revision; tratamento de reenvio; ações de navegação; resultado de gravação. O componente deve chamar as mesmas transições. Sem callback verificável, usar texto. Não desenhar botões Markdown e alegar que são funcionais.

Visualizações HTML locais podem manter estado visual, mas não há neste pacote uma ponte validada entre esses controles e o estado do tutor. Não usar uma visualização isolada como registro canônico. Tabelas Markdown de progresso e desempenho são suficientes; gráficos opcionais devem ser derivados do relatório já calculado, com valor e amostra visíveis.

Não há temporizador, proctoring, banco de dados ou UI customizada nesta versão. O aluno pode usar cronômetro externo; duração só é relatada se houver medida confiável, nunca estimada pelo número de mensagens.

## Retomada e ocultação

Guardar `exam_session` e banco congelado separadamente. Apresentar apenas a allowlist de `view`. O checkpoint público contém respostas do aluno e questões; uma sessão ativa de mock não deve conter resoluções do gabarito. Nunca enviar o arquivo `.private.json` durante o mock. O detentor dos arquivos consegue lê-los: a ocultação é de apresentação, não uma garantia de sigilo técnico.

Em perda de contexto, validar arquivos, hash, código e revisão. Sem banco, não reconstruir respostas corretas a posteriori. Sem o registro de respostas, não adivinhar escolhas; solicitar checkpoint ou reiniciar. Sem ferramentas, registrar uma tabela ou JSON explícito na conversa, com próximo item e modo.

Cada escrita gera um novo arquivo de revisão, com criação exclusiva. Usar um escritor por sessão e aplicar eventos em série. Em timeout, ler o arquivo de saída antes de repetir; um ID repetido idêntico é idempotente, e um ID reutilizado para outra ação falha. Não mesclar ramos concorrentes automaticamente.
