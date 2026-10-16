import os
import re
import requests
from playwright.sync_api import sync_playwright

URL = 'https://buyticketbrasil.com/event/bts-2026worldtourarirang/'
PRECO_MAX = 99999  # valor de teste; troque pelo real depois
TOPICO = os.getenv('NTFY_TOPIC')
if not TOPICO:
    raise RuntimeError('NTFY_TOPIC não definido')

respostas = []


def ao_responder(r):
    tipo = r.headers.get('content-type', '')
    if 'json' in tipo:
        respostas.append(r.url)


with sync_playwright() as p:
    navegador = p.chromium.launch(headless=True, args=['--no-sandbox'])
    contexto = navegador.new_context(
        locale='pt-BR',
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    )
    pagina = contexto.new_page()
    pagina.on('response', ao_responder)
    pagina.goto(URL, wait_until='domcontentloaded')
    pagina.wait_for_timeout(10000)
    texto = pagina.inner_text('body')
    navegador.close()

print('Tamanho do texto:', len(texto))
print('--- INICIO DO TEXTO ---')
print(texto[:1500])
print('--- FIM DO TRECHO ---')
print('Respostas JSON:')
for u in respostas[:20]:
    print(u)

precos = []
for x in re.findall(r'R\$\s*([\d.]+(?:,\d{2})?)', texto):
    precos.append(float(x.replace('.', '').replace(',', '.')))
print('Preços encontrados:', precos)

baratos = [x for x in precos if x <= PRECO_MAX]
if baratos:
    mensagem = f'Ingresso por R${min(baratos):.2f}! {URL}'
    requests.post(f'https://ntfy.sh/{TOPICO}', data=mensagem.encode('utf-8'))
    print('Aviso enviado.')
else:
    print('Nada abaixo do limite.')
