# Projetos e fontes de conteúdo

## Critério

Selecionar trabalhos que combinem interfaces e contexto de negócio. Distinguir estudos de interface de sistemas com autenticação, integração ou operação real. Não inferir funcionalidades pelo nome do repositório e não publicar métricas sem evidências.

## Seleção incluída

| Projeto                             | Fonte                                                               | Conteúdo confirmado                                                                                                                                        | Limite da avaliação                                                                                     |
| ----------------------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Etiquetas ZPL e painel de expedição | Descrição fornecida pelo proprietário nesta conversa                | Python, conversão PDF para ZPL, impressão de etiquetas dos Correios e mini DANFE, painel gráfico de desempenho da expedição; desenvolvido para uma empresa | Sem repositório público. Código analisado estaticamente; sem teste no Windows nem medição independente. |
| Treinamento de frete no Omie        | https://github.com/IvannVictor/treinamentofreteomie — `index.html`  | Apresentação interativa, roteiro, etapas de cotação, etiqueta e rastreio, navegação por teclado                                                            | Não implica integração implementada com APIs dos Correios ou do Omie.                                   |
| Pokédex                             | https://github.com/IvannVictor/pokedex — `index.html`               | Catálogo visual de Pokémon com cartões e descrições                                                                                                        | Não foi identificada integração com API no HTML inspecionado; não foi anunciada essa capacidade.        |
| Lista de tarefas                    | https://github.com/IvannVictor/To-Do-List — `index.html`            | Campo de tarefa, botão de adicionar, lista e referência a JavaScript                                                                                       | Persistência local confirmada no JavaScript e testada na demonstração; sem sincronização.               |
| Interface de login                  | https://github.com/IvannVictor/tela-login-responsiva — `index.html` | Formulário visual com usuário e senha                                                                                                                      | Apresentado como interface de estudo, sem afirmar autenticação.                                         |

As prévias de Pokédex e login foram otimizadas a partir das imagens que já existiam neste portfólio. As artes de treinamento e tarefas são composições ilustrativas, não capturas das aplicações. O fluxo PDF → ZPL → impressão ilustra as funcionalidades descritas pelo proprietário.

## Outros repositórios encontrados

A listagem pública do perfil também apresentou `portfolio`, `relogio-digital`, `Python`, `SendScriptWhatsAppV2`, `PHP`, `Linguagem_C`, `HTML5` e `JavaScript`. Seus conteúdos não foram examinados nesta seleção. Projetos privados ou não listados não foram acessados.

## Próximos materiais úteis

- Futuras capturas com dados demonstrativos claramente identificados, caso disponíveis.
- Detalhamento da contribuição individual e das bibliotecas utilizadas.
- Resultados mensuráveis, somente após confirmação.
- Demonstrações públicas validadas para os projetos que puderem ser hospedados.

## Complemento documental — Gerenciador de Etiquetas ZPL

Fonte adicional: manual fornecido pelo proprietário, `manual operacional fornecido pelo proprietário`, datado de 02/11/2026. O PDF não foi copiado para os arquivos públicos do site.

A documentação descreve Python, CustomTkinter, Windows, Zebra GC420t e Poppler, processamento de ZPL/TXT/PDF e lotes ZIP, arquivamento, controle de duplicidade, reimpressão justificada, pendências, rastreabilidade, auditoria e produtividade com períodos diário/semanal/mensal. O cartão público apresenta um resumo dessas funcionalidades e um estudo de caso expansível.

Essas informações são evidências documentais, não resultados de testes do aplicativo. O manual identifica a base 15.4.1 como homologada e a versão 15.5.2 como pendente de homologação final no Windows. Não foram anunciadas certificação, validação física da versão nova ou métricas de ganho.

Limites preservados na apresentação:

- Aceite pelo spooler não equivale a impressão física.
- Não há integração direta documentada com APIs do Omie/Correios.
- Não há evidência de banco de dados central, operação concorrente em rede ou histórico criptograficamente imutável.
- Não foram publicados registros reais, dados de destinatários ou o manual completo.

## Referência visual recebida

O proprietário forneceu sete capturas de tela na conversa: Produtividade da Expedição, Central de Impressão, Reimpressão Operacional, Pendências de Impressão, Rastreabilidade de Etiquetas, Indicadores Operacionais e Auditoria do Histórico.

As capturas mostram a interface sem registros operacionais: contadores zerados, consultas sem resultados e auditoria com estado `SEM_HISTORICO`. Não demonstram desempenho, entrega de impressão física ou homologação. Na Central de Impressão, a seleção exibida é Microsoft Print to PDF, não uma Zebra física.

