# Rota Eventos

Agenda de eventos de comunicação, jornalismo, publicidade, relações públicas, cerimonial e audiovisual, com destaque para a Bahia e para Salvador. Um projeto do YLuna85 LABs, assinado por Yuri Luna.

## Estado atual

Fase 1 concluída em 16/10/2026: esqueleto do repositório, identidade visual, página inicial com cartões de teste e páginas institucionais (Sobre, Metodologia, Privacidade, Termos, Contato e 404). Os cartões da página inicial são marcados como "Evento de teste". Eventos reais entram a partir da Fase 2 (coletor local).

## Estrutura

Tudo fica na mesma pasta do `index.html`, para enviar ao GitHub pelo navegador, arrastando os arquivos. A única exceção prevista é o fluxo `.github/workflows/indexar.yml` da Fase 4.

```
eventos/
├── index.html, sobre.html, metodologia.html, privacidade.html, termos.html,
│   contato.html, 404.html, sitemap.xml, robots.txt     (gerados por construir_site.py)
├── fonte-index.html, fonte-sobre.html, ...             corpo de cada página, com cabeçalho "chave: valor"
├── modelo-base.html                                    cabeçalho, rodapé e metadados
├── construir_site.py                                   gerador das páginas, do sitemap e do robots
├── style.css                                           tokens, Bento Grid, componentes
├── site.js                                             acessibilidade, menu, cookies, filtros, contato
├── avatar-bolinho-de-chuva.png, favicon-yluna85-labs.ico, favicon-yluna85-labs.png
├── eventos.json                                        índice publicado (vazio até a Fase 4)
└── local/                                              coleta e rascunhos, fora do GitHub (.gitignore)
```

## Como gerar as páginas

```
python construir_site.py
```

O script lê `modelo-base.html` e cada arquivo `fonte-*.html`, valida o cabeçalho (descrição de até 155 caracteres) e grava as páginas ao lado. Edite sempre os arquivos `fonte-*.html` e `modelo-base.html`, nunca as páginas geradas. O `robots.txt` bloqueia a indexação dos arquivos `fonte-` e `modelo-`.

## Como enviar ao GitHub sem o aplicativo de desktop

No repositório, use "Add file" e "Upload files" e arraste os arquivos desta pasta, menos a pasta `local/`, que fica só na sua máquina. A página de upload aceita até 100 arquivos por envio.

## Pendências de configuração

- E-mail de contato: definir em `site.js` (constante `EMAIL_CONTATO`) e em `fonte-contato.html` (marcador `[inserir e-mail de contato]`).
- Endereço público: `URL_BASE` em `construir_site.py` está como `https://yuriluna85.github.io/eventos` e muda quando houver domínio próprio.
- Código do anúncio (ad-client e ad-slot): área reservada no `<head>` de `modelos/base.html`, a preencher só depois da aprovação.

## Diretrizes do projeto

- Coleta de dados em modo local, com revisão manual de cada artigo antes da publicação. O fluxo automático do repositório só indexa o que foi aprovado.
- Sem emojis, sem borda lateral decorativa, contraste mínimo de 7:1 no texto corrido.

## Log de atualizações

- **16/10/2026, versão 0.1.1**: estrutura achatada a pedido de Yuri, para enviar ao GitHub pelo navegador. `assets/css/style.css` virou `style.css`, `assets/js/site.js` virou `site.js`, `assets/img/avatar-bolinho-de-chuva.png` subiu para a raiz, `modelos/base.html` virou `modelo-base.html`, `conteudo/paginas/*.html` viraram `fonte-*.html`, `scripts/construir_site.py` virou `construir_site.py` e `dados/eventos.json` virou `eventos.json`. O `robots.txt` passou a bloquear `/fonte-` e `/modelo-`. Páginas geradas e conferidas de novo.

- **16/10/2026, versão 0.1.0**: Fase 1. Criados o esqueleto do repositório, `assets/css/style.css` (tokens do System Design do YLuna85 LABs com texto secundário `#B1BAC4`, 8,8:1 a 9,6:1 de contraste, e artigos em superfície sólida), `assets/js/site.js` (A-, A, A+, alto contraste, gaveta de navegação, aviso de cookies com LGPD, filtros e formulário de contato), `modelos/base.html`, `scripts/construir_site.py` e as páginas inicial, Sobre, Metodologia, Privacidade, Termos, Contato e 404, além de `sitemap.xml` e `robots.txt`. Auditorias `verify_app_baseline.py` e `audit_ui_anti_generic.py` sem pendências.
