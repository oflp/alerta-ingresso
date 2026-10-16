import os
import requests

SESSAO = 'efba49ae-e7ac-4a9d-bcc7-09c51d093fd5'
API = f'https://buyticketbrasil.com/api/backend/marketplaces/sessions/{SESSAO}/tickets'
LINK = 'https://buyticketbrasil.com/event/primaverasound-2026/session/efba49ae-e7ac-4a9d-bcc7-09c51d093fd5'
PRECO_MAX = 200  # valor de teste; troque pelo seu valor máximo real
SETORES = ['Inteira','Meia Social']  # vazio = todos; ou por exemplo ['Pista', 'Meia Social']
TITULO = 'INGRESSO DISPONÍVEL - PRIMAVERA 05/12'
TOPICO = os.getenv('NTFY_TOPIC')
if not TOPICO:
    raise RuntimeError('NTFY_TOPIC não definido')


def formatar(valor):
    texto = f'{valor:,.2f}'
    texto = texto.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f'R$ {texto}'


resposta = requests.get(API, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
resposta.raise_for_status()
ingressos = resposta.json().get('tickets', [])

achados = []
for t in ingressos:
    nome = t['ticketType']
    preco = t['amount']['value']
    print(nome, preco)
    if preco <= 0:
        continue
    if SETORES and nome not in SETORES:
        continue
    if preco <= PRECO_MAX:
        achados.append((preco, nome))

if achados:
    achados.sort()
    linhas = [f'{nome} - {formatar(preco)}' for preco, nome in achados]
    mensagem = TITULO + '\n' + '\n'.join(linhas)
    requests.post(
        f'https://ntfy.sh/{TOPICO}',
        data=mensagem.encode('utf-8'),
        headers={'Click': LINK},
    )
    print('Aviso enviado.')
else:
    print('Nada abaixo do limite.')
