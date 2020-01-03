import requests
import json

def search_promotion(r, index, list):
  if r['posts'][index]['title'].find('promocao') != -1: # procura por produtos em promocao
    obj = {'product_id': r['posts'][index]['product_id'], 'price_field': r['posts'][index]['price']}
    list.append(obj) # salva o id do produto e o preco

def search_post(r, index, list):
  if r['posts'][index]['media'] == "instagram_cpc" and r['posts'][index]['likes'] > 700: # procura por posts com mais de 700 likes no instagram
    obj = {'post_id': r['posts'][index]['post_id'], 'price_field': r['posts'][index]['price']}
    list.append(obj) # salva o id do post e o preco

def search_may_post(r, index):
  if r['posts'][index]['media'].find('cpc') != -1 and r['posts'][index]['date'].find('/05/') != -1: # procura posts de maio nas midias pagas
    return r['posts'][index]['likes']
  return 0

def remove_duplicate(list):
  i = 1
  while(i != len(list)):
    if list[i]['product_id'] == list[i-1]['product_id']:
      list.pop(i)
    else:
      i += 1

def search_inconsistency(r, list):
  i = 1
  while(i != len(r['posts'])):
    if r['posts'][i]['product_id'] == r['posts'][i-1]['product_id'] and r['posts'][i]['price'] != r['posts'][i-1]['price']: # procura uma inconsistencia
      obj = r['posts'][i]['product_id']
      list.append(obj) # salva o id do produto
      i += 1
      while(i != len(r['posts']) and r['posts'][i]['product_id'] == r['posts'][i-1]['product_id']):
        i += 1
    else:
      i += 1

def build_json(answer_A, answer_B, answer_C, answer_D):
  r = {'full_name': 'Gustavo Issamu Amano Tanaka', 'email': 'gustavo-tanaka@usp.br', 'code_link': 'http://www.github.com/GustavoTanaka/psel-raccoon'}

  r['response_a'] = answer_A
  r['response_b'] = answer_B
  r['response_c'] = answer_C
  r['response_d'] = answer_D

  return r

def main():

  #   RECEBE OS DADOS   #

  r = requests.get('https://us-central1-psel-clt-ti-junho-2019.cloudfunctions.net/psel_2019_get')
  r_error = requests.get('https://us-central1-psel-clt-ti-junho-2019.cloudfunctions.net/psel_2019_get_error')
  r = r.json()
  r_error = r_error.json()

  list_A = []
  list_B = []
  cont = 0

  #   TRATAMENTO DOS DADOS   #

  for i in range(0,len(r['posts'])):
    search_promotion(r,i,list_A)
    search_post(r,i,list_B)
    cont +=  search_may_post(r, i) # soma em cont os likes da postagem (caso encontre)

  #   ORDENA AS LISTAS DE POR PRECO E DEPOIS ID DE FORMA CRESCENTE   #

  list_A.sort(key = lambda product: (product['price_field'], product['product_id']))
  list_B.sort(key = lambda product: (product['price_field'], product['post_id']))

  #   ELIMINA PRODUTOS REPETIDOS DA LIST_A   #

  remove_duplicate(list_A)

  #   ORDENA TODOS OS PRODUTOS POR ID DO PRODUTO   #

  r_error['posts'].sort(key = lambda x: (x['product_id']))

  #   COMPARA PRECOS DE PRODUTOS IGUAIS   #

  list_D = []
  search_inconsistency(r_error, list_D)

  #   CRIA ARQUIVO .JSON   #

  resposta = build_json(list_A,list_B,cont,list_D)
  with open('resposta.json', 'w') as outfile:
    json.dump(resposta, outfile)

if __name__ == "__main__":
  main()