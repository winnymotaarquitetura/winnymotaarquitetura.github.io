#!/usr/bin/env python3
"""Interactive project manager for the portfolio.

Features:
1. Add a new project.
2. Edit an existing project.
3. Remove a project.
"""

from __future__ import annotations

import re
import shutil
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROJECTS_DIR = ROOT / "assets" / "projetos"
DATA_FILE = ROOT / "assets" / "js" / "project-data.js"
INDEX_FILE = ROOT / "index.html"


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text.strip().lower())
    return slug.strip("-")


def ask(prompt: str, required: bool = True, default: str | None = None) -> str:
    while True:
        suffix = f" [{default}]" if default is not None else ""
        value = input(f"{prompt}{suffix}: ").strip()
        if not value and default is not None:
            return default
        if value or not required:
            return value
        print("Campo obrigatorio. Tente novamente.")


def ask_int(prompt: str, default: int | None = None, min_value: int = 1) -> int:
    while True:
        default_str = str(default) if default is not None else None
        raw = ask(prompt, default=default_str)
        try:
            value = int(raw)
            if value < min_value:
                print(f"Digite um numero maior ou igual a {min_value}.")
                continue
            return value
        except ValueError:
            print("Digite um numero valido.")


def ask_yes_no(prompt: str, default_yes: bool = True) -> bool:
    default_hint = "Y/n" if default_yes else "y/N"
    while True:
        value = input(f"{prompt} ({default_hint}): ").strip().lower()
        if value == "":
            return default_yes
        if value in {"y", "yes", "s", "sim"}:
            return True
        if value in {"n", "no", "nao"}:
            return False
        print("Resposta invalida. Digite y ou n.")


def ask_multiline(title: str) -> str:
    print(f"{title} (pressione Enter em linha vazia para finalizar):")
    lines: list[str] = []
    while True:
        line = input().strip()
        if not line:
            break
        lines.append(line)
    return " ".join(lines)


def ask_highlights() -> list[str]:
    print("Digite os pontos de destaque (linha vazia para finalizar):")
    items: list[str] = []
    while True:
        line = input(f"- Destaque {len(items) + 1}: ").strip()
        if not line:
            break
        items.append(line)
    if not items:
        items.append("Destaques em atualizacao.")
    return items


def ask_choice() -> str:
    print("\nEscolha uma opcao:")
    print("1) Adicionar projeto")
    print("2) Editar projeto")
    print("3) Remover projeto")

    while True:
        choice = input("Opcao [1/2/3]: ").strip()
        if choice in {"1", "2", "3"}:
            return choice
        print("Opcao invalida. Digite 1, 2 ou 3.")


def copy_image(src_input: str, destination: Path) -> bool:
    src = Path(src_input).expanduser()
    if not src.is_absolute():
        src = (ROOT / src).resolve()

    if not src.exists() or not src.is_file():
        print(f"Aviso: arquivo nao encontrado, pulando copia -> {src_input}")
        return False

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, destination)
    return True


def parse_js_string(value: str) -> str:
    value = value.strip()
    if value.startswith("'") and value.endswith("'"):
        value = value[1:-1]
    return value.replace("\\'", "'").replace("\\\\", "\\")


def update_project_order(content: str, slug: str) -> str:
    match = re.search(r"window\.PROJECTS_ORDER\s*=\s*\[(.*?)\];", content, re.S)
    if not match:
        raise ValueError("Nao foi possivel localizar PROJECTS_ORDER em project-data.js")

    inner = match.group(1)
    ids = re.findall(r"'([^']+)'", inner)
    if slug in ids:
        return content

    ids.append(slug)
    order_lines = ["window.PROJECTS_ORDER = ["]
    for item in ids:
        order_lines.append(f"    '{item}',")
    order_lines.append("];\n")
    new_block = "\n".join(order_lines)
    return content[: match.start()] + new_block + content[match.end() :]


def parse_project_order(content: str) -> list[str]:
    match = re.search(r"window\.PROJECTS_ORDER\s*=\s*\[(.*?)\];", content, re.S)
    if not match:
        raise ValueError("Nao foi possivel localizar PROJECTS_ORDER em project-data.js")
    return re.findall(r"'([^']+)'", match.group(1))


def replace_project_order(content: str, ids: list[str]) -> str:
    match = re.search(r"window\.PROJECTS_ORDER\s*=\s*\[(.*?)\];", content, re.S)
    if not match:
        raise ValueError("Nao foi possivel localizar PROJECTS_ORDER em project-data.js")

    order_lines = ["window.PROJECTS_ORDER = ["]
    for item in ids:
        order_lines.append(f"    '{item}',")
    order_lines.append("];\n")
    new_block = "\n".join(order_lines)
    return content[: match.start()] + new_block + content[match.end() :]


