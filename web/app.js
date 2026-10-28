import {
  PERSONA_MAP,
  QUIZ,
  QUOTES,
  SAGES as SAGE_PROFILES,
  SCENARIOS,
  VOICES,
  WUDE,
} from "./data.js";
import {
  applyStaticI18n,
  formatGanzhi,
  formatTodayDate,
  getLang,
  initI18n,
  isEn,
  joinPrompts,
  localizeConvTitle,
  localizeTimeLabel,
  modeUi,
  onLangChange,
  personaUi,
  quizUi,
  setLang,
  t,
  te,
  tp,
  voiceUi,
  wudeDesc,
  wudeLabel,
} from "./i18n.js?v=36";

const ASK_KEY = "lunyu.ask";
const FAV_KEY = "lunyu.favs";
const SAGE_KEY = "lunyu.sages";
const MODE_API = { study: "治学", heart: "修心", body: "修身" };
const MODE_UI = { 治学: "study", 修心: "heart", 修身: "body" };
const CAT_META = {
  原文: { cat: "论语", label: "論語", en: "The Analects", cv: "cv-classic" },
  注疏: { cat: "注疏", label: "注疏", en: "Commentaries", cv: "cv-indigo" },
  礼: { cat: "礼记", label: "禮記", en: "The Book of Rites", cv: "cv-jade" },
  史传: { cat: "史传", label: "史傳", en: "Historical Works", cv: "cv-cinnabar" },
};
const SHELF_ORDER = ["论语", "注疏", "礼记", "史传", "家语"];
const SHELF_LABEL = {
  论语: { label: "論語", en: "The Analects" },
  注疏: { label: "注疏", en: "Commentaries" },
  礼记: { label: "禮記", en: "The Book of Rites" },
  史传: { label: "史傳", en: "Historical Works" },
  家语: { label: "家語", en: "Family Sayings" },
};
const PATHS = { home: "/", library: "/library", read: "/book", ask: "/ask", sages: "/sages", create: "/presence", me: "/me" };

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
const esc = (s) =>
  String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const icon = (id, style = "") => `<svg class="i"${style ? ` style="${style}"` : ""}><use href="#${id}"/></svg>`;

