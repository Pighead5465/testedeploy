# NÃO ESQUECE DE FAZER ITERAÇÃO NO NÚMERO DE COLUNAS DA TABELA PEDIDOS PRO FETCHALL FUNCIONAR!
from django.shortcuts import render
from django.http import HttpResponse
import psycopg2 as pgre
import json
import datetime


# ------------------------------------DEFINIÇÃO LISTA DE PRODUTOS/PREÇOS E NÚMERO DO PEDIDO ATUAL
def index(request):
    conn = pgre.connect(
        host="127.0.0.1",
        database="cienciae_db002",
        user="cienciaemp",
        password="ciencia#2023"
    )


    cursor = conn.cursor()


    cursor.execute("select * from produtos")
    prodbruto = cursor.fetchall()

    
    fetchprodutos = [t[0] for t in prodbruto]
    fetchprecos = [t[1] for t in prodbruto]

    cursor.execute("select * from pedidos")
    registros = cursor.fetchall()
    temppedidoatual = len(registros) //5


    conn.commit()


    cursor.close()
    conn.close()
    listaprodutos = json.dumps(fetchprodutos)
    listaprecos = json.dumps(fetchprecos)



# ---------------------------------------------REDIRECIONAMENTO POST NULO OU ERRO DE PREENCHIMENTO
    if request.method != "POST":
        return render(request, 'main.html', {"error": 0, "listaprodutos": listaprodutos, "listaprecos": listaprecos})
    if request.POST["nomecliente"] == "" or request.POST["reservmesa"] == "" or int(request.POST["counteritens"]) == 0:
        return render(request, 'main.html', {"error": 1, "listaprodutos": listaprodutos, "listaprecos": listaprecos})
 
 

# ----------------------------------------------------DEFINIÇÃO DE VARIÁVEIS BÁSICAS
    agora = datetime.now
    data = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M:%S")
    numeropedido = temppedidoatual # "5"
    nomecliente = request.POST["nomecliente"] # "Nome"
    reservmesa = request.POST["reservmesa"] # "4" (não relevante)
    quantitens = int(request.POST["counteritens"]) # "2"
    totalpedido = request.POST["totalpedido"] # "15"
    ptemp = request.POST["listprodutos"]
    ptemp = ptemp.split("@")
    produtos = ptemp[:-1] # ["X-salada", "milkshake"]
    request.POST=None
    request._load_post_and_files()


# ----------------------------------------------------ITERAÇÃO LISTA DE QUANTIDADE
    listqtt = [] # ["3", "2", "1"]
    c=1
    while c<= quantitens:
        listqtt += request.POST[f"qttitem{c}"]
        c+=1
    if len(listqtt) != quantitens:
        return render(request, 'main.html', {"error": 1, "listaprodutos": listaprodutos, "listaprecos": listaprecos})



# --------------------------------------------------------ORGANIZAÇÃO LISTA DE PREÇOS (PAREAMENTO COM LISTA DE PRODUTOS)
    conn = pgre.connect(
    host="127.0.0.1",
    database="cienciae_db002",
    user="cienciaemp",
    password="ciencia#2023"
    )

    placeholders = ','.join(['%s']*len(produtos))

    # connect to the database and execute the SQL query
    cursor = conn.cursor()
    query = f"SELECT precoproduto FROM produtos WHERE nomeproduto IN ({placeholders}) ORDER BY CASE nomeproduto {' '.join([f'WHEN %s THEN {i+1}' for i in range(len(produtos))])} END"
    cursor.execute(query, produtos+produtos)
    results = cursor.fetchall()

    # convert the results to a list of prices
    price_list = [result[0] for result in results]

    # close the database connection
    conn.close()




# ----------------------------------------------------TESTE
    inputclientes = ""
    inputclientes+= nomecliente


    inputpedido = ""
    inputpedido+= (numeropedido+1)
    inputpedido+= reservmesa
    inputpedido+= nomecliente
    inputpedido+= f"{data} - {hora}"
    inputpedido+= totalpedido


    inputitens = ""
    c=0
    while c < quantitens:
        inputitens+= f"PEDIDO {numeropedido+1} // PRODUTO {produtos[c]} // QUANTIDADE {listqtt[c]} // UNITÁRIO {price_list[c]} // TOTAL ITEM {str(int(listqtt[c]) * int(price_list[c]))} ====="
        c+=1


    prodfinal = f"********CLIENTES {inputclientes} ********PEDIDO {inputpedido} ********ITENS {inputitens}"

    return HttpResponse(prodfinal)
    
    return HttpResponse(f"===CLIENTES ({nomecliente}) ===PEDIDOS (fetchall/5+1, {reservmesa}) ===ITENS ({quantitens} registros / 1: (fetchall/5+1, {produtos[0]}, {listqtt[0]}, select where checagem de nome [2o valor], {listqtt[0]} * Val. unit.))")


