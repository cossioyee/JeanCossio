from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)

HTML = '''
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Mi sitio minimalista</title>
  <style>
    :root{--bg:#0f1724;--card:#111827;--muted:#94a3b8;--accent:#60a5fa}
    *{box-sizing:border-box}
    html,body{height:100%;margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,'Helvetica Neue',Arial}
    body{background:linear-gradient(180deg,var(--bg),#071024);color:#e6eef8;display:flex;align-items:center;justify-content:center}
    .card{width:min(760px,92%);background:rgba(255,255,255,0.03);padding:32px;border-radius:12px;box-shadow:0 6px 30px rgba(2,6,23,0.6)}
    header{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px}
    h1{font-size:1.4rem;margin:0}
    p.lead{color:var(--muted);margin:8px 0 18px}
    .actions{display:flex;gap:8px}
    a.button{padding:8px 12px;background:linear-gradient(90deg,var(--accent),#3b82f6);color:#07203a;text-decoration:none;border-radius:8px;font-weight:600}
    .grid{display:grid;grid-template-columns:1fr 280px;gap:18px}
    .box{background:rgba(255,255,255,0.02);padding:16px;border-radius:10px}
    form label{display:block;font-size:0.85rem;color:var(--muted);margin-bottom:6px}
    input[type=text],textarea{width:100%;padding:10px;border-radius:8px;border:1px solid rgba(255,255,255,0.03);background:transparent;color:inherit}
    textarea{min-height:90px}
    footer{margin-top:16px;font-size:0.85rem;color:var(--muted);text-align:center}
    @media (max-width:820px){.grid{grid-template-columns:1fr}}
  </style>
</head>
<body>
  <div class="card">
    <header>
      <div>
        <h1>Mi sitio minimalista</h1>
        <p class="lead">Diseño limpio, rápido y fácil de mantener.</p>
      </div>
      <div class="actions">
        <a class="button" href="#contact">Contacto</a>
      </div>
    </header>

    <main class="grid">
      <section>
        <div class="box">
          <h2>Bienvenido</h2>
          <p class="lead">Este es un ejemplo de sitio minimalista construido con Python + Flask. Ideal para landing pages, portafolios sencillos o páginas "coming soon".</p>

          <h3>Características</h3>
          <ul>
            <li>Una sola ruta (/) que sirve HTML simple.</li>
            <li>Formulario de contacto que simula envío (no guarda datos).</li>
            <li>Responsive y con CSS embebido para máxima simplicidad.</li>
          </ul>
        </div>
      </section>

      <aside>
        <div id="contact" class="box">
          <h3>Contacto</h3>
          {% if message_sent %}
            <p>Gracias — recibimos tu mensaje:</p>
            <div style="white-space:pre-wrap;background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;margin-top:8px">{{submitted}}</div>
          {% else %}
            <form method="post" action="/contact">
              <label for="name">Nombre</label>
              <input id="name" name="name" type="text" placeholder="Tu nombre" required>

              <label for="msg" style="margin-top:8px">Mensaje</label>
              <textarea id="msg" name="message" placeholder="Escribe algo..." required></textarea>

              <div style="margin-top:10px;display:flex;justify-content:flex-end">
                <button type="submit" style="padding:8px 12px;border-radius:8px;border:none;background:var(--accent);font-weight:600">Enviar</button>
              </div>
            </form>
          {% endif %}
        </div>
      </aside>
    </main>

    <footer>
      <small>Hecho con ❤️ — Minimal &amp; Python</small>
    </footer>
  </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML, message_sent=False)

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name', '').strip()
    message = request.form.get('message', '').strip()
    submitted = f"{name}: {message}"
    # En una app real aquí podrías guardar en DB o enviar email.
    return render_template_string(HTML, message_sent=True, submitted=submitted)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2000, debug=True)

