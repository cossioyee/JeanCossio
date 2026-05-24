import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import create_engine
from datetime import datetime

DB = "sqlite:////data/finanzas.db"
REPORTS_DIR = "/reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

engine = create_engine(DB)

C = {
    'verde':      '#00C853',
    'rojo':       '#FF1744',
    'azul':       '#2979FF',
    'naranja':    '#FF9100',
    'morado':     '#D500F9',
    'cyan':       '#00E5FF',
    'fondo':      '#0A0E1A',
    'superficie': '#141824',
    'borde':      '#1E2537',
    'texto':      '#E2E8F0',
    'subtexto':   '#94A3B8',
}

LAYOUT = dict(
    paper_bgcolor=C['fondo'],
    plot_bgcolor=C['superficie'],
    font=dict(color=C['texto'], family='Inter, Segoe UI, Arial', size=12),
    margin=dict(l=50, r=30, t=50, b=50),
    legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor=C['borde']),
    xaxis=dict(gridcolor=C['borde'], linecolor=C['borde']),
    yaxis=dict(gridcolor=C['borde'], linecolor=C['borde'], tickformat=',.0f'),
)


# ── Carga ──────────────────────────────────────────────────────────────────────

def cargar_datos():
    try:
        ahorros  = pd.read_sql("SELECT * FROM ahorros",  engine)
        tarjetas = pd.read_sql("SELECT * FROM tarjetas", engine)
    except Exception as e:
        raise RuntimeError(f"Error al cargar datos: {e}")

    ahorros['fecha']  = pd.to_datetime(ahorros['fecha'])
    ahorros['monto']  = pd.to_numeric(ahorros['monto'], errors='coerce')
    ahorros['total']  = pd.to_numeric(ahorros['total'], errors='coerce')
    ahorros = ahorros.sort_values('fecha').reset_index(drop=True)

    tarjetas['fecha_transaccion'] = pd.to_datetime(tarjetas['fecha_transaccion'])
    tarjetas['cargos_db'] = pd.to_numeric(tarjetas['cargos_db'], errors='coerce').fillna(0).abs()
    tarjetas['pagos_cr']  = pd.to_numeric(tarjetas['pagos_cr'],  errors='coerce').fillna(0).abs()
    tarjetas['categoria']   = tarjetas['categoria'].fillna('Sin categoría').astype(str).str.strip()
    tarjetas['descripcion'] = tarjetas['descripcion'].fillna('Sin descripción').astype(str).str.strip()

    return ahorros, tarjetas


# ── Métricas ───────────────────────────────────────────────────────────────────

def calcular_metricas(ahorros, tarjetas):
    balance_actual = ahorros['total'].dropna().iloc[-1]

    ahorros = ahorros.copy()
    ahorros['mes'] = ahorros['fecha'].dt.to_period('M')
    mov = ahorros.groupby('mes')['monto'].sum()
    ingresos_prom = mov[mov > 0].mean()
    egresos_prom  = mov[mov < 0].mean()
    neto_prom     = mov.mean()

    tarjetas = tarjetas.copy()
    tarjetas['mes'] = tarjetas['fecha_transaccion'].dt.to_period('M')
    mens = tarjetas.groupby('mes').agg(cargos=('cargos_db', 'sum'), pagos=('pagos_cr', 'sum'))
    gasto_prom = mens['cargos'].mean()
    cobertura   = (mens['pagos'] / mens['cargos'].replace(0, float('nan')) * 100).tail(3).mean()
    meses_def   = int((mens['pagos'] < mens['cargos']).sum())
    tasa_ahorro = (neto_prom / ingresos_prom * 100) if ingresos_prom else 0.0

    return {
        'balance_actual':         balance_actual,
        'ingresos_prom_mes':      ingresos_prom if pd.notna(ingresos_prom) else 0,
        'egresos_prom_mes':       abs(egresos_prom) if pd.notna(egresos_prom) else 0,
        'tasa_ahorro':            tasa_ahorro,
        'gasto_tarjeta_prom_mes': gasto_prom,
        'cobertura_deuda':        cobertura if pd.notna(cobertura) else 0,
        'meses_deficit':          meses_def,
        'periodo_ahorros':  f"{ahorros['fecha'].min().strftime('%b %Y')} – {ahorros['fecha'].max().strftime('%b %Y')}",
        'periodo_tarjetas': f"{tarjetas['fecha_transaccion'].min().strftime('%b %Y')} – {tarjetas['fecha_transaccion'].max().strftime('%b %Y')}",
    }


