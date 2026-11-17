# Fontes, atualização e limites

Consultas desta baseline: **2026-11-16**. URLs são referências, não dependências carregadas automaticamente. Revalidar no início de um ciclo de preparação e diante de mudanças de versão, fontes conflitantes ou contestação. O motor não faz essa consulta.

## Ambiente OpenAI

| Fonte oficial | Alegação sustentada | Limite |
|---|---|---|
| [Build skills](https://learn.chatgpt.com/docs/build-skills) | Pasta com SKILL.md, name/description, recursos opcionais e ativação explícita/implícita | Documentação não equivale a importação desta entrega |
| [Build skills — Plugins](https://developers.openai.com/plugins/build/skills) | Skill pode funcionar sem MCP; scripts se justificam para cálculo e processamento determinístico | Não concede ferramentas, armazenamento ou UI por si só |

A rota `https://developers.openai.com/codex/skills/` redirecionou para Build skills na consulta. A documentação diferencia autoria por pasta e distribuição por plugin. Esta entrega é uma distribuição de arquivos de uma Skill e um pacote de desenvolvimento, **sem manifest de plugin**. Nenhum procedimento de instalação foi executado.

Recursos interativos são dependentes do host. As limitações de widgets descritas em interaction-and-state.md foram observadas nas instruções de capacidades desta sessão, não estabelecidas como contrato público universal. Nenhum componente de prova com callback foi validado. Não há dependência obrigatória de outras Skills.

## Certificação de referência

Organização: AWS. Certificação: AWS Certified Cloud Practitioner. Código: CLF-C02. Versão separada do exame: não publicada nas páginas consultadas (`null`). Revisão do guia: 1.3, publicada em 2026-10-29, conforme a página de revisões. A vigência exata para um agendamento não foi confirmada; não converter a indicação aproximada de atualização em data garantida.

| Fonte oficial | Objetivos/alegação | Atualização e limite |
|---|---|---|
| [Exam guide](https://docs.aws.amazon.com/aws-certification/latest/cloud-practitioner-02/cloud-practitioner-02.html) | Domínios, pesos 24/30/34/12 e formatos single/multiple | Snapshot consultado; não é lista exaustiva do exame |
| [Revisions](https://docs.aws.amazon.com/aws-certification/latest/cloud-practitioner-02/clf-02-revisions.html) | Última revisão publicada 1.3 | Publicação não confirma vigência do exame do aluno |
| [Domain 1](https://docs.aws.amazon.com/aws-certification/latest/cloud-practitioner-02/cloud-practitioner-02-domain1.html) | 1.1–1.4 | Títulos em JSON são resumos, não reprodução integral |
| [Domain 2](https://docs.aws.amazon.com/aws-certification/latest/cloud-practitioner-02/cloud-practitioner-02-domain2.html) | 2.1–2.4 | Mesmo limite |
| [Domain 3](https://docs.aws.amazon.com/aws-certification/latest/cloud-practitioner-02/cloud-practitioner-02-domain3.html) | 3.1–3.8; AZs para alta disponibilidade | Mesmo limite |
| [Domain 4](https://docs.aws.amazon.com/aws-certification/latest/cloud-practitioner-02/cloud-practitioner-02-domain4.html) | 4.1–4.3 | Mesmo limite |
| [Cloud advantages](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/six-advantages-of-cloud-computing.html) | 1.1 e 1.4; elasticidade e consumo | Não garante economia em todo caso |
| [IAM practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) | 2.3; roles, MFA e least privilege | Aplicar ao contexto da questão |
| [Shared responsibility](https://aws.amazon.com/compliance/shared-responsibility-model/) | 2.1; SO convidado em EC2 | Responsabilidades variam conforme serviço |
| [Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html) | 3.6; armazenamento de objetos | Sem inferir características de todas as storage classes |
| [AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html) | 3.3; execução sem gerenciar servidores | O item usa apenas a capacidade de execução por evento |
| [Amazon RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html) | 3.4; PostgreSQL gerenciado | Não significa ausência de responsabilidades do cliente |
| [Pricing Calculator](https://docs.aws.amazon.com/pricing-calculator/latest/userguide/what-is-pricing-calculator.html) | 4.2; estimativa prévia | Não é fatura nem garantia de custo |
| [Certification agreement](https://aws.amazon.com/certification/certification-agreement/) | Confidencialidade de itens e restrição a ajuda não autorizada em avaliação | Referência de integridade; não é aconselhamento jurídico |

Todos os itens do banco têm metadados próprios em `source_references`, com organização, exame/código/versão, URL, data, objetivos, status `checked_snapshot` e limites. A classificação é revisão documental pelo autor, não aprovação da certificadora. O exemplo de 10 questões distribui D1=2, D2=3, D3=4 e D4=1; o arredondamento não reproduz a escala oficial. Resposta aberta é extensão didática separada.

## Outras certificações

Para Palo Alto Networks, Microsoft, ISC2, CompTIA ou outro emissor, localizar primeiro o catálogo/guia oficial específico. Não transportar pesos ou códigos do exemplo AWS. Conferir versão, retirement, idioma e guia aplicável ao prazo do aluno; preencher o mesmo contrato. Não há banco previamente validado desses emissores nesta versão.

## Protocolo de atualização

Registrar URL final, data real, status da fonte, escopo sustentado e lacunas. Se o exame mudar, criar novo snapshot, revisar itens afetados e preservar banco/sessões anteriores. Publicação nova não valida automaticamente conteúdo antigo. Se a documentação não puder ser aberta, marcar unavailable; não promover snippet, memória do modelo ou o relatório de pesquisa a fonte suficiente do gabarito.