Proposta de galeria: Central de Impressão como imagem principal; Produtividade e Rastreabilidade como complementos; demais telas em sequência com legendas e ampliação acessível. Descrever as imagens como capturas da interface sem dados operacionais. Não criar registros ou gráficos fictícios para representar resultados reais.

Os arquivos foram recebidos posteriormente no ZIP `Telas_GerenciadorZPL.zip`. As sete capturas PNG foram inspecionadas e incluídas inicialmente sem alteração de conteúdo em `images/zpl/`, com nomes descritivos, legendas e ampliação por diálogo acessível. Os caminhos locais padrão visíveis na Central de Impressão fazem parte da captura original fornecida; não há registros de clientes visíveis. A galeria apresenta estados vazios, sem inferir resultados operacionais. O PDF do manual continua fora dos arquivos públicos.

## Estudo de caso e confidencialidade

O proprietário solicitou retirar a identificação da empresa. A descrição pública passa a usar “Gerenciador de Etiquetas ZPL”. O código e o manual enviados para análise permanecem fora do checkout público e não devem ser publicados.

Relato do autor: antes eram montadas etiquetas com dados de notas fiscais, com impressão em papel, recorte e fixação com fita. O desenvolvimento foi individual, com apoio de IA, incluindo levantamento de necessidades e testes. O aplicativo está em uso em um computador. O autor estima uma redução próxima de metade do tempo de expedição e relata ausência de erros de digitação nessa etapa após eliminar a entrada manual. Não há medição independente ou série histórica que sustente uma porcentagem auditada.

O arquivo Python foi analisado estaticamente, sem execução. Foram identificados CustomTkinter, win32print, pdf2image, pypdf, Pillow e chamadas a módulos auxiliares próprios. Na primeira análise, esses módulos não haviam sido fornecidos. Posteriormente, o ZIP trouxe o arquivo principal e seis módulos auxiliares, que foram examinados estaticamente. A aplicação desktop depende de Windows; não foi executada no ambiente Linux do portfólio.

A integração com dados do Omie ocorre pelo fluxo de arquivos descrito pelo autor; não foi inferida integração direta via API. Banco de dados compartilhado e uso multiusuário são evolução em desenvolvimento, não funcionalidades prontas.

## Código completo recebido e anonimização das capturas

O ZIP de código-fonte fornecido pelo proprietário contém um arquivo principal e seis módulos auxiliares Python. Foram analisados estaticamente os imports e as rotinas de classificação, chave de duplicidade por rastreio ou NF/tipo, seleção e montagem de reimpressões e mutex local do Windows, além da organização dos módulos de indicadores e produtividade. Não foram executados os fontes, binários ou arquivos de cache fornecidos. A presença dessas rotinas não comprova homologação, impressão física ou segurança para uso concorrente em rede.

Com autorização explícita do proprietário para edição por código, foi aplicado desfoque forte sobre os dois locais de identificação da empresa em cada uma das sete capturas: barra de título e marca no menu lateral. Dimensões e pixels fora dessas áreas foram preservados. O salvamento não reaproveita metadados das imagens originais. Originais e código ficam em área de revisão fora do checkout público; nenhuma cópia não anonimizada deve ser recolocada em `images/`.

## Demonstrações e estudos complementares

Foram baixadas cópias dos ramos `main` dos três repositórios de estudo via codeload do GitHub, sem alterar suas origens. As cópias são mantidas em `demos/` como adaptações para demonstração. Não são espelhos automaticamente atualizados.

A inspeção do JavaScript original confirmou alternância de tema na Pokédex e inclusão, conclusão, exclusão e localStorage na lista de tarefas. A cópia da lista substitui a interpolação de texto do usuário em innerHTML por textContent, rejeita entradas vazias e usa controles de teclado. Também trata falhas de armazenamento e dados salvos inválidos. A interface de login corrige a classe de layout divergente, associa rótulos aos campos e apresenta retorno local sem autenticação. Fontes remotas foram removidas das cópias para permitir demonstração sem recursos externos. Marcas e imagens de terceiros permanecem como referências dos projetos de estudo; a Pokédex identifica que não há afiliação oficial.

O treinamento de frete foi inspecionado, mas sua apresentação incorpora marca empresarial e imagens embutidas. Por isso, não foi replicado como demonstração local. A descrição no portfólio explica o escopo educacional e não afirma integração com APIs.

O acesso às quatro URLs de GitHub Pages falhou por negação explícita do proxy. As demonstrações locais foram preparadas para possibilitar validação funcional sem contornar essa restrição de rede.