def split_projects_data(content: str) -> tuple[str, str, str]:
    marker = "window.PROJECTS_DATA = {"
    start = content.find(marker)
    if start == -1:
        raise ValueError("Nao foi possivel localizar PROJECTS_DATA em project-data.js")

    end = content.rfind("\n};")
    if end == -1 or end <= start:
        raise ValueError("Nao foi possivel localizar fim de PROJECTS_DATA em project-data.js")

    prefix = content[: start + len(marker)]
    body = content[start + len(marker) : end]
    suffix = content[end:]
    return prefix, body, suffix


def parse_entries_map(body: str) -> dict[str, str]:
    pattern = re.compile(r"(?ms)^\s{4}'([^']+)': \{\n.*?^\s{4}\}(?=,\n\s{4}'[^']+': \{|\n$)")
    entries: dict[str, str] = {}
    for match in pattern.finditer(body.strip()):
        slug = match.group(1)
        block = match.group(0)
        entries[slug] = block
    return entries


def js_string(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def build_project_entry(
    slug: str,
    title: str,
    category: str,
    year: str,
    location: str,
    summary: str,
    description: str,
    scope: str,
    tools: str,
    highlights: list[str],
    image_count: int,
) -> str:
    lines: list[str] = []
    lines.append(f"    '{slug}': {{")
    lines.append(f"        title: {js_string(title)},")
    lines.append(f"        category: {js_string(category)},")
    lines.append(f"        year: {js_string(year)},")
    lines.append(f"        location: {js_string(location)},")
    lines.append(f"        summary: {js_string(summary)},")
    lines.append(f"        description: {js_string(description)},")
    lines.append(f"        scope: {js_string(scope)},")
    lines.append(f"        tools: {js_string(tools)},")
    lines.append("        highlights: [")
    for item in highlights:
        lines.append(f"            {js_string(item)},")
    lines.append("        ],")
    lines.append("        images: [")
    for i in range(1, image_count + 1):
        lines.append(f"            './assets/projetos/{slug}/foto-{i:02d}.png',")
    lines.append("        ]")
    lines.append("    }")
    return "\n".join(lines)


def parse_project_entry(entry_block: str) -> dict[str, object]:
    def field(name: str, fallback: str = "") -> str:
        match = re.search(rf"\n\s{{8}}{name}:\s*('(?:\\'|[^'])*'),", entry_block)
        if not match:
            return fallback
        return parse_js_string(match.group(1))

    title = field("title")
    category = field("category")
    year = field("year")
    location = field("location")
    summary = field("summary")
    description = field("description")
    scope = field("scope")
    tools = field("tools")

    highlights_match = re.search(r"highlights:\s*\[(.*?)\],", entry_block, re.S)
    highlights = []
    if highlights_match:
        highlights = [parse_js_string(item) for item in re.findall(r"('(?:\\'|[^'])*')", highlights_match.group(1))]

    images_match = re.search(r"images:\s*\[(.*?)\]", entry_block, re.S)
    images = []
    if images_match:
        images = [parse_js_string(item) for item in re.findall(r"('(?:\\'|[^'])*')", images_match.group(1))]

    return {
        "title": title,
        "category": category,
        "year": year,
        "location": location,
        "summary": summary,
        "description": description,
        "scope": scope,
        "tools": tools,
        "highlights": highlights,
        "images": images,
    }


def write_project_data(content: str, ids: list[str], entries: dict[str, str]) -> None:
    content = replace_project_order(content, ids)
    prefix, _, suffix = split_projects_data(content)

    ordered_blocks = [entries[item] for item in ids if item in entries]
    if ordered_blocks:
        body = "\n" + ",\n".join(ordered_blocks) + "\n"
    else:
        body = "\n"

    DATA_FILE.write_text(prefix + body + suffix, encoding="utf-8")


def load_project_data() -> tuple[str, list[str], dict[str, str]]:
    content = DATA_FILE.read_text(encoding="utf-8")
    order_ids = parse_project_order(content)
    _, body, _ = split_projects_data(content)
    entries = parse_entries_map(body)
    return content, order_ids, entries


def build_card(slug: str, title: str, category: str, year: str, location: str) -> str:
    return (
        "\n\n"
        f"                <!-- Projeto Novo -->\n"
        f"                <a href=\"./projeto.html?id={slug}\" class=\"project-card group relative aspect-[4/5] overflow-hidden rounded-sm bg-stone-100 cursor-pointer block\" aria-label=\"Abrir projeto {title}\">\n"
        f"                    <img src=\"./assets/projetos/{slug}/capa.png\" alt=\"{title}\" class=\"object-cover w-full h-full transition-transform duration-700 ease-out\">\n"
        "                    <div class=\"project-overlay absolute inset-0 bg-gradient-to-t from-stone-900/90 via-stone-900/40 to-transparent opacity-0 transition-opacity duration-300 flex flex-col justify-end p-6\">\n"
        f"                        <span class=\"text-earth/90 text-xs tracking-widest uppercase font-semibold mb-1\">{year} | {category} ({location})</span>\n"
        f"                        <h4 class=\"text-white font-serif text-2xl\">{title}</h4>\n"
        "                    </div>\n"
        "                </a>"
    )


def remove_card_from_index(content: str, slug: str) -> str:
    pattern = re.compile(
        rf"\n\s*(?:<!--[^\n]*-->\n\s*)?<a href=\"\./projeto\.html\?id={re.escape(slug)}\"[\s\S]*?</a>",
        re.S,
    )
    return pattern.sub("", content)


def update_index_html(slug: str, title: str, category: str, year: str, location: str, remove_only: bool = False) -> None:
    content = INDEX_FILE.read_text(encoding="utf-8")

    content = remove_card_from_index(content, slug)

    if remove_only:
        INDEX_FILE.write_text(content, encoding="utf-8")
        return

    section_start = content.find('<section id="projetos"')
    if section_start == -1:
        raise ValueError("Secao de projetos nao encontrada em index.html")

    section_end = content.find("</section>", section_start)
    if section_end == -1:
        raise ValueError("Fim da secao de projetos nao encontrado em index.html")

    section_content = content[section_start:section_end]
    marker = "\n\n            </div>\n        </div>"
    marker_pos = section_content.rfind(marker)
    if marker_pos == -1:
        raise ValueError("Nao foi possivel localizar o fechamento do grid de projetos em index.html")

    absolute_insert = section_start + marker_pos
    card = build_card(slug, title, category, year, location)
    content = content[:absolute_insert] + card + content[absolute_insert:]

    INDEX_FILE.write_text(content, encoding="utf-8")


def list_projects(ids: list[str], entries: dict[str, str]) -> None:
    print("\nProjetos cadastrados:")
    for idx, slug in enumerate(ids, start=1):
        title = slug
        if slug in entries:
            parsed = parse_project_entry(entries[slug])
            title = str(parsed.get("title") or slug)
        print(f"{idx:02d}) {title} [{slug}]")


def choose_project(ids: list[str], entries: dict[str, str], action: str) -> str:
    if not ids:
        raise ValueError("Nao ha projetos cadastrados.")

    list_projects(ids, entries)
    while True:
        raw = ask(f"Digite o numero do projeto para {action}")
        try:
            idx = int(raw)
            if 1 <= idx <= len(ids):
                return ids[idx - 1]
        except ValueError:
            pass
        print("Numero invalido.")


def collect_project_inputs(defaults: dict[str, object] | None = None) -> tuple[dict[str, object], int, bool]:
    defaults = defaults or {}

    title = ask("Titulo do projeto", default=str(defaults.get("title") or None))
    suggested_slug = slugify(title)
    slug_default = str(defaults.get("slug") or suggested_slug)
    slug = slugify(ask("ID/slug do projeto (sem espacos)", default=slug_default))

    category = ask("Categoria", default=str(defaults.get("category") or None))
    year = ask("Ano", default=str(defaults.get("year") or None))
    location = ask("Localizacao (ex: Salvador-BA)", default=str(defaults.get("location") or None))
    summary = ask("Resumo curto", default=str(defaults.get("summary") or None))

    default_description = str(defaults.get("description") or "")
    if default_description:
        print(f"Descricao atual: {default_description}")
        if ask_yes_no("Quer manter a descricao atual?", default_yes=True):
            description = default_description
        else:
            description = ask_multiline("Nova descricao completa") or summary
    else:
        description = ask_multiline("Descricao completa") or summary

    scope = ask("Escopo", default=str(defaults.get("scope") or None))
    tools = ask("Ferramentas (separadas por virgula)", default=str(defaults.get("tools") or None))

    current_highlights = list(defaults.get("highlights") or [])
    if current_highlights:
        print("Destaques atuais:")
        for item in current_highlights:
            print(f"- {item}")
        keep = ask_yes_no("Quer manter os destaques atuais?", default_yes=True)
        highlights = current_highlights if keep else ask_highlights()
    else:
        highlights = ask_highlights()

    current_images = list(defaults.get("images") or [])
    default_count = len(current_images) if current_images else 3
    image_count = ask_int("Quantidade de fotos da galeria", default=default_count, min_value=1)
    update_images_now = ask_yes_no("Quer copiar/substituir imagens agora?", default_yes=True)

    payload = {
        "slug": slug,
        "title": title,
        "category": category,
        "year": year,
        "location": location,
        "summary": summary,
        "description": description,
        "scope": scope,
        "tools": tools,
        "highlights": highlights,
    }
    return payload, image_count, update_images_now


def copy_project_images(slug: str, image_count: int) -> tuple[bool, int]:
    project_folder = PROJECTS_DIR / slug
    project_folder.mkdir(parents=True, exist_ok=True)

    cover_input = ask("Caminho da imagem de capa (arquivo)")
    copied_cover = copy_image(cover_input, project_folder / "capa.png")

    copied_gallery = 0
    for i in range(1, image_count + 1):
        src = ask(f"Caminho da foto {i:02d} (arquivo)")
        if copy_image(src, project_folder / f"foto-{i:02d}.png"):
            copied_gallery += 1

    return copied_cover, copied_gallery


def add_project() -> None:
    content, order_ids, entries = load_project_data()
    payload, image_count, update_images_now = collect_project_inputs()
    slug = str(payload["slug"])

    if slug in entries:
        raise ValueError(f"Ja existe um projeto com id '{slug}'.")

    copied_cover = False
    copied_gallery = 0
    if update_images_now:
        copied_cover, copied_gallery = copy_project_images(slug, image_count)

    entry_block = build_project_entry(
        slug=slug,
        title=str(payload["title"]),
        category=str(payload["category"]),
        year=str(payload["year"]),
        location=str(payload["location"]),
        summary=str(payload["summary"]),
        description=str(payload["description"]),
        scope=str(payload["scope"]),
        tools=str(payload["tools"]),
        highlights=list(payload["highlights"]),
        image_count=image_count,
    )

    entries[slug] = entry_block
    order_ids.append(slug)
    write_project_data(content, order_ids, entries)
    update_index_html(slug, str(payload["title"]), str(payload["category"]), str(payload["year"]), str(payload["location"]))

    print("\nProjeto cadastrado com sucesso!")
    print(f"- Pasta: {PROJECTS_DIR / slug}")
    print(f"- Capa copiada: {'sim' if copied_cover else 'nao'}")
    print(f"- Fotos copiadas: {copied_gallery}/{image_count}")


def edit_project() -> None:
    content, order_ids, entries = load_project_data()
    slug_to_edit = choose_project(order_ids, entries, "editar")
    defaults = parse_project_entry(entries[slug_to_edit])
    defaults["slug"] = slug_to_edit

    payload, image_count, update_images_now = collect_project_inputs(defaults)
    new_slug = str(payload["slug"])

    if new_slug != slug_to_edit and new_slug in entries:
        raise ValueError(f"Ja existe um projeto com id '{new_slug}'.")

    if update_images_now:
        copy_project_images(new_slug, image_count)

    entry_block = build_project_entry(
        slug=new_slug,
        title=str(payload["title"]),
        category=str(payload["category"]),
        year=str(payload["year"]),
        location=str(payload["location"]),
        summary=str(payload["summary"]),
        description=str(payload["description"]),
        scope=str(payload["scope"]),
        tools=str(payload["tools"]),
        highlights=list(payload["highlights"]),
        image_count=image_count,
    )

    del entries[slug_to_edit]
    entries[new_slug] = entry_block
    order_ids = [new_slug if item == slug_to_edit else item for item in order_ids]
    write_project_data(content, order_ids, entries)

    update_index_html(
        new_slug,
        str(payload["title"]),
        str(payload["category"]),
        str(payload["year"]),
        str(payload["location"]),
    )
    if new_slug != slug_to_edit:
        update_index_html(slug_to_edit, "", "", "", "", remove_only=True)
        old_folder = PROJECTS_DIR / slug_to_edit
        if old_folder.exists() and ask_yes_no("Remover pasta antiga do projeto?", default_yes=False):
            shutil.rmtree(old_folder)

    print("\nProjeto atualizado com sucesso!")
    print(f"- ID atual: {new_slug}")


def remove_project() -> None:
    content, order_ids, entries = load_project_data()
    slug = choose_project(order_ids, entries, "remover")
    parsed = parse_project_entry(entries[slug])
    title = str(parsed.get("title") or slug)

    if not ask_yes_no(f"Confirmar remocao de '{title}'?", default_yes=False):
        print("Operacao cancelada.")
        return

    order_ids = [item for item in order_ids if item != slug]
    del entries[slug]
    write_project_data(content, order_ids, entries)
    update_index_html(slug, "", "", "", "", remove_only=True)

    folder = PROJECTS_DIR / slug
    if folder.exists() and ask_yes_no("Remover tambem a pasta de imagens?", default_yes=False):
        shutil.rmtree(folder)
        print(f"- Pasta removida: {folder}")

    print("\nProjeto removido com sucesso!")


def main() -> None:
    print("=== Assistente de Projetos ===")
    choice = ask_choice()

    if choice == "1":
        add_project()
    elif choice == "2":
        edit_project()
    elif choice == "3":
        remove_project()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(f"\nErro: {exc}")
        raise SystemExit(1)
