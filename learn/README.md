# Soyla Web Kursi — HTML, CSS, JavaScript noldan

Bu papka — shu loyiha uchun yozilgan **interaktiv o'quv kursi**. 12 dars: web asoslaridan
boshlab, oxirida `app/webapp/index.html` (Soyla Mini App) kodini o'qishgacha.

Har bir darsda:

- qisqa nazariya (o'zbek tilida),
- **jonli kod maydonlari** — kodni o'zgartirasiz, natija darhol yonida ko'rinadi,
- mashqlar va yopiq holda turgan namuna yechimlar,
- tekshiruv savollari,
- "o'zlashtirdim" belgisi (brauzer xotirasida saqlanadi, bosh sahifada progress ko'rinadi).

## Kursni ochish

Eng yaxshi yo'l — loyiha ildizida kichik server ishga tushirish:

```bash
# loyiha papkasida
python -m http.server 5500
```

Keyin brauzerda: <http://localhost:5500/learn/>

> Fayllarni ikki marta bosib ham ochish mumkin, lekin server bilan hamma narsa
> (`fetch` misollari va progress xotirasi) haqiqiy sayt kabi ishlaydi.

Docker orqali API ishlab turgan bo'lsa, kurs `http://localhost:8000/learn/` da ochilmaydi —
u FastAPI faqat `/webapp/` ni beradi. Kurs uchun yuqoridagi alohida server ishlatiladi.

## Darslar

| № | Dars | Mavzu |
|---|------|-------|
| 00 | Web qanday ishlaydi | Brauzer, server, birinchi HTML sahifa, DevTools |
| 01 | HTML asoslari | Teglar, atributlar, matn, ro'yxat, havola, rasm, semantik teglar |
| 02 | Formalar va jadvallar | `input` turlari, `label`, `select`, validatsiya, `table` |
| 03 | CSS asoslari | Selektorlar, rang, shrift, box model, birliklar, `var()` |
| 04 | Flexbox va Grid | `display`, flex o'qlari, `gap`, grid `auto-fit`, `position` |
| 05 | Responsive va animatsiya | `@media`, mobile-first, `transition`, `transform`, `@keyframes` |
| 06 | JavaScript asoslari | `let/const`, turlar, shart, tsikl, funksiya, massiv, obyekt |
| 07 | DOM | `querySelector`, `textContent`, `classList`, `createElement` |
| 08 | Hodisalar va xotira | `addEventListener`, forma `submit`, delegatsiya, `localStorage` |
| 09 | Asinxron JS va fetch | `Promise`, `async/await`, `fetch`, JSON, xatolar |
| 10 | Yakuniy loyiha | HTML+CSS+JS: qidiruv, filtr, saqlanganlar — to'liq ilova |
| 11 | Soyla kodini o'qish | `app/webapp/index.html` naqshlari va birinchi o'zgartirish |

Tavsiya: kuniga bitta dars, har bir kod maydonini albatta o'zgartirib ko'rish.
Faqat o'qish bilan o'rganilmaydi — kod yozish kerak.

## Fayllar tuzilishi

```
learn/
├── index.html                  # kurs bosh sahifasi (darslar ro'yxati + progress)
├── README.md
├── assets/
│   ├── course.css              # kursning umumiy uslubi
│   ├── course.js               # jonli kod maydonlari, progress, navigatsiya
│   ├── lessons.js              # darslar ro'yxati (yagona manba)
│   └── demo-odamlar.json       # 09 va 10-darslardagi fetch misollari uchun
└── lessons/
    ├── 00-boshlash.html
    ├── ...
    └── 11-soyla-kodini-oqish.html
```

## Yangi dars qo'shish

1. `lessons/` ichida yangi HTML fayl yarating. Andoza sifatida mavjud darsni nusxalang:
   - `<body data-lesson="12">` — dars raqami,
   - oxirida `<div class="lesson-foot"></div>` (tugma va navigatsiya avtomatik qo'shiladi),
   - pastda `lessons.js` va `course.js` skriptlari.
2. `assets/lessons.js` ga yangi yozuv qo'shing (`id`, `file`, `group`, `title`, `summary`, `minutes`).
   Bosh sahifa kartasi va darslar orasidagi o'tish havolalari o'zi yasaladi.

### Jonli kod maydoni yozish

```html
<div class="pg" data-title="Misol nomi" data-tall>
<textarea>
  <h1>Salom</h1>
</textarea>
</div>
```

- `data-mode="js"` — faqat JavaScript rejimi: kod `console.log` chiqishi bilan ko'rsatiladi.
- `data-tall` — balandroq maydon (uzun misollar uchun).
- Kod chekilgan holda yozilsa ham, yuklanishda chap chegaraga tekislanadi.
- Kod ichida **yopiluvchi `textarea` tegini yozib bo'lmaydi** (u maydonni vaqtidan oldin yopadi).
  Kerak bo'lsa `@@/textarea@@` belgisini yozing — yuklanishda haqiqiy tegga almashtiriladi.
- Kod maydoni ichida `&lt;` kabi HTML belgilaridan foydalanmang: `textarea` ularni ochib yuboradi.
  Oddiy `<` va `>` yozing.

Nazariy matndagi kod namunalari esa `<pre><code>` ichida bo'ladi va u yerda, aksincha,
`&lt;` / `&gt;` / `&amp;` shaklida yozish kerak.
