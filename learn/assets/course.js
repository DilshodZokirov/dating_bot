/* Soyla Web Kursi — kurs dvigateli:
   1) jonli kod maydonlari (playground),
   2) o'zlashtirilgan darslar belgisi (localStorage),
   3) bosh sahifa kartalari va darslar orasidagi navigatsiya. */

(function () {
  "use strict";

  var STORE_KEY = "soyla-web-kursi-progress";
  var lessons = window.LESSONS || [];

  /* ——— Progress (brauzer xotirasi) ——— */

  function readProgress() {
    try {
      return JSON.parse(localStorage.getItem(STORE_KEY) || "{}") || {};
    } catch (err) {
      // file:// ochilganda yoki xotira o'chirilganda — shunchaki bo'sh holat
      return {};
    }
  }

  function writeProgress(data) {
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify(data));
    } catch (err) {
      /* saqlanmasa ham kurs ishlashda davom etadi */
    }
  }

  /* ——— Jonli kod maydoni ——— */

  // Faylda chiroyli qilib chekingan kodni chap chegaraga tekislaydi.
  function dedent(text) {
    var lines = text.replace(/\t/g, "  ").split("\n");
    while (lines.length && lines[0].trim() === "") lines.shift();
    while (lines.length && lines[lines.length - 1].trim() === "") lines.pop();
    var indent = lines.reduce(function (min, line) {
      if (!line.trim()) return min;
      var spaces = line.match(/^ */)[0].length;
      return Math.min(min, spaces);
    }, Infinity);
    if (!isFinite(indent) || indent === 0) return lines.join("\n");
    return lines
      .map(function (line) {
        return line.slice(indent);
      })
      .join("\n");
  }

  /* Kod maydoni <textarea> ichida saqlanadi, shuning uchun misol kodida
     yopiluvchi textarea tegini to'g'ridan-to'g'ri yozib bo'lmaydi (u maydonni
     vaqtidan oldin yopib qo'yadi). Shu sababli darslarda @@/textarea@@ belgisi
     ishlatiladi va yuklanishda haqiqiy tegga almashtiriladi. */
  function unescapeTokens(text) {
    return text.replace(/@@\/textarea@@/g, "</textarea>");
  }

  // JS rejimidagi kodni console chiqishi ko'rinadigan sahifaga o'raydi.
  function wrapJs(code) {
    return [
      '<!DOCTYPE html><html lang="uz"><head><meta charset="utf-8"><style>',
      "body{margin:0;padding:12px;background:#05100e;color:#d8f3e8;",
      'font:13px/1.6 Consolas,"Courier New",monospace}',
      ".ln{padding:2px 0;border-bottom:1px solid rgba(255,255,255,.06);white-space:pre-wrap}",
      ".ln.err{color:#ff8b8b}.ln.warn{color:#ffd465}",
      ".hint{color:#8aa39a}",
      '</style></head><body><div id="__console"><div class="hint">console.log(...) natijasi shu yerda chiqadi</div></div>',
      "<script>(function(){",
      'var box=document.getElementById("__console");var clean=false;',
      "function show(kind,args){",
      "  if(!clean){box.innerHTML=\"\";clean=true;}",
      '  var row=document.createElement("div");row.className="ln "+kind;',
      '  row.textContent=Array.prototype.map.call(args,function(v){',
      '    if(typeof v==="string")return v;',
      "    try{return JSON.stringify(v);}catch(e){return String(v);}",
      '  }).join(" ");',
      "  box.appendChild(row);",
      "}",
      'var log=console.log;console.log=function(){show("",arguments);log.apply(console,arguments);};',
      'console.error=function(){show("err",arguments);};',
      'console.warn=function(){show("warn",arguments);};',
      'window.onerror=function(m){show("err",["Xato: "+m]);};',
      "try{",
      code.replace(/<\/script>/gi, "<\\/script>"),
      "\n}catch(e){show(\"err\",[\"Xato: \"+e.message]);}",
      "})();<\/script></body></html>",
    ].join("\n");
  }

  function buildPlayground(pg) {
    var source = pg.querySelector("textarea");
    if (!source) return;

    var mode = pg.getAttribute("data-mode") || "html";
    var title = pg.getAttribute("data-title") || (mode === "js" ? "JavaScript" : "HTML");
    var original = unescapeTokens(dedent(source.value));

    var head = document.createElement("div");
    head.className = "pg-head";
    head.innerHTML =
      '<span class="pg-title"></span>' +
      '<button type="button" class="pg-run">Ishga tushirish</button>' +
      '<button type="button" class="pg-reset">Boshidan</button>';
    head.querySelector(".pg-title").textContent = title;

    var body = document.createElement("div");
    body.className = "pg-body";

    source.className = "pg-src";
    source.value = original;
    source.spellcheck = false;
    source.setAttribute("aria-label", title + " — kod maydoni");

    var out = document.createElement("iframe");
    out.className = "pg-out";
    out.title = title + " — natija";

    body.appendChild(source);
    body.appendChild(out);
    pg.insertBefore(head, pg.firstChild);
    pg.appendChild(body);

    function run() {
      var code = source.value;
      out.srcdoc = mode === "js" ? wrapJs(code) : code;
    }

    var timer = null;
    source.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(run, 700);
    });
    // Tab tugmasi sahifani emas, kodni chekitsin
    source.addEventListener("keydown", function (event) {
      if (event.key !== "Tab") return;
      event.preventDefault();
      var start = source.selectionStart;
      source.value = source.value.slice(0, start) + "  " + source.value.slice(source.selectionEnd);
      source.selectionStart = source.selectionEnd = start + 2;
    });
    head.querySelector(".pg-run").addEventListener("click", run);
    head.querySelector(".pg-reset").addEventListener("click", function () {
      source.value = original;
      run();
    });

    run();
  }

  /* ——— Dars sahifasi ——— */

  function lessonIndexById(id) {
    for (var i = 0; i < lessons.length; i++) {
      if (lessons[i].id === id) return i;
    }
    return -1;
  }

  function setupLessonPage(id) {
    var at = lessonIndexById(id);
    var lesson = lessons[at];
    var crumb = document.querySelector(".topbar .crumb");
    if (crumb && lesson) {
      crumb.textContent = "Dars " + lesson.id + " · " + lesson.group + " · ~" + lesson.minutes + " daqiqa";
    }

    var foot = document.querySelector(".lesson-foot");
    if (!foot) return;

    var button = document.createElement("button");
    button.type = "button";
    button.className = "done-btn";

    function paint() {
      var done = readProgress()[id];
      button.classList.toggle("is-done", !!done);
      button.textContent = done ? "✓ Bu darsni o'zlashtirdim" : "Bu darsni o'zlashtirdim";
    }

    button.addEventListener("click", function () {
      var data = readProgress();
      if (data[id]) delete data[id];
      else data[id] = true;
      writeProgress(data);
      paint();
    });
    paint();
    foot.appendChild(button);

    var nav = document.createElement("div");
    nav.className = "nav-row";
    var prev = lessons[at - 1];
    var next = lessons[at + 1];
    if (prev) {
      nav.innerHTML +=
        '<a class="prev" href="' + prev.file + '"><small>← Oldingi dars</small>' + prev.id + ". " + prev.title + "</a>";
    }
    nav.innerHTML += '<a href="../index.html"><small>Kurs</small>Barcha darslar</a>';
    if (next) {
      nav.innerHTML +=
        '<a class="next" href="' + next.file + '"><small>Keyingi dars →</small>' + next.id + ". " + next.title + "</a>";
    }
    foot.appendChild(nav);
  }

  /* ——— Bosh sahifa ——— */

  function setupIndexPage() {
    var host = document.querySelector("[data-cards]");
    if (!host) return;
    var done = readProgress();
    var group = "";
    var html = "";

    lessons.forEach(function (lesson) {
      if (lesson.group !== group) {
        group = lesson.group;
        html += "<h2>" + group + "</h2>";
      }
      var isDone = !!done[lesson.id];
      html +=
        '<a class="card' + (isDone ? " done" : "") + '" href="lessons/' + lesson.file + '">' +
        '<div class="row"><span class="num">' + lesson.id + "</span>" +
        '<span class="pill ' + lesson.group.toLowerCase() + '">' + lesson.group + "</span>" +
        (isDone ? '<span class="tick">✓ o\'zlashtirildi</span>' : "") +
        "</div>" +
        "<h3>" + lesson.title + "</h3>" +
        "<p>" + lesson.summary + "</p>" +
        '<div class="meta">~' + lesson.minutes + " daqiqa</div>" +
        "</a>";
    });
    host.innerHTML = html;

    var count = lessons.filter(function (lesson) {
      return done[lesson.id];
    }).length;
    var fill = document.querySelector(".bar > i");
    var label = document.querySelector("[data-progress-label]");
    var percent = lessons.length ? Math.round((count / lessons.length) * 100) : 0;
    if (fill) fill.style.width = percent + "%";
    if (label) label.textContent = count + " / " + lessons.length + " dars (" + percent + "%)";
  }

  /* ——— Ishga tushirish ——— */

  document.addEventListener("DOMContentLoaded", function () {
    Array.prototype.forEach.call(document.querySelectorAll(".pg"), buildPlayground);
    var id = document.body.getAttribute("data-lesson");
    if (id) setupLessonPage(id);
    else setupIndexPage();
  });
})();
