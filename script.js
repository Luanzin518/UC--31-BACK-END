/* CineRepertório — interações da interface */
document.addEventListener("DOMContentLoaded", function () {
  // Botão "copiar parágrafo-modelo" ------------------------------------------
  document.querySelectorAll("[data-citacao]").forEach(function (botao) {
    botao.addEventListener("click", function () {
      var texto = botao.getAttribute("data-citacao") || "";
      var rotulo = botao.textContent;
      function feedback() {
        botao.textContent = "Copiado!";
        setTimeout(function () { botao.textContent = rotulo; }, 1600);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(texto).then(feedback);
      } else {
        var area = document.createElement("textarea");
        area.value = texto;
        document.body.appendChild(area);
        area.select();
        document.execCommand("copy");
        document.body.removeChild(area);
        feedback();
      }
    });
  });

  // Botão "copiar citação" -------------------------------------------------
  document.querySelectorAll("[data-copiar]").forEach(function (botao) {
    botao.addEventListener("click", function () {
      var alvo = document.querySelector(botao.dataset.copiar);
      if (!alvo) return;
      var texto = alvo.textContent.trim();
      var rotuloOriginal = botao.textContent;

      function confirmar() {
        botao.textContent = "Citação copiada!";
        setTimeout(function () {
          botao.textContent = rotuloOriginal;
        }, 2000);
      }

      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(texto).then(confirmar);
      } else {
        var campo = document.createElement("textarea");
        campo.value = texto;
        document.body.appendChild(campo);
        campo.select();
        document.execCommand("copy");
        document.body.removeChild(campo);
        confirmar();
      }
    });
  });

  // Esteiras: pausa também ao tocar na tela (dispositivos móveis) -----------
  document.querySelectorAll("[data-esteira]").forEach(function (esteira) {
    var trilha = esteira.querySelector(".esteira-trilha");
    if (!trilha) return;
    esteira.addEventListener("touchstart", function () {
      trilha.style.animationPlayState = "paused";
    });
    esteira.addEventListener("touchend", function () {
      trilha.style.animationPlayState = "running";
    });
  });

  // Envio automático dos filtros ao trocar de opção -------------------------
  var formFiltros = document.querySelector(".filtros");
  if (formFiltros) {
    formFiltros.querySelectorAll("select").forEach(function (campo) {
      campo.addEventListener("change", function () {
        formFiltros.submit();
      });
    });
  }
});

/* =========================================================================
   Acessibilidade — daltonismo, contraste, fonte, movimento, Libras e voz
   ========================================================================= */
