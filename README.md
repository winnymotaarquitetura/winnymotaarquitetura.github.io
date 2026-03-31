# Winny Mota | Portfólio de Arquitetura e Urbanismo

Site de portfólio pessoal com foco em apresentação de projetos arquitetônicos e de interiores.

## Visão geral

O projeto foi desenvolvido como site estático, com:

- Página inicial com apresentação, trajetória e grade de projetos.
- Página de detalhe de projeto com:
	- galeria de fotos,
	- descrição completa,
	- detalhes técnicos,
	- navegação entre projetos,
	- lightbox para ampliar imagens.
- Script Python para gerenciar projetos pelo terminal (adicionar, editar e remover).

## Tecnologias

- HTML5
- Tailwind CSS (CDN)
- JavaScript (vanilla)
- Python 3 (script de automação de conteúdo)

## Estrutura do projeto

```text
.
├── index.html
├── projeto.html
├── add_project.py
├── README.md
└── assets
		├── css
		│   └── style.css
		├── img
		│   └── WINNY.jpg
		├── js
		│   ├── main.js
		│   ├── project-data.js
		│   ├── projeto.js
		│   └── tailwind-config.js
		└── projetos
				└── <slug-do-projeto>
						├── capa.png
						├── foto-01.png
						├── foto-02.png
						└── foto-03.png
```

## Gerenciamento de projetos (script)

O arquivo `add_project.py` oferece um menu interativo para manutenção dos projetos.

Execute:

```bash
python3 add_project.py
```

Menu disponível:

1. Adicionar projeto
2. Editar projeto
3. Remover projeto

### O que o script atualiza

- Cria/atualiza pasta de imagens em `assets/projetos/<slug>/`.
- Atualiza dados em `assets/js/project-data.js`.
- Adiciona, atualiza ou remove card na seção de projetos em `index.html`.

## Padrão de imagens por projeto

Para manter consistência visual, cada projeto deve usar:

- `capa.png` (imagem de capa do card)
- `foto-01.png`
- `foto-02.png`
- `foto-03.png`

Você pode usar mais fotos, desde que ajuste a quantidade no fluxo do script e os caminhos no `project-data.js`.

## Personalizações comuns

- Textos e estrutura da página inicial: `index.html`
- Layout da página de projeto: `projeto.html`
- Estilos globais e componentes: `assets/css/style.css`
- Interações da home: `assets/js/main.js`
- Interações da página de projeto: `assets/js/projeto.js`
- Dados dos projetos: `assets/js/project-data.js`
