import os
import requests

EVENTOS = [
    {
        'titulo': 'PRIMAVERA 05/12',
        'sessao': 'efba49ae-e7ac-4a9d-bcc7-09c51d093fd5',
        'link': 'https://buyticketbrasil.com/event/primaverasound-2026/session/efba49ae-e7ac-4a9d-bcc7-09c51d093fd5',
        'preco_max': 200,  # troque pelo seu valor máximo real
        'setores': ['Inteira','Meia Social'],  # vazio = todos; ou por exemplo ['Pista', 'Meia Social']
    },
    {
        'titulo': '',  # nome que aparece na notificação
        'sessao': '',  # código da sessão (deixe vazio para ignorar este bloco)
        'link': '',  # link da página do evento
        'preco_max': 99999,  # valor máximo em reais
        'setores': [],  # vazio = todos
    },
]

TOPICO = os.getenv('NTFY_TOPIC')
if not TOPICO:
    raise RuntimeError('NTFY_TOPIC não definido')


def formatar(valor):
    texto = f'{valor:,.2f}'
    texto = texto.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f'R$ {texto}'


def checar(evento):
    api = f"https://buyticketbrasil.com/api/backend/marketplaces/sessions/{evento['sessao']}/tickets"
    resposta = requests.get(api, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
    resposta.raise_for_status()
    ingressos = resposta.json().get('tickets', [])

    achados = []
    for t in ingressos:
        nome = t['ticketType']
        preco = t['amount']['value']
        print(' ', nome, preco)
        if preco <= 0:
            continue
        if evento['setores'] and nome not in evento['setores']:
            continue
        if preco <= evento['preco_max']:
            achados.append((preco, nome))

    if achados:
        achados.sort()
        linhas = [f'{nome} - {formatar(preco)}' for preco, nome in achados]
        mensagem = 'INGRESSO DISPONÍVEL - ' + evento['titulo'] + '\n' + '\n'.join(linhas)
        cabecalhos = {}
        if evento['link']:
            cabecalhos['Click'] = evento['link']
        requests.post(
            f'https://ntfy.sh/{TOPICO}',
            data=mensagem.encode('utf-8'),
            headers=cabecalhos,
        )
        print('  Aviso enviado.')
    else:
        print('  Nada abaixo do limite.')


for evento in EVENTOS:
    if not evento['sessao'].strip():
        continue
    print(evento['titulo'])
    try:
        checar(evento)
    except Exception as erro:
        print('  Erro:', erro)