function richText(text) {
  let raw = String(text || "").replace(/\r\n/g, "\n").trim();
  raw = raw.replace(/^#{1,6}\s*/gm, "");
  raw = raw.replace(/#{1,6}/g, "");
  raw = raw.replace(/^\s*[-*•]\s+/gm, "");
  raw = raw.replace(/^\s*\d+\.\s+/gm, "");
  raw = raw.replace(/\*\*([^*]+)\*\*/g, "$1");
  raw = raw.replace(/__([^_]+)__/g, "$1");
  raw = raw.replace(/`{1,3}([^`]+)`{1,3}/g, "$1");
  raw = raw.replace(/[ \t]{2,}/g, " ");
  if (!/\n{2,}/.test(raw) && raw.length > 160) {
    raw = raw.replace(/([。！？])(?=(原文|译文|简单来说|第一步|第二步|第三步|第四步|从现代|如果转换))/g, "$1\n\n");
  }
  const blocks = raw
    .split(/\n{2,}/)
    .map((block) => block.trim())
    .filter(Boolean);
  if (!blocks.length) return "";
  return blocks.map((block) => `<p>${esc(block).replace(/\n/g, "<br>")}</p>`).join("");
}

function toast(msg) {
  const root = $("#toastRoot");
  const el = document.createElement("div");
  el.className = "toast";
  el.textContent = msg;
  root.appendChild(el);
  setTimeout(() => {
    el.classList.add("out");
    setTimeout(() => el.remove(), 400);
  }, 2400);
}
window.__i18nToast = toast;

function loadJson(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

function saveJson(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

async function request(path, init = {}, ms = 20000) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), ms);
  try {
        const response = await fetch(path, { credentials: "same-origin", ...init, signal: ctrl.signal });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(typeof data.detail === "string" ? te(data.detail) : t("err.request"));
    }
    return data;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error(t("err.timeout"));
    }
    if (error instanceof Error) throw error;
    throw new Error(t("err.request"));
  } finally {
    clearTimeout(timer);
  }
}

function post(path, body, ms) {
  return request(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }, ms);
}

function go(view, param) {
  let url = PATHS[view] || "/";
  const query = new URLSearchParams();
  if (view === "read" && param) query.set("name", param);
  if (view === "sages" && param) query.set("who", param);
  if (view === "me" && param) query.set("tab", param);
  const qs = query.toString();
  if (qs) url += `?${qs}`;
  if (`${location.pathname}${location.search}` !== url) history.pushState({ view, param }, "", url);
  route();
}
window.go = go;

function parseRoute() {
  const path = location.pathname.replace(/\/$/, "") || "/";
  const params = new URLSearchParams(location.search);
  if (path === "/ask") return { view: "ask" };
  if (path === "/library") return { view: "library" };
  if (path === "/book") return { view: "read", param: params.get("name") || "" };
  if (path === "/sages") return { view: "sages", param: params.get("who") || "" };
  if (path === "/presence") return { view: "create" };
  if (path === "/me") return { view: "me", param: params.get("tab") || "" };
  if (path === "/login") return { view: "me", param: "login" };
  if (path === "/register") return { view: "me", param: "reg" };
  const hash = (location.hash || "").replace(/^#\/?/, "");
  if (hash) {
    const [name, extra] = hash.split("/");
    if (name && PATHS[name]) return { view: name, param: extra || "" };
  }
  return { view: "home" };
}

function openModal(html) {
  const root = $("#modalRoot");
  root.innerHTML = `<div class="modal" data-modal><div class="modal-card">${html}
    <button class="modal-close" data-close aria-label="${t("lang.close")}">${icon("ic-plus", "transform:rotate(45deg)")}</button></div></div>`;
  const modal = $("[data-modal]", root);
  modal.addEventListener("click", (event) => {
    if (event.target === modal || event.target.closest("[data-close]")) closeModal();
  });
  document.body.classList.add("locked");
}

function closeModal() {
  $("#modalRoot").innerHTML = "";
  document.body.classList.remove("locked");
}

let io;
function observeReveal() {
  if (!("IntersectionObserver" in window)) {
    $$(".rv").forEach((el) => el.classList.add("in"));
    return;
  }
  if (!io) {
    io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("in");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 },
    );
  }
  $$(".rv:not(.in)").forEach((el) => io.observe(el));
}

function loadAskStore() {
  const raw = loadJson(ASK_KEY, null);
  if (Array.isArray(raw)) {
    const first = raw.find((turn) => turn.role === "user");
    const conv = {
      id: "legacy",
      mode: MODE_UI[first?.mode] || "study",
      title: (first?.text || t("err.legacyAsk")).slice(0, 18),
      msgs: raw.map((turn) =>
        turn.role === "user"
          ? { role: "me", text: turn.text }
          : { role: "agent", text: turn.text, sources: turn.sources || [] },
      ),
    };
    return { convs: [conv], activeConv: conv.id };
  }
  if (raw?.sessions) {
    const convs = raw.sessions.map((session) => ({
      id: session.id,
      mode: MODE_UI[session.mode] || session.mode || "study",
      title: session.title,
      msgs: (session.turns || session.msgs || []).map((turn) => {
        if (turn.role === "me" || turn.role === "agent") return turn;
        if (turn.role === "user") return { role: "me", text: turn.text };
        return { role: "agent", text: turn.text, sources: turn.sources || [] };
      }),
    }));
    return { convs, activeConv: raw.currentId || convs[0]?.id || null };
  }
  if (raw?.convs) return { convs: raw.convs, activeConv: raw.activeConv };
  return { convs: [], activeConv: null };
}

const askStore = loadAskStore();
const state = {
  favs: new Set(loadJson(FAV_KEY, [])),
  quoteOffset: 0,
  readBook: "",
  readPage: 0,
  readOutline: null,
  libQuery: "",
  books: [],
  askMode: "study",
  convs: askStore.convs,
  activeConv: askStore.activeConv,
  people: SAGE_PROFILES.slice(),
  im: { active: "group", msgs: [], priv: loadJson(SAGE_KEY, {}).priv || {}, last: {}, scenario: "geyan" },
  quizAnswers: {},
  persona: null,
  voice: "longxiang",
  voices: VOICES.slice(),
  logged: false,
  user: { name: "未登录", char: "学" },
  authTab: "login",
  askBusy: false,
  imBusy: false,
  presence: {
    photoId: "",
    photoPreview: "",
    figureId: "",
    figureUrl: "",
    gender: "",
    audioId: "",
    clonedVoiceId: "",
    voicePreviewUrl: "",
    voicePreviews: {},
    videoUrl: "",
  },
};

function persistAsk() {
  saveJson(ASK_KEY, {
    convs: state.convs.slice(0, 30),
    activeConv: state.activeConv,
    sessions: state.convs.slice(0, 30).map((conv) => ({
      id: conv.id,
      title: conv.title,
      mode: MODE_API[conv.mode] || conv.mode,
      turns: conv.msgs
        .filter((msg) => !msg.typing)
        .map((msg) =>
          msg.role === "me"
            ? { role: "user", text: msg.text, mode: MODE_API[conv.mode] }
            : { role: "assistant", text: msg.text, sources: msg.sources || [] },
        ),
    })),
    currentId: state.activeConv,
  });
}

function persistFavs() {
  saveJson(FAV_KEY, [...state.favs]);
}

function persistIm() {
  saveJson(SAGE_KEY, { priv: state.im.priv });
}

function bookMeta(groupId, name) {
  if (name.includes("家语") || name.includes("集语")) {
    return { cat: "家语", cv: "cv-ink", author: t("lib.authorFallback") };
  }
  const meta = CAT_META[groupId] || CAT_META["注疏"];
  return { cat: meta.cat, cv: meta.cv, author: t("lib.authorFallback") };
}

function ingestBooks(payload) {
  const categories = Array.isArray(payload) ? payload : payload?.categories || [];
  const flat = Array.isArray(payload?.books) ? payload.books : [];
  const books = [];
  if (flat.length) {
    for (const item of flat) {
      const name = item.id || item.title || "";
      if (!name) continue;
      const groupId = item.group || "";
      const meta = bookMeta(groupId, name);
      books.push({
        id: name,
        title: name,
        author: item.desc || meta.author,
        cat: meta.cat,
        cv: meta.cv,
        kw: `${name} ${groupId} ${item.desc || ""}`,
      });
    }
  } else {
    for (const group of categories) {
      for (const name of group.books || []) {
        const meta = bookMeta(group.id, name);
        books.push({
          id: name,
          title: name,
          author: group.desc || meta.author,
          cat: meta.cat,
          cv: meta.cv,
          kw: `${name} ${group.name || ""} ${group.desc || ""}`,
        });
      }
    }
  }
  state.books = books;
}

async function loadBooks(force = false) {
  if (!force && state.books.length) return state.books.length;
  try {
    const data = await request("/api/books");
    ingestBooks(data || {});
    if (!state.books.length) {
      console.warn("[books] empty catalog", data);
    }
  } catch (error) {
    console.warn("[books] load failed", error);
    if (!state.books.length) ingestBooks({});
  }
  return state.books.length;
}

function route() {
  const { view, param } = parseRoute();
  $$(".view").forEach((el) => el.classList.toggle("on", el.id === `v-${view}`));
  $$("#menu a").forEach((link) =>
    link.classList.toggle("on", link.dataset.nav === view || (view === "read" && link.dataset.nav === "library")),
  );
  $("#menu").classList.remove("open");
  if (view === "home") renderHome();
  if (view === "library") renderLibrary();
  if (view === "read") renderRead(param);
  if (view === "ask") {
    renderAsk();
    focusSoon("#askInput");
  }
  if (view === "sages") renderSages(param);
  if (view === "create") renderCreate();
  if (view === "me") {
    if (param === "login" || param === "reg") state.authTab = param;
    renderMe();
  }
  window.scrollTo(0, 0);
  requestAnimationFrame(observeReveal);
}

function focusSoon(sel) {
  setTimeout(() => $(sel)?.focus(), 260);
}

function ganzhi(year) {
  const stem = "甲乙丙丁戊己庚辛壬癸";
  const branch = "子丑寅卯辰巳午未申酉戌亥";
  return `${stem[(year - 4) % 10]}${branch[(year - 4) % 12]}年`;
}

function todayIndex() {
  const day = new Date();
  const doy = Math.floor((day - new Date(day.getFullYear(), 0, 0)) / 86400000);
  return (doy + state.quoteOffset) % QUOTES.length;
}

function renderToday() {
  const day = new Date();
  const quote = QUOTES[todayIndex()];
  $("#todayGanzhi").textContent = formatGanzhi(ganzhi(day.getFullYear()));
  $("#todayDate").textContent = formatTodayDate(day);
  $("#todayQuote").innerHTML = `<b>「</b>${esc(quote.t)}<b>」</b>`;
  $("#todaySrc").textContent = quote.s;
  $("#todayPlain").textContent = quote.p;
}

function renderPicks() {
  const fallback = [
    { id: "论语", t: "论语", a: "春秋 · 孔子及弟子", cv: "cv-classic", cat: "论语", p: "二十篇。可逐篇精读，亦可随手向问答发问。" },
    { id: "礼记", t: "礼记", a: "汉 · 戴圣 编", cv: "cv-jade", cat: "礼记", p: "读《论语》不可不参《礼记》，方知礼之所由。" },
    { id: "史记孔子世家", t: "史记孔子世家", a: "汉 · 司马迁", cv: "cv-cinnabar", cat: "史传", p: "太史公为孔子立世家，记其一生行迹。" },
  ];
  const picks = state.books.length
    ? SHELF_ORDER.flatMap((cat) => state.books.filter((book) => book.cat === cat).slice(0, 1)).slice(0, 3)
    : fallback;
  $("#pickGrid").innerHTML = picks
    .map((book) => {
      const title = book.title || book.t;
      const author = book.author || book.a || "";
      const cover = book.cv;
      const shelf = SHELF_LABEL[book.cat] || {};
      const coverLabel = shelf.label || String(title).replace(/\s|·/g, "").slice(0, 4);
      // 简介单独字段；勿回退到 author，避免与副标题重复
      const intro = book.p || t("home.pickFallback");
      const metaLine = author && author !== title ? `<em>${esc(author)}</em>` : "";
      return `<article class="pick card rv" data-book="${esc(book.id)}">
        <span class="pc ${cover}"><span>${esc(coverLabel)}</span></span>
        <div><b>${esc(title)}</b>${metaLine}<p>${esc(intro)}</p></div>
      </article>`;
    })
    .join("");
  $$("#pickGrid .pick").forEach((el) => el.addEventListener("click", () => go("read", el.dataset.book)));
}

function renderHome() {
  renderToday();
  renderPicks();
}

function renderTags() {
  const tags = [...new Set(state.books.flatMap((book) => book.title.match(/[\u4e00-\u9fff]{2,4}/g) || []))].slice(0, 12);
  const row = $("#libTags");
  row.innerHTML =
    `<span class="lead-tag">${t("lib.index")}</span>` +
    (tags.length ? tags : ["论语", "礼记", "注疏"]).map((tag) => `<button class="tag" data-tag="${esc(tag)}">${esc(tag)}</button>`).join("");
  $$("#libTags .tag").forEach((button) =>
    button.addEventListener("click", () => {
      $("#libSearch").value = button.dataset.tag;
      state.libQuery = button.dataset.tag;
      $$("#libTags .tag").forEach((item) => item.classList.toggle("on", item === button));
      renderShelf();
    }),
  );
}

function matchBook(book, query) {
  if (!query) return true;
  const hay = `${book.title} ${book.author} ${book.cat} ${book.kw || ""}`;
  return query.split(/\s+/).every((key) => hay.includes(key));
}

function bookCard(book) {
  const on = state.favs.has(book.id);
  const title = (book.title || "").replace(/\s/g, "");
  const coverTitle = title.replace(/[-—–_]/g, "");
  const size = coverTitle.length > 10 ? "long" : coverTitle.length > 6 ? "mid" : "";
  return `<article class="book" data-book="${esc(book.id)}">
    <div class="cover ${book.cv}">
      <button class="star${on ? " on" : ""}" data-fav="${esc(book.id)}" aria-label="${esc(t("lib.favTitle", { title: book.title }))}" title="${esc(t("lib.fav"))}"><span class="star-mark">★</span></button>
      <span class="cover-frame"></span>
      <span class="cover-title${size ? ` ${size}` : ""}">${esc(coverTitle)}</span>
      <span class="cover-author">${esc((book.author || "").slice(0, 8))}</span>
    </div>
    <div class="book-meta"><b>${esc(book.title)}</b><span>${esc(book.author)}</span></div>
  </article>`;
}

function renderShelf() {
  const query = state.libQuery.trim();
  const root = $("#shelfRoot");
  let html = "";
  let total = 0;
  for (const cat of SHELF_ORDER) {
    const list = state.books.filter((book) => book.cat === cat && matchBook(book, query));
    if (!list.length) continue;
    total += list.length;
    const label = SHELF_LABEL[cat];
    html += `<section class="shelf">
      <div class="shelf-label">${label.label}<small>${label.en}</small></div>
      <div class="shelf-grid">${list.map(bookCard).join("")}</div>
    </section>`;
  }
  if (!total) {
    if (!state.books.length) {
      html = `<div class="shelf-empty">${t("lib.emptyLoad")}<br><span class="note">${t("lib.emptyLoadHint")}</span></div>`;
    } else {
      html = `<div class="shelf-empty">${t("lib.emptyQuery", { query: esc(query || t("lib.filter")) })}<br><span class="note">${t("lib.emptyHint")}</span></div>`;
    }
  }
  root.innerHTML = html;
  $$("#shelfRoot [data-fav]").forEach((button) =>
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      const id = button.dataset.fav;
      if (state.favs.has(id)) {
        state.favs.delete(id);
        toast(t("lib.favOff"));
      } else {
        state.favs.add(id);
        toast(t("lib.favOn"));
      }
      persistFavs();
      button.classList.toggle("on");
    }),
  );
  $$("#shelfRoot .book").forEach((el) => el.addEventListener("click", () => go("read", el.dataset.book)));
}

async function renderLibrary() {
  if (!state.books.length) {
    await loadBooks(true);
  }
  renderTags();
  $("#libSearch").value = state.libQuery;
  renderShelf();
}

async function renderRead(name) {
  const bookName = name || state.readBook || state.books[0]?.id || "";
  state.readBook = bookName;
  const book = state.books.find((item) => item.id === bookName);
  $("#readCrumb").textContent = bookName || t("read.crumb");
  $("#readFav").classList.toggle("on", state.favs.has(bookName));
  if (!bookName) {
    $("#readCols").innerHTML = `<div class="rd-title">${t("read.noBook")}</div><p class="rd-body">${t("read.noBookHint")}</p>`;
    $("#readPage").textContent = "00 / 00";
    return;
  }
  $("#readCols").innerHTML = `<div class="rd-title">${esc(bookName)}</div><p class="rd-body">${t("read.opening")}</p>`;
  try {
    const outline = await request(`/api/book?${new URLSearchParams({ name: bookName })}`);
    state.readOutline = outline;
    if (name !== undefined && name !== "") state.readPage = 0;
    const index = Math.max(0, Math.min(state.readPage, outline.sections.length - 1));
    state.readPage = index;
    await paintReadSection(book, outline, index);
  } catch (error) {
    $("#readCols").innerHTML = `<div class="rd-title">${esc(bookName)}</div><p class="rd-body">${esc(error.message)}</p>`;
    $("#readPage").textContent = "00 / 00";
  }
}

function formatReadingBody(text) {
  let raw = String(text || "").replace(/\r\n/g, "\n").trim();
  if (!raw) return "";
  const numbered = /(?:^|\n)\s*\d+\.\d+\s*/.test(raw);
  let parts;
  if (numbered) {
    parts = raw
      .split(/(?:^|\n)\s*\d+\.\d+\s*/)
      .map((part) => part.trim())
      .filter(Boolean);
  } else {
    parts = raw
      .split(/\n{2,}/)
      .map((part) => part.trim())
      .filter(Boolean);
    if (parts.length === 1) {
      const lines = raw
        .split(/\n+/)
        .map((line) => line.trim())
        .filter(Boolean);
      if (lines.length > 1 && lines.every((line) => line.length <= 48)) parts = lines;
    }
  }
  return parts
    .map((part) => {
      const clean = part
        .replace(/^\d+\.\d+\s*/, "")
        .replace(/\n+/g, "")
        .trim();
      return clean ? `<p class="rd-verse">${esc(clean)}</p>` : "";
    })
    .join("");
}

async function paintReadSection(book, outline, index) {
  const section = outline.sections[index];
  $("#readPage").textContent = `${String(index + 1).padStart(2, "0")} / ${String(outline.sections.length).padStart(2, "0")}`;
  try {
    const data = await request(`/api/book/text?${new URLSearchParams({ name: outline.name, index: String(index) })}`);
    const note = data.truncated ? `<p class="rd-note">${t("read.truncated")}</p>` : "";
    const verses = formatReadingBody(data.text) || `<p class="rd-verse">${t("read.emptySection")}</p>`;
    $("#readCols").innerHTML = `
      <div class="rd-title">${esc(outline.name)}</div>
      <div class="rd-seal seal-mark">論語</div>
      <div class="rd-meta">${esc(book?.author || outline.layer || "")} · ${esc(data.title)}</div>
      ${verses}${note}`;
  } catch (error) {
    $("#readCols").innerHTML = `
      <div class="rd-title">${esc(outline.name)}</div>
      <div class="rd-meta">${esc(section?.title || "")}</div>
      <p class="rd-verse">${esc(error.message)}</p>`;
  }
  const paper = $("#readPaper");
  requestAnimationFrame(() => {
    paper.scrollLeft = paper.scrollWidth;
  });
}

function readStep(delta) {
  const outline = state.readOutline;
  if (!outline?.sections?.length) return;
  const next = state.readPage + delta;
  if (next < 0) {
    toast(t("read.atStart"));
    return;
  }
  if (next > outline.sections.length - 1) {
    toast(t("read.atEnd"));
    return;
  }
  state.readPage = next;
  const book = state.books.find((item) => item.id === state.readBook);
  paintReadSection(book, outline, next);
}

function askFromReading() {
  const outline = state.readOutline;
  const section = outline?.sections?.[state.readPage];
  state.askMode = "study";
  const sectionTitle = section?.title || "";
  const conv = newConv("study", t("read.askTitle", { book: state.readBook, section: sectionTitle }));
  state.activeConv = conv.id;
  addMsg("agent", { text: t("read.askPrompt", { book: state.readBook, section: sectionTitle }) }, conv.id);
  persistAsk();
  go("ask");
}
window.askFromReading = askFromReading;

function newConv(mode, title) {
  const conv = { id: `c${Date.now()}${Math.random().toString(16).slice(2, 6)}`, mode, title: title || modeUi(mode).defaultConv, msgs: [] };
  state.convs.unshift(conv);
  state.activeConv = conv.id;
  persistAsk();
  return conv;
}

function activeConv() {
  return state.convs.find((conv) => conv.id === state.activeConv) || state.convs[0];
}

function addMsg(role, payload, convId) {
  const conv = state.convs.find((item) => item.id === (convId || state.activeConv));
  if (!conv) return;
  conv.msgs.push(Object.assign({ role }, payload));
  if (state.activeConv === conv.id && $("#v-ask").classList.contains("on")) paintMsgs();
}

function sourcesBlock(items) {
  if (!items?.length) return "";
  return items
    .map(
      (item) =>
        `<details class="cite-block"><summary class="cite">${esc(item.label)}</summary><span>${esc(item.excerpt || "")}</span></details>`,
    )
    .join("");
}

function paintMsgs() {
  const conv = activeConv();
  const body = $("#askBody");
  const prev = body.scrollTop;
  const wasTop = prev < 8;
  const stick = prev > 0 && body.scrollHeight - prev - body.clientHeight < 80;
  if (!conv || !conv.msgs.length) {
    body.innerHTML = `<div class="msg"><span class="av">語</span><div class="bub">${t("ask.welcome")}</div></div>`;
    return;
  }
  body.innerHTML = conv.msgs
    .map((msg) => {
      if (msg.role === "me") return `<div class="msg me"><span class="av">${t("ask.me")}</span><div class="bub">${richText(msg.text)}</div></div>`;
      if (msg.typing) return `<div class="msg typing"><span class="av">語</span><div class="bub"><i></i><i></i><i></i></div></div>`;
      const bodyHtml = msg.text
        ? msg.streaming
          ? `<div class="stream-text">${esc(msg.text).replace(/\n/g, "<br>")}</div>`
          : richText(msg.text)
        : msg.streaming
          ? `<p class="waiting">${t("ask.waiting")}</p>`
          : "";
      return `<div class="msg${msg.streaming ? " streaming" : ""}"><span class="av">語</span><div class="bub" data-stream-bub>
        ${bodyHtml}
        ${msg.streaming ? "" : sourcesBlock(msg.sources)}
      </div></div>`;
    })
    .join("");
  const streaming = conv.msgs.some((msg) => msg.streaming);
  if (streaming || stick) body.scrollTop = body.scrollHeight;
  else if (!wasTop) body.scrollTop = prev;
  else body.scrollTop = 0;
}

function updateStreamingBubble(text) {
  const body = $("#askBody");
  const bub = body?.querySelector(".msg.streaming [data-stream-bub]");
  if (!bub) {
    paintMsgs();
    return;
  }
  let stream = bub.querySelector(".stream-text");
  if (!stream) {
    bub.innerHTML = `<div class="stream-text"></div>`;
    stream = bub.querySelector(".stream-text");
  }
  stream.innerHTML = esc(text).replace(/\n/g, "<br>");
  body.scrollTop = body.scrollHeight;
}

function paintConvs() {
  $("#convList").innerHTML = state.convs
    .map((conv) => {
      const last = [...conv.msgs].reverse().find((msg) => msg.text);
      const preview = last ? last.text.slice(0, 16) : t("ask.noMsgs");
      return `<div class="conv${conv.id === state.activeConv ? " on" : ""}" data-conv="${esc(conv.id)}">
        <span class="ci">${(modeUi(conv.mode).who || "Q")[0]}</span>
        <span class="ct"><b>${esc(localizeConvTitle(conv.title, conv.mode))}</b><em>${esc(preview)}</em></span>
        <span class="cx">${icon("ic-next")}</span>
      </div>`;
    })
    .join("");
  $$("#convList .conv").forEach((el) =>
    el.addEventListener("click", () => {
      const conv = state.convs.find((item) => item.id === el.dataset.conv);
      if (!conv) return;
      state.activeConv = conv.id;
      state.askMode = conv.mode;
      persistAsk();
      paintMode();
      paintConvs();
      paintMsgs();
    }),
  );
}

function paintMode() {
  const mode = modeUi(state.askMode);
  $$("#modeSwitch button").forEach((button) => button.classList.toggle("on", button.dataset.mode === state.askMode));
  $("#askWho").textContent = mode.who;
  $("#askDesc").textContent = mode.desc;
  $("#wsFoot").textContent = t("ask.currentMode", { label: mode.label });
  $("#askChips").innerHTML = mode.chips.map((chip) => `<button data-chip="${esc(chip)}">${esc(chip)}</button>`).join("");
  $$("#askChips button").forEach((button) =>
    button.addEventListener("click", () => {
      $("#askInput").value = button.dataset.chip;
      sendAsk();
    }),
  );
}

async function sendAsk() {
  const input = $("#askInput");
  const text = input.value.trim();
  if (!text || state.askBusy) return;
  let conv = activeConv();
  if (!conv || conv.mode !== state.askMode) conv = newConv(state.askMode);
  if (!conv.msgs.length) conv.title = text.replace(/\s+/g, " ").slice(0, 48);
  addMsg("me", { text });
  input.value = "";
  persistAsk();
  paintConvs();
  const holder = { role: "agent", text: "", sources: [], streaming: true };
  conv.msgs.push(holder);
  paintMsgs();
  state.askBusy = true;
  try {
    const response = await fetch("/api/ask/stream", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: text,
        mode: MODE_API[state.askMode],
        lang: getLang() === "en" ? "en" : "zh",
      }),
    });
    if (!response.ok || !response.body) {
      const data = await response.json().catch(() => ({}));
      throw new Error(typeof data.detail === "string" ? te(data.detail) : t("err.request"));
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const chunks = buffer.split("\n\n");
      buffer = chunks.pop() || "";
      for (const chunk of chunks) {
        const line = chunk
          .split("\n")
          .map((part) => part.trim())
          .find((part) => part.startsWith("data:"));
        if (!line) continue;
        let data;
        try {
          data = JSON.parse(line.replace(/^data:\s*/, ""));
        } catch {
          continue;
        }
        if (data.type === "meta") {
          holder.sources = data.sources || [];
        } else if (data.type === "delta") {
          holder.text = `${holder.text || ""}${data.text || ""}`;
          updateStreamingBubble(holder.text);
        } else if (data.type === "error") {
          throw new Error(te(data.detail) || t("err.request"));
        }
      }
    }
    holder.streaming = false;
    if (!holder.text) holder.text = t("ask.noReply");
    persistAsk();
    paintMsgs();
    paintConvs();
  } catch (error) {
    holder.streaming = false;
    holder.text = error instanceof Error ? te(error.message) : t("err.request");
    holder.sources = [];
    paintMsgs();
  } finally {
    state.askBusy = false;
  }
}

function renderAsk() {
  if (!state.convs.length) {
    newConv("study");
    state.activeConv = state.convs[0].id;
  }
  paintMode();
  paintConvs();
  paintMsgs();
}

function sageById(id) {
  return state.people.find((sage) => sage.id === id);
}

function enrichSage(card) {
  const extra = SAGE_PROFILES.find((sage) => sage.id === card.id) || {};
  return {
    time: "今日",
    unread: 0,
    ...extra,
    id: card.id,
    name: extra.name || card.name,
    line: card.line,
    bio: extra.bio || card.line || "",
    ping: extra.ping || { q: card.line || "", src: "" },
    greet: extra.greet || card.line || "你先说。",
    last: extra.last || card.line || "",
    av: extra.av || card.name.slice(0, 1),
    short: extra.short || card.name,
    zi: extra.zi || "",
    ke: extra.ke || "德行",
  };
}

function renderContacts() {
  const query = ($("#imSearch").value || "").trim();
  const list = state.people.filter((sage) => !query || sage.name.includes(query) || sage.short?.includes(query));
  let html = `
    <div class="contact${state.im.active === "group" ? " on" : ""}" data-im="group">
      <span class="av grp">門</span>
      <span class="ct"><b>${t("sages.group")}</b><em>${esc(state.im.lastGroup || t("sages.groupLast"))}</em></span>
      <span class="cm"><span>${t("sages.justNow")}</span><i class="dim">0</i></span>
    </div>
    <div class="im-group-title">${t("sages.disciples", { count: list.length })}</div>`;
  html += list
    .map(
      (sage) => `
    <div class="contact${state.im.active === sage.id ? " on" : ""}" data-im="${sage.id}">
      <span class="av${sage.id === "kongzi" ? " zi" : ""}">${sage.av}</span>
      <span class="ct"><b>${esc(sage.name)}</b><em>${esc(state.im.last[sage.id] || sage.last)}</em></span>
      <span class="cm"><span>${esc(localizeTimeLabel(sage.time || ""))}</span><i class="dim">0</i></span>
    </div>`,
    )
    .join("");
  $("#contacts").innerHTML = html;
  $$("#contacts .contact").forEach((el) => el.addEventListener("click", () => openIm(el.dataset.im)));
}

function renderScenarios() {
  $("#scenarios").innerHTML = SCENARIOS.map(
    (item) => `<button data-sc="${item.id}" class="${item.id === state.im.scenario ? "on" : ""}">${item.name}</button>`,
  ).join("");
  $$("#scenarios button").forEach((button) => button.addEventListener("click", () => pushScenario(button.dataset.sc, false)));
}

function openIm(id) {
  state.im.active = id;
  const head = $("#scenarios");
  if (id === "group") {
    $("#imTitle").textContent = t("sages.group");
    $("#imSub").textContent = tp("sages.membersRound", state.people.length, { count: state.people.length });
    renderScenarios();
    if (state.im.msgsOwner !== "group") {
      state.im.msgsOwner = "group";
      state.im.msgs = [];
      paintIm();
      $("#imBody").innerHTML = `<div class="im-note">${t("sages.empty")}</div>`;
    } else paintIm();
  } else {
    const sage = sageById(id);
    if (!sage) return;
    $("#imTitle").textContent = sage.name;
    const role =
      sage.id === "kongzi"
        ? t("sages.master")
        : sage.ke
          ? t(`sages.ke.${sage.ke}`)
          : t("sages.disciple");
    $("#imSub").textContent = `${sage.zi || sage.name} · ${role}`;
    if (id === "kongzi" && !isEn()) {
      const says = [0, 1, 2, 3].map((i) => t(`sages.say${i}`));
      head.innerHTML = says.map((label) => `<button data-say="${esc(label)}">${esc(label)}</button>`).join("");
      $$("#scenarios button").forEach((button) =>
        button.addEventListener("click", () => {
          $("#imInput").value = button.dataset.say;
          sendIm();
        }),
      );
    } else {
      head.innerHTML = "";
    }
    if (!state.im.priv[id]) state.im.priv[id] = [{ role: "sage", id, text: sage.greet, src: "" }];
    state.im.msgs = state.im.priv[id];
    state.im.msgsOwner = id;
    paintIm();
  }
  renderJoin(id);
  imComposerState();
  renderContacts();
}

function pushScenario(id, silent) {
  const scene = SCENARIOS.find((item) => item.id === id) || SCENARIOS[0];
  state.im.scenario = id;
  state.im.msgsOwner = "group";
  state.im.msgs = [];
  state.im.lastGroup = scene.name;
  if (!silent) renderScenarios();
  paintIm();
  const body = $("#imBody");
  const note = document.createElement("div");
  note.className = "im-note";
  note.textContent = t("sages.sceneNote", { name: scene.name, src: scene.src });
  body.appendChild(note);
  let index = 0;
  const step = () => {
    if (state.im.msgsOwner !== "group" || index >= scene.lines.length) {
      renderContacts();
      return;
    }
    const line = scene.lines[index++];
    state.im.msgs.push({ role: "sage", id: line.who, text: line.text, src: line.src });
    paintIm();
    body.scrollTop = body.scrollHeight;
    setTimeout(step, 700);
  };
  setTimeout(step, 350);
}

function renderJoin(id) {
  const row = $("#imJoin");
  if (!row) return;
  const list = joinPrompts(id);
  row.innerHTML =
    `<span class="im-join-lead">${t("sages.join")}</span>` +
    list.map((text) => `<button type="button" data-join="${esc(text)}">${esc(text)}</button>`).join("");
  $$("#imJoin button").forEach((button) =>
    button.addEventListener("click", () => {
      const input = $("#imInput");
      input.value = button.dataset.join;
      imComposerState();
      input.focus();
    }),
  );
}

function imComposerState() {
  const input = $("#imInput");
  if (!input) return;
  const count = input.value.length;
  const counter = $("#imCount");
  if (counter) {
    counter.textContent = `${count} / 300`;
    counter.classList.toggle("warn", count > 255);
  }
  $("#imSend")?.classList.toggle("dim", !input.value.trim());
  input.style.height = "auto";
  input.style.height = `${Math.min(150, Math.max(56, input.scrollHeight))}px`;
}

function paintIm() {
  const body = $("#imBody");
  body.innerHTML = (state.im.msgs || [])
    .map((msg) => {
      if (msg.role === "me") {
        return `<div class="im-msg me"><span class="av">${t("sages.me")}</span><div class="wrap2"><div class="nm">${t("sages.me")}</div><div class="bub">${richText(msg.text)}</div></div></div>`;
      }
      if (msg.role === "typing") {
        const sage = sageById(msg.id) || state.people[0];
        return `<div class="im-msg typing"><span class="av${sage.id === "kongzi" ? " zi" : ""}">${sage.av}</span><div class="wrap2"><div class="nm">${esc(t("sages.typing", { name: sage.name }))}</div><div class="bub"><i></i><i></i><i></i></div></div></div>`;
      }
      const sage = sageById(msg.id) || { id: msg.id, name: msg.name || msg.id, av: (msg.name || msg.id).slice(0, 1) };
      return `<div class="im-msg">
        <span class="av${msg.id === "kongzi" || sage.id === "kongzi" ? " zi" : ""}" data-profile="${sage.id}" title="${esc(t("sages.profile"))}">${sage.av}</span>
        <div class="wrap2">
          <div class="nm">${esc(sage.name)}${msg.src ? ` · <span style="opacity:.75">${esc(msg.src)}</span>` : ""}</div>
          <div class="bub">${richText(msg.text)}${sourcesBlock(msg.sources)}</div>
        </div></div>`;
    })
    .join("");
  $$("#imBody .av[data-profile]").forEach((el) => el.addEventListener("click", () => showProfile(el.dataset.profile)));
  body.scrollTop = body.scrollHeight;
}

function keMark(sage, key) {
  if (!sage) return "—";
  if (sage.id === "kongzi" || sage.ke === "总持") return t("sages.markMaster");
  if (sage.ke === key) return t("sages.markPrimary");
  return "—";
}

function showProfile(id) {
  const sage = sageById(id);
  if (!sage) return;
  const fourKe = ["德行", "言语", "政事", "文学"];
  const keTitle =
    sage.id === "kongzi" || sage.ke === "总持"
      ? t("sages.keAll")
      : t("sages.keOf", { subject: sage.ke || t("sages.disciple") });
  const markMaster = t("sages.markMaster");
  const markPrimary = t("sages.markPrimary");
  openModal(`
    <div class="pcard">
      <div class="pcard-top">
        <span class="pav${id === "kongzi" ? " zi" : ""}">${sage.av}</span>
        <div><h3>${esc(sage.name)}</h3>
        <div class="sub">${esc(sage.zi || "")} · ${id === "kongzi" ? t("sages.supreme") : t("sages.disciple")}</div></div>
      </div>
      <p class="bio">${esc(sage.bio || sage.line || "")}</p>
      <div class="ke-caption">${esc(keTitle)}</div>
      <div class="ke-row">
        ${fourKe
          .map((key) => {
            const mark = keMark(sage, key);
            const on = mark === markPrimary || mark === markMaster;
            return `<div class="ke${on ? " on" : ""}"><b>${t(`sages.ke.${key}`)}</b><span>${mark}</span></div>`;
          })
          .join("")}
      </div>
      <div class="quote-block">
        <div class="qh">${t("sages.ping")}</div>
        <p>「${esc(sage.ping?.q || sage.line || "")}」</p>
        <span class="src">${esc(sage.ping?.src || "")}</span>
      </div>
      <div class="modal-actions">
        <button class="btn btn-ghost btn-sm" data-chat="${sage.id}">${t("sages.chat")}</button>
      </div>
    </div>`);
  $("[data-chat]").addEventListener("click", () => {
    closeModal();
    openIm(sage.id);
  });
}

async function sendIm() {
  const input = $("#imInput");
  const text = input.value.trim().slice(0, 300);
  if (!text || state.imBusy) return;
  input.value = "";
  imComposerState();
  const id = state.im.active;
  state.imBusy = true;
  if (id === "group") {
    state.im.msgs.push({ role: "me", text });
    state.im.msgs.push({ role: "typing", id: "kongzi" });
    paintIm();
    try {
      const seated = await post("/api/seat", { query: text }, 20000);
      const speakers = seated.speakers || [];
      const earlier = [];
      for (let i = 0; i < speakers.length; i += 1) {
        if (state.im.msgsOwner !== "group") break;
        const person = speakers[i];
        state.im.msgs = state.im.msgs.filter((msg) => msg.role !== "typing");
        state.im.msgs.push({ role: "typing", id: person.id });
        paintIm();
        const result = await post(
          "/api/talk",
          {
            who: person.id,
            query: text,
            earlier,
          },
          120000,
        );
        if (state.im.msgsOwner !== "group") break;
        state.im.msgs = state.im.msgs.filter((msg) => msg.role !== "typing");
        const spoken = result.turns?.[0];
        const line = {
          role: "sage",
          id: spoken?.id || person.id,
          name: spoken?.name || person.name,
          text: spoken?.text || "",
          sources: [],
        };
        state.im.msgs.push(line);
        earlier.push({ name: line.name, text: line.text });
        state.im.lastGroup = `${line.name}：${(line.text || "").slice(0, 10)}`;
        paintIm();
      }
      renderContacts();
    } catch (error) {
      state.im.msgs = state.im.msgs.filter((msg) => msg.role !== "typing");
      state.im.msgs.push({ role: "sage", id: "kongzi", text: error.message });
      paintIm();
    } finally {
      state.imBusy = false;
    }
    return;
  }
  const sage = sageById(id);
  state.im.msgs.push({ role: "me", text });
  state.im.priv[id] = state.im.msgs;
  persistIm();
  const holder = { role: "typing", id };
  state.im.msgs.push(holder);
  paintIm();
  try {
    const result = await post("/api/talk", { who: id, query: text }, 120000);
    const index = state.im.msgs.indexOf(holder);
    if (index >= 0) state.im.msgs.splice(index, 1);
    const spoken = result.turns?.[0];
    state.im.msgs.push({
      role: "sage",
      id: spoken?.id || id,
      name: spoken?.name || sage?.name,
      text: spoken?.text || "",
      sources: result.sources || [],
    });
    state.im.priv[id] = state.im.msgs;
    persistIm();
    state.im.last[id] = (spoken?.text || "").slice(0, 16);
    paintIm();
    renderContacts();
  } catch (error) {
    const index = state.im.msgs.indexOf(holder);
    if (index >= 0) state.im.msgs.splice(index, 1);
    state.im.msgs.push({ role: "sage", id, text: error.message });
    paintIm();
  } finally {
    state.imBusy = false;
  }
}

function renderSages(param) {
  $("#imSearch").value = "";
  openIm(param && sageById(param) ? param : state.im.active || "group");
}

let curStep = 1;
function renderQuiz() {
  $("#quiz").innerHTML = QUIZ.map((question, qi) => {
    const ui = quizUi(qi);
    return `
    <div class="q">
      <div class="q-head">
        <span class="dim">${esc(ui.dim)}</span>
        <h4>${esc(ui.q)}</h4>
      </div>
      <div class="opts">
        ${question.opts
          .map(
            (option, oi) =>
              `<button type="button" class="opt${state.quizAnswers[qi] === oi ? " on" : ""}" data-q="${qi}" data-o="${oi}"><span class="opt-mark">${oi + 1}</span><span class="opt-text">${esc(ui.opts[oi]?.t || option.t)}</span></button>`,
          )
          .join("")}
      </div>
    </div>`;
  }).join("");
  $$("#quiz .opt").forEach((button) =>
    button.addEventListener("click", () => {
      state.quizAnswers[button.dataset.q] = Number(button.dataset.o);
      $$(`#quiz .opt[data-q="${button.dataset.q}"]`).forEach((item) => item.classList.remove("on"));
      button.classList.add("on");
      $("#quizProgress").textContent = t("create.answered", {
        n: Object.keys(state.quizAnswers).length,
        total: QUIZ.length,
      });
    }),
  );
  $("#quizProgress").textContent = t("create.answered", {
    n: Object.keys(state.quizAnswers).length,
    total: QUIZ.length,
  });
}

