# MedSourcing — Medical Product Sourcing & Procurement Coordination

A clean, professional, fully **static** website for a medical product sourcing and
procurement coordination service. Built with semantic HTML5, CSS (custom properties),
and vanilla JavaScript — **no frameworks, no build step, no backend**. It is ready to
host for free on **GitHub Pages**.

The site presents the service to two audiences:

- **Buyers / importers / distributors / procurement projects** — who need sourcing,
  RFQ preparation, quotation collection, offer comparison, and documentation follow-up.
- **Manufacturers / suppliers** — who receive structured RFQs and want to quote.

---

## Files

| File | Purpose |
|------|---------|
| `index.html` | All page content and sections (semantic HTML5, SEO + Open Graph tags). |
| `styles.css` | Design system (colors, type, layout) and responsive styling. |
| `script.js`  | Mobile menu, smooth-scroll behavior, contact form (mailto), scroll reveal. |
| `README.md`  | This file. |

The site has **no external dependencies** — fonts use the system font stack and all
icons are emoji or CSS, so it works offline and loads instantly.

---

## Run locally

Because everything is static, you can simply open the file:

1. Download or clone this folder.
2. Double-click `index.html` to open it in your browser.

**Recommended (avoids some browser security quirks):** serve it with a tiny local
web server.

Using Python (already installed on most systems):

```bash
# from inside the project folder
python3 -m http.server 8000
```

Then visit **http://localhost:8000** in your browser.

Using Node.js, if you prefer:

```bash
npx serve .
```

---

## Deploy on GitHub Pages

1. Create a new repository on GitHub (for example `medsourcing`).
2. Upload `index.html`, `styles.css`, `script.js`, and `README.md` to the repository
   root (drag-and-drop in the GitHub web UI, or push with Git).
3. In the repository, go to **Settings → Pages**.
4. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
5. Choose branch **`main`** and folder **`/ (root)`**, then click **Save**.
6. Wait about a minute. Your site will be published at:

   ```
   https://YOUR-USERNAME.github.io/medsourcing/
   ```

> Tip: If you name the repository `YOUR-USERNAME.github.io`, the site is served at the
> root `https://YOUR-USERNAME.github.io/` instead.

### Push with Git (optional)

```bash
git init
git add .
git commit -m "Initial commit: MedSourcing static site"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/medsourcing.git
git push -u origin main
```

---

## Customize: name, email, WhatsApp, and branding

Most edits live in just **two places**.

### 1. Contact details — edit `script.js`

Open `script.js` and update the `CONFIG` block at the very top. These values are applied
automatically to **every** email button, WhatsApp button, and the contact form:

```js
const CONFIG = {
  email: "your-email@example.com",   // your real email
  whatsapp: "000000000",             // digits only, international format (no +)
  whatsappDisplay: "+000000000",     // how the number is shown on screen
  brand: "MedSourcing",              // used in the email subject line
};
```

- `whatsapp` must contain **digits only** (country code + number), e.g. `15551234567`.
  It becomes the link `https://wa.me/15551234567`.
- `whatsappDisplay` is just for display, so you can format it nicely (e.g. `+1 555 123 4567`).

> The contact name shown on the page is **"Ahmed"**. Change it directly in `index.html`
> in the Contact section (search for `Ahmed`) and in the footer.

### 2. Brand name & wording — edit `index.html`

Search and replace **`MedSourcing`** in `index.html` with your business name. It appears in:

- The page `<title>` and meta tags
- The header logo (`brand__name`)
- The footer logo and copyright line

The fallback email/WhatsApp text in `index.html` is also overwritten by `CONFIG`, so you
only need to set them once in `script.js`.

### 3. Colors & fonts — edit `styles.css`

All colors live as variables at the top of `styles.css` under `:root`:

```css
--navy-900: #0c2340;   /* primary deep navy */
--blue-600: #2e74b5;   /* action / links */
--sky-400:  #5aa0e0;   /* light blue accent */
--gray-50:  #f4f6f9;   /* soft gray surface */
```

Change these and the whole site updates. Typography uses system fonts via
`--font-sans` and `--font-mono` (the monospace face is used for labels and data tags).

### 4. Favicon & social image

- **Favicon:** an inline SVG placeholder (a navy square with a light-blue cross) is set in
  the `<head>`. Replace the `href` on the `<link rel="icon">` tag with your own image, or
  add a `favicon.ico` / `favicon.svg` file and point to it.
- **Open Graph image:** the meta tags reference `og-image.png`. Add a `1200 × 630` PNG named
  `og-image.png` to the repository root and update the URLs in the `<head>` to your live
  GitHub Pages address so link previews show your image.

---

## Editing the content sections

All sections are clearly commented in `index.html`:

1. Hero
2. About
3. Services (8 service cards)
4. Product Categories (8 categories)
5. How We Work (5-step process)
6. Supplier Collaboration
7. Why Work With Us
8. Contact

To add or remove a service card, copy one `<article class="card"> … </article>` block.
To add a product category, copy one `<li class="category"> … </li>` block. The grids are
responsive and will reflow automatically.

---

## How the contact form works (no backend)

GitHub Pages only serves static files, so the form does **not** send email by itself.
When submitted, `script.js` validates the fields and opens the visitor's email app with
the subject and message **pre-filled** to your address (a `mailto:` link). The visitor
then presses send from their own email client.

If you later want true server-side form delivery, you can connect a free third-party form
service (for example, Formspree or Getform) by adding their endpoint — but that is optional
and not required for the site to work.

---

## Accessibility & performance notes

- Semantic landmarks (`header`, `main`, `nav`, `section`, `footer`) and ARIA labels.
- Visible keyboard focus, a skip-to-content link, and labeled form fields.
- Honors `prefers-reduced-motion` (animations are disabled for users who request it).
- Responsive from large desktop down to small phones.
- No external requests, so it is fast and works offline.

---

## License

You own this code for your project. Replace all placeholder text and contact details
before publishing.