(function () {
  const html = document.documentElement;
  const salvar = (chave, valor) => localStorage.setItem("acess-" + chave, valor);
  const ler = (chave) => localStorage.getItem("acess-" + chave);

  const abrir = document.getElementById("acess-abrir");
  const painel = document.getElementById("acess-painel");
  if (abrir && painel) {
    abrir.addEventListener("click", () => {
      const aberto = !painel.hidden;
      painel.hidden = aberto;
      abrir.setAttribute("aria-expanded", String(!aberto));
    });
  }

  const daltonismo = document.getElementById("acess-daltonismo");
  function aplicarDaltonismo(valor) {
    ["protanopia", "deuteranopia", "tritanopia", "monocromatico"].forEach((m) =>
      html.classList.remove("daltonismo-" + m)
    );
    if (valor && valor !== "nenhum") html.classList.add("daltonismo-" + valor);
    salvar("daltonismo", valor);
  }
  if (daltonismo) {
    daltonismo.value = ler("daltonismo") || "nenhum";
    aplicarDaltonismo(daltonismo.value);
    daltonismo.addEventListener("change", () => aplicarDaltonismo(daltonismo.value));
  }

  const alternadores = [
    ["acess-contraste", "alto-contraste"],
    ["acess-fonte", "fonte-ampliada"],
    ["acess-movimento", "sem-movimento"],
  ];
  alternadores.forEach(([id, classe]) => {
    const campo = document.getElementById(id);
    if (!campo) return;
    const ativo = ler(classe) === "1";
    campo.checked = ativo;
    html.classList.toggle(classe, ativo);
    campo.addEventListener("change", () => {
      html.classList.toggle(classe, campo.checked);
      salvar(classe, campo.checked ? "1" : "0");
    });
  });

  // VLibras (tradutor oficial de Libras do Governo Federal)
  const libras = document.getElementById("acess-libras");
  function ligarVLibras() {
    if (document.getElementById("vlibras-wrapper")) return;
    const wrapper = document.createElement("div");
    wrapper.id = "vlibras-wrapper";
    wrapper.setAttribute("vw", "");
    wrapper.className = "enabled";
    wrapper.innerHTML =
      '<div vw-access-button class="active"></div><div vw-plugin-wrapper><div class="vw-plugin-top-wrapper"></div></div>';
    document.body.appendChild(wrapper);
    const script = document.createElement("script");
    script.src = "https://vlibras.gov.br/app/vlibras-plugin.js";
    script.onload = () => {
      try { new window.VLibras.Widget("https://vlibras.gov.br/app"); } catch (e) { console.warn(e); }
    };
    document.body.appendChild(script);
  }
  if (libras) {
    libras.checked = ler("libras") === "1";
    if (libras.checked) ligarVLibras();
    libras.addEventListener("change", () => {
      salvar("libras", libras.checked ? "1" : "0");
      if (libras.checked) ligarVLibras();
      else location.reload();
    });
  }

  const ler_voz = document.getElementById("acess-ler");
  if (ler_voz) {
    ler_voz.addEventListener("click", () => {
      if (!("speechSynthesis" in window)) return alert("Seu navegador não tem síntese de voz.");
      const principal = document.getElementById("conteudo");
      if (speechSynthesis.speaking) { speechSynthesis.cancel(); return; }
      const fala = new SpeechSynthesisUtterance(principal.innerText.slice(0, 4000));
      fala.lang = "pt-BR";
      speechSynthesis.speak(fala);
    });
  }

  const limpar = document.getElementById("acess-limpar");
  if (limpar) {
    limpar.addEventListener("click", () => {
      ["daltonismo", "alto-contraste", "fonte-ampliada", "sem-movimento", "libras"].forEach((c) =>
        localStorage.removeItem("acess-" + c)
      );
      location.reload();
    });
  }
})();

/* =========================================================================
   Assistente de redação (IA) — abre ao passar o mouse, voz e câmera
   ========================================================================= */