function quizScore() {
  const score = { 温: 0, 良: 0, 恭: 0, 俭: 0, 让: 0 };
  Object.keys(state.quizAnswers).forEach((qi) => {
    const weights = QUIZ[qi].opts[state.quizAnswers[qi]].w;
    Object.keys(weights).forEach((key) => {
      score[key] += weights[key];
    });
  });
  return score;
}

function quizAnswersPayload() {
  return Object.keys(state.quizAnswers).map((qi) => {
    const question = QUIZ[qi];
    const option = question.opts[state.quizAnswers[qi]];
    return { dim: question.dim, q: question.q, a: option.t, w: option.w };
  });
}

function calcPersonaLocal() {
  const score = quizScore();
  const max = Math.max(...WUDE.map((item) => score[item]), 1);
  const top = WUDE.slice().sort((a, b) => score[b] - score[a]);
  const map = PERSONA_MAP[top[0]];
  const second = PERSONA_MAP[top[1]];
  const ui = personaUi(top[0], map);
  const secondUi = second ? personaUi(top[1], second) : null;
  const line = ui.line || map.line;
  return {
    name: ui.name || map.name,
    motto: map.motto,
    mottoSrc: map.mottoSrc,
    line,
    tags: [...new Set([...(ui.tags || map.tags), secondUi ? secondUi.tags[0] : ""])].filter(Boolean),
    analysis: t("create.analysis", {
      primary: wudeDesc(top[0]),
      secondary: wudeDesc(top[1]),
      line,
    }),
    score,
    top,
    max,
  };
}

