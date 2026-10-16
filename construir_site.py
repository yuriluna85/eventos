"""Constrói as páginas estáticas do Rota Eventos a partir de modelo-base.html e dos arquivos fonte-*.html.

Tudo fica na mesma pasta do index.html, para o envio ao GitHub ser só arrastar os arquivos. Cada
arquivo fonte-<slug>.html começa com linhas "chave: valor" (titulo, descricao, slug, robots, json_ld),
uma linha "---" e o corpo em HTML. O script gera <slug>.html ao lado, mais sitemap.xml e robots.txt.
Na Fase 4 este mesmo script passa a gerar também os artigos de evento.

Uso:
    python construir_site.py
"""

from __future__ import annotations

import html
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
URL_BASE = "https://yuriluna85.github.io/eventos"  # trocar quando houver domínio próprio
NOME_SITE = "Rota Eventos"
IMAGEM_SOCIAL = "favicon-yluna85-labs.png"
CHAVES_OBRIGATORIAS = ("titulo", "descricao", "slug", "robots", "json_ld")
JSON_LD_VALIDOS = ("website", "sobre", "pagina", "nenhum")


@dataclass(frozen=True)
class Pagina:
    titulo: str
    descricao: str
    slug: str
    robots: str
    json_ld: str
    corpo: str
    modificada: datetime

    @property
    def arquivo(self) -> str:
        return f"{self.slug}.html"

    @property
    def url(self) -> str:
        return f"{URL_BASE}/" if self.slug == "index" else f"{URL_BASE}/{self.arquivo}"


def ler_pagina(caminho: Path) -> Pagina:
    """Lê um fragmento de página e valida o cabeçalho."""
    texto = caminho.read_text(encoding="utf-8")
    cabecalho, separador, corpo = texto.partition("\n---\n")
    if not separador:
        raise ValueError(f"{caminho.name}: falta a linha '---' entre o cabeçalho e o corpo")
    campos: dict[str, str] = {}
    for linha in cabecalho.splitlines():
        if not linha.strip():
            continue
        chave, dois_pontos, valor = linha.partition(":")
        if not dois_pontos:
            raise ValueError(f"{caminho.name}: linha de cabeçalho inválida: {linha!r}")
        campos[chave.strip()] = valor.strip()
    faltando = [c for c in CHAVES_OBRIGATORIAS if c not in campos]
    if faltando:
        raise ValueError(f"{caminho.name}: faltam as chaves {', '.join(faltando)}")
    if campos["json_ld"] not in JSON_LD_VALIDOS:
        raise ValueError(f"{caminho.name}: json_ld deve ser um de {', '.join(JSON_LD_VALIDOS)}")
    if len(campos["descricao"]) > 155:
        raise ValueError(f"{caminho.name}: a descrição passa de 155 caracteres ({len(campos['descricao'])})")
    return Pagina(
        titulo=campos["titulo"], descricao=campos["descricao"], slug=campos["slug"],
        robots=campos["robots"], json_ld=campos["json_ld"], corpo=corpo.strip("\n"),
        modificada=datetime.fromtimestamp(caminho.stat().st_mtime),
    )


def montar_json_ld(pagina: Pagina) -> str:
    """Devolve o bloco <script> de dados estruturados da página, ou vazio."""
    if pagina.json_ld == "nenhum":
        return ""
    data_iso = pagina.modificada.strftime("%Y-%m-%d")
    if pagina.json_ld == "website":
        dados: dict[str, object] = {
            "@context": "https://schema.org", "@type": "WebSite", "name": NOME_SITE,
            "url": f"{URL_BASE}/", "inLanguage": "pt-BR", "description": pagina.descricao,
        }
    else:
        tipo = "AboutPage" if pagina.json_ld == "sobre" else "WebPage"
        dados = {
            "@context": "https://schema.org", "@type": tipo, "name": pagina.titulo,
            "url": pagina.url, "inLanguage": "pt-BR", "description": pagina.descricao,
            "dateModified": data_iso,
            "isPartOf": {"@type": "WebSite", "name": NOME_SITE, "url": f"{URL_BASE}/"},
            "author": {"@type": "Person", "name": "Yuri Luna"},
        }
    corpo_json = json.dumps(dados, ensure_ascii=False, indent=2)
    return f'  <script type="application/ld+json">\n{corpo_json}\n  </script>'


def aplicar_modelo(modelo: str, pagina: Pagina) -> str:
    """Preenche o modelo base com os dados da página."""
    esc = lambda valor: html.escape(valor, quote=True)  # noqa: E731
    marcas_menu = re.compile(r"\{\{atual:([a-z0-9-]+)\}\}")
    saida = marcas_menu.sub(lambda m: ' aria-current="page"' if m.group(1) == pagina.slug else "", modelo)
    base_tag = f'  <base href="{URL_BASE}/">\n' if pagina.slug == "404" else ""
    trocas = {
        "{{base_tag}}": base_tag,
        "{{titulo}}": esc(pagina.titulo),
        "{{descricao}}": esc(pagina.descricao),
        "{{robots}}": esc(pagina.robots),
        "{{url}}": esc(pagina.url),
        "{{og_imagem}}": esc(f"{URL_BASE}/{IMAGEM_SOCIAL}"),
        "{{bloco_json_ld}}": montar_json_ld(pagina),
        "{{atualizado}}": pagina.modificada.strftime("%d/%m/%Y"),
        "{{conteudo}}": pagina.corpo,
    }
    for marca, valor in trocas.items():
        saida = saida.replace(marca, valor)
    restantes = re.findall(r"\{\{[^}]+\}\}", saida)
    if restantes:
        raise ValueError(f"{pagina.slug}: marcas sem preencher: {', '.join(sorted(set(restantes)))}")
    return saida


def montar_sitemap(paginas: list[Pagina]) -> str:
    """Sitemap com as páginas indexáveis."""
    itens = [
        f"  <url>\n    <loc>{html.escape(p.url)}</loc>\n    <lastmod>{p.modificada:%Y-%m-%d}</lastmod>\n  </url>"
        for p in sorted(paginas, key=lambda p: p.slug) if "noindex" not in p.robots
    ]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(itens) + "\n</urlset>\n")


def montar_robots() -> str:
    return f"User-agent: *\nAllow: /\nDisallow: /fonte-\nDisallow: /modelo-\n\nSitemap: {URL_BASE}/sitemap.xml\n"


def main() -> int:
    modelo_caminho = RAIZ / "modelo-base.html"
    if not modelo_caminho.is_file():
        print("Estrutura incompleta: falta modelo-base.html.", file=sys.stderr)
        return 1
    modelo = modelo_caminho.read_text(encoding="utf-8")
    try:
        paginas = [ler_pagina(c) for c in sorted(RAIZ.glob("fonte-*.html"))]
        for pagina in paginas:
            (RAIZ / pagina.arquivo).write_text(aplicar_modelo(modelo, pagina), encoding="utf-8", newline="\n")
            print(f"gerada: {pagina.arquivo}")
    except ValueError as erro:
        print(f"Erro de conteúdo: {erro}", file=sys.stderr)
        return 1
    (RAIZ / "sitemap.xml").write_text(montar_sitemap(paginas), encoding="utf-8", newline="\n")
    (RAIZ / "robots.txt").write_text(montar_robots(), encoding="utf-8", newline="\n")
    print(f"{len(paginas)} páginas, sitemap.xml e robots.txt gerados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