# ── Ahorros ────────────────────────────────────────────────────────────────────

def grafica_balance(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['fecha'], y=df['total'],
        name='Balance',
        line=dict(color=C['azul'], width=2),
        fill='tozeroy', fillcolor='rgba(41,121,255,0.08)',
        hovertemplate='%{x|%d %b %Y}<br>Balance: %{y:,.2f}<extra></extra>',
    ))
    for idx, label, color in [
        (df['total'].idxmax(), 'Máx', C['verde']),
        (df['total'].idxmin(), 'Mín', C['rojo']),
    ]:
        fig.add_annotation(
            x=df.loc[idx, 'fecha'], y=df.loc[idx, 'total'],
            text=f"{label}: {df.loc[idx, 'total']:,.0f}",
            showarrow=True, arrowhead=2, arrowcolor=color,
            font=dict(color=color, size=11),
            bgcolor=C['superficie'], bordercolor=color,
        )
    fig.update_layout(**LAYOUT, title='Balance de Ahorros en el Tiempo')
    return fig


def grafica_movimientos_mensuales(df):
    df = df.copy()
    df['mes'] = df['fecha'].dt.to_period('M')
    meses = sorted(df['mes'].unique())
    meses_str = [str(m) for m in meses]
    ing  = df[df['monto'] > 0].groupby('mes')['monto'].sum()
    egr  = df[df['monto'] < 0].groupby('mes')['monto'].sum().abs()
    neto = df.groupby('mes')['monto'].sum()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=meses_str, y=[ing.get(m, 0) for m in meses],
        name='Ingresos', marker_color=C['verde'],
        hovertemplate='%{x}<br>Ingresos: %{y:,.2f}<extra></extra>',
    ))
    fig.add_trace(go.Bar(
        x=meses_str, y=[-egr.get(m, 0) for m in meses],
        name='Egresos', marker_color=C['rojo'],
        hovertemplate='%{x}<br>Egresos: %{y:,.2f}<extra></extra>',
    ))
    fig.add_trace(go.Scatter(
        x=meses_str, y=[neto.get(m, 0) for m in meses],
        name='Neto', mode='lines+markers',
        line=dict(color=C['cyan'], width=2), marker=dict(size=6),
        hovertemplate='%{x}<br>Neto: %{y:,.2f}<extra></extra>',
    ))
    fig.update_layout(**LAYOUT, title='Ingresos y Egresos Mensuales', barmode='relative')
    return fig


# ── Tarjetas ───────────────────────────────────────────────────────────────────

