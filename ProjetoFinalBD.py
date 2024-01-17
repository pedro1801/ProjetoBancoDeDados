import psycopg2
from itertools import groupby
import tkinter as tk
from tkinter import messagebox

# Função para conectar ao banco de dados
def connect():
    try:
        connection = psycopg2.connect(
            user="postgres", #Usuário do seu PGADMIN
            password="postgres", #Senha do seu PGADMIN
            host="localhost",
            port="5432",
            database="ProjetoFinal"
        )
        return connection
    except (Exception, psycopg2.Error) as error:
        print("Erro ao conectar ao banco de dados:", error)

# Função para criar tabelas no banco de dados
def create_tables(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                telefone VARCHAR(15) NOT NULL,
                codigo VARCHAR(10) UNIQUE NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                codigo VARCHAR(10) UNIQUE NOT NULL,
                valor DECIMAL(10, 2) NOT NULL,
                quantidade_estoque INT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id SERIAL PRIMARY KEY,
                cliente_id INT REFERENCES clientes(id) NOT NULL,
                total DECIMAL(10, 2) NOT NULL,
                forma_pagamento VARCHAR(20) NOT NULL,
                data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_venda (
                id SERIAL PRIMARY KEY,
                venda_id INT REFERENCES vendas(id) NOT NULL,
                produto_id INT REFERENCES produtos(id) NOT NULL,
                quantidade INT NOT NULL
            )
        """)
        connection.commit()
        cursor.close()
    except (Exception, psycopg2.Error) as error:
        print("Erro ao criar tabelas:", error)

# Função para cadastrar um cliente
def cadastrar_cliente(connection, nome, telefone, codigo):
    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO clientes (nome, telefone, codigo) VALUES (%s, %s, %s)", (nome, telefone, codigo))
        connection.commit()
        cursor.close()
        messagebox.showinfo("Popup", "Cliente cadastrado com sucesso!")
    except (Exception, psycopg2.Error) as error:
        messagebox.showinfo("Popup","Erro ao cadastrar cliente:")

# Função para cadastrar um produto
def cadastrar_produto(connection, nome, codigo, valor, quantidade_estoque):
    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO produtos (nome, codigo, valor, quantidade_estoque) VALUES (%s, %s, %s, %s)",
                       (nome, codigo, valor, quantidade_estoque))
        connection.commit()
        cursor.close()
        messagebox.showinfo("Popup", "Produto cadastrado com sucesso!")
    except (Exception, psycopg2.Error) as error:
        messagebox.showinfo("Popup","Erro ao cadastrar Produto:")

# Função para cadastrar uma venda
def cadastrar_venda(connection, cliente_id, total, forma_pagamento, itens):
    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO vendas (cliente_id, total, forma_pagamento) VALUES (%s, %s, %s) RETURNING id",
                       (cliente_id, total, forma_pagamento))
        venda_id = cursor.fetchone()[0]
        for item in itens:
            cursor.execute("INSERT INTO itens_venda (venda_id, produto_id, quantidade) VALUES (%s, %s, %s)",
                           (venda_id, item['produto_id'], item['quantidade']))
            # Atualiza o estoque
            cursor.execute("UPDATE produtos SET quantidade_estoque = quantidade_estoque - %s WHERE id = %s",
                           (item['quantidade'], item['produto_id']))
        connection.commit()
        cursor.close()
        print("Venda cadastrada com sucesso!")
    except (Exception, psycopg2.Error) as error:
        print("Erro ao cadastrar venda:", error)

# Função para buscar informações de um cliente
def buscar_cliente(connection, codigo):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM clientes WHERE codigo = %s", (codigo,))
        cliente = cursor.fetchone()
        cursor.close()
        return cliente
    except (Exception, psycopg2.Error) as error:
        print("Erro ao buscar cliente:", error)

# Função para exibir todos os clientes cadastrados
def exibir_clientes(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM clientes")
        clientes = cursor.fetchall()
        cursor.close()
        for cliente in clientes:
            print("ID:", cliente[0])
            print("Nome:", cliente[1])
            print("Telefone:", cliente[2])
            print("Código:", cliente[3])
            print("-----")
    except (Exception, psycopg2.Error) as error:
        print("Erro ao exibir clientes:", error)

# Função para exibir o total de vendas do empreendimento
def exibir_total_vendas(connection):
    try:
        cunter = 0
        vendas = []
        valorGeral = 0
        id_venda = []
        venda_id = []
        produto_id = []
        qtd_vendida = []
        Nome_Produto = []
        valor_Produto = []
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM vendas")
        total_vendas = cursor.fetchall()
        for total_venda in total_vendas:
            vendas.append(total_venda[0])
        for i in range(len(vendas)):
            cursor.execute("SELECT * FROM itens_venda WHERE venda_id = %s", (vendas[i],))
            total_vendas = cursor.fetchall()
            for toltal_venda in total_vendas:
                id_venda.append(toltal_venda[0])
                venda_id.append(toltal_venda[1])
                produto_id.append(toltal_venda[2])
                qtd_vendida.append(toltal_venda[3])
        for i in range(len(produto_id)):
            cursor.execute("SELECT * FROM produtos WHERE codigo = %s", (str(produto_id[i]),))
            produtos = cursor.fetchall()
            for produto in produtos:
                Nome_Produto.append(produto[1])
                valor_Produto.append(float(produto[3]))
        cursor.close()
        venda_id = [list(g) for k, g in groupby(venda_id)]
        for i in range(len(venda_id)):
            valortoal = 0
            print("-----------------------------------")
            print("Codigo_Venda:",venda_id[i][0])
            for j in range(len(venda_id[i])):
                print("Nome_Produto:",Nome_Produto[cunter])
                print("qtd_vendida:",qtd_vendida[cunter])
                print("valor_Produto:",valor_Produto[cunter])
                valortoal = qtd_vendida[cunter]*valor_Produto[cunter]+valortoal
                cunter+=1
            valorGeral = valorGeral+valortoal
            print("Valor Total Da Venda:",valortoal)
            print("-----------------------------------")
        print("Valor De Todas as compras:",valorGeral)
    except (Exception, psycopg2.Error) as error:
        print("Erro ao exibir total de vendas:", error)

# Função para exibir o total de vendas por cliente
def exibir_total_vendas_cliente(connection, cliente_id):
    try:
        cunter = 0
        valorGeral = 0
        vendas = []
        id_venda = []
        venda_id = []
        produto_id = []
        qtd_vendida = []
        Nome_Produto = []
        valor_Produto = []
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM vendas WHERE cliente_id = %s", (cliente_id,))
        total_vendas = cursor.fetchall()
        for toltal_venda in total_vendas:
            vendas.append(toltal_venda[0])
        for i in range(len(vendas)):
            cursor.execute("SELECT * FROM itens_venda WHERE venda_id = %s", (vendas[i],))
            total_vendas = cursor.fetchall()
            for toltal_venda in total_vendas:
                id_venda.append(toltal_venda[0])
                venda_id.append(toltal_venda[1])
                produto_id.append(toltal_venda[2])
                qtd_vendida.append(toltal_venda[3])
        for i in range(len(produto_id)):
            cursor.execute("SELECT * FROM produtos WHERE codigo = %s", (str(produto_id[i]),))
            produtos = cursor.fetchall()
            for produto in produtos:
                Nome_Produto.append(produto[1])
                valor_Produto.append(float(produto[3]))
        cursor.close()
        venda_id = [list(g) for k, g in groupby(venda_id)]

        for i in range(len(venda_id)):
            valortoal = 0
            print("-----------------------------------")
            print("Codigo_Venda:",venda_id[i][0])
            for j in range(len(venda_id[i])):
                print("Nome_Produto:",Nome_Produto[cunter])
                print("qtd_vendida:",qtd_vendida[cunter])
                print("valor_Produto:",valor_Produto[cunter])
                valortoal = qtd_vendida[cunter]*valor_Produto[cunter]+valortoal
                cunter+=1
            valorGeral = valorGeral+valortoal
            print("Valor Total Da Venda:",valortoal)
            print("-----------------------------------")
        print("Valor De Todas as compras:",valorGeral)
    except (Exception, psycopg2.Error) as error:
        print("Erro ao exibir total de vendas do cliente:", error)

# Função principal
def main(opcao):
    connection = connect()
    create_tables(connection)

    if opcao == "1":
        nome = Nome_cliente
        telefone = Telefone_Cliente
        codigo = Codigo_Cliente
        cadastrar_cliente(connection, nome, telefone, codigo)

    elif opcao == "2":
        nome_produto = Nome_Produto
        codigo_produto = Codigo_Produto
        valor_produto = Valor_Produto
        quantidade_estoque = Quantidade_Produto
        cadastrar_produto(connection, nome_produto, codigo_produto, valor_produto, quantidade_estoque)

    elif opcao == "3":
        codigo_cliente = input("Código do cliente: ")
        cliente = buscar_cliente(connection, codigo_cliente)

        if cliente:
            total_venda = 0
            itens_venda = []

            while True:
                codigo_produto = input("Código do produto (0 para finalizar): ")

                if codigo_produto == "0":
                    break

                quantidade = int(input("Quantidade: "))
                itens_venda.append({'produto_id': codigo_produto, 'quantidade': quantidade})
                # Calcula o total da venda
                cursor = connection.cursor()
                cursor.execute("SELECT valor FROM produtos WHERE codigo = %s", (codigo_produto,))
                valor_produto = cursor.fetchone()[0]
                total_venda += valor_produto * quantidade
                cursor.close()

            forma_pagamento = input("Forma de pagamento (à vista/credito): ")
            cadastrar_venda(connection, cliente[0], total_venda, forma_pagamento, itens_venda)

        else:
            print("Cliente não encontrado.")

    elif opcao == "4":
        codigo_produto = input("Código do produto: ")
        Irpara_Estoque = int(input("Quantidade de Itens:"))
        cursor = connection.cursor()
        cursor.execute("UPDATE produtos SET quantidade_estoque = quantidade_estoque + %s WHERE codigo = %s", (Irpara_Estoque, codigo_produto))
        connection.commit()            
        cursor.close()
    elif opcao == "5":
        codigo_cliente = input("Código do cliente: ")
        cliente = buscar_cliente(connection, codigo_cliente)
        if cliente:
            print("\nInformações do cliente:")
            print("Nome:", cliente[1])
            print("Telefone:", cliente[2])
            print("Código:", cliente[3])

            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM vendas WHERE cliente_id = %s", (cliente[0],))
            total_vendas = cursor.fetchone()[0]
            cursor.close()

            print("Total de compras realizadas no estabelecimento:", total_vendas)

        else:
            print("Cliente não encontrado.")

    elif opcao == "6":
        exibir_clientes(connection)

    elif opcao == "7":
        exibir_total_vendas(connection)

    elif opcao == "8":
        codigo_cliente = input("Código do cliente: ")
        cliente = buscar_cliente(connection, codigo_cliente)

        if cliente:
            exibir_total_vendas_cliente(connection, cliente[0])
        else:
            print("Cliente não encontrado.")

    connection.close()

def centralizar_janela(janela):
    largura_janela = 400
    altura_janela = 600

    # Obtenha as dimensões da tela
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()

    # Calcule as coordenadas x e y para centralizar a janela
    x = (largura_tela - largura_janela) // 2
    y = (altura_tela - altura_janela) // 2

    # Defina a geometria da janela para as coordenadas calculadas
    janela.geometry(f"{largura_janela}x{altura_janela}+{x}+{y}")

def Insere_Clientes():
    btnClientes.config(state="disabled")

    def fechar_janela():
        segunda_janela.destroy()
        btnClientes.config(state="active")
    def Insere():
        global Nome_cliente,Codigo_Cliente,Telefone_Cliente,Controle
        fechar = 1
        Nome_cliente = Nome.get()
        Codigo_Cliente = Codigo.get()
        Telefone_Cliente = Telefone.get()
        if Nome_cliente == "" or Codigo_Cliente == "" or Telefone_Cliente == "":
            fechar = 0
            messagebox.showinfo("Popup", "Faltou Informar alguma informação")
            segunda_janela.lift()
        if fechar == 1:
            btnClientes.config(state="active")
            segunda_janela.destroy()
            Controle = "1"
            main(Controle)
    segunda_janela = tk.Toplevel(janela)
    segunda_janela.title("Inserir Clientes")
    segunda_janela.protocol("WM_DELETE_WINDOW", fechar_janela)
    centralizar_janela(segunda_janela)
    Nome_label = tk.Label(segunda_janela, text="Digite o nome do cliente:")
    Nome_label.place(x=10,y=10)
    Nome = tk.Entry(segunda_janela,width=63)
    Nome.place(x=10,y=30)
    Codigo_label = tk.Label(segunda_janela, text="Digite o Codigo do cliente:")
    Codigo_label.place(x=10,y=50)
    Codigo = tk.Entry(segunda_janela,width=63)
    Codigo.place(x=10,y=70)
    Telefone_label = tk.Label(segunda_janela, text="Digite o Telefone do cliente:")
    Telefone_label.place(x=10,y=90)
    Telefone = tk.Entry(segunda_janela,width=63)
    Telefone.place(x=10,y=110)
    botao = tk.Button(segunda_janela, text="Inserir",command=Insere,height=2,width=10,bd=1,relief="solid")
    botao.place(x=160,y=150)

def Insere_Produtos():
    btnClientes.config(state="disabled")
    def fechar_janela():
        Terceira_janela.destroy()
        btnClientes.config(state="active")
    def Insere():
        global Nome_Produto,Codigo_Produto,Valor_Produto,Quantidade_Produto,Controle
        fechar = 1
        Nome_Produto = Nome.get()
        Codigo_Produto = Codigo.get()
        Valor_Produto = float(Valor_Produtos.get())
        Quantidade_Produto = int(qtd_Produtos.get())
        if Nome_Produto == "" or Codigo_Produto == "" or Valor_Produto == ""or Quantidade_Produto == "":
            fechar = 0
            messagebox.showinfo("Popup", "Faltou Informar alguma informação")
            Terceira_janela.lift()
        if fechar == 1:
            btnClientes.config(state="active")
            Terceira_janela.destroy()
            Controle = "2"
            main(Controle)
    Terceira_janela = tk.Toplevel(janela)
    Terceira_janela.title("Inserir Produtos")
    Terceira_janela.protocol("WM_DELETE_WINDOW", fechar_janela)
    centralizar_janela(Terceira_janela)
    Nome_label = tk.Label(Terceira_janela, text="Digite o nome do produto:")
    Nome_label.place(x=10,y=10)
    Nome = tk.Entry(Terceira_janela,width=63)
    Nome.place(x=10,y=30)
    Codigo_label = tk.Label(Terceira_janela, text="Digite o Codigo do produto:")
    Codigo_label.place(x=10,y=50)
    Codigo = tk.Entry(Terceira_janela,width=63)
    Codigo.place(x=10,y=70)
    Valor_label = tk.Label(Terceira_janela, text="Digite o Valor do produto:")
    Valor_label.place(x=10,y=90)
    Valor_Produtos = tk.Entry(Terceira_janela,width=63)
    Valor_Produtos.place(x=10,y=110)
    qtd_label = tk.Label(Terceira_janela, text="Digite a Quantidade do produto:")
    qtd_label.place(x=10,y=130)
    qtd_Produtos = tk.Entry(Terceira_janela,width=63)
    qtd_Produtos.place(x=10,y=150)
    botao = tk.Button(Terceira_janela, text="Inserir",command=Insere,height=2,width=10,bd=1,relief="solid")
    botao.place(x=160,y=180)

# Crie uma instância da classe Tk, que representa a janela principal
janela = tk.Tk()
janela.title("Projeto Final Banco De Dados")
janela.state('zoomed')
janela.config(bg="#808080")
# Crie um frame para a barra de aplicativo
app_bar = tk.Frame(janela, bg="#b4b4b4",height=50)
app_bar.pack(side="top", fill="x")

# Adicione um botão de saída à barra de aplicativo
#sair_button = tk.Button(app_bar, text="Sair", command=sair, bg="red", fg="white")
#sair_button.pack(side="right", padx=10)

btnClientes = tk.Button(app_bar, text="Clientes",command=Insere_Clientes,height=2,width=10,bd=1,relief="solid")
btnClientes.place(x=10,y=5)

btnProdutos = tk.Button(app_bar, text="Produtos",command=Insere_Produtos,height=2,width=10,bd=1,relief="solid")
btnProdutos.place(x=100,y=5)
# Inicie o loop principal da interface gráfica
janela.mainloop()
