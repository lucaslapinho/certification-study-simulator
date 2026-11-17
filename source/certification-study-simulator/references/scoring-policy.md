# Política de pontuação v1

- **Fechadas:** `exact_match`. A resposta deve ter exatamente os IDs corretos, independente da ordem. Seleção incompleta ou com IDs a mais é entrada inválida quando contraria a contagem pedida; pedir ajuste antes de avançar. Um conjunto válido, mas incorreto recebe 0. Não há crédito parcial nem pontuação negativa.
- **Abertas:** `rubric`. O avaliador atribui pontos a todos os critérios, cita evidências da resposta e registra `estimated: true`. Cada critério admite de zero ao máximo. O motor confere limites e soma; não interpreta a resposta. Sem avaliação, o item é pending e o relatório é provisório.
- **Não respondidas:** zero, mantendo o máximo no denominador.
- **Contestadas ou anuladas:** excluded, zero no numerador e denominador. Contestação pendente torna o relatório provisório. Anulação resolvida permanece documentada e não é erro do estudante.
- **Total:** soma dos pontos / soma dos máximos dos itens válidos. Pesos do blueprint orientam seleção; não ponderar novamente os resultados e contar o peso duas vezes. Máximos diferentes por rubrica têm efeito explícito na pontuação; não confundir percentual de pontos com percentual de questões corretas.
- **Sem itens válidos:** percentual `null`, apresentado como N/A. Contar excluídas e pendentes separadamente.

O motor usa Decimal nos cálculos e arredonda o percentual final a duas casas; não arredonda cada crédito antes de somar. `correct`, `incorrect`, `partial`, `unanswered`, `excluded` e `pending` são mutuamente exclusivos. `valid` soma os quatro primeiros. Os totais por domínio e subdomínio devem reconciliar com o total.

Exemplo: 7 corretas de 10 itens de 1 ponto = 7/10, 70% de prática. Se uma das três erradas for anulada: 7/9 = 77,78%. Isso não significa 700, aprovação ou prontidão em uma escala oficial.

## Contestação

Registrar `challenge` com motivo. No mock ativo, não discutir o gabarito. Depois de submetido, verificar documentação e contexto; executar `resolve` com `uphold` ou `void` e fundamento/fonte. A versão inicial não altera gabaritos dentro de uma tentativa congelada: anular e revisar o banco para tentativas futuras. Relatórios de revisões anteriores ficam preservados.

Mudança de interpretação em questão aberta permite nova `grade_open` após revisão, com novo evento e relatório. Registrar motivo na evidência dos critérios. Nenhuma alteração deve reescrever um export anterior.