function paintPersona() {
  const persona = state.persona;
  if (!persona) return;
  const max = persona.max || Math.max(...WUDE.map((item) => persona.score?.[item] || 0), 1);
  const primary = persona.top?.[0];
  const secondary = persona.top?.[1];
  const ui = primary ? personaUi(primary, PERSONA_MAP[primary]) : null;
  const secondUi = secondary ? personaUi(secondary, PERSONA_MAP[secondary]) : null;
  const name = ui?.name || persona.name;
  const line = ui?.line || persona.line;
  const tags = ui
    ? [...new Set([...(ui.tags || []), secondUi ? secondUi.tags[0] : ""])].filter(Boolean)
    : persona.tags || [];
  const lead = primary ? wudeDesc(primary) : "";
  const analysis =
    primary && secondary
      ? t("create.analysis", {
          primary: wudeDesc(primary),
          secondary: wudeDesc(secondary),
          line,
        })
      : persona.analysis;
  $("#personaCard").innerHTML = `
    <h3>${esc(name)}</h3>
    <div class="ptag">
      <span class="tag">${t("create.wudeTag", { virtue: lead })}</span>
      <span class="tag">${esc(line)}</span>
    </div>
    <div class="wude">
      ${WUDE.map(
        (item) =>
          `<div class="w"><div class="bar"><i data-h="${Math.round(((persona.score?.[item] || 0) / max) * 100)}"></i></div><b>${esc(wudeLabel(item))}</b><span>${esc(wudeDesc(item))}</span></div>`,
      ).join("")}
    </div>
    <div class="motto">${t("create.motto")} · ${esc(persona.motto)}<span class="note" style="display:block;margin-top:8px">${esc(persona.mottoSrc || "")}</span></div>
    ${analysis ? `<p class="note" style="margin-top:16px;line-height:1.9;letter-spacing:.06em">${esc(analysis)}</p>` : ""}
    <div class="ptag" style="margin-top:18px">
      <span class="note" style="align-self:center">${t("create.tags")}</span>
      ${tags.map((tag) => `<span class="tag on">${esc(tag)}</span>`).join("")}
    </div>`;
  requestAnimationFrame(() => $$("#personaCard .bar i").forEach((bar) => (bar.style.height = `${bar.dataset.h}%`)));
}

