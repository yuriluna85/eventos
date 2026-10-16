/* Rota Eventos | comportamento base: acessibilidade, menu, cookies, filtros e contato */
(function () {
  'use strict';

  // E-mail de contato: preencher aqui e nas páginas quando definido.
  var EMAIL_CONTATO = '';

  function guardar(chave, valor) {
    try { window.localStorage.setItem(chave, valor); } catch (e) { /* armazenamento indisponível */ }
  }
  function ler(chave) {
    try { return window.localStorage.getItem(chave); } catch (e) { return null; }
  }

  /* Acessibilidade: tamanho da fonte e alto contraste */
  var raiz = document.documentElement;
  var PASSOS = [0.875, 1, 1.125, 1.25, 1.5];

  function aplicarEscala(indice) {
    var i = Math.max(0, Math.min(PASSOS.length - 1, indice));
    raiz.style.setProperty('--escala-fonte', String(PASSOS[i]));
    guardar('rota-escala', String(i));
    return i;
  }

  var indiceEscala = parseInt(ler('rota-escala'), 10);
  if (isNaN(indiceEscala)) { indiceEscala = 1; }
  aplicarEscala(indiceEscala);

  function aplicarContraste(ligado) {
    raiz.classList.toggle('high-contrast', ligado);
    guardar('rota-contraste', ligado ? '1' : '0');
    var botao = document.getElementById('btn-contraste');
    if (botao) { botao.setAttribute('aria-pressed', ligado ? 'true' : 'false'); }
  }
  aplicarContraste(ler('rota-contraste') === '1');

  function ligar(id, acao) {
    var el = document.getElementById(id);
    if (el) { el.addEventListener('click', acao); }
  }
  ligar('btn-fonte-menos', function () { indiceEscala = aplicarEscala(indiceEscala - 1); });
  ligar('btn-fonte-normal', function () { indiceEscala = aplicarEscala(1); });
  ligar('btn-fonte-mais', function () { indiceEscala = aplicarEscala(indiceEscala + 1); });
  ligar('btn-contraste', function () { aplicarContraste(!raiz.classList.contains('high-contrast')); });

  /* Gaveta de navegação (telas abaixo de 1024px) */
  var botaoMenu = document.getElementById('btn-menu');
  var gaveta = document.getElementById('gaveta-menu');
  if (botaoMenu && gaveta) {
    botaoMenu.addEventListener('click', function () {
      var aberta = gaveta.classList.toggle('aberta');
      botaoMenu.setAttribute('aria-expanded', aberta ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape' && gaveta.classList.contains('aberta')) {
        gaveta.classList.remove('aberta');
        botaoMenu.setAttribute('aria-expanded', 'false');
        botaoMenu.focus();
      }
    });
  }

  /* Aviso de cookies (LGPD) */
  var banner = document.getElementById('cookie-banner');
  if (banner && !ler('rota-cookies')) {
    banner.hidden = false;
    var escolher = function (valor) {
      guardar('rota-cookies', valor);
      banner.hidden = true;
    };
    ligar('cookie-aceitar', function () { escolher('todos'); });
    ligar('cookie-necessarios', function () { escolher('necessarios'); });
  }

  /* Filtros da lista de eventos */
  var cartoes = Array.prototype.slice.call(document.querySelectorAll('.card-evento[data-modalidade]'));
  var campoBusca = document.getElementById('filtro-busca');
  if (cartoes.length && campoBusca) {
    var filtros = {
      modalidade: document.getElementById('filtro-modalidade'),
      area: document.getElementById('filtro-area'),
      uf: document.getElementById('filtro-uf'),
      mes: document.getElementById('filtro-mes')
    };
    var vazio = document.getElementById('sem-resultado');

    var normalizar = function (texto) {
      return String(texto || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    };

    var filtrar = function () {
      var termo = normalizar(campoBusca.value);
      var visiveis = 0;
      cartoes.forEach(function (cartao) {
        var ok = true;
        Object.keys(filtros).forEach(function (chave) {
          var campo = filtros[chave];
          if (campo && campo.value && cartao.dataset[chave] !== campo.value) { ok = false; }
        });
        if (ok && termo && normalizar(cartao.textContent).indexOf(termo) === -1) { ok = false; }
        cartao.hidden = !ok;
        if (ok) { visiveis += 1; }
      });
      if (vazio) { vazio.hidden = visiveis > 0; }
    };

    campoBusca.addEventListener('input', filtrar);
    Object.keys(filtros).forEach(function (chave) {
      if (filtros[chave]) { filtros[chave].addEventListener('change', filtrar); }
    });
  }

  /* Formulário de contato: abre o programa de e-mail com a mensagem pronta */
  var formulario = document.getElementById('form-contato');
  if (formulario) {
    formulario.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var retorno = document.getElementById('retorno-contato');
      var nome = formulario.elements.nome.value.trim();
      var email = formulario.elements.email.value.trim();
      var assunto = formulario.elements.assunto.value.trim();
      var mensagem = formulario.elements.mensagem.value.trim();
      if (!nome || !email || !assunto || !mensagem) {
        retorno.textContent = 'Preencha todos os campos antes de enviar.';
        retorno.hidden = false;
        return;
      }
      if (!EMAIL_CONTATO) {
        retorno.textContent = 'O canal de e-mail do portal ainda não foi configurado. Tente novamente em breve.';
        retorno.hidden = false;
        return;
      }
      var corpo = 'Nome: ' + nome + '\nE-mail: ' + email + '\n\n' + mensagem;
      window.location.href = 'mailto:' + EMAIL_CONTATO + '?subject=' + encodeURIComponent('[Rota Eventos] ' + assunto) +
        '&body=' + encodeURIComponent(corpo);
      retorno.textContent = 'Seu programa de e-mail foi aberto com a mensagem pronta. Falta só enviar. Respondemos em até 48 horas úteis.';
      retorno.hidden = false;
      formulario.reset();
    });
  }
})();
