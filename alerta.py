import os
import requests

SESSAO = 'ced30381-0cc4-4779-9c6b-ba05f44d086e'
API = f'https://buyticketbrasil.com/api/backend/marketplaces/sessions/{SESSAO}/tickets'
LINK = 'https://buyticketbrasil.com/event/bts-2026worldtourarirang/'
PRECO_MAX = 99999  # valor de teste; troque pelo real depois
SETORES = []  # vazio = todos; ou por exemplo ['Pista', 'Cadeira Inferior']
TOPICO = os.getenv('NTFY_TOPIC')
if not TOPICO:
    raise RuntimeError('NTFY_TOPIC não definido')

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
    linhas = [f'{nome}: R${preco:.2f}' for preco, nome in achados]
    mensagem = 'Ingresso disponível!\n' + '\n'.join(linhas) + '\n' + LINK
    requests.post(f'https://ntfy.sh/{TOPICO}', data=mensagem.encode('utf-8'))
    print('Aviso enviado.')
else:
    print('Nada abaixo do limite.')