function activeVoice() {
  if (state.voice === "mine") {
    if (!state.presence.clonedVoiceId) {
      throw new Error(t("create.needClone"));
    }
    return state.presence.clonedVoiceId;
  }
  return state.voice || "longxiang";
}

function voiceCatalog() {
  return Array.isArray(state.voices) && state.voices.length ? state.voices : VOICES;
}

function voiceLabel() {
  if (state.voice === "mine" || (state.presence.clonedVoiceId && state.voice === state.presence.clonedVoiceId)) {
    return t("create.myClone");
  }
  const found = voiceCatalog().find((voice) => voice.id === state.voice);
  return found ? voiceUi(found.id, found.name, found.desc).name : t("create.systemVoice");
}

const VOICE_SAMPLE = "君子和而不同，小人同而不和。";
let voicePreviewSeq = 0;

function isCloneVoice() {
  return state.voice === "mine" || (state.presence.clonedVoiceId && state.voice === state.presence.clonedVoiceId);
}

function paintVoicePlayBtn() {
  const btn = $("#voicePlay");
  if (!btn) return;
  btn.classList.toggle("hide", !isCloneVoice());
}

async function previewVoice() {
  const seq = ++voicePreviewSeq;
  const audio = $("#voiceAudio");
  const stage = $("#audioName");
  let voice;
  try {
    voice = activeVoice();
  } catch (error) {
    toast(error.message);
    return;
  }
  const cacheKey = isCloneVoice() ? `mine:${state.presence.clonedVoiceId}` : voice;
  const cache = state.presence.voicePreviews || {};
  if (stage) stage.textContent = t("create.previewBusy");
  try {
    let url = cache[cacheKey];
    if (!url) {
      const data = await post("/api/presence/voice/preview", { text: VOICE_SAMPLE, voice }, 90000);
      url = data.url;
      state.presence.voicePreviews = { ...cache, [cacheKey]: url };
    }
    if (seq !== voicePreviewSeq) return;
    state.presence.voicePreviewUrl = url;
    if (audio) {
      audio.src = url;
      audio.style.display = "block";
      await audio.play().catch(() => {});
    }
    if (stage) stage.textContent = t("create.previewPlay", { sample: VOICE_SAMPLE });
  } catch (error) {
    if (seq !== voicePreviewSeq) return;
    toast(te(error.message) || t("create.previewFail"));
    if (stage) stage.textContent = te(error.message) || t("create.previewFail");
  }
}

