# Validação do plugin 0.1.2

| Área | Resultado | Como reproduzir |
|---|---|---|
| Skill e motor | 20 testes passaram | `python tests/run_checks.py` |
| Manifesto e arquivos do plugin | 4 testes passaram | `python tests/test_plugin_package.py -v` |
| Simulado de referência | 10 questões, 7 acertos com respostas sintéticas | `python tools/demo.py` |
| Arquivos do ZIP | Manifesto e ícone nas posições declaradas. Os 18 arquivos da Skill são iguais aos da versão 0.1.0. | `python tools/package.py --plugin --version 0.1.2` |

Os testes de empacotamento rejeitam `interface.longDescription` ausente, vazia ou formada só por espaços. Também cobrem metadados de desenvolvedor e referências de ícone que não apontam para um arquivo do pacote.

Os testes do motor cobrem cálculo da pontuação, ocultação do gabarito até a entrega, questões contestadas, recomendações e exportação. Ao executar o teste e a demonstração, consulte os resultados gerados em `evidence/`.

A validação automatizada roda localmente. A confirmação do upload, da instalação e da seleção via `@` depende da interface e da conta ChatGPT. O banco AWS CLF-C02 é uma amostra datada com dez questões e cobertura parcial. A pontuação do simulado é diagnóstica.
