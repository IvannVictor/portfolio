# Victor Azevedo — Portfólio

Site estático em português, feito com HTML, CSS e JavaScript. Não depende de ferramentas de build, fontes externas ou bibliotecas de ícones.

## Executar

Requisitos: Python 3 para servir os arquivos. Node.js é opcional para verificar a sintaxe do JavaScript.

Na raiz do repositório:

```sh
python3 -m http.server 8000 --bind 0.0.0.0
```

Acesse a porta 8000 no seu ambiente de desenvolvimento. O servidor de Python é destinado a desenvolvimento; publique os arquivos em uma hospedagem estática para produção.

## Estrutura

- `index.html`: conteúdo, projetos, navegação e formulário.
- `css/style.css`: identidade visual, layout responsivo e estados de interação.
- `js/menu.js`: navegação mobile com suporte a teclado e mudança de viewport.
- `images/`: imagens locais; as versões WebP são usadas para reduzir transferência.
- `docs/projetos.md`: fontes e critérios de seleção dos projetos.
- `tests/smoke.py`: verificações funcionais em Chromium.

## Verificar

```sh
node --check js/menu.js
python3 tests/smoke.py
python3 tests/demos.py
python3 tests/contact.py
```

O teste de navegador requer o pacote Python `playwright` e um executável Chromium. O teste usa o Chromium do sistema; defina `CHROMIUM_PATH` caso esteja em outro local. Não envia mensagens reais. Para executar verificações adicionais de acessibilidade, forneça uma cópia local confiável do axe-core:

```sh
python3 tests/smoke.py --axe /caminho/axe.min.js
python3 tests/demos.py --axe /caminho/axe.min.js
```

A ausência de violações automáticas não substitui uma avaliação manual completa de acessibilidade.

## Contato e publicação

O e-mail confirmado é `iivanvictor@outlook.com`. O FormSubmit foi removido após o proprietário relatar timeout e ausência de recebimento.

A integração está configurada com o endpoint Formspree fornecido pelo proprietário. A entrega real ainda depende de confirmação na caixa de entrada. Se o envio direto não estiver configurado e o formulário usar uma ação mailto, o botão “Preparar e-mail” gera um link mailto com os campos preenchidos; o usuário precisa abrir seu aplicativo de e-mail e confirmar o envio. Preparar não significa enviar. E-mail direto e WhatsApp permanecem disponíveis. Sem JavaScript, o formulário usa POST HTML nativo para o mesmo endpoint. E-mail e WhatsApp também continuam disponíveis.

Endpoint configurado: `https://formspree.io/f/myeelkay`. Para trocar futuramente:

1. Crie um formulário em https://formspree.io e confirme o endereço destinatário.
2. Copie a URL pública no formato `https://formspree.io/f/SEU_ID`.
3. Atualize o atributo `action` do formulário em `index.html`, preservando `method="post"`. O JavaScript usa essa mesma URL como fonte única. Não coloque senha ou token privado no site.
4. O script muda o botão para “Enviar mensagem” e informa o processamento pelo Formspree.
5. Publique a mudança quando decidir e faça um teste real, conferindo recebimento e spam.

A implementação mostra progresso, impede submissões simultâneas e preserva o texto em caso de falha ou timeout. Uma resposta aceita pelo serviço não comprova entrega na caixa de entrada. Nenhum e-mail real foi enviado nos testes locais. As verificações de integração simulam respostas do provedor; não validam uma conta Formspree real.

Os links de projetos levam aos repositórios públicos; a execução das aplicações externas não foi validada como parte da construção do portfólio. O projeto ZPL foi descrito pelo proprietário e complementado com seu manual operacional. Não tem código público nem métricas verificadas. As sete capturas fornecidas pelo proprietário, com identificação da empresa borrada, mostram a interface sem registros e estão em `images/zpl/`, com galeria e ampliação acessível. As funcionalidades documentadas não foram validadas pela execução do aplicativo.

Antes de publicar, configure o domínio e acrescente a URL canônica e uma imagem de compartilhamento com URL absoluta quando essas informações estiverem definidas. A preparação local não publica o site.

## Demonstrações locais

As cópias em `demos/pokedex/`, `demos/tarefas/` e `demos/login/` derivam dos repositórios públicos do proprietário e podem ser abertas pelos botões “Ver demonstração”. Todos os caminhos são relativos, compatíveis com publicação em subdiretório, e os recursos usados pelas três cópias são locais. As adaptações corrigem navegação, acessibilidade e falhas da lista de tarefas; não foram enviadas aos repositórios de origem.

- Pokédex: catálogo estático e alternância de tema. Não utiliza API.
- Tarefas: operações locais e persistência na chave `portfolio.demo.tasks.v1` do localStorage. Trate a lista como demonstração, não como armazenamento de informações importantes.
- Login: somente interface; não envia ou salva credenciais. Use dados fictícios.

O treinamento de frete não foi copiado para `demos/` por conter identificação empresarial. As URLs de GitHub Pages dos quatro projetos não puderam ser validadas neste ambiente: o proxy bloqueou o domínio. Isso não é evidência de indisponibilidade das páginas públicas.

## Publicação preparada, sem execução automática

Foi incluído `.github/workflows/pages.yml`, com acionamento exclusivamente manual (`workflow_dispatch`). Ele prepara apenas `index.html`, `css/`, `js/`, `images/` e `demos/`, excluindo documentação, testes e outros arquivos da raiz do artefato público. Nenhum workflow de publicação foi executado nesta tarefa.

Após revisar os arquivos:

1. Envie as mudanças ao repositório GitHub quando decidir publicá-las.
2. Em Settings → Pages, selecione GitHub Actions como fonte de publicação.
3. Em Actions, execute manualmente “Publicar portfólio no GitHub Pages”.
4. Use a URL informada pelo job `deploy` para conferir links, imagens e demonstrações.
5. Envie uma mensagem de teste pelo formulário com seu próprio e-mail e confirme o recebimento. Confirme previamente o formulário na conta Formspree e o endereço destinatário.
6. Configure domínio, URL canônica e imagem de compartilhamento depois de confirmar a URL pública. Não preencha esses campos com um domínio provisório ou não confirmado.

A publicação pode depender de permissões e configurações do GitHub; o workflow foi preparado, mas o deploy real ainda não foi testado.