function setProgress(id, pct) {
  const bar = $(id);
  if (bar) bar.style.width = `${Math.max(0, Math.min(100, pct))}%`;
}

function paintFigurePreview() {
  const img = $("#figImage");
  const ph = $("#figPlaceholder");
  const url = state.presence.figureUrl || state.presence.photoPreview;
  if (img && ph) {
    if (url) {
      img.src = url;
      img.hidden = false;
      img.style.display = "block";
      ph.hidden = true;
      ph.style.display = "none";
    } else {
      img.removeAttribute("src");
      img.hidden = true;
      img.style.display = "none";
      ph.hidden = false;
      ph.style.display = "";
    }
  }
}

function paintGender() {
  $$("#genderPick .opt").forEach((btn) => {
    btn.classList.toggle("on", btn.dataset.gender === state.presence.gender);
  });
}

function paintVideoPreview() {
  const video = $("#videoPlayer");
  const placeholder = $("#videoPlaceholder");
  const download = $("#downloadBtn");
  if (!video || !placeholder) return;
  if (state.presence.videoUrl) {
    video.src = state.presence.videoUrl;
    video.style.display = "block";
    placeholder.style.display = "none";
    if (download) download.disabled = false;
    $("#videoTitle").textContent = state.persona?.name ? t("create.videoTitleNamed", { name: state.persona.name }) : t("create.videoTitle");
    $("#videoSub").textContent = t("create.videoReady");
  } else {
    video.removeAttribute("src");
    video.style.display = "none";
    placeholder.style.display = "";
    if (download) download.disabled = true;
  }
}

async function uploadPresence(kind, file) {
  const fd = new FormData();
  fd.append("file", file);
  const path = kind === "photo" ? "/api/presence/upload/photo" : "/api/presence/upload/audio";
  return request(path, { method: "POST", body: fd }, 60000);
}

function setStep(n) {
  const target = Math.max(1, Math.min(5, n));
  if (target >= 3 && !state.persona) {
    toast(t("create.needQuiz"));
    return;
  }
  if (target >= 4 && !state.presence.figureUrl) {
    toast(t("create.needFigure"));
    return;
  }
  curStep = target;
  for (let i = 1; i <= 5; i++) $("#cp" + i).classList.toggle("hide", i !== curStep);
  $$("#steps .step").forEach((el) => {
    const step = Number(el.dataset.step);
    el.classList.toggle("on", step === curStep);
    el.classList.toggle("done", step < curStep);
  });
  $("#stepHint").textContent = t("create.hint", {
    current: t(`create.n${curStep}`),
    total: t("create.n5"),
  });
  const back = $("#stepBack");
  const next = $("#stepNext");
  if (back) back.disabled = curStep === 1;
  if (next) {
    next.textContent = t(`create.nextBtn${curStep - 1}`);
  }
}

function renderVoices() {
  const root = $("#voiceGrid");
  if (!root) return;
  const selected =
    state.voice === state.presence.clonedVoiceId && state.presence.clonedVoiceId ? "mine" : state.voice;
  const groups = [
    { key: "male", title: t("create.voicesMale") },
    { key: "female", title: t("create.voicesFemale") },
    { key: "clone", title: t("create.voicesMine") },
  ];
  const catalog = voiceCatalog();
  root.innerHTML = groups
    .map((group) => {
      const items = catalog.filter((voice) => (voice.gender || "male") === group.key);
      if (!items.length) return "";
      return `<div class="voice-group"><h3>${group.title}</h3><div class="voice-grid">${items
        .map((voice) => {
          const ui = voiceUi(voice.id, voice.name, voice.desc);
          const cloned = voice.id === "mine" && state.presence.clonedVoiceId ? ` · ${t("create.cloned")}` : "";
          return `
        <div class="voice${selected === voice.id ? " on" : ""}" data-voice="${voice.id}">
          <div class="wave${selected === voice.id ? " play" : ""}">${Array.from({ length: 6 }, (_, i) => `<i style="height:${8 + ((i * 7) % 20)}px"></i>`).join("")}</div>
          <div><b>${esc(ui.name)}</b><span>${esc(ui.desc)}${cloned}</span></div>
        </div>`;
        })
        .join("")}</div></div>`;
    })
    .join("");
  $$("#voiceGrid .voice").forEach((el) =>
    el.addEventListener("click", () => {
      const id = el.dataset.voice;
      if (id === "mine" && !state.presence.clonedVoiceId) {
        toast(t("create.needCloneShort"));
        return;
      }
      state.voice = id === "mine" ? "mine" : id;
      $("#voiceName").textContent = voiceLabel();
      renderVoices();
      if (id === "mine") {
        paintVoicePlayBtn();
        toast(t("create.cloneHint"));
        return;
      }
      previewVoice();
    }),
  );
  $("#voiceName").textContent = voiceLabel();
  paintVoicePlayBtn();
}

function renderCreate() {
  renderQuiz();
  renderVoices();
  if (state.persona) paintPersona();
  paintFigurePreview();
  paintGender();
  paintVideoPreview();
  $("#scriptCount").textContent = tp("create.chars", ($("#scriptText").value || "").length, { count: ($("#scriptText").value || "").length });
  setStep(curStep);
}

