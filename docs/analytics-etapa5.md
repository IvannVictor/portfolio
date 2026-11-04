# v3.9 — Etapa 5: métricas e privacidade

## Objetivo
Medir o interesse no portfólio e nos currículos, sem coletar dados de formulários ou identificar individualmente visitantes.

## Situação
Nenhum serviço de analytics foi habilitado nesta etapa. Não há código de rastreamento nem envio de eventos. O serviço de contato Formspree é independente de analytics e já está configurado no site.

## Métricas propostas
- Visualizações da página inicial e das páginas de currículo (Operações, Tecnologia, Fiscal-Contábil).
- Cliques em chamadas para projetos, currículos e contato, apenas por categoria agregada.
- Visitas às demonstrações ZPL e demais projetos.
- Evolução semanal de acessos e de cliques nos currículos.

## Eventos permitidos (sem identificadores pessoais)
- `portfolio_resume_open` com `area` em `operacoes | tecnologia | fiscal-contabil`.
- `portfolio_project_open` com `project` de uma lista fixa e pública.
- `portfolio_contact_click` com `channel` em `email | whatsapp | linkedin`.

## Eventos e dados proibidos
Não registrar nome, e-mail, telefone, mensagem, conteúdo de formulário, endereço IP em logs próprios, texto livre, URL com parâmetros de identificação, identificadores persistentes ou conteúdo de contatos. Não registrar tentativas de envio ou sucesso do formulário como conversão sem revisão específica.

## Critérios para escolher o provedor
1. Política de privacidade e processamento de dados documentados.
2. Sem cookies de rastreamento, fingerprinting ou perfis individuais.
3. Possibilidade de configurar métricas agregadas e retenção limitada.
4. Script pequeno, assíncrono, que não bloqueie a renderização.
5. Documentação transparente para visitantes e análise de conformidade LGPD antes de ativar.
6. Controle de acesso à conta e capacidade de excluir dados.

## Implementação planejada após escolha do provedor
1. Criar configuração isolada e desabilitada por padrão na branch de desenvolvimento.
2. Instrumentar somente links públicos com atributos estáticos, sem ler campos de formulário.
3. Testar ausência de requisições quando analytics estiver desabilitado.
4. Testar os eventos permitidos e bloquear propriedades extras.
5. Validar Lighthouse, Playwright, acessibilidade e impacto na carga.
6. Obter aprovação expressa antes de habilitar e publicar.

## Indicadores
CTR de currículo = cliques no link do currículo / visualizações da página inicial, quando ambas as contagens forem comparáveis. Não interpretar cliques como candidaturas ou entrevistas. Atribuição de recrutadores não é possível apenas com visitas anônimas.