(function () {
  const caixa = document.getElementById("ia-caixa");
  const painel = document.getElementById("ia-painel");
  const abrir = document.getElementById("ia-abrir");
  const fechar = document.getElementById("ia-fechar");
  const form = document.getElementById("ia-form");
  const entrada = document.getElementById("ia-entrada");
  const lista = document.getElementById("ia-mensagens");
  if (!caixa || !painel) return;

  let fixado = false;

  function mostrar(estado) {
    painel.hidden = !estado;
    abrir.setAttribute("aria-expanded", String(estado));
  }
  caixa.addEventListener("mouseenter", () => mostrar(true));
  caixa.addEventListener("mouseleave", () => { if (!fixado) mostrar(false); });
  caixa.addEventListener("focusin", () => mostrar(true));
  abrir.addEventListener("click", () => { fixado = !fixado; mostrar(true); entrada.focus(); });
  fechar.addEventListener("click", () => { fixado = false; mostrar(false); });
  document.querySelectorAll("[data-abrir-ia]").forEach((b) =>
    b.addEventListener("click", () => { fixado = true; mostrar(true); entrada.focus(); })
  );

  function bolha(texto, quem) {
    const div = document.createElement("div");
    div.className = "ia-msg " + quem;
    div.textContent = texto;
    lista.appendChild(div);
    lista.scrollTop = lista.scrollHeight;
    return div;
  }

  function renderizar(dados) {
    const div = bolha(dados.texto, "bot");
    (dados.blocos || []).forEach((b) => {
      const bloco = document.createElement("div");
      bloco.className = "ia-bloco";
      bloco.innerHTML = "<strong></strong><p class='mb-0'></p>";
      bloco.querySelector("strong").textContent = b.titulo;
      bloco.querySelector("p").textContent = b.texto;
      div.appendChild(bloco);
    });
    (dados.filmes || []).forEach((f) => {
      const link = document.createElement("a");
      link.className = "ia-chip d-inline-block mt-2 me-1";
      link.href = "/filmes/" + f.id;
      link.textContent = `${f.titulo} (${f.ano}) · IMDb ${f.imdb}`;
      div.appendChild(link);
    });
    (dados.videos || []).forEach((v) => {
      const link = document.createElement("a");
      link.className = "ia-chip d-inline-block mt-2 me-1";
      link.href = v.url;
      link.target = "_blank";
      link.rel = "noopener";
      link.textContent = `▶ ${v.tipo}: ${v.titulo} (${v.duracao})`;
      div.appendChild(link);
    });
    const chips = document.getElementById("ia-sugestoes");
    if (dados.sugestoes && dados.sugestoes.length) {
      chips.innerHTML = "";
      dados.sugestoes.forEach((s) => {
        const botao = document.createElement("button");
        botao.type = "button";
        botao.className = "ia-chip";
        botao.textContent = s;
        chips.appendChild(botao);
      });
    }
    lista.scrollTop = lista.scrollHeight;
  }

  async function perguntar(mensagem) {
    if (!mensagem.trim()) return;
    bolha(mensagem, "eu");
    entrada.value = "";
    const carregando = bolha("Pensando...", "bot");
    try {
      const resposta = await fetch("/api/assistente", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensagem }),
      });
      const dados = await resposta.json();
      carregando.remove();
      renderizar(dados);
    } catch (erro) {
      carregando.textContent = "Não consegui responder agora. Tente novamente.";
    }
  }

  form.addEventListener("submit", (e) => { e.preventDefault(); perguntar(entrada.value); });
  document.addEventListener("click", (e) => {
    const chip = e.target.closest(".ia-chip");
    if (!chip || chip.tagName === "A") return;
    const texto = chip.dataset.pergunta || chip.textContent;
    fixado = true; mostrar(true);
    perguntar(texto);
  });

  // Comando de voz (pede permissão do microfone)
  const botaoVoz = document.getElementById("ia-voz");
  botaoVoz.addEventListener("click", async () => {
    const Reconhecimento = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Reconhecimento) return alert("Seu navegador não suporta reconhecimento de voz.");
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (e) {
      return alert("Precisamos da sua permissão para usar o microfone.");
    }
    const rec = new Reconhecimento();
    rec.lang = "pt-BR";
    rec.interimResults = false;
    botaoVoz.textContent = "🎙️ Ouvindo...";
    rec.onresult = (evento) => { entrada.value = evento.results[0][0].transcript; };
    rec.onend = () => { botaoVoz.textContent = "🎤 Voz"; };
    rec.onerror = () => { botaoVoz.textContent = "🎤 Voz"; };
    rec.start();
  });

  // Câmera (pede permissão antes de ligar)
  const camera = document.getElementById("ia-camera");
  const video = document.getElementById("ia-video");
  const canvas = document.getElementById("ia-canvas");
  let fluxo = null;

  document.getElementById("ia-foto").addEventListener("click", async () => {
    try {
      fluxo = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
      video.srcObject = fluxo;
      camera.hidden = false;
    } catch (e) {
      alert("Precisamos da sua permissão para usar a câmera.");
    }
  });

  function pararCamera() {
    if (fluxo) fluxo.getTracks().forEach((t) => t.stop());
    fluxo = null;
    camera.hidden = true;
  }
  document.getElementById("ia-cancelar-camera").addEventListener("click", pararCamera);
  document.getElementById("ia-capturar").addEventListener("click", () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    const img = document.createElement("img");
    img.src = canvas.toDataURL("image/png");
    img.alt = "Foto da redação capturada pela câmera";
    img.className = "img-fluid rounded mt-2";
    const div = bolha("Foto da minha redação:", "eu");
    div.appendChild(img);
    pararCamera();
    perguntar("Tirei uma foto da minha redação. Como faço para melhorar a estrutura e a proposta de intervenção?");
  });

  bolha("Olá! Sou o assistente de redação do CineRepertório. Posso escrever uma redação completa, corrigir a sua pelas 5 competências, sugerir filmes e videoaulas. Clique numa sugestão abaixo ou escreva sua dúvida.", "bot");
})();