def grafica_cargos_pagos(df):
    df = df.copy()
    df['mes'] = df['fecha_transaccion'].dt.to_period('M')
    mens = df.groupby('mes').agg(
        cargos=('cargos_db', 'sum'), pagos=('pagos_cr', 'sum')
    ).reset_index()
    mens['mes_str']   = mens['mes'].astype(str)
    mens['cobertura'] = (mens['pagos'] / mens['cargos'].replace(0, float('nan')) * 100).fillna(0)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=mens['mes_str'], y=mens['cargos'], name='Cargos', marker_color=C['rojo'],
        hovertemplate='%{x}<br>Cargos: %{y:,.2f}<extra></extra>',
    ))
    fig.add_trace(go.Bar(
        x=mens['mes_str'], y=mens['pagos'], name='Pagos', marker_color=C['verde'],
        hovertemplate='%{x}<br>Pagos: %{y:,.2f}<extra></extra>',
    ))
    fig.add_trace(go.Scatter(
        x=mens['mes_str'], y=mens['cobertura'],
        name='Cobertura %', yaxis='y2', mode='lines+markers',
        line=dict(color=C['naranja'], width=2, dash='dot'), marker=dict(size=6),
        hovertemplate='%{x}<br>Cobertura: %{y:.1f}%<extra></extra>',
    ))
    layout = {
        **LAYOUT,
        'title':   'Cargos vs Pagos Mensuales',
        'barmode': 'group',
        'yaxis2':  dict(
            title='Cobertura %', overlaying='y', side='right',
            tickformat='.0f', ticksuffix='%',
            gridcolor='rgba(0,0,0,0)', linecolor=C['borde'],
        ),
    }
    fig.update_layout(**layout)
    return fig


def grafica_tendencia_categorias(df):
    df = df.copy()
    df['mes'] = df['fecha_transaccion'].dt.to_period('M')
    top_cats = (
        df[df['cargos_db'] > 0].groupby('categoria')['cargos_db']
        .sum().nlargest(5).index.tolist()
    )
    pivot = (
        df[df['categoria'].isin(top_cats) & (df['cargos_db'] > 0)]
        .groupby(['mes', 'categoria'])['cargos_db'].sum()
        .unstack(fill_value=0)
    )
    meses_str = pivot.index.astype(str).tolist()
    palette   = [C['azul'], C['verde'], C['naranja'], C['morado'], C['cyan']]

    fig = go.Figure()
    for i, cat in enumerate(top_cats):
        if cat in pivot.columns:
            fig.add_trace(go.Scatter(
                x=meses_str, y=pivot[cat], name=str(cat),
                mode='lines+markers',
                line=dict(color=palette[i % len(palette)], width=2), marker=dict(size=6),
                hovertemplate=f'{cat}<br>%{{x}}<br>%{{y:,.2f}}<extra></extra>',
            ))
    fig.update_layout(**LAYOUT, title='Tendencia Mensual – Top 5 Categorías')
    return fig


# ── Categorías ─────────────────────────────────────────────────────────────────

def grafica_categoria_total(df):
    por_cat = (
        df[df['cargos_db'] > 0]
        .groupby('categoria')['cargos_db'].sum()
        .sort_values(ascending=True)
    )
    palette = px.colors.sequential.Plasma_r
    colors  = [palette[int(i * (len(palette) - 1) / max(len(por_cat) - 1, 1))]
               for i in range(len(por_cat))]
    fig = go.Figure(go.Bar(
        x=por_cat.values, y=por_cat.index.astype(str),
        orientation='h', marker=dict(color=colors),
        hovertemplate='%{y}<br>Total: %{x:,.2f}<extra></extra>',
    ))
    layout = {**LAYOUT, 'title': 'Gasto Total por Categoría'}
    layout['xaxis'] = {**layout['xaxis'], 'tickformat': ',.0f'}
    layout['yaxis'] = {**layout['yaxis'], 'tickformat': ''}
    fig.update_layout(**layout)
    return fig


def grafica_categoria_mensual(df):
    df = df.copy()
    df['mes'] = df['fecha_transaccion'].dt.to_period('M')
    pivot = (
        df[df['cargos_db'] > 0]
        .groupby(['categoria', 'mes'])['cargos_db'].sum()
        .unstack(fill_value=0)
    )
    pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=True).index]
    meses_str = pivot.columns.astype(str).tolist()

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=meses_str,
        y=pivot.index.astype(str).tolist(),
        colorscale='Plasma',
        hovertemplate='%{y}<br>%{x}<br>Gasto: %{z:,.2f}<extra></extra>',
        colorbar=dict(tickformat=',.0f', title='Monto'),
    ))
    layout = {**LAYOUT, 'title': 'Gasto por Categoría × Mes'}
    layout['yaxis'] = {**layout['yaxis'], 'tickformat': ''}
    layout['xaxis'] = {**layout['xaxis'], 'tickformat': ''}
    fig.update_layout(**layout)
    return fig