function renderMe() {
  const root = $("#meRoot");
  if (!state.logged) {
    root.innerHTML = `
      <div class="card auth rv">
        <div class="tabs" id="authTabs">
          <button class="${state.authTab !== "reg" ? "on" : ""}" data-tab="login">${t("me.login")}</button>
          <button class="${state.authTab === "reg" ? "on" : ""}" data-tab="reg">${t("me.register")}</button>
        </div>
        <div id="authBody"></div>
      </div>`;
    paintAuth(state.authTab === "reg" ? "reg" : "login");
    $$("#authTabs button").forEach((button) =>
      button.addEventListener("click", () => {
        state.authTab = button.dataset.tab;
        $$("#authTabs button").forEach((item) => item.classList.toggle("on", item === button));
        paintAuth(button.dataset.tab);
      }),
    );
    requestAnimationFrame(observeReveal);
    return;
  }
  const favBooks = state.books.filter((book) => state.favs.has(book.id));
  const askTurns = state.convs.flatMap((conv) => conv.msgs.filter((msg) => msg.role === "me"));
  root.innerHTML = `
    <div class="card me-head rv">
      <span class="me-av">${esc(state.user.char)}</span>
      <div>
        <h2>${esc(state.user.name)}</h2>
        <div class="note">${t("me.note")}</div>
        <div class="mtag">
          <span class="tag on">${esc(state.persona?.name || t("create.noPersona"))}</span>
          <span class="tag">${tp("me.favCount", favBooks.length, { count: favBooks.length })}</span>
        </div>
      </div>
      <div style="margin-left:auto;display:flex;gap:10px;flex-wrap:wrap">
        <button class="btn btn-ghost btn-sm" id="toCreate">${t("me.toCreate")}</button>
        <button class="btn btn-ghost btn-sm" id="logoutBtn">${t("me.logoutBtn")}</button>
      </div>
    </div>
    <section class="sec-sm">
      <div class="sec-head"><h2>${t("me.local")}</h2><p>${t("me.localDesc")}</p></div>
      <div class="stat-grid">
        <div class="card stat rv"><b>${askTurns.length}</b><span>${t("me.statAsk")}</span><em>${t("me.statAskSub")}</em></div>
        <div class="card stat rv"><b>${favBooks.length}</b><span>${t("me.statFav")}</span><em>${t("me.statFavSub")}</em></div>
        <div class="card stat rv"><b>${state.convs.length}</b><span>${t("me.statConv")}</span><em>${t("me.statConvSub")}</em></div>
      </div>
    </section>
    <section class="sec-sm">
      <div class="sec-head"><h2>${t("me.favs")}</h2></div>
      <div class="fav-grid">
        ${
          favBooks.length
            ? favBooks
                .map(
                  (book) => `
          <article class="fav card rv" data-book="${esc(book.id)}">
            <span class="fc ${book.cv}"><span>${esc(book.title)}</span></span>
            <div><b>${esc(book.title)}</b><p>${esc(book.author)}<br>${t("me.favCard")}</p></div>
          </article>`,
                )
                .join("")
            : `<p class="note">${t("me.favEmpty")}</p>`
        }
      </div>
    </section>
    <section class="sec-sm">
      <div class="sec-head"><h2>${t("me.recent")}</h2></div>
      <div class="card rv" style="padding:30px 34px">
        <div class="timeline">
          ${
            askTurns.length
              ? askTurns
                  .slice(-6)
                  .reverse()
                  .map((msg) => `<div class="tl"><b>${esc(msg.text)}</b><span>${t("me.fromAsk")}</span></div>`)
                  .join("")
              : `<div class="tl"><b>${t("me.noAsk")}</b><span>${t("me.fromAsk")}</span></div>`
          }
        </div>
      </div>
    </section>`;
  $("#toCreate").addEventListener("click", () => go("create"));
  $("#logoutBtn").addEventListener("click", async () => {
    await post("/api/logout", {});
    state.logged = false;
    state.user = { name: t("nav.guest"), char: t("nav.guestChar") };
    syncUser();
    renderMe();
    toast(t("me.logout"));
  });
  $$("#meRoot [data-book]").forEach((el) => el.addEventListener("click", () => go("read", el.dataset.book)));
  requestAnimationFrame(observeReveal);
}

function paintAuth(tab) {
  const isLogin = tab !== "reg";
  $("#authBody").innerHTML = `
    <div class="field"><label>${t("me.username")}</label><input id="auName" autocomplete="username" placeholder="${isLogin ? t("me.userPhLogin") : t("me.userPhReg")}"></div>
    <div class="field"><label>${t("me.password")}</label><input id="auPwd" type="password" autocomplete="${isLogin ? "current-password" : "new-password"}" placeholder="${t("me.pwdPh")}"></div>
    <p class="auth-error" id="authError"></p>
    <div class="form-actions" style="margin-top:24px">
      <button class="btn btn-seal" id="authGo">${isLogin ? t("me.loginBtn") : t("me.regBtn")}</button>
      <span class="note">  </span>
    </div>`;
  $("#authGo").addEventListener("click", async () => {
    const name = ($("#auName").value || "").trim();
    const password = $("#auPwd").value;
    const error = $("#authError");
    error.textContent = "";
    if (!name || !password) {
      error.textContent = t("me.fillBoth");
      return;
    }
    $("#authGo").disabled = true;
    try {
      const data = await post(isLogin ? "/api/login" : "/api/register", { username: name, password });
      state.logged = true;
      state.user = { name: data.username.slice(0, 12), char: data.username.slice(0, 1) };
      syncUser();
      renderMe();
      toast(isLogin ? t("me.welcome", { name: state.user.name }) : t("me.regOk"));
    } catch (err) {
      error.textContent = te(err.message);
    } finally {
      $("#authGo").disabled = false;
    }
  });
}

function syncUser() {
  $("#navUserName").textContent = state.logged ? state.user.name : t("nav.guest");
  $("#navUserChar").textContent = state.logged ? state.user.char : t("nav.guestChar");
}

window.addEventListener("popstate", route);
$("#burger").addEventListener("click", () => $("#menu").classList.toggle("open"));
document.addEventListener("click", (event) => {
  const link = event.target.closest("a[href]");
  if (!link || link.target === "_blank" || event.metaKey || event.ctrlKey || event.shiftKey) return;
  const url = new URL(link.href, location.origin);
  if (url.origin !== location.origin) return;
  const known = ["/", "/ask", "/library", "/book", "/sages", "/presence", "/me", "/login", "/register"];
  const path = url.pathname.replace(/\/$/, "") || "/";
  if (!known.includes(path) && !path.startsWith("/static")) return;
  if (path.startsWith("/static") || path.startsWith("/api")) return;
  event.preventDefault();
  history.pushState({}, "", path + url.search);
  route();
});

$("#quoteRefresh").addEventListener("click", () => {
  state.quoteOffset++;
  renderToday();
  toast(t("home.refreshed"));
});
$("#quoteCopy").addEventListener("click", () => {
  const quote = QUOTES[todayIndex()];
  const text = `${quote.t}　—— ${quote.s}`;
  if (navigator.clipboard?.writeText) navigator.clipboard.writeText(text).then(() => toast(t("home.copied"))).catch(() => toast(text));
  else toast(text);
});

$("#libSearchBtn").addEventListener("click", () => {
  state.libQuery = $("#libSearch").value.trim();
  $$("#libTags .tag").forEach((item) => item.classList.remove("on"));
  renderShelf();
});
$("#libSearch").addEventListener("input", (event) => {
  state.libQuery = event.target.value.trim();
  renderShelf();
});
$("#libSearch").addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    state.libQuery = event.target.value.trim();
    renderShelf();
  }
});

$("#readPrev").addEventListener("click", () => readStep(-1));
$("#readNext").addEventListener("click", () => readStep(1));
$("#readFav").addEventListener("click", () => {
  const id = state.readBook;
  if (!id) return;
  const on = !state.favs.has(id);
  if (on) state.favs.add(id);
  else state.favs.delete(id);
  persistFavs();
  $("#readFav").classList.toggle("on", on);
  toast(on ? t("read.favOn") : t("read.favOff"));
});
document.querySelector("[onclick=\"go('home')\"]")?.addEventListener("click", (event) => {
  event.preventDefault();
  go("home");
});

$("#modeSwitch").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-mode]");
  if (!button) return;
  state.askMode = button.dataset.mode;
  const exist = state.convs.find((conv) => conv.mode === state.askMode);
  state.activeConv = exist ? exist.id : newConv(state.askMode).id;
  persistAsk();
  paintMode();
  paintConvs();
  paintMsgs();
});
$("#newConv").addEventListener("click", () => {
  newConv(state.askMode);
  paintConvs();
  paintMsgs();
  $("#askInput").focus();
});
$("#newConv2").addEventListener("click", () => {
  newConv(state.askMode);
  paintConvs();
  paintMsgs();
  $("#askInput").focus();
});
$("#clearChat").addEventListener("click", () => {
  const conv = activeConv();
  if (!conv) return;
  conv.msgs = [];
  conv.title = modeUi(conv.mode).defaultConv;
  persistAsk();
  paintConvs();
  paintMsgs();
  toast(t("ask.cleared"));
});
$("#askSend").addEventListener("click", sendAsk);
$("#askInput").addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendAsk();
  }
});

$("#imSearch").addEventListener("input", renderContacts);
$("#imSend").addEventListener("click", sendIm);
$("#imInput").addEventListener("input", imComposerState);
$("#imInput").addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendIm();
  }
});
imComposerState();
renderJoin("group");

$("#steps").addEventListener("click", (event) => {
  const el = event.target.closest(".step");
  if (el) setStep(Number(el.dataset.step));
});
$$(".create-panel").forEach((panel) =>
  panel.addEventListener("click", (event) => {
    const button = event.target.closest("[data-goto]");
    if (button) setStep(Number(button.dataset.goto));
  }),
);
$("#quizSubmit").addEventListener("click", async () => {
  const miss = QUIZ.length - Object.keys(state.quizAnswers).length;
  if (miss > 0) {
    toast(tp("create.quizMiss", miss, { count: miss }));
    return;
  }
  const btn = $("#quizSubmit");
  btn.disabled = true;
  const local = calcPersonaLocal();
  state.persona = local;
  paintPersona();
  setStep(2);
  toast(t("create.refining"));
  try {
    const data = await post(
      "/api/presence/persona",
      { answers: quizAnswersPayload(), score: quizScore() },
      60000,
    );
    if (data.persona) {
      state.persona = {
        ...local,
        ...data.persona,
        score: data.persona.score || local.score,
        top: data.persona.top || local.top,
        max: data.persona.max || local.max,
      };
      paintPersona();
      toast(t("create.personaCreated", { name: state.persona.name }));
    }
  } catch (error) {
    toast(te(error.message) || t("create.aiFallback"));
  } finally {
    btn.disabled = false;
  }
});
$("#quizReset").addEventListener("click", () => {
  state.quizAnswers = {};
  renderQuiz();
});
$("#retakeQuiz").addEventListener("click", () => setStep(1));

