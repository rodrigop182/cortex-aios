const demoSteps = [
  {
    before: "“Me fala seus objetivos, seu contexto, suas restrições e o que você já tentou.”",
    after:
      "“Vou ler seu perfil, prioridades e projeto ativo. Depois volto com uma recomendação e a primeira ação concreta.”",
  },
  {
    before: "“Cole aqui seu briefing, seu tom de voz e as regras do projeto.”",
    after:
      "“Encontrei prioridade ativa, regras de execução e referências. Vou usar só o que sustenta esta decisão.”",
  },
  {
    before: "“Aqui vão várias ideias possíveis para você escolher.”",
    after:
      "“Recomendação: faça a vitrine do produto primeiro. Motivo: ela prova valor antes de expandir arquitetura.”",
  },
  {
    before: "“Entendi, vou tentar lembrar na próxima conversa.”",
    after:
      "“Registrei a regra na fila certa. Na próxima sessão, vou aplicar isso sem pedir a mesma correção.”",
  },
];

const runtimes = {
  claude: {
    level: "Full",
    title: "Claude Code",
    copy:
      "Usa o pacote completo: skills, hooks, onboard, audit, destilação, atualização e segurança por hook.",
  },
  codex: {
    level: "Médio",
    title: "Codex CLI ou extensão no VSCode",
    copy:
      "Usa AGENTS.md, memória externa e scripts locais. Onde o runtime não tiver hook, a destilação roda por comando manual.",
  },
  ide: {
    level: "Básico a médio",
    title: "Cursor, Cline, Windsurf e similares",
    copy:
      "Usa regras de projeto, referências sob demanda e memória em Markdown. A automação depende do acesso a shell e arquivos.",
  },
};

const demoTabs = document.querySelectorAll("[data-demo-step]");
const demoBefore = document.querySelector("[data-demo-before]");
const demoAfter = document.querySelector("[data-demo-after]");

demoTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    const step = demoSteps[Number(tab.dataset.demoStep)];
    demoBefore.textContent = step.before;
    demoAfter.textContent = step.after;

    demoTabs.forEach((item) => {
      item.classList.remove("is-active");
      item.setAttribute("aria-selected", "false");
    });

    tab.classList.add("is-active");
    tab.setAttribute("aria-selected", "true");
  });
});

const runtimeTabs = document.querySelectorAll("[data-runtime]");
const runtimeLevel = document.querySelector("[data-runtime-level]");
const runtimeTitle = document.querySelector("[data-runtime-title]");
const runtimeCopy = document.querySelector("[data-runtime-copy]");

runtimeTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    const runtime = runtimes[tab.dataset.runtime];
    runtimeLevel.textContent = runtime.level;
    runtimeTitle.textContent = runtime.title;
    runtimeCopy.textContent = runtime.copy;

    runtimeTabs.forEach((item) => {
      item.classList.remove("is-active");
      item.setAttribute("aria-selected", "false");
    });

    tab.classList.add("is-active");
    tab.setAttribute("aria-selected", "true");
  });
});