def tabla_categoria_mensual(df):
    df = df.copy()
    df['mes'] = df['fecha_transaccion'].dt.to_period('M')
    pivot = (
        df[df['cargos_db'] > 0]
        .groupby(['categoria', 'mes'])['cargos_db'].sum()
        .unstack(fill_value=0)
    )
    pivot['TOTAL'] = pivot.sum(axis=1)
    pivot = pivot.sort_values('TOTAL', ascending=False)
    totales = pivot.sum(axis=0)
    totales.name = 'TOTAL'
    pivot = pd.concat([pivot, totales.to_frame().T])

    def fmt_mes(p):
        try:
            return p.to_timestamp().strftime('%b %y')
        except Exception:
            return str(p)

    col_headers = [fmt_mes(c) if c != 'TOTAL' else 'TOTAL' for c in pivot.columns]
    cats = pivot.index.astype(str).tolist()

    def fmt_val(v):
        return f"{v:,.0f}" if v > 0 else '–'

    data_cols = [
        [fmt_val(pivot.iloc[r, c]) for r in range(len(pivot))]
        for c in range(len(pivot.columns))
    ]

    row_colors = []
    for i, cat in enumerate(cats):
        if cat == 'TOTAL':
            row_colors.append('#2A3050')
        elif i % 2 == 0:
            row_colors.append(C['superficie'])
        else:
            row_colors.append('#111520')

    n_cols = 1 + len(pivot.columns)
    cell_fill = [row_colors] * n_cols

    fig = go.Figure(go.Table(
        columnwidth=[3] + [1.5] * len(pivot.columns),
        header=dict(
            values=['Categoría'] + col_headers,
            fill_color=C['borde'],
            font=dict(color=C['texto'], size=11, family='Inter, Segoe UI, Arial'),
            align=['left'] + ['right'] * len(pivot.columns),
            line_color=C['fondo'],
            height=32,
        ),
        cells=dict(
            values=[cats] + data_cols,
            fill_color=cell_fill,
            font=dict(color=C['texto'], size=11, family='Inter, Segoe UI, Arial'),
            align=['left'] + ['right'] * len(pivot.columns),
            line_color=C['fondo'],
            height=28,
        ),
    ))
    height = max(400, 90 + len(pivot) * 28)
    fig.update_layout(
        paper_bgcolor=C['fondo'],
        font=dict(color=C['texto'], family='Inter, Segoe UI, Arial'),
        title='Gasto Mensual por Categoría',
        margin=dict(l=20, r=20, t=50, b=10),
        height=height,
    )
    return fig


# ── Descripciones ──────────────────────────────────────────────────────────────

def grafica_descripcion_total(df, top_n=20):
    top = (
        df[df['cargos_db'] > 0]
        .groupby('descripcion')['cargos_db'].sum()
        .sort_values(ascending=True)
        .tail(top_n)
    )
    fig = go.Figure(go.Bar(
        x=top.values, y=top.index.astype(str),
        orientation='h', marker=dict(color=C['morado']),
        hovertemplate='%{y}<br>Total: %{x:,.2f}<extra></extra>',
    ))
    layout = {**LAYOUT, 'title': f'Gasto Total por Descripción (Top {top_n})'}
    layout['xaxis'] = {**layout['xaxis'], 'tickformat': ',.0f'}
    layout['yaxis'] = {**layout['yaxis'], 'tickformat': ''}
    fig.update_layout(**layout)
    return fig