$("#photoUpload").addEventListener("click", () => $("#photoFile").click());
$("#photoUpload").addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    $("#photoFile").click();
  }
});
$("#photoFile").addEventListener("change", async (event) => {
  const file = event.target.files?.[0];
  if (!file) return;
  $("#photoName").textContent = t("create.uploading", { filename: file.name });
  $("#figStage").textContent = t("create.uploadingPhoto");
  setProgress("#figProgress", 18);
  try {
    if (state.presence.photoPreview) URL.revokeObjectURL(state.presence.photoPreview);
    state.presence.photoPreview = URL.createObjectURL(file);
    state.presence.figureId = "";
    state.presence.figureUrl = "";
    paintFigurePreview();
    const data = await uploadPresence("photo", file);
    state.presence.photoId = data.id;
    $("#photoName").textContent = t("create.uploaded", { filename: data.name || file.name });
    $("#figStage").textContent = t("create.pickGender");
    setProgress("#figProgress", 40);
    toast(t("create.photoOk"));
  } catch (error) {
    $("#photoName").textContent = t("create.uploadFail");
    $("#figStage").textContent = te(error.message) || t("create.uploadFail");
    setProgress("#figProgress", 0);
    toast(te(error.message) || t("create.uploadFail"));
  }
});

$("#genderPick")?.addEventListener("click", (event) => {
  const btn = event.target.closest("[data-gender]");
  if (!btn) return;
  state.presence.gender = btn.dataset.gender;
  paintGender();
});

$("#genFigure").addEventListener("click", async () => {
  if (!state.presence.photoId) {
    toast(t("create.needPhoto"));
    return;
  }
  if (!state.persona) {
    toast(t("create.needPersonaQuiz"));
    return;
  }
  if (!state.presence.gender) {
    toast(t("create.needGender"));
    return;
  }
  const btn = $("#genFigure");
  btn.disabled = true;
  $("#figStage").textContent = t("create.genFigureBusy");
  setProgress("#figProgress", 55);
  try {
    const virtue = state.persona.top?.[0] || "温";
    const data = await post(
      "/api/presence/figure",
      { photo_id: state.presence.photoId, virtue, gender: state.presence.gender },
      180000,
    );
    state.presence.figureId = data.id;
    state.presence.figureUrl = data.url;
    paintFigurePreview();
    setProgress("#figProgress", 100);
    $("#figStage").textContent = t("create.figDone");
    toast(t("create.figDoneToast"));
  } catch (error) {
    setProgress("#figProgress", 40);
    $("#figStage").textContent = te(error.message) || t("create.genFail");
    toast(te(error.message) || t("create.figFail"));
  } finally {
    btn.disabled = false;
  }
});

$("#audioUpload").addEventListener("click", () => $("#audioFile").click());
$("#audioUpload").addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    $("#audioFile").click();
  }
});
$("#audioFile").addEventListener("change", async (event) => {
  const file = event.target.files?.[0];
  if (!file) return;
  $("#audioName").textContent = t("create.uploading", { filename: file.name });
  try {
    const uploaded = await uploadPresence("audio", file);
    state.presence.audioId = uploaded.id;
    $("#audioName").textContent = t("create.uploadedCloning", { filename: uploaded.name || file.name });
    toast(t("create.audioStart"));
    const cloned = await post("/api/presence/voice/clone", { audio_id: uploaded.id }, 120000);
    state.presence.clonedVoiceId = cloned.voice_id;
    state.voice = "mine";
    $("#audioName").textContent = t("create.cloneDone");
    $("#voiceName").textContent = voiceLabel();
    renderVoices();
    toast(t("create.cloneOk"));
  } catch (error) {
    $("#audioName").textContent = te(error.message) || t("create.cloneFail");
    toast(te(error.message) || t("create.cloneFail"));
  }
});

$("#voicePlay").addEventListener("click", async () => {
  if (!isCloneVoice()) return;
  const btn = $("#voicePlay");
  btn.disabled = true;
  try {
    await previewVoice();
  } finally {
    btn.disabled = false;
  }
});

$("#scriptText").addEventListener("input", (event) => {
  $("#scriptCount").textContent = tp("create.chars", event.target.value.length, { count: event.target.value.length });
});
$("#scriptDemo").addEventListener("click", () => {
  $("#scriptText").value =
    "读《论语·里仁》至「君子欲讷于言而敏于行」，忽然明白少说一句的好处。近来事多心烦，总想先把打算讲给别人听，讲完力气就散了。此后不如把话按下来，把手上的事做完一件，再说一件。";
  $("#scriptCount").textContent = tp("create.chars", $("#scriptText").value.length, { count: $("#scriptText").value.length });
});
$("#scriptAi").addEventListener("click", async () => {
  if (!state.persona) {
    toast(t("create.needQuizOnly"));
    return;
  }
  const btn = $("#scriptAi");
  btn.disabled = true;
  try {
    const data = await post("/api/presence/script", { persona: state.persona }, 60000);
    $("#scriptText").value = data.text || "";
    $("#scriptCount").textContent = tp("create.chars", ($("#scriptText").value || "").length, { count: ($("#scriptText").value || "").length });
    toast(t("create.scriptOk"));
  } catch (error) {
    toast(te(error.message) || t("create.scriptFail"));
  } finally {
    btn.disabled = false;
  }
});

$("#genVideo").addEventListener("click", async () => {
  const text = ($("#scriptText").value || "").trim();
  if (!text) {
    toast(t("create.needScript"));
    return;
  }
  if (!state.presence.figureId && !state.presence.photoId) {
    toast(t("create.needPhotoOrFigure"));
    return;
  }
  let voice;
  try {
    voice = activeVoice();
  } catch (error) {
    toast(error.message);
    return;
  }
  const btn = $("#genVideo");
  btn.disabled = true;
  $("#videoStage").textContent = t("create.videoSubmit");
  setProgress("#videoProgress", 8);
  const tick = setInterval(() => {
    const bar = $("#videoProgress");
    const cur = Number.parseFloat(bar?.style.width || "8");
    if (cur < 90) setProgress("#videoProgress", cur + 1.2);
  }, 2500);
  try {
    const started = await post(
      "/api/presence/video",
      {
        text,
        voice,
        image_id: state.presence.figureId || "",
        photo_id: state.presence.figureId ? "" : state.presence.photoId || "",
      },
      20000,
    );
    const jobId = started.job_id;
    if (!jobId) throw new Error(t("create.noJob"));
    let job = started;
    const deadline = Date.now() + 12 * 60 * 1000;
    while (job.status === "running" || job.status === "pending") {
      if (Date.now() > deadline) throw new Error(t("create.videoSlow"));
      $("#videoStage").textContent = job.message || t("create.videoBusy");
      await new Promise((resolve) => setTimeout(resolve, 2500));
      job = await request(`/api/presence/video/${jobId}`, {}, 15000);
    }
    if (job.status !== "succeeded" || !job.video_url) {
      throw new Error(te(job.detail || job.message) || t("create.videoFail"));
    }
    state.presence.videoUrl = job.video_url;
    paintVideoPreview();
    setProgress("#videoProgress", 100);
    $("#videoStage").textContent = t("create.videoDone");
    toast(t("create.videoOk"));
  } catch (error) {
    setProgress("#videoProgress", 0);
    $("#videoStage").textContent = te(error.message) || t("create.genFail");
    toast(te(error.message) || t("create.videoFail"));
  } finally {
    clearInterval(tick);
    btn.disabled = false;
  }
});

$("#downloadBtn").addEventListener("click", () => {
  if (!state.presence.videoUrl) {
    toast(t("create.noDownload"));
    return;
  }
  const a = document.createElement("a");
  a.href = state.presence.videoUrl;
  a.download = t("create.downloadName", { ts: Date.now() });
  a.target = "_blank";
  a.rel = "noopener";
  document.body.appendChild(a);
  a.click();
  a.remove();
});
$("#stepBack").addEventListener("click", () => setStep(curStep - 1));
$("#stepNext").addEventListener("click", () => {
  if (curStep === 1) {
    $("#quizSubmit").click();
    return;
  }
  if (curStep === 5) {
    $("#genVideo").click();
    return;
  }
  if (curStep === 2 && !state.persona) {
    toast(t("create.needQuiz"));
    return;
  }
  if (curStep === 3 && !state.presence.figureUrl) {
    toast(t("create.needFigure"));
    return;
  }
  setStep(curStep + 1);
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeModal();
  if (!$("#v-read").classList.contains("on")) return;
  const tag = (event.target.tagName || "").toUpperCase();
  if (tag === "INPUT" || tag === "TEXTAREA") return;
  if (event.key === "ArrowLeft") readStep(1);
  if (event.key === "ArrowRight") readStep(-1);
});

const askFromBtn = document.querySelector("#readAsk, [onclick*='askFromReading']");
if (typeof window.askFromReading !== "function") window.askFromReading = askFromReading;
if (askFromBtn) askFromBtn.addEventListener("click", askFromReading);

async function boot() {
  initI18n();
  applyStaticI18n();
  const langSwitch = $("#langSwitch");
  if (langSwitch && !langSwitch.dataset.bound) {
    langSwitch.dataset.bound = "1";
    langSwitch.addEventListener("click", (event) => {
      const btn = event.target.closest("[data-lang]");
      if (!btn) return;
      setLang(btn.dataset.lang);
    });
  }
  onLangChange(() => {
    syncUser();
    route();
  });


  try {
    const me = await request("/api/me", {}, 8000);
    if (me?.username) {
      state.logged = true;
      state.user = { name: me.username.slice(0, 12), char: me.username.slice(0, 1) };
    }
  } catch {
    state.logged = false;
  }
  syncUser();
  await loadBooks(true);
  try {
    const data = await request("/api/sages");
    if (data.sages?.length) state.people = data.sages.map(enrichSage);
  } catch {
    state.people = SAGE_PROFILES.slice();
  }
  try {
    const data = await request("/api/presence/voices");
    if (data.voices?.length) state.voices = data.voices;
  } catch {
    state.voices = VOICES.slice();
  }
  route();
}

boot();
