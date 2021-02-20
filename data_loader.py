import requests


def main():
    url = 'https://webapi.investagrams.com/InvestaApi/Stock/GetStockTransactionByStockIdAndDate' \
          '?stockId=146&fromDate=2021/02/19&toDate=2021/02/19'

    with open('./cookie.txt') as fd:
        headers = {
            'Origin': 'https://www.investagrams.com',
            'Referer': 'https://www.investagrams.com/',
            'Cookie': fd.read()
        }

    response = requests.post(url, data={}, headers=headers)
    print(response.json())


if __name__ == '__main__':
    main()