def grafica_descripcion_mensual(df, top_n=15):
    df = df.copy()
    df['mes'] = df['fecha_transaccion'].dt.to_period('M')
    top_desc = (
        df[df['cargos_db'] > 0]
        .groupby('descripcion')['cargos_db'].sum()
        .nlargest(top_n).index.tolist()
    )
    pivot = (
        df[df['descripcion'].isin(top_desc) & (df['cargos_db'] > 0)]
        .groupby(['descripcion', 'mes'])['cargos_db'].sum()
        .unstack(fill_value=0)
    )
    pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=True).index]
    meses_str = pivot.columns.astype(str).tolist()

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=meses_str,
        y=pivot.index.astype(str).tolist(),
        colorscale='Viridis',
        hovertemplate='%{y}<br>%{x}<br>Gasto: %{z:,.2f}<extra></extra>',
        colorbar=dict(tickformat=',.0f', title='Monto'),
    ))
    layout = {**LAYOUT, 'title': f'Gasto por Descripción × Mes (Top {top_n})'}
    layout['yaxis'] = {**layout['yaxis'], 'tickformat': ''}
    layout['xaxis'] = {**layout['xaxis'], 'tickformat': ''}
    fig.update_layout(**layout)
    return fig


# ── HTML ───────────────────────────────────────────────────────────────────────

def _card(titulo, valor, subtitulo, color, alerta=False):
    border = C['rojo'] if alerta else color
    return f"""<div class="card" style="border-left:3px solid {border}">
      <div class="card-title">{titulo}</div>
      <div class="card-value" style="color:{border}">{valor}</div>
      <div class="card-sub">{subtitulo}</div>
    </div>"""


def _fig(fig):
    return fig.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})


def generar_html(metricas, figs):
    m = metricas
    cob_ok  = m['cobertura_deuda'] >= 100
    tasa_ok = m['tasa_ahorro'] > 10

    cards = ''.join([
        _card('Balance Actual',      f"{m['balance_actual']:,.2f}",         m['periodo_ahorros'],   C['azul']),
        _card('Ingreso Prom./Mes',   f"{m['ingresos_prom_mes']:,.2f}",       'histórico',            C['verde']),
        _card('Egreso Prom./Mes',    f"{m['egresos_prom_mes']:,.2f}",        'histórico',            C['rojo']),
        _card('Tasa de Ahorro',      f"{m['tasa_ahorro']:.1f}%",            'sobre ingresos',       C['verde'] if tasa_ok else C['naranja']),
        _card('Gasto Tarjeta/Mes',   f"{m['gasto_tarjeta_prom_mes']:,.2f}", 'histórico',            C['naranja']),
        _card('Cobertura de Deuda',  f"{m['cobertura_deuda']:.1f}%",        'últ. 3 meses',         C['verde'] if cob_ok else C['rojo'], alerta=not cob_ok),
    ])

    alerta = (
        f'<div class="alerta">⚠ {m["meses_deficit"]} meses con pagos menores a los cargos</div>'
        if m['meses_deficit'] > 0 else ''
    )

    ts = datetime.now().strftime('%d/%m/%Y %H:%M')

    # figs index:
    # 0 balance        1 mov_mensual
    # 2 cargos_pagos   3 tendencia_cats
    # 4 cat_total      5 cat_mensual    8 cat_tabla
    # 6 desc_total     7 desc_mensual

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>Análisis Financiero Personal</title>
  <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:{C['fondo']};color:{C['texto']};font-family:Inter,'Segoe UI',Arial,sans-serif;padding:28px 32px}}
    h1{{font-size:1.75rem;font-weight:700;color:#fff;margin-bottom:4px}}
    .gen{{color:{C['subtexto']};font-size:.85rem;margin-bottom:28px}}
    h2{{font-size:.8rem;font-weight:600;color:{C['subtexto']};text-transform:uppercase;
        letter-spacing:.08em;margin:36px 0 14px;border-left:3px solid {C['azul']};padding-left:10px}}
    .cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin-bottom:10px}}
    .card{{background:{C['superficie']};border-radius:10px;padding:16px 18px}}
    .card-title{{font-size:.7rem;color:{C['subtexto']};text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px}}
    .card-value{{font-size:1.35rem;font-weight:700;margin-bottom:3px}}
    .card-sub{{font-size:.72rem;color:{C['subtexto']}}}
    .alerta{{background:rgba(255,23,68,.12);border:1px solid {C['rojo']};border-radius:8px;
             padding:10px 16px;color:{C['rojo']};font-size:.85rem;margin:12px 0}}
    .grid2{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:0}}
    .chart{{background:{C['superficie']};border-radius:10px;padding:8px}}
    .span2{{grid-column:span 2}}
    .footer{{text-align:center;color:{C['subtexto']};font-size:.75rem;margin-top:32px}}
    @media(max-width:768px){{.grid2{{grid-template-columns:1fr}}.span2{{grid-column:span 1}}}}
  </style>
