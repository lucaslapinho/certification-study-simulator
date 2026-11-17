# Ensino, planejamento e adaptação

Estas são regras pedagógicas da implementação, não um algoritmo clínico, psicométrico ou oficial de certificadora. Não prometer efeito universal nem tratar os intervalos propostos como otimização comprovada para uma pessoa.

## Diagnóstico e plano

Separar conhecimento autodeclarado, resposta correta, justificativa e confiança. Acerto com baixa confiança pede nova aplicação; erro com alta confiança indica possível concepção equivocada. Perguntar o raciocínio depois da correção no mock, evitando influenciar a resposta.

Distribuir tempo por `peso × (1 + lacuna)`. Lacuna é 1 menos fração de pontos observados; sem diagnóstico, usar 1 menos autoconfiança/4, com nível neutro 2 quando não informado. Reservar, como ponto de partida ajustável, 60% para estudo, 25% para prática e 15% para revisão. São escolhas de engenharia. Não abandonar domínios bem pontuados.

Transformar minutos em sessões compatíveis com a rotina: um objetivo delimitado, explicação, cenário, tentativa de recuperação e evidência de conclusão. Registrar o que ficou fora da cobertura. Adaptar a semana final à revisão de erros e a um treino misto; evitar concentrar material novo na véspera.

## Aula e recuperação

Pedir que o estudante recupere a ideia antes de mostrar a solução. Após feedback, pedir uma explicação própria ou um cenário novo. Evitar ciclos que premiem apenas memorizar a letra. Explicitar o erro conceitual: por exemplo, confundir autorização IAM com conectividade de rede.

Para revisar, propor 1, 3, 7 e 14 dias depois da correção. Reduzir o intervalo se houver erro; ampliar após respostas corretas explicadas em ocasiões diferentes. Excluir datas posteriores ao exame do cronograma principal ou perguntar sobre continuidade. Datas no export são recomendações, não automações.

## Dificuldade e interleaving

- Menos de 5 itens válidos no domínio: tratar como amostra pequena; manter dificuldade e coletar mais evidência.
- Com pelo menos 5 itens, menos de 50%: voltar a fundamentos e exemplos mais curtos.
- Entre 50% e 79%: manter o nível, variar cenários e revisar a concepção equivocada.
- Pelo menos 80% em duas tentativas comparáveis, cada uma com pelo menos 5 itens novos válidos no domínio, e justificativas coerentes: propor subir um nível. Confirmar que não houve repetição de itens ou revelação antecipada. Não chamar isso de domínio definitivo.
- Intercalar objetivos frágeis com outros domínios. No começo de um tema, permitir um bloco curto focado antes de misturar.

`recommend` automatiza prioridades, datas e redução conservadora de dificuldade. A promoção depende da análise explícita de histórico e justificativas pelo tutor, pois percentuais sozinhos não demonstram compreensão. `start --mode adaptive --recommendations ...` dobra a prioridade de domínios frágeis e intercala a seleção; não é CAT nem Item Response Theory.

## Comparação

Comparar códigos, versões, revisões, modo e política iguais. Mesmo assim, reportar n, cobertura, banco/dificuldade e repetição. Separar sessões guiadas de mocks. Não calcular tendência com registros inexistentes; não usar dados de outro aluno. Solicitar o export necessário, não dados pessoais extras.
