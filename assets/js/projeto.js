document.addEventListener('DOMContentLoaded', () => {
    const projectTitle = document.getElementById('project-title');
    const projectMeta = document.getElementById('project-meta');
    const projectSummary = document.getElementById('project-summary');
    const projectDescription = document.getElementById('project-description');
    const projectScope = document.getElementById('project-scope');
    const projectTools = document.getElementById('project-tools');
    const projectHighlights = document.getElementById('project-highlights');
    const projectMainImage = document.getElementById('project-main-image');
    const projectThumbnails = document.getElementById('project-thumbnails');
    const projectPrevLink = document.getElementById('project-prev-link');
    const projectNextLink = document.getElementById('project-next-link');

    if (
        !projectTitle ||
        !projectMeta ||
        !projectSummary ||
        !projectDescription ||
        !projectScope ||
        !projectTools ||
        !projectHighlights ||
        !projectMainImage ||
        !projectThumbnails ||
        !projectPrevLink ||
        !projectNextLink
    ) {
        return;
    }

    const params = new URLSearchParams(window.location.search);
    const projectId = params.get('id');

    if (!projectId || !window.PROJECTS_DATA || !window.PROJECTS_DATA[projectId]) {
        projectTitle.textContent = 'Projeto nao encontrado';
        projectMeta.textContent = 'Erro';
        projectSummary.textContent = 'Nao foi possivel carregar este projeto. Volte para o portfolio e selecione novamente.';
        projectDescription.textContent = 'Verifique se o link acessado esta correto.';
        projectScope.textContent = '-';
        projectTools.textContent = '-';
        projectHighlights.innerHTML = '<li>Nenhuma informacao disponivel.</li>';
        projectMainImage.src = './assets/projetos/residencia-u/capa.png';
        projectMainImage.alt = 'Projeto nao encontrado';
        return;
    }

    const project = window.PROJECTS_DATA[projectId];
    const projectOrder = window.PROJECTS_ORDER || Object.keys(window.PROJECTS_DATA);
    const images = project.images || [];

    document.title = `${project.title} | Winny Mota`;
    projectTitle.textContent = project.title;
    projectMeta.textContent = `${project.year} | ${project.category} | ${project.location}`;
    projectSummary.textContent = project.summary;
    projectDescription.textContent = project.description;
    projectScope.textContent = project.scope || 'Nao informado.';
    projectTools.textContent = project.tools || 'Nao informado.';

    projectHighlights.innerHTML = '';
    (project.highlights || []).forEach((item) => {
        const li = document.createElement('li');
        li.textContent = item;
        projectHighlights.appendChild(li);
    });

    if (projectHighlights.children.length === 0) {
        const li = document.createElement('li');
        li.textContent = 'Sem destaques cadastrados para este projeto.';
        projectHighlights.appendChild(li);
    }

    const currentIndex = projectOrder.indexOf(projectId);
    const prevIndex = currentIndex <= 0 ? projectOrder.length - 1 : currentIndex - 1;
    const nextIndex = currentIndex >= projectOrder.length - 1 ? 0 : currentIndex + 1;
    const prevId = projectOrder[prevIndex];
    const nextId = projectOrder[nextIndex];
    const prevProject = window.PROJECTS_DATA[prevId];
    const nextProject = window.PROJECTS_DATA[nextId];

    projectPrevLink.href = `./projeto.html?id=${prevId}`;
    projectPrevLink.innerHTML = `<i class="ph ph-arrow-left"></i> ${prevProject ? prevProject.title : 'Projeto anterior'}`;

    projectNextLink.href = `./projeto.html?id=${nextId}`;
    projectNextLink.innerHTML = `${nextProject ? nextProject.title : 'Proximo projeto'} <i class="ph ph-arrow-right"></i>`;

    const updateMainImage = (imageSrc) => {
        projectMainImage.src = imageSrc;
        projectMainImage.alt = `Imagem do projeto ${project.title}`;
    };

    if (images.length > 0) {
        updateMainImage(images[0]);

        images.forEach((imageSrc, index) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'project-thumb overflow-hidden rounded-sm border border-stone-200 bg-stone-100';
            button.setAttribute('aria-label', `Abrir foto ${index + 1} do projeto ${project.title}`);
            button.dataset.image = imageSrc;

            const image = document.createElement('img');
            image.src = imageSrc;
            image.alt = `Miniatura ${index + 1} de ${project.title}`;
            image.className = 'w-full h-20 md:h-24 object-cover';

            button.appendChild(image);
            projectThumbnails.appendChild(button);
        });

        const thumbnailButtons = projectThumbnails.querySelectorAll('.project-thumb');

        const setActiveThumb = (currentSrc) => {
            thumbnailButtons.forEach((button) => {
                button.classList.toggle('project-thumb-active', button.dataset.image === currentSrc);
            });
        };

        setActiveThumb(images[0]);

        thumbnailButtons.forEach((button) => {
            button.addEventListener('click', () => {
                const imageSrc = button.dataset.image;
                if (!imageSrc) {
                    return;
                }
                updateMainImage(imageSrc);
                setActiveThumb(imageSrc);
            });
        });
    }
});