</head>
<body>
  <h1>Análisis Financiero Personal</h1>
  <div class="gen">Generado el {ts}</div>

  <h2>Resumen General</h2>
  <div class="cards">{cards}</div>
  {alerta}

  <h2>Ahorros — {m['periodo_ahorros']}</h2>
  <div class="grid2">
    <div class="chart span2">{_fig(figs[0])}</div>
    <div class="chart span2">{_fig(figs[1])}</div>
  </div>

  <h2>Tarjetas — {m['periodo_tarjetas']}</h2>
  <div class="grid2">
    <div class="chart span2">{_fig(figs[2])}</div>
    <div class="chart span2">{_fig(figs[3])}</div>
  </div>

  <h2>Análisis por Categoría</h2>
  <div class="grid2">
    <div class="chart">{_fig(figs[4])}</div>
    <div class="chart">{_fig(figs[5])}</div>
    <div class="chart span2">{_fig(figs[8])}</div>
  </div>

  <h2>Análisis por Descripción / Comercio</h2>
  <div class="grid2">
    <div class="chart">{_fig(figs[6])}</div>
    <div class="chart">{_fig(figs[7])}</div>
  </div>

  <div class="footer">finanzas.db · {ts}</div>
</body>
</html>"""


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("Cargando datos...")
    ahorros, tarjetas = cargar_datos()

    print("Calculando métricas...")
    metricas = calcular_metricas(ahorros, tarjetas)

    print("Generando gráficas...")
    figs = [
        grafica_balance(ahorros),                  # 0
        grafica_movimientos_mensuales(ahorros),    # 1
        grafica_cargos_pagos(tarjetas),            # 2
        grafica_tendencia_categorias(tarjetas),    # 3
        grafica_categoria_total(tarjetas),         # 4
        grafica_categoria_mensual(tarjetas),       # 5
        grafica_descripcion_total(tarjetas),       # 6
        grafica_descripcion_mensual(tarjetas),     # 7
        tabla_categoria_mensual(tarjetas),         # 8
    ]

    ruta = f"{REPORTS_DIR}/reporte_financiero.html"
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(generar_html(metricas, figs))

    print(f"\nReporte guardado en: {ruta}")
    print(f"\n{'='*52}")
    print("  RESUMEN FINANCIERO")
    print(f"{'='*52}")
    print(f"  Balance actual:      {metricas['balance_actual']:>18,.2f}")
    print(f"  Ingreso prom/mes:    {metricas['ingresos_prom_mes']:>18,.2f}")
    print(f"  Egreso prom/mes:     {metricas['egresos_prom_mes']:>18,.2f}")
    print(f"  Tasa de ahorro:      {metricas['tasa_ahorro']:>17.1f}%")
    print(f"  Gasto tarjeta/mes:   {metricas['gasto_tarjeta_prom_mes']:>18,.2f}")
    print(f"  Cobertura deuda:     {metricas['cobertura_deuda']:>17.1f}%")
    if metricas['meses_deficit'] > 0:
        print(f"  !! Meses con deficit: {metricas['meses_deficit']:>17}")
    print(f"{'='*52}")
