import os
import re
import requests
from playwright.sync_api import sync_playwright

URL = 'https://buyticketbrasil.com/event/primaverasound-2026'
PRECO_MAX = 99999  # <-- TROQUE pelo seu valor máximo, em reais
TOPICO = os.getenv('NTFY_TOPIC')
if not TOPICO:
    raise RuntimeError('NTFY_TOPIC environment variable is not set')

with sync_playwright() as p:
    navegador = p.chromium.launch(headless=True, args=['--no-sandbox'])
    pagina = navegador.new_page()
    pagina.goto(URL, wait_until='networkidle')
    texto = pagina.inner_text('body')
    navegador.close()

precos = [
    float(x.replace('.', '').replace(',', '.'))
    for x in re.findall(r'R\$\s*([\d.]+,\d{2})', texto)
]
print('Preços encontrados:', precos)
baratos = [x for x in precos if x <= PRECO_MAX]
if baratos:
    mensagem = f'Primavera Sound por R${min(baratos):.2f}! {URL}'
    requests.post(f'https://ntfy.sh/{TOPICO}', data=mensagem.encode('utf-8'))
    print('Aviso enviado.')
else:
    print('Nada abaixo do limite.')
