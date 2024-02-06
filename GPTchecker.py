import requests
import asyncio
# оставлю пустой для ввода юзером
wallet_address = 'bc1qvhxafz8dqk8c25jsx669yd6qrxhl5dx72dyryp'

async def check_new_transaction(wallet_address):
    url = f'https://blockchain.info/rawaddr/{wallet_address}'
    response = requests.get(url)
    data = response.json()
    global NEW_TRANSACTION
    while True:
        print('Новые 30 секунд поехали!')
        # Проверяем, есть ли новые транзакции
        if data['n_tx'] > 0:
            for tx in data['txs']:
                print('ID транзакции:', tx['tx_index'])
                print('Сумма:', tx['result']/100000000)
                print('------------')
            old_data = data['n_tx']
            print(data['n_tx'])
            if old_data != data['n_tx']:
                print('💸Новая транзакция!💸')
                NEW_TRANSACTION = '💸Новая транзакция!💸'
        else:
            print('Транзакций на вашем кошельке нет или вы неправильно ввели кошелек или сервер не отвечает')
        await asyncio.sleep(30)
# check_new_transaction(wallet_address)
