from flask import Flask, jsonify, request, redirect, url_for, render_template, session, flash 
import mysql.connector, os
from dotenv import load_dotenv
from datetime import datetime

app = Flask(__name__)

app.secret_key = "chave-secreta-arapua-hoteis"

# Carrega as credenciais antes de montar a configuração do banco.
load_dotenv("env")

# ==========================================================ws
# CONFIGURAÇÃO DO BANCO DE DADOS
# ==========================================================

db_config = {
    "host":  os.getenv('DB_HOST'),
    "port":  int(os.getenv('DB_PORT', '3306')),
    "user":   os.getenv('DB_USER'),
    "password":   os.getenv('DB_PASSWORD'),
    "database":   os.getenv('DB_NAME'),
    "auth_plugin": "mysql_native_password",
}


# ==========================================================
# CONEXÃO COM O BANCO
# ==========================================================
def conectar_banco():
    try:
        print("Tentando conectar ao MySQL...")

        conexao = mysql.connector.connect(**db_config)

        print("Conexão criada:", conexao)

        if conexao.is_connected():
            return conexao

        print("MySQL não está conectado.")
        return None

    except Exception as erro:
        return None

@app.route("/")
def inicio():

    if "usuario_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


#################### ROTA - LOGIN ####################

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()

        conexao = conectar_banco()

        if conexao is None:
            flash("Erro ao conectar ao banco de dados.", "danger")
            return redirect(url_for("login"))

        try:

            cursor = conexao.cursor(dictionary=True)

            sql = """
                SELECT
                    id_usuario,
                    nome,
                    email,
                    senha,
                    perfil,
                    id_hotel
                FROM usuarios
                WHERE email = %s
                AND senha = %s
            """

            cursor.execute(sql, (email, senha))

            usuario = cursor.fetchone()

            if usuario:

                session["usuario_id"] = usuario["id_usuario"]
                session["nome"] = usuario["nome"]
                session["email"] = usuario["email"]
                session["perfil"] = usuario["perfil"]
                session["id_hotel"] = usuario["id_hotel"]

                print("LOGIN REALIZADO:", usuario["nome"])

                return redirect(url_for("dashboard"))

            else:

                print("USUÁRIO NÃO ENCONTRADO")

                flash("E-mail ou senha incorretos.", "danger")

                return redirect(url_for("login"))

        except mysql.connector.Error as erro:

            print("ERRO NA CONSULTA DO LOGIN:")
            print(erro)

            flash("Erro ao consultar o banco de dados.", "danger")

            return redirect(url_for("login"))

        finally:

            if conexao:
                conexao.close()

    return render_template("login.html")



@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

################### CRUD - HOTEIS ############

@app.route("/hoteis", methods=["GET"])
def get_hoteis():

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                h.id_hotel,
                h.nome,
                h.cnpj,
                h.telefone,
                h.email,
                h.cep,
                h.rua,
                h.numero,
                h.bairro,
                h.cidade,
                h.estado,
                h.id_categoria,
                c.nome AS categoria,
                c.quantidade_estrelas,
                h.status,
                h.criado_em

            FROM hoteis h

            INNER JOIN categorias_hotel c
                ON h.id_categoria = c.id_categoria

            ORDER BY h.id_hotel DESC
        """)

        hoteis = cursor.fetchall()

        return jsonify(hoteis), 200

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/hoteis", methods=["POST"])
def post_hotel():

    dados = request.get_json()

    if not dados:
        return jsonify({
            "erro": "Nenhum dado foi enviado."
        }), 400

    nome = dados.get("nome")
    cnpj = dados.get("cnpj")
    telefone = dados.get("telefone")
    email = dados.get("email")
    cep = dados.get("cep")
    rua = dados.get("rua")
    numero = dados.get("numero")
    bairro = dados.get("bairro")
    cidade = dados.get("cidade")
    estado = dados.get("estado")
    id_categoria = dados.get("id_categoria")

    if not nome:
        return jsonify({
            "erro": "O nome do hotel é obrigatório."
        }), 400

    if not cnpj:
        return jsonify({
            "erro": "O CNPJ é obrigatório."
        }), 400

    if not id_categoria:
        return jsonify({
            "erro": "A categoria do hotel é obrigatória."
        }), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_hotel
            FROM hoteis
            WHERE cnpj = %s
        """, (cnpj,))

        if cursor.fetchone():

            return jsonify({
                "erro": "Já existe um hotel com este CNPJ."
            }), 409

        cursor.execute("""
            INSERT INTO hoteis
            (
            nome,cnpj,telefone,email,cep,rua,numero,bairro,cidade,estado,id_categoria
            )
            VALUES
            (
                %s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s
            )
        """, (
            nome,cnpj,telefone,email,cep,rua,numero,bairro,cidade,estado,id_categoria
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Hotel cadastrado com sucesso.",
            "id_hotel": cursor.lastrowid
        }), 201

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/hoteis/<int:id_hotel>", methods=["PUT"])
def put_hotel(id_hotel):

    dados = request.get_json()

    if not dados:
        return jsonify({
            "erro": "Nenhum dado foi enviado."
        }), 400

    nome = dados.get("nome")
    cnpj = dados.get("cnpj")
    telefone = dados.get("telefone")
    email = dados.get("email")
    cep = dados.get("cep")
    rua = dados.get("rua")
    numero = dados.get("numero")
    bairro = dados.get("bairro")
    cidade = dados.get("cidade")
    estado = dados.get("estado")
    id_categoria = dados.get("id_categoria")
    status = dados.get("status", "ATIVO")

    if not nome:
        return jsonify({
            "erro": "O nome do hotel é obrigatório."
        }), 400

    if not cnpj:
        return jsonify({
            "erro": "O CNPJ é obrigatório."
        }), 400

    if not id_categoria:
        return jsonify({
            "erro": "A categoria do hotel é obrigatória."
        }), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_hotel
            FROM hoteis
            WHERE id_hotel = %s
        """, (id_hotel,))

        if not cursor.fetchone():

            return jsonify({
                "erro": "Hotel não encontrado."
            }), 404


        cursor.execute("""
            SELECT id_hotel
            FROM hoteis
            WHERE cnpj = %s
            AND id_hotel <> %s
        """, (cnpj, id_hotel))

        if cursor.fetchone():

            return jsonify({
                "erro": "Este CNPJ já pertence a outro hotel."
            }), 409

        cursor.execute("""
            UPDATE hoteis
            SET
                nome = %s,
                cnpj = %s,
                telefone = %s,
                email = %s,
                cep = %s,
                rua = %s,
                numero = %s,
                bairro = %s,
                cidade = %s,
                estado = %s,
                id_categoria = %s,
                status = %s
            WHERE id_hotel = %s
        """, (
            nome,
            cnpj,
            telefone,
            email,
            cep,
            rua,
            numero,
            bairro,
            cidade,
            estado,
            id_categoria,
            status,
            id_hotel
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Hotel atualizado com sucesso."
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/hoteis/<int:id_hotel>", methods=["DELETE"])
def delete_hotel(id_hotel):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_hotel
            FROM hoteis
            WHERE id_hotel = %s
        """, (id_hotel,))

        if not cursor.fetchone():

            return jsonify({
                "erro": "Hotel não encontrado."
            }), 404


        cursor.execute("""
            SELECT COUNT(*)
            FROM quartos
            WHERE id_hotel = %s
        """, (id_hotel,))

        quantidade_quartos = cursor.fetchone()[0]

        if quantidade_quartos > 0:

            return jsonify({
                "erro": "Não é possível excluir o hotel porque existem quartos vinculados a ele."
            }), 409


        cursor.execute("""
            DELETE FROM hoteis
            WHERE id_hotel = %s
        """, (id_hotel,))

        conexao.commit()

        return jsonify({
            "mensagem": "Hotel excluído com sucesso."
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()       

################### CRUD - HOTEIS ############


################ CRUD - QUARTOS###################

@app.route("/quartos", methods=["GET"])
def get_quartos():

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                q.id_quarto,
                q.numero,
                q.andar,
                q.capacidade,
                q.status,

                q.id_categoria,
                cq.nome AS categoria,
                cq.valor_diaria,

                q.id_hotel,
                h.nome AS hotel

            FROM quartos q

            INNER JOIN categorias_quarto cq
                ON q.id_categoria = cq.id_categoria

            INNER JOIN hoteis h
                ON q.id_hotel = h.id_hotel

            ORDER BY q.id_hotel, q.andar, q.numero
        """)

        quartos = cursor.fetchall()

        return jsonify(quartos), 200

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/quartos", methods=["POST"])
def post_quarto():

    dados = request.get_json()

    if not dados:
        return jsonify({
            "erro": "Nenhum dado foi enviado."
        }), 400

    numero = dados.get("numero")
    andar = dados.get("andar")
    capacidade = dados.get("capacidade")
    status = dados.get("status", "LIVRE")
    id_categoria = dados.get("id_categoria")
    id_hotel = dados.get("id_hotel")

    if not numero:
        return jsonify({
            "erro": "O número do quarto é obrigatório."
        }), 400

    if andar is None:
        return jsonify({
            "erro": "O andar é obrigatório."
        }), 400

    if capacidade is None:
        return jsonify({
            "erro": "A capacidade é obrigatória."
        }), 400

    if not id_categoria:
        return jsonify({
            "erro": "A categoria do quarto é obrigatória."
        }), 400

    if not id_hotel:
        return jsonify({
            "erro": "O hotel é obrigatório."
        }), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_hotel
            FROM hoteis
            WHERE id_hotel = %s
        """, (id_hotel,))

        if not cursor.fetchone():

            return jsonify({
                "erro": "Hotel não encontrado."
            }), 404

        cursor.execute("""
            SELECT id_categoria
            FROM categorias_quarto
            WHERE id_categoria = %s
        """, (id_categoria,))

        if not cursor.fetchone():

            return jsonify({
                "erro": "Categoria de quarto não encontrada."
            }), 404


        cursor.execute("""
            SELECT id_quarto
            FROM quartos
            WHERE numero = %s
            AND id_hotel = %s
        """, (numero, id_hotel))

        if cursor.fetchone():

            return jsonify({
                "erro": "Já existe um quarto com este número neste hotel."
            }), 409

        cursor.execute("""
            INSERT INTO quartos
            (
                numero,
                andar,
                capacidade,
                status,
                id_categoria,
                id_hotel
            )
            VALUES
            (%s, %s, %s, %s, %s, %s)
        """, (
            numero,
            andar,
            capacidade,
            status,
            id_categoria,
            id_hotel
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Quarto cadastrado com sucesso.",
            "id_quarto": cursor.lastrowid
        }), 201

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/quartos/<int:id_quarto>", methods=["PUT"])
def put_quarto(id_quarto):

    dados = request.get_json()

    if not dados:
        return jsonify({
            "erro": "Nenhum dado foi enviado."
        }), 400

    numero = dados.get("numero")
    andar = dados.get("andar")
    capacidade = dados.get("capacidade")
    status = dados.get("status")
    id_categoria = dados.get("id_categoria")
    id_hotel = dados.get("id_hotel")

    if not numero:
        return jsonify({
            "erro": "O número do quarto é obrigatório."
        }), 400

    if andar is None:
        return jsonify({
            "erro": "O andar é obrigatório."
        }), 400

    if capacidade is None:
        return jsonify({
            "erro": "A capacidade é obrigatória."
        }), 400

    if not id_categoria or not id_hotel:
        return jsonify({
            "erro": "Categoria e hotel são obrigatórios."
        }), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_quarto
            FROM quartos
            WHERE id_quarto = %s
        """, (id_quarto,))

        if not cursor.fetchone():

            return jsonify({
                "erro": "Quarto não encontrado."
            }), 404

        cursor.execute("""
            SELECT id_quarto
            FROM quartos
            WHERE numero = %s
            AND id_hotel = %s
            AND id_quarto <> %s
        """, (
            numero,
            id_hotel,
            id_quarto
        ))

        if cursor.fetchone():

            return jsonify({
                "erro": "Já existe outro quarto com este número neste hotel."
            }), 409

        cursor.execute("""
            UPDATE quartos
            SET
                numero = %s,
                andar = %s,
                capacidade = %s,
                status = %s,
                id_categoria = %s,
                id_hotel = %s
            WHERE id_quarto = %s
        """, (
            numero,
            andar,
            capacidade,
            status,
            id_categoria,
            id_hotel,
            id_quarto
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Quarto atualizado com sucesso."
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/quartos/<int:id_quarto>", methods=["DELETE"])
def delete_quarto(id_quarto):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:


        cursor.execute("""
            SELECT id_quarto
            FROM quartos
            WHERE id_quarto = %s
        """, (id_quarto,))

        if not cursor.fetchone():

            return jsonify({
                "erro": "Quarto não encontrado."
            }), 404


        cursor.execute("""
            SELECT COUNT(*)
            FROM reservas
            WHERE id_quarto = %s
        """, (id_quarto,))

        quantidade_reservas = cursor.fetchone()[0]

        if quantidade_reservas > 0:

            return jsonify({
                "erro": "Não é possível excluir o quarto porque existem reservas vinculadas a ele."
            }), 409

        cursor.execute("""
            DELETE FROM quartos
            WHERE id_quarto = %s
        """, (id_quarto,))

        conexao.commit()

        return jsonify({
            "mensagem": "Quarto excluído com sucesso."
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

################ CRUD - QUARTOS###################


################ CRUD - HOSPEDES ##########

@app.route("/hospedes", methods=["GET"])
def get_hospedes():

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id_hospede,
                nome,
                cpf,
                telefone,
                email,
                data_nascimento,
                nacionalidade,
                criado_em
            FROM hospedes
            ORDER BY id_hospede DESC
        """)

        hospedes = cursor.fetchall()

        return jsonify(hospedes), 200

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/hospedes", methods=["POST"])
def post_hospede():

    dados = request.get_json()

    if not dados:
        return jsonify({
            "erro": "Nenhum dado foi enviado."
        }), 400

    nome = dados.get("nome")
    cpf = dados.get("cpf")
    telefone = dados.get("telefone")
    email = dados.get("email")
    data_nascimento = dados.get("data_nascimento")
    nacionalidade = dados.get("nacionalidade", "Brasileira")

    if not nome:
        return jsonify({
            "erro": "O nome do hóspede é obrigatório."
        }), 400

    if not cpf:
        return jsonify({
            "erro": "O CPF é obrigatório."
        }), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_hospede
            FROM hospedes
            WHERE cpf = %s
        """, (cpf,))

        if cursor.fetchone():

            return jsonify({
                "erro": "Já existe um hóspede cadastrado com este CPF."
            }), 409

        cursor.execute("""
            INSERT INTO hospedes
            (
                nome,
                cpf,
                telefone,
                email,
                data_nascimento,
                nacionalidade
            )
            VALUES
            (%s, %s, %s, %s, %s, %s)
        """, (
            nome,
            cpf,
            telefone,
            email,
            data_nascimento,
            nacionalidade
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Hóspede cadastrado com sucesso.",
            "id_hospede": cursor.lastrowid
        }), 201

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/hospedes/<int:id_hospede>", methods=["PUT"])
def put_hospede(id_hospede):

    dados = request.get_json()

    if not dados:
        return jsonify({
            "erro": "Nenhum dado foi enviado."
        }), 400

    nome = dados.get("nome")
    cpf = dados.get("cpf")
    telefone = dados.get("telefone")
    email = dados.get("email")
    data_nascimento = dados.get("data_nascimento")
    nacionalidade = dados.get("nacionalidade", "Brasileira")

    if not nome:
        return jsonify({
            "erro": "O nome do hóspede é obrigatório."
        }), 400

    if not cpf:
        return jsonify({
            "erro": "O CPF é obrigatório."
        }), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_hospede
            FROM hospedes
            WHERE id_hospede = %s
        """, (id_hospede,))

        if not cursor.fetchone():

            return jsonify({
                "erro": "Hóspede não encontrado."
            }), 404

        cursor.execute("""
            SELECT id_hospede
            FROM hospedes
            WHERE cpf = %s
            AND id_hospede <> %s
        """, (cpf, id_hospede))

        if cursor.fetchone():

            return jsonify({
                "erro": "Este CPF já pertence a outro hóspede."
            }), 409

        cursor.execute("""
            UPDATE hospedes
            SET
                nome = %s,
                cpf = %s,
                telefone = %s,
                email = %s,
                data_nascimento = %s,
                nacionalidade = %s
            WHERE id_hospede = %s
        """, (
            nome,
            cpf,
            telefone,
            email,
            data_nascimento,
            nacionalidade,
            id_hospede
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Hóspede atualizado com sucesso."
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/hospedes/<int:id_hospede>", methods=["DELETE"])
def delete_hospede(id_hospede):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_hospede
            FROM hospedes
            WHERE id_hospede = %s
        """, (id_hospede,))

        if not cursor.fetchone():

            return jsonify({
                "erro": "Hóspede não encontrado."
            }), 404


        cursor.execute("""
            SELECT COUNT(*)
            FROM reservas
            WHERE id_hospede = %s
        """, (id_hospede,))

        quantidade_reservas = cursor.fetchone()[0]

        if quantidade_reservas > 0:

            return jsonify({
                "erro": "Não é possível excluir o hóspede porque existem reservas vinculadas a ele."
            }), 409

        cursor.execute("""
            DELETE FROM hospedes
            WHERE id_hospede = %s
        """, (id_hospede,))

        conexao.commit()

        return jsonify({
            "mensagem": "Hóspede excluído com sucesso."
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

################ CRUD - HOSPEDES ##########

####### CRUD - RESERVAS ###########

@app.route("/reservas", methods=["GET"])
def get_reservas():

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                r.id_reserva,
                r.codigo_reserva,
                r.data_reserva,
                r.checkin_previsto,
                r.checkout_previsto,
                r.quantidade_hospedes,
                r.observacao,
                r.status,

                r.id_hospede,
                h.nome AS hospede,

                r.id_quarto,
                q.numero AS quarto,

                q.id_hotel,
                ht.nome AS hotel,

                r.id_usuario,
                u.nome AS usuario

            FROM reservas r

            INNER JOIN hospedes h
                ON r.id_hospede = h.id_hospede

            INNER JOIN quartos q
                ON r.id_quarto = q.id_quarto

            INNER JOIN hoteis ht
                ON q.id_hotel = ht.id_hotel

            LEFT JOIN usuarios u
                ON r.id_usuario = u.id_usuario

            ORDER BY r.id_reserva DESC
        """)

        reservas = cursor.fetchall()

        return jsonify(reservas), 200

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/reservas", methods=["POST"])
def post_reserva():

    dados = request.get_json()

    if not dados:
        return jsonify({
            "erro": "Nenhum dado foi enviado."
        }), 400

    codigo_reserva = dados.get("codigo_reserva")
    checkin_previsto = dados.get("checkin_previsto")
    checkout_previsto = dados.get("checkout_previsto")
    quantidade_hospedes = dados.get("quantidade_hospedes", 1)
    observacao = dados.get("observacao")
    status = dados.get("status", "PENDENTE")
    id_hospede = dados.get("id_hospede")
    id_quarto = dados.get("id_quarto")
    id_usuario = dados.get("id_usuario")

    if not codigo_reserva:
        return jsonify({
            "erro": "O código da reserva é obrigatório."
        }), 400

    if not checkin_previsto or not checkout_previsto:
        return jsonify({
            "erro": "As datas de check-in e check-out são obrigatórias."
        }), 400

    if not id_hospede:
        return jsonify({
            "erro": "O hóspede é obrigatório."
        }), 400

    if not id_quarto:
        return jsonify({
            "erro": "O quarto é obrigatório."
        }), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_reserva
            FROM reservas
            WHERE codigo_reserva = %s
        """, (codigo_reserva,))

        if cursor.fetchone():

            return jsonify({
                "erro": "Já existe uma reserva com este código."
            }), 409


        cursor.execute("""
            SELECT id_hospede
            FROM hospedes
            WHERE id_hospede = %s
        """, (id_hospede,))

        if not cursor.fetchone():

            return jsonify({
                "erro": "Hóspede não encontrado."
            }), 404


        cursor.execute("""
            SELECT
                id_quarto,
                capacidade,
                status
            FROM quartos
            WHERE id_quarto = %s
        """, (id_quarto,))

        quarto = cursor.fetchone()

        if not quarto:

            return jsonify({
                "erro": "Quarto não encontrado."
            }), 404


        if int(quantidade_hospedes) > quarto[1]:

            return jsonify({
                "erro": "A quantidade de hóspedes ultrapassa a capacidade do quarto."
            }), 400

        if quarto[2] == "MANUTENCAO":

            return jsonify({
                "erro": "Não é possível reservar um quarto em manutenção."
            }), 409


        if id_usuario:

            cursor.execute("""
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = %s
            """, (id_usuario,))

            if not cursor.fetchone():

                return jsonify({
                    "erro": "Usuário não encontrado."
                }), 404


        cursor.execute("""
            SELECT id_reserva
            FROM reservas
            WHERE id_quarto = %s
            AND status IN ('PENDENTE', 'CONFIRMADA')
            AND checkin_previsto < %s
            AND checkout_previsto > %s
        """, (
            id_quarto,
            checkout_previsto,
            checkin_previsto
        ))

        if cursor.fetchone():

            return jsonify({
                "erro": "O quarto já possui uma reserva para esse período."
            }), 409

        cursor.execute("""
            INSERT INTO reservas
            (
                codigo_reserva,
                checkin_previsto,
                checkout_previsto,
                quantidade_hospedes,
                observacao,
                status,
                id_hospede,
                id_quarto,
                id_usuario
            )
            VALUES
            (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """, (
            codigo_reserva,
            checkin_previsto,
            checkout_previsto,
            quantidade_hospedes,
            observacao,
            status,
            id_hospede,
            id_quarto,
            id_usuario
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Reserva cadastrada com sucesso.",
            "id_reserva": cursor.lastrowid
        }), 201

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/reservas/<int:id_reserva>", methods=["PUT"])
def put_reserva(id_reserva):

    dados = request.get_json()

    if not dados:
        return jsonify({
            "erro": "Nenhum dado foi enviado."
        }), 400

    checkin_previsto = dados.get("checkin_previsto")
    checkout_previsto = dados.get("checkout_previsto")
    quantidade_hospedes = dados.get("quantidade_hospedes", 1)
    observacao = dados.get("observacao")
    status = dados.get("status")
    id_hospede = dados.get("id_hospede")
    id_quarto = dados.get("id_quarto")
    id_usuario = dados.get("id_usuario")

    if not checkin_previsto or not checkout_previsto:
        return jsonify({
            "erro": "As datas são obrigatórias."
        }), 400

    if not id_hospede or not id_quarto:
        return jsonify({
            "erro": "Hóspede e quarto são obrigatórios."
        }), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_reserva
            FROM reservas
            WHERE id_reserva = %s
        """, (id_reserva,))

        if not cursor.fetchone():

            return jsonify({
                "erro": "Reserva não encontrada."
            }), 404

        cursor.execute("""
            SELECT id_hospede
            FROM hospedes
            WHERE id_hospede = %s
        """, (id_hospede,))

        if not cursor.fetchone():

            return jsonify({
                "erro": "Hóspede não encontrado."
            }), 404


        cursor.execute("""
            SELECT capacidade, status
            FROM quartos
            WHERE id_quarto = %s
        """, (id_quarto,))

        quarto = cursor.fetchone()

        if not quarto:

            return jsonify({
                "erro": "Quarto não encontrado."
            }), 404

        if int(quantidade_hospedes) > quarto[0]:

            return jsonify({
                "erro": "A quantidade de hóspedes ultrapassa a capacidade do quarto."
            }), 400

        if quarto[1] == "MANUTENCAO":

            return jsonify({
                "erro": "Não é possível reservar um quarto em manutenção."
            }), 409


        cursor.execute("""
            SELECT id_reserva
            FROM reservas
            WHERE id_quarto = %s
            AND id_reserva <> %s
            AND status IN ('PENDENTE', 'CONFIRMADA')
            AND checkin_previsto < %s
            AND checkout_previsto > %s
        """, (
            id_quarto,
            id_reserva,
            checkout_previsto,
            checkin_previsto
        ))

        if cursor.fetchone():

            return jsonify({
                "erro": "O quarto já possui uma reserva para esse período."
            }), 409

        if id_usuario:

            cursor.execute("""
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = %s
            """, (id_usuario,))

            if not cursor.fetchone():

                return jsonify({
                    "erro": "Usuário não encontrado."
                }), 404

        cursor.execute("""
            UPDATE reservas
            SET
                checkin_previsto = %s,
                checkout_previsto = %s,
                quantidade_hospedes = %s,
                observacao = %s,
                status = %s,
                id_hospede = %s,
                id_quarto = %s,
                id_usuario = %s
            WHERE id_reserva = %s
        """, (
            checkin_previsto,
            checkout_previsto,
            quantidade_hospedes,
            observacao,
            status,
            id_hospede,
            id_quarto,
            id_usuario,
            id_reserva
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Reserva atualizada com sucesso."
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/reservas/<int:id_reserva>", methods=["DELETE"])
def delete_reserva(id_reserva):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_reserva
            FROM reservas
            WHERE id_reserva = %s
        """, (id_reserva,))

        if not cursor.fetchone():

            return jsonify({
                "erro": "Reserva não encontrada."
            }), 404


        cursor.execute("""
            SELECT COUNT(*)
            FROM checkin
            WHERE id_reserva = %s
        """, (id_reserva,))

        quantidade_checkin = cursor.fetchone()[0]

        if quantidade_checkin > 0:

            return jsonify({
                "erro": "Não é possível excluir esta reserva porque existe um check-in vinculado."
            }), 409

        cursor.execute("""
            DELETE FROM reservas
            WHERE id_reserva = %s
        """, (id_reserva,))

        conexao.commit()

        return jsonify({
            "mensagem": "Reserva excluída com sucesso."
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

####### CRUD - RESERVAS ###########

######## CRUD - CHECK-IN  ###########
@app.route("/checkins", methods=["GET"])
def get_checkins():

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                c.id_checkin,
                c.data_checkin,
                c.observacao,

                c.id_reserva,
                r.codigo_reserva,
                r.checkin_previsto,
                r.checkout_previsto,
                r.status AS status_reserva,

                h.id_hospede,
                h.nome AS hospede,
                h.cpf,

                q.id_quarto,
                q.numero AS quarto,

                ht.id_hotel,
                ht.nome AS hotel,

                c.id_usuario,
                u.nome AS usuario

            FROM checkin c

            INNER JOIN reservas r
                ON c.id_reserva = r.id_reserva

            INNER JOIN hospedes h
                ON r.id_hospede = h.id_hospede

            INNER JOIN quartos q
                ON r.id_quarto = q.id_quarto

            INNER JOIN hoteis ht
                ON q.id_hotel = ht.id_hotel

            LEFT JOIN usuarios u
                ON c.id_usuario = u.id_usuario

            ORDER BY c.id_checkin DESC
        """)

        checkins = cursor.fetchall()

        return jsonify(checkins), 200

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/checkin", methods=["POST"])
def confirmar_checkin():

    if "usuario_id" not in session:
        return jsonify({
            "erro": "Usuário não está logado."
        }), 401

    conexao = None
    cursor = None

    try:
        dados = request.get_json(silent=True)

        if not dados:
            return jsonify({
                "erro": "Nenhum dado foi enviado."
            }), 400

        id_reserva = dados.get("id_reserva")
        observacao = dados.get("observacao")

        if not id_reserva:
            return jsonify({
                "erro": "A reserva é obrigatória."
            }), 400

        id_usuario = session.get("usuario_id")

        conexao = conectar_banco()

        if not conexao:
            return jsonify({
                "erro": "Erro ao conectar ao banco de dados."
            }), 500

        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                r.id_reserva,
                r.codigo_reserva,
                r.status,
                r.id_hospede,
                r.id_quarto
            FROM reservas r
            WHERE r.id_reserva = %s
        """, (id_reserva,))

        reserva = cursor.fetchone()

        if not reserva:
            return jsonify({
                "erro": "Reserva não encontrada."
            }), 404

        if reserva["status"] not in ("PENDENTE", "CONFIRMADA"):
            return jsonify({
                "erro": "Esta reserva não está disponível para check-in."
            }), 409

        cursor.execute("""
            SELECT
                id_checkin
            FROM checkin
            WHERE id_reserva = %s
        """, (id_reserva,))

        checkin_existente = cursor.fetchone()

        if checkin_existente:
            return jsonify({
                "erro": "Esta reserva já possui um check-in."
            }), 409

        cursor.execute("""
            SELECT
                id_usuario
            FROM usuarios
            WHERE id_usuario = %s
            AND status = 'ATIVO'
        """, (id_usuario,))

        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({
                "erro": "Usuário não encontrado ou está inativo."
            }), 404

        cursor.execute("""
            INSERT INTO checkin
            (
                data_checkin,
                observacao,
                id_reserva,
                id_usuario
            )
            VALUES
            (
                NOW(),
                %s,
                %s,
                %s
            )
        """, (
            observacao,
            id_reserva,
            id_usuario
        ))

        id_checkin = cursor.lastrowid

        cursor.execute("""
            UPDATE reservas
            SET status = 'CONFIRMADA'
            WHERE id_reserva = %s
        """, (id_reserva,))

        cursor.execute("""
            UPDATE quartos
            SET status = 'OCUPADO'
            WHERE id_quarto = %s
        """, (reserva["id_quarto"],))

        conexao.commit()

        return jsonify({
            "sucesso": True,
            "mensagem": "Check-in realizado com sucesso!",
            "id_checkin": id_checkin,
            "id_reserva": id_reserva
        }), 201

    except mysql.connector.Error as erro:

        if conexao:
            conexao.rollback()

        print(f"Erro MySQL no check-in: {erro}")

        return jsonify({
            "erro": f"Erro no banco de dados: {erro}"
        }), 500

    except Exception as erro:

        if conexao:
            conexao.rollback()

        print(f"Erro no check-in: {erro}")

        return jsonify({
            "erro": f"Erro ao realizar check-in: {erro}"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


@app.route("/checkins/<int:id_checkin>", methods=["PUT"])
def put_checkin(id_checkin):

    dados = request.get_json()

    if not dados:

        return jsonify({
            "erro": "Nenhum dado foi enviado."
        }), 400

    observacao = dados.get("observacao")
    id_usuario = dados.get("id_usuario")

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_checkin
            FROM checkin
            WHERE id_checkin = %s
        """, (id_checkin,))

        if not cursor.fetchone():

            return jsonify({
                "erro": "Check-in não encontrado."
            }), 404


        if id_usuario:

            cursor.execute("""
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = %s
                AND status = 'ATIVO'
            """, (id_usuario,))

            if not cursor.fetchone():

                return jsonify({
                    "erro": "Usuário não encontrado ou está inativo."
                }), 404

        cursor.execute("""
            UPDATE checkin
            SET
                observacao = %s,
                id_usuario = %s
            WHERE id_checkin = %s
        """, (
            observacao,
            id_usuario,
            id_checkin
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Check-in atualizado com sucesso."
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/checkins/<int:id_checkin>", methods=["DELETE"])
def delete_checkin(id_checkin):
    if "usuario_id" not in session:
        return jsonify({"erro": "Usuário não está logado."}), 401
    conexao = None
    cursor = None
    try:
        conexao = conectar_banco()
        if not conexao:
            return jsonify({"erro": "Erro ao conectar ao banco de dados."}), 500
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                c.id_checkin,
                c.id_reserva,
                r.id_quarto
            FROM checkin c
            INNER JOIN reservas r
                ON c.id_reserva = r.id_reserva
            WHERE c.id_checkin = %s
        """, (id_checkin,))
        checkin = cursor.fetchone()
        if not checkin:
            return jsonify({"erro": "Check-in não encontrado."}), 404
        cursor.execute("""
            SELECT id_checkout
            FROM checkout
            WHERE id_checkin = %s
        """, (id_checkin,))
        checkout = cursor.fetchone()
        if checkout:
            return jsonify({
                "erro": "Não é possível excluir este check-in porque existe um checkout vinculado."
            }), 409
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM consumo_servicos
            WHERE id_checkin = %s
        """, (id_checkin,))
        consumo = cursor.fetchone()
        if consumo and consumo["total"] > 0:
            return jsonify({
                "erro": "Não é possível excluir este check-in porque existem consumos vinculados a ele."
            }), 409
        cursor.execute("""
            DELETE FROM checkin
            WHERE id_checkin = %s
        """, (id_checkin,))
        if cursor.rowcount == 0:
            conexao.rollback()
            return jsonify({"erro": "Nenhum check-in foi excluído."}), 404
        cursor.execute("""
            UPDATE quartos
            SET status = 'LIVRE'
            WHERE id_quarto = %s
        """, (checkin["id_quarto"],))
        conexao.commit()
        return jsonify({
            "sucesso": True,
            "mensagem": "Check-in excluído com sucesso.",
            "id_checkin": id_checkin
        }), 200
    except mysql.connector.Error as erro:
        if conexao:
            conexao.rollback()
        print(f"Erro MySQL ao excluir check-in: {erro}")
        return jsonify({
            "sucesso": False,
            "erro": "Erro no banco de dados.",
            "detalhes": str(erro)
        }), 500
    except Exception as erro:
        if conexao:
            conexao.rollback()
        print(f"Erro ao excluir check-in: {erro}")
        return jsonify({
            "sucesso": False,
            "erro": "Erro interno ao excluir check-in.",
            "detalhes": str(erro)
        }), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
######## CRUD - CHECK-IN  ###########


############ CRUD - CHECKOUT ############

@app.route("/checkouts", methods=["GET"])
def get_checkouts():

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                co.id_checkout,
                co.data_checkout,
                co.valor_diarias,
                co.valor_servicos,
                co.descontos,
                co.valor_total,
                co.observacao,

                co.id_checkin,

                c.data_checkin,

                r.id_reserva,
                r.codigo_reserva,

                h.id_hospede,
                h.nome AS hospede,

                q.id_quarto,
                q.numero AS quarto,

                ht.id_hotel,
                ht.nome AS hotel,

                co.id_usuario,
                u.nome AS usuario

            FROM checkout co

            INNER JOIN checkin c
                ON co.id_checkin = c.id_checkin

            INNER JOIN reservas r
                ON c.id_reserva = r.id_reserva

            INNER JOIN hospedes h
                ON r.id_hospede = h.id_hospede

            INNER JOIN quartos q
                ON r.id_quarto = q.id_quarto

            INNER JOIN hoteis ht
                ON q.id_hotel = ht.id_hotel

            LEFT JOIN usuarios u
                ON co.id_usuario = u.id_usuario

            ORDER BY co.id_checkout DESC
        """)

        checkouts = cursor.fetchall()

        return jsonify(checkouts), 200

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/checkouts", methods=["POST"])
def post_checkout():

    dados = request.get_json()

    if not dados:
        return jsonify({
            "erro": "Nenhum dado foi enviado."
        }), 400

    id_checkin = dados.get("id_checkin")
    id_usuario = dados.get("id_usuario") or session.get("usuario_id")
    descontos = dados.get("descontos", 0)
    observacao = dados.get("observacao")

    if not id_checkin:
        return jsonify({
            "erro": "O check-in é obrigatório."
        }), 400

    try:
        descontos = float(descontos)
    except (TypeError, ValueError):
        return jsonify({
            "erro": "O desconto informado é inválido."
        }), 400

    if descontos < 0:
        return jsonify({
            "erro": "O desconto não pode ser negativo."
        }), 400

    conexao = conectar_banco()

    if not conexao:
        return jsonify({
            "erro": "Erro ao conectar ao banco de dados."
        }), 500

    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                c.id_checkin,
                c.data_checkin,
                c.id_reserva,
                r.checkin_previsto,
                r.checkout_previsto,
                r.id_quarto,
                r.status AS status_reserva,
                q.numero AS numero_quarto,
                q.id_categoria,
                cq.nome AS categoria,
                cq.valor_diaria,
                h.nome AS hospede
            FROM checkin c
            INNER JOIN reservas r
                ON c.id_reserva = r.id_reserva
            INNER JOIN quartos q
                ON r.id_quarto = q.id_quarto
            INNER JOIN categorias_quarto cq
                ON q.id_categoria = cq.id_categoria
            INNER JOIN hospedes h
                ON r.id_hospede = h.id_hospede
            WHERE c.id_checkin = %s
        """, (id_checkin,))

        checkin = cursor.fetchone()

        if not checkin:
            return jsonify({
                "erro": "Check-in não encontrado."
            }), 404

        cursor.execute("""
            SELECT id_checkout
            FROM checkout
            WHERE id_checkin = %s
        """, (id_checkin,))

        if cursor.fetchone():
            return jsonify({
                "erro": "Este check-in já possui um checkout."
            }), 409

        if checkin["status_reserva"] == "CANCELADA":
            return jsonify({
                "erro": "Não é possível realizar checkout de uma reserva cancelada."
            }), 409

        quantidade_diarias = (
            checkin["checkout_previsto"] -
            checkin["checkin_previsto"]
        ).days

        if quantidade_diarias <= 0:
            quantidade_diarias = 1

        valor_diaria = float(
            checkin["valor_diaria"] or 0
        )

        valor_diarias = (
            quantidade_diarias *
            valor_diaria
        )

        cursor.execute("""
            SELECT
                COALESCE(SUM(valor_total), 0) AS total_consumo
            FROM consumo_servicos
            WHERE id_checkin = %s
        """, (id_checkin,))

        resultado_consumo = cursor.fetchone()

        valor_servicos = float(
            resultado_consumo["total_consumo"] or 0
        )

        valor_hospedagem = (
            valor_diarias +
            valor_servicos
        )

        if descontos > valor_hospedagem:
            return jsonify({
                "erro": (
                    f"O desconto não pode ser maior que "
                    f"R$ {valor_hospedagem:.2f}."
                )
            }), 400

        valor_total = (
            valor_hospedagem -
            descontos
        )

        if id_usuario:

            cursor.execute("""
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = %s
                AND status = 'ATIVO'
            """, (id_usuario,))

            if not cursor.fetchone():
                return jsonify({
                    "erro": "Usuário não encontrado ou está inativo."
                }), 404

        cursor.execute("""
            INSERT INTO checkout
            (
                data_checkout,
                valor_diarias,
                valor_servicos,
                descontos,
                valor_total,
                observacao,
                id_checkin,
                id_usuario
            )
            VALUES
            (
                %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """, (
            datetime.now(),
            valor_diarias,
            valor_servicos,
            descontos,
            valor_total,
            observacao,
            id_checkin,
            id_usuario
        ))

        id_checkout = cursor.lastrowid

        cursor.execute("""
            UPDATE reservas
            SET status = 'FINALIZADA'
            WHERE id_reserva = %s
        """, (
            checkin["id_reserva"],
        ))

        cursor.execute("""
            UPDATE quartos
            SET status = 'LIVRE'
            WHERE id_quarto = %s
        """, (
            checkin["id_quarto"],
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Checkout realizado com sucesso.",
            "id_checkout": id_checkout,
            "hospede": checkin["hospede"],
            "quarto": checkin["numero_quarto"],
            "categoria": checkin["categoria"],
            "quantidade_diarias": quantidade_diarias,
            "valor_diaria": valor_diaria,
            "valor_diarias": valor_diarias,
            "valor_servicos": valor_servicos,
            "valor_hospedagem": valor_hospedagem,
            "descontos": descontos,
            "valor_total": valor_total
        }), 201

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    except Exception as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()


@app.route("/checkouts/<int:id_checkout>", methods=["PUT"])
def put_checkout(id_checkout):

    dados = request.get_json()

    if not dados:

        return jsonify({
            "erro": "Nenhum dado foi enviado."
        }), 400

    valor_diarias = dados.get("valor_diarias", 0)
    valor_servicos = dados.get("valor_servicos", 0)
    descontos = dados.get("descontos", 0)
    observacao = dados.get("observacao")
    id_usuario = dados.get("id_usuario")

    try:

        valor_diarias = float(valor_diarias)
        valor_servicos = float(valor_servicos)
        descontos = float(descontos)

    except (TypeError, ValueError):

        return jsonify({
            "erro": "Os valores financeiros são inválidos."
        }), 400

    if valor_diarias < 0 or valor_servicos < 0 or descontos < 0:

        return jsonify({
            "erro": "Os valores não podem ser negativos."
        }), 400

    valor_total = (
        valor_diarias
        + valor_servicos
        - descontos
    )

    if valor_total < 0:

        return jsonify({
            "erro": "O desconto não pode ser maior que o valor da hospedagem."
        }), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_checkout
            FROM checkout
            WHERE id_checkout = %s
        """, (id_checkout,))

        if not cursor.fetchone():

            return jsonify({
                "erro": "Checkout não encontrado."
            }), 404

        if id_usuario:

            cursor.execute("""
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = %s
                AND status = 'ATIVO'
            """, (id_usuario,))

            if not cursor.fetchone():

                return jsonify({
                    "erro": "Usuário não encontrado ou está inativo."
                }), 404

        cursor.execute("""
            UPDATE checkout
            SET
                valor_diarias = %s,
                valor_servicos = %s,
                descontos = %s,
                valor_total = %s,
                observacao = %s,
                id_usuario = %s
            WHERE id_checkout = %s
        """, (
            valor_diarias,
            valor_servicos,
            descontos,
            valor_total,
            observacao,
            id_usuario,
            id_checkout
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Checkout atualizado com sucesso.",
            "valor_total": valor_total
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/checkouts/<int:id_checkout>", methods=["DELETE"])
def delete_checkout(id_checkout):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT
                id_checkout,
                id_checkin
            FROM checkout
            WHERE id_checkout = %s
        """, (id_checkout,))

        checkout = cursor.fetchone()

        if not checkout:

            return jsonify({
                "erro": "Checkout não encontrado."
            }), 404

        id_checkin = checkout[1]

        cursor.execute("""
            SELECT COUNT(*)
            FROM pagamentos
            WHERE id_checkout = %s
        """, (id_checkout,))

        quantidade_pagamentos = cursor.fetchone()[0]

        if quantidade_pagamentos > 0:

            return jsonify({
                "erro": "Não é possível excluir o checkout porque existem pagamentos vinculados."
            }), 409

        cursor.execute("""
            SELECT
                c.id_reserva,
                r.id_quarto
            FROM checkin c

            INNER JOIN reservas r
                ON c.id_reserva = r.id_reserva

            WHERE c.id_checkin = %s
        """, (id_checkin,))

        dados_reserva = cursor.fetchone()

        cursor.execute("""
            DELETE FROM checkout
            WHERE id_checkout = %s
        """, (id_checkout,))

        if dados_reserva:

            id_reserva = dados_reserva[0]
            id_quarto = dados_reserva[1]

            cursor.execute("""
                UPDATE reservas
                SET status = 'CONFIRMADA'
                WHERE id_reserva = %s
            """, (id_reserva,))

            cursor.execute("""
                UPDATE quartos
                SET status = 'OCUPADO'
                WHERE id_quarto = %s
            """, (id_quarto,))

        conexao.commit()

        return jsonify({
            "mensagem": "Checkout excluído com sucesso."
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

############ CRUD - CHECKOUT ############

######## CRUD - SERVIÇOS ################

@app.route("/servicos", methods=["GET"])
def get_servicos():

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id_servico,
                nome,
                descricao,
                preco,
                status,
                criado_em
            FROM servicos
            ORDER BY id_servico DESC
        """)

        servicos = cursor.fetchall()

        return jsonify(servicos), 200

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/servicos", methods=["POST"])
def post_servico():

    try:
        dados = request.get_json(silent=True)

        if not dados:
            return jsonify({
                "erro": "Nenhum dado foi enviado."
            }), 400

        nome = dados.get("nome")
        descricao = dados.get("descricao")
        preco = dados.get("preco")
        status = dados.get("status", "ATIVO")

        if not nome:
            return jsonify({
                "erro": "O nome do serviço é obrigatório."
            }), 400

        if preco is None:
            return jsonify({
                "erro": "O preço do serviço é obrigatório."
            }), 400

        try:
            preco = float(preco)
        except (TypeError, ValueError):
            return jsonify({
                "erro": "O preço informado é inválido."
            }), 400

        if preco < 0:
            return jsonify({
                "erro": "O preço não pode ser negativo."
            }), 400

        if status not in ["ATIVO", "INATIVO"]:
            return jsonify({
                "erro": "Status inválido."
            }), 400

        conexao = conectar_banco()

        if not conexao:
            return jsonify({
                "erro": "Não foi possível conectar ao banco de dados."
            }), 500

        cursor = conexao.cursor()

        try:

            cursor.execute("""
                INSERT INTO servicos
                (
                    nome,
                    descricao,
                    preco,
                    status
                )
                VALUES
                (%s, %s, %s, %s)
            """, (
                nome,
                descricao,
                preco,
                status
            ))

            conexao.commit()

            return jsonify({
                "mensagem": "Serviço cadastrado com sucesso.",
                "id_servico": cursor.lastrowid,
                "nome": nome,
                "descricao": descricao,
                "preco": preco,
                "status": status
            }), 201

        except mysql.connector.Error as erro:

            conexao.rollback()

            print("ERRO MYSQL:", erro)

            return jsonify({
                "erro": "Erro ao cadastrar serviço.",
                "detalhes": str(erro)
            }), 500

        except Exception as erro:

            conexao.rollback()

            print("ERRO AO CADASTRAR SERVIÇO:", erro)

            return jsonify({
                "erro": "Erro interno ao cadastrar serviço.",
                "detalhes": str(erro)
            }), 500

        finally:

            cursor.close()
            conexao.close()

    except Exception as erro:

        print("ERRO GERAL /servicos:", erro)

        return jsonify({
            "erro": "Erro interno no servidor.",
            "detalhes": str(erro)
        }), 500

@app.route("/servicos/<int:id_servico>", methods=["PUT"])
def put_servico(id_servico):

    dados = request.get_json()

    if not dados:

        return jsonify({
            "erro": "Nenhum dado foi enviado."
        }), 400

    nome = dados.get("nome")
    descricao = dados.get("descricao")
    preco = dados.get("preco")
    status = dados.get("status")

    if not nome:

        return jsonify({
            "erro": "O nome do serviço é obrigatório."
        }), 400

    if preco is None:

        return jsonify({
            "erro": "O preço do serviço é obrigatório."
        }), 400

    try:

        preco = float(preco)

    except (TypeError, ValueError):

        return jsonify({
            "erro": "O preço informado é inválido."
        }), 400

    if preco < 0:

        return jsonify({
            "erro": "O preço não pode ser negativo."
        }), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_servico
            FROM servicos
            WHERE id_servico = %s
        """, (id_servico,))

        if not cursor.fetchone():

            return jsonify({
                "erro": "Serviço não encontrado."
            }), 404

        cursor.execute("""
            UPDATE servicos
            SET
                nome = %s,
                descricao = %s,
                preco = %s,
                status = %s
            WHERE id_servico = %s
        """, (
            nome,
            descricao,
            preco,
            status,
            id_servico
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Serviço atualizado com sucesso."
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/servicos/<int:id_servico>", methods=["DELETE"])
def delete_servico(id_servico):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_servico
            FROM servicos
            WHERE id_servico = %s
        """, (id_servico,))

        if not cursor.fetchone():

            return jsonify({
                "erro": "Serviço não encontrado."
            }), 404

        cursor.execute("""
            SELECT COUNT(*)
            FROM consumo_servicos
            WHERE id_servico = %s
        """, (id_servico,))

        quantidade_consumos = cursor.fetchone()[0]

        if quantidade_consumos > 0:

            return jsonify({
                "erro": "Não é possível excluir este serviço porque existem consumos vinculados a ele."
            }), 409

        cursor.execute("""
            DELETE FROM servicos
            WHERE id_servico = %s
        """, (id_servico,))

        conexao.commit()

        return jsonify({
            "mensagem": "Serviço excluído com sucesso."
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

######## CRUD - SERVIÇOS ################


############# CRUD - CONSUMO DE SERVIÇOS #############

@app.route("/consumos", methods=["GET"])
def get_consumos():

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                cs.id_consumo,
                cs.quantidade,
                cs.valor_unitario,
                cs.valor_total,
                cs.data_consumo,
                cs.observacao,

                cs.id_servico,
                s.nome AS servico,

                cs.id_checkin,
                c.data_checkin,

                r.id_reserva,
                r.codigo_reserva,

                h.id_hospede,
                h.nome AS hospede,

                q.id_quarto,
                q.numero AS quarto,

                ht.id_hotel,
                ht.nome AS hotel

            FROM consumo_servicos cs

            INNER JOIN servicos s
                ON cs.id_servico = s.id_servico

            INNER JOIN checkin c
                ON cs.id_checkin = c.id_checkin

            INNER JOIN reservas r
                ON c.id_reserva = r.id_reserva

            INNER JOIN hospedes h
                ON r.id_hospede = h.id_hospede

            INNER JOIN quartos q
                ON r.id_quarto = q.id_quarto

            INNER JOIN hoteis ht
                ON q.id_hotel = ht.id_hotel

            ORDER BY cs.id_consumo DESC
        """)

        consumos = cursor.fetchall()

        return jsonify(consumos), 200

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/consumos", methods=["POST"])
def post_consumo():

    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({
            "erro": "Nenhum dado JSON foi enviado."
        }), 400

    quantidade = dados.get("quantidade", 1)
    id_servico = dados.get("id_servico")
    id_checkin = dados.get("id_checkin")
    observacao = dados.get("observacao")

    if not id_servico:
        return jsonify({
            "erro": "O serviço é obrigatório."
        }), 400

    if not id_checkin:
        return jsonify({
            "erro": "O check-in é obrigatório."
        }), 400

    try:
        quantidade = int(quantidade)
    except (TypeError, ValueError):
        return jsonify({
            "erro": "A quantidade informada é inválida."
        }), 400

    if quantidade <= 0:
        return jsonify({
            "erro": "A quantidade deve ser maior que zero."
        }), 400

    conexao = conectar_banco()

    if not conexao:
        return jsonify({
            "erro": "Erro ao conectar ao banco de dados."
        }), 500

    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT
                id_servico,
                preco,
                status
            FROM servicos
            WHERE id_servico = %s
        """, (id_servico,))

        servico = cursor.fetchone()

        if not servico:
            return jsonify({
                "erro": "Serviço não encontrado."
            }), 404

        valor_unitario = float(servico[1])
        status_servico = servico[2]

        if status_servico != "ATIVO":
            return jsonify({
                "erro": "Este serviço está inativo."
            }), 409

        cursor.execute("""
            SELECT
                c.id_checkin,
                r.status
            FROM checkin c
            INNER JOIN reservas r
                ON c.id_reserva = r.id_reserva
            WHERE c.id_checkin = %s
        """, (id_checkin,))

        checkin = cursor.fetchone()

        if not checkin:
            return jsonify({
                "erro": "Check-in não encontrado."
            }), 404

        status_reserva = checkin[1]

        if status_reserva == "FINALIZADA":
            return jsonify({
                "erro": "Não é possível lançar consumo em uma hospedagem finalizada."
            }), 409

        if status_reserva == "CANCELADA":
            return jsonify({
                "erro": "Não é possível lançar consumo em uma reserva cancelada."
            }), 409

        valor_total = quantidade * valor_unitario

        cursor.execute("""
            INSERT INTO consumo_servicos
            (
                quantidade,
                valor_unitario,
                valor_total,
                observacao,
                id_servico,
                id_checkin
            )
            VALUES
            (%s, %s, %s, %s, %s, %s)
        """, (
            quantidade,
            valor_unitario,
            valor_total,
            observacao,
            id_servico,
            id_checkin
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Consumo registrado com sucesso.",
            "id_consumo": cursor.lastrowid,
            "quantidade": quantidade,
            "id_servico": id_servico,
            "id_checkin": id_checkin,
            "valor_unitario": valor_unitario,
            "valor_total": valor_total
        }), 201

    except mysql.connector.Error as erro:

        conexao.rollback()

        print("ERRO MYSQL:", erro)

        return jsonify({
            "erro": "Erro no banco de dados.",
            "detalhes": str(erro)
        }), 500

    except Exception as erro:

        conexao.rollback()

        print("ERRO:", erro)

        return jsonify({
            "erro": "Erro interno ao registrar consumo.",
            "detalhes": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/consumos/<int:id_consumo>", methods=["PUT"])
def put_consumo(id_consumo):

    dados = request.get_json()

    if not dados:

        return jsonify({
            "erro": "Nenhum dado foi enviado."
        }), 400

    quantidade = dados.get("quantidade")
    id_servico = dados.get("id_servico")
    observacao = dados.get("observacao")

    if quantidade is None:

        return jsonify({
            "erro": "A quantidade é obrigatória."
        }), 400

    if not id_servico:

        return jsonify({
            "erro": "O serviço é obrigatório."
        }), 400

    try:

        quantidade = int(quantidade)

    except (TypeError, ValueError):

        return jsonify({
            "erro": "A quantidade informada é inválida."
        }), 400

    if quantidade <= 0:

        return jsonify({
            "erro": "A quantidade deve ser maior que zero."
        }), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_consumo
            FROM consumo_servicos
            WHERE id_consumo = %s
        """, (id_consumo,))

        if not cursor.fetchone():

            return jsonify({
                "erro": "Consumo não encontrado."
            }), 404


        cursor.execute("""
            SELECT
                preco,
                status
            FROM servicos
            WHERE id_servico = %s
        """, (id_servico,))

        servico = cursor.fetchone()

        if not servico:

            return jsonify({
                "erro": "Serviço não encontrado."
            }), 404

        if servico[1] != "ATIVO":

            return jsonify({
                "erro": "Este serviço está inativo."
            }), 409

        valor_unitario = float(servico[0])

        valor_total = quantidade * valor_unitario

        cursor.execute("""
            UPDATE consumo_servicos
            SET
                quantidade = %s,
                valor_unitario = %s,
                valor_total = %s,
                observacao = %s,
                id_servico = %s
            WHERE id_consumo = %s
        """, (
            quantidade,
            valor_unitario,
            valor_total,
            observacao,
            id_servico,
            id_consumo
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Consumo atualizado com sucesso.",
            "valor_total": valor_total
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/consumos/<int:id_consumo>", methods=["DELETE"])
def delete_consumo(id_consumo):
    if "usuario_id" not in session:
        return jsonify({"erro": "Usuário não está logado."}), 401
    conexao = None
    cursor = None
    try:
        conexao = conectar_banco()
        if not conexao:
            return jsonify({"erro": "Erro ao conectar ao banco de dados."}), 500
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT id_consumo, id_checkin
            FROM consumo_servicos
            WHERE id_consumo = %s
        """, (id_consumo,))
        consumo = cursor.fetchone()
        if not consumo:
            return jsonify({"erro": "Consumo não encontrado."}), 404
        id_checkin = consumo[1]
        cursor.execute("""
            SELECT id_checkout
            FROM checkout
            WHERE id_checkin = %s
        """, (id_checkin,))
        if cursor.fetchone():
            return jsonify({
                "erro": "Não é possível excluir o consumo porque o checkout desta hospedagem já foi realizado."
            }), 409
        cursor.execute("""
            DELETE FROM consumo_servicos
            WHERE id_consumo = %s
        """, (id_consumo,))
        conexao.commit()
        return jsonify({
            "mensagem": "Consumo excluído com sucesso."
        }), 200
    except mysql.connector.Error as erro:
        if conexao:
            conexao.rollback()
        print("ERRO MYSQL AO EXCLUIR CONSUMO:", erro)
        return jsonify({
            "erro": f"Erro no banco de dados: {erro}"
        }), 500
    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("ERRO AO EXCLUIR CONSUMO:", erro)
        return jsonify({
            "erro": f"Erro ao excluir consumo: {erro}"
        }), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
############# CRUD - CONSUMO DE SERVIÇOS #############


######### CRUD - PAGAMENTOS ###########

@app.route("/pagamentos", methods=["GET"])
def get_pagamentos():

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                p.id_pagamento,
                p.valor,
                p.forma_pagamento,
                p.status,
                p.data_pagamento,
                p.observacao,

                p.id_checkout,

                co.valor_total,

                ci.id_checkin,

                r.id_reserva,
                r.codigo_reserva,

                h.id_hospede,
                h.nome AS hospede

            FROM pagamentos p

            INNER JOIN checkout co
                ON p.id_checkout = co.id_checkout

            INNER JOIN checkin ci
                ON co.id_checkin = ci.id_checkin

            INNER JOIN reservas r
                ON ci.id_reserva = r.id_reserva

            INNER JOIN hospedes h
                ON r.id_hospede = h.id_hospede

            ORDER BY p.id_pagamento DESC
        """)

        pagamentos = cursor.fetchall()

        return jsonify(pagamentos), 200

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/pagamentos", methods=["POST"])
def post_pagamento():
    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Nenhum dado foi enviado."}), 400

    valor = dados.get("valor")
    forma_pagamento = dados.get("forma_pagamento")
    status = dados.get("status", "PENDENTE")
    observacao = dados.get("observacao")
    id_checkout = dados.get("id_checkout")

    if valor is None:
        return jsonify({"erro": "O valor do pagamento é obrigatório."}), 400

    if not forma_pagamento:
        return jsonify({"erro": "A forma de pagamento é obrigatória."}), 400

    if not id_checkout:
        return jsonify({"erro": "O checkout é obrigatório."}), 400

    try:
        valor = float(valor)
        id_checkout = int(id_checkout)
    except (TypeError, ValueError):
        return jsonify({"erro": "Valor ou checkout inválido."}), 400

    if valor <= 0:
        return jsonify({"erro": "O valor deve ser maior que zero."}), 400

    formas_validas = [
        "DINHEIRO",
        "PIX",
        "CARTAO_CREDITO",
        "CARTAO_DEBITO",
        "TRANSFERENCIA"
    ]

    if forma_pagamento not in formas_validas:
        return jsonify({"erro": "Forma de pagamento inválida."}), 400

    status_validos = [
        "PENDENTE",
        "PAGO",
        "CANCELADO"
    ]

    if status not in status_validos:
        return jsonify({"erro": "Status de pagamento inválido."}), 400

    conexao = conectar_banco()

    if not conexao:
        return jsonify({
            "erro": "Não foi possível conectar ao banco de dados."
        }), 500

    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                id_checkout,
                valor_total
            FROM checkout
            WHERE id_checkout = %s
        """, (id_checkout,))

        checkout = cursor.fetchone()

        if not checkout:
            return jsonify({
                "erro": "Checkout não encontrado."
            }), 404

        valor_checkout = float(checkout["valor_total"] or 0)

        cursor.execute("""
            SELECT
                COALESCE(SUM(valor), 0) AS total_pago
            FROM pagamentos
            WHERE id_checkout = %s
            AND status = 'PAGO'
        """, (id_checkout,))

        resultado = cursor.fetchone()

        valor_pago = float(resultado["total_pago"] or 0)

        valor_disponivel = max(valor_checkout - valor_pago, 0)

        if status == "PAGO" and valor > valor_disponivel + 0.01:
            return jsonify({
                "erro": "O valor informado é maior que o valor disponível para este checkout.",
                "valor_checkout": round(valor_checkout, 2),
                "valor_ja_pago": round(valor_pago, 2),
                "valor_disponivel": round(valor_disponivel, 2)
            }), 409

        if status == "PAGO":
            data_pagamento = datetime.now()
        else:
            data_pagamento = None

        cursor.execute("""
            INSERT INTO pagamentos
            (
                valor,
                forma_pagamento,
                status,
                data_pagamento,
                observacao,
                id_checkout
            )
            VALUES
            (%s, %s, %s, %s, %s, %s)
        """, (
            valor,
            forma_pagamento,
            status,
            data_pagamento,
            observacao,
            id_checkout
        ))

        id_pagamento = cursor.lastrowid

        conexao.commit()

        valor_restante = max(valor_disponivel - valor, 0)

        return jsonify({
            "mensagem": "Pagamento cadastrado com sucesso.",
            "id_pagamento": id_pagamento,
            "valor": round(valor, 2),
            "status": status,
            "data_pagamento": data_pagamento.strftime("%d/%m/%Y %H:%M:%S") if data_pagamento else None,
            "valor_checkout": round(valor_checkout, 2),
            "valor_ja_pago": round(valor_pago, 2),
            "valor_restante": round(valor_restante, 2)
        }), 201

    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"Erro ao cadastrar pagamento: {erro}")

        return jsonify({
            "erro": str(erro)
        }), 500

    except Exception as erro:
        conexao.rollback()
        print(f"Erro inesperado ao cadastrar pagamento: {erro}")

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:
        cursor.close()
        conexao.close()

@app.route("/pagamentos/<int:id_pagamento>", methods=["PUT"])
def put_pagamento(id_pagamento):

    dados = request.get_json()

    if not dados:

        return jsonify({
            "erro": "Nenhum dado foi enviado."
        }), 400

    valor = dados.get("valor")
    forma_pagamento = dados.get("forma_pagamento")
    status = dados.get("status")
    data_pagamento = dados.get("data_pagamento")
    observacao = dados.get("observacao")

    if valor is None:

        return jsonify({
            "erro": "O valor do pagamento é obrigatório."
        }), 400

    if not forma_pagamento:

        return jsonify({
            "erro": "A forma de pagamento é obrigatória."
        }), 400

    try:

        valor = float(valor)

    except (TypeError, ValueError):

        return jsonify({
            "erro": "O valor informado é inválido."
        }), 400

    if valor <= 0:

        return jsonify({
            "erro": "O valor deve ser maior que zero."
        }), 400

    formas_validas = [
        "DINHEIRO",
        "PIX",
        "CARTAO_CREDITO",
        "CARTAO_DEBITO"
    ]

    if forma_pagamento not in formas_validas:

        return jsonify({
            "erro": "Forma de pagamento inválida."
        }), 400

    status_validos = [
        "PENDENTE",
        "PAGO",
        "CANCELADO"
    ]

    if status not in status_validos:

        return jsonify({
            "erro": "Status de pagamento inválido."
        }), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT
                id_pagamento,
                id_checkout
            FROM pagamentos
            WHERE id_pagamento = %s
        """, (id_pagamento,))

        pagamento = cursor.fetchone()

        if not pagamento:

            return jsonify({
                "erro": "Pagamento não encontrado."
            }), 404

        id_checkout = pagamento[1]

        cursor.execute("""
            SELECT valor_total
            FROM checkout
            WHERE id_checkout = %s
        """, (id_checkout,))

        checkout = cursor.fetchone()

        if not checkout:

            return jsonify({
                "erro": "Checkout não encontrado."
            }), 404

        valor_checkout = float(checkout[0])

        cursor.execute("""
            SELECT
                COALESCE(SUM(valor), 0)
            FROM pagamentos
            WHERE id_checkout = %s
            AND status = 'PAGO'
            AND id_pagamento <> %s
        """, (
            id_checkout,
            id_pagamento
        ))

        outros_pagamentos = float(cursor.fetchone()[0])

        if status == "PAGO":

            if outros_pagamentos + valor > valor_checkout:

                return jsonify({
                    "erro": "O valor informado ultrapassa o valor restante do checkout.",
                    "valor_checkout": valor_checkout,
                    "valor_ja_pago": outros_pagamentos,
                    "valor_disponivel": valor_checkout - outros_pagamentos
                }), 409

        cursor.execute("""
            UPDATE pagamentos
            SET
                valor = %s,
                forma_pagamento = %s,
                status = %s,
                data_pagamento = %s,
                observacao = %s
            WHERE id_pagamento = %s
        """, (
            valor,
            forma_pagamento,
            status,
            data_pagamento,
            observacao,
            id_pagamento
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Pagamento atualizado com sucesso."
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/pagamentos/<int:id_pagamento>", methods=["DELETE"])
def delete_pagamento(id_pagamento):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_pagamento
            FROM pagamentos
            WHERE id_pagamento = %s
        """, (id_pagamento,))

        if not cursor.fetchone():

            return jsonify({
                "erro": "Pagamento não encontrado."
            }), 404

        cursor.execute("""
            DELETE FROM pagamentos
            WHERE id_pagamento = %s
        """, (id_pagamento,))

        conexao.commit()

        return jsonify({
            "mensagem": "Pagamento excluído com sucesso."
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

######### CRUD - PAGAMENTOS ###########

######## CRUD - CATEGORIAS DE HOTEL ############

@app.route("/categorias-hotel", methods=["GET"])
def get_categorias_hotel():

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                id_categoria,
                nome,
                descricao,
                quantidade_estrelas
            FROM categorias_hotel
            ORDER BY id_categoria DESC
        """)

        categorias = cursor.fetchall()

        return jsonify(categorias), 200

    except mysql.connector.Error as erro:
        return jsonify({"erro": str(erro)}), 500

    finally:
        cursor.close()
        conexao.close()

@app.route("/categorias-hotel", methods=["POST"])
def post_categoria_hotel():

    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Nenhum dado foi enviado."}), 400

    nome = dados.get("nome")
    descricao = dados.get("descricao")
    quantidade_estrelas = dados.get("quantidade_estrelas")

    if not nome:
        return jsonify({"erro": "O nome é obrigatório."}), 400

    if quantidade_estrelas is None:
        return jsonify({"erro": "A quantidade de estrelas é obrigatória."}), 400

    try:
        quantidade_estrelas = int(quantidade_estrelas)
    except (TypeError, ValueError):
        return jsonify({"erro": "Quantidade de estrelas inválida."}), 400

    if quantidade_estrelas < 1 or quantidade_estrelas > 5:
        return jsonify({
            "erro": "A quantidade de estrelas deve estar entre 1 e 5."
        }), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            INSERT INTO categorias_hotel
            (nome, descricao, quantidade_estrelas)
            VALUES (%s, %s, %s)
        """, (
            nome,
            descricao,
            quantidade_estrelas
        ))

        id_categoria = cursor.lastrowid

        conexao.commit()

        return jsonify({
            "mensagem": "Categoria de hotel cadastrada com sucesso.",
            "id_categoria": id_categoria
        }), 201

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({"erro": str(erro)}), 500

    finally:
        cursor.close()
        conexao.close()

@app.route("/categorias-hotel/<int:id_categoria>", methods=["PUT"])
def put_categoria_hotel(id_categoria):

    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Nenhum dado foi enviado."}), 400

    nome = dados.get("nome")
    descricao = dados.get("descricao")
    quantidade_estrelas = dados.get("quantidade_estrelas")

    if not nome:
        return jsonify({"erro": "O nome é obrigatório."}), 400

    try:
        quantidade_estrelas = int(quantidade_estrelas)
    except (TypeError, ValueError):
        return jsonify({"erro": "Quantidade de estrelas inválida."}), 400

    if quantidade_estrelas < 1 or quantidade_estrelas > 5:
        return jsonify({
            "erro": "A quantidade de estrelas deve estar entre 1 e 5."
        }), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_categoria
            FROM categorias_hotel
            WHERE id_categoria = %s
        """, (id_categoria,))

        if not cursor.fetchone():
            return jsonify({
                "erro": "Categoria de hotel não encontrada."
            }), 404

        cursor.execute("""
            UPDATE categorias_hotel
            SET
                nome = %s,
                descricao = %s,
                quantidade_estrelas = %s
            WHERE id_categoria = %s
        """, (
            nome,
            descricao,
            quantidade_estrelas,
            id_categoria
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Categoria de hotel atualizada com sucesso."
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({"erro": str(erro)}), 500

    finally:
        cursor.close()
        conexao.close()

@app.route("/categorias-hotel/<int:id_categoria>", methods=["DELETE"])
def delete_categoria_hotel(id_categoria):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_categoria
            FROM categorias_hotel
            WHERE id_categoria = %s
        """, (id_categoria,))

        if not cursor.fetchone():
            return jsonify({
                "erro": "Categoria de hotel não encontrada."
            }), 404

        cursor.execute("""
            SELECT COUNT(*)
            FROM hoteis
            WHERE id_categoria = %s
        """, (id_categoria,))

        quantidade = cursor.fetchone()[0]

        if quantidade > 0:
            return jsonify({
                "erro": "Não é possível excluir esta categoria porque existem hotéis vinculados a ela."
            }), 409

        cursor.execute("""
            DELETE FROM categorias_hotel
            WHERE id_categoria = %s
        """, (id_categoria,))

        conexao.commit()

        return jsonify({
            "mensagem": "Categoria de hotel excluída com sucesso."
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({"erro": str(erro)}), 500

    finally:
        cursor.close()
        conexao.close()

######## CRUD - CATEGORIAS DE HOTEL ############

######### CRUD - CATEGORIAS DE QUARTO ############

@app.route("/categorias-quarto", methods=["GET"])
def get_categorias_quarto():

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id_categoria,
                nome,
                descricao,
                valor_diaria,
                capacidade_padrao,
                status
            FROM categorias_quarto
            ORDER BY id_categoria DESC
        """)

        categorias = cursor.fetchall()

        return jsonify(categorias), 200

    except mysql.connector.Error as erro:
        return jsonify({"erro": str(erro)}), 500

    finally:
        cursor.close()
        conexao.close()

@app.route("/categorias-quarto", methods=["POST"])
def post_categoria_quarto():

    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Nenhum dado foi enviado."}), 400

    nome = dados.get("nome")
    descricao = dados.get("descricao")
    valor_diaria = dados.get("valor_diaria")
    capacidade_padrao = dados.get("capacidade_padrao")

    if not nome:
        return jsonify({"erro": "O nome é obrigatório."}), 400

    if valor_diaria is None:
        return jsonify({"erro": "O valor da diária é obrigatório."}), 400

    if capacidade_padrao is None:
        return jsonify({
            "erro": "A capacidade padrão é obrigatória."
        }), 400

    try:
        valor_diaria = float(valor_diaria)
        capacidade_padrao = int(capacidade_padrao)
    except (TypeError, ValueError):
        return jsonify({
            "erro": "Valor da diária ou capacidade inválida."
        }), 400

    if valor_diaria < 0:
        return jsonify({
            "erro": "O valor da diária não pode ser negativo."
        }), 400

    if capacidade_padrao <= 0:
        return jsonify({
            "erro": "A capacidade deve ser maior que zero."
        }), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            INSERT INTO categorias_quarto
            (
                nome,
                descricao,
                valor_diaria,
                capacidade_padrao
            )
            VALUES (%s, %s, %s, %s)
        """, (
            nome,
            descricao,
            valor_diaria,
            capacidade_padrao
        ))

        id_categoria = cursor.lastrowid

        conexao.commit()

        return jsonify({
            "mensagem": "Categoria de quarto cadastrada com sucesso.",
            "id_categoria": id_categoria
        }), 201

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({"erro": str(erro)}), 500

    finally:
        cursor.close()
        conexao.close()

@app.route("/categorias-quarto/<int:id_categoria>", methods=["PUT"])
def put_categoria_quarto(id_categoria):

    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Nenhum dado foi enviado."}), 400

    nome = dados.get("nome")
    descricao = dados.get("descricao")
    valor_diaria = dados.get("valor_diaria")
    capacidade_padrao = dados.get("capacidade_padrao")
    status = dados.get("status", "ATIVO")

    if not nome:
        return jsonify({"erro": "O nome é obrigatório."}), 400

    try:
        valor_diaria = float(valor_diaria)
        capacidade_padrao = int(capacidade_padrao)
    except (TypeError, ValueError):
        return jsonify({
            "erro": "Valor da diária ou capacidade inválida."
        }), 400

    if valor_diaria < 0 or capacidade_padrao <= 0:
        return jsonify({
            "erro": "Valores informados são inválidos."
        }), 400

    if status not in ["ATIVO", "INATIVO"]:
        return jsonify({
            "erro": "Status inválido."
        }), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_categoria
            FROM categorias_quarto
            WHERE id_categoria = %s
        """, (id_categoria,))

        if not cursor.fetchone():
            return jsonify({
                "erro": "Categoria de quarto não encontrada."
            }), 404

        cursor.execute("""
            UPDATE categorias_quarto
            SET
                nome = %s,
                descricao = %s,
                valor_diaria = %s,
                capacidade_padrao = %s,
                status = %s
            WHERE id_categoria = %s
        """, (
            nome,
            descricao,
            valor_diaria,
            capacidade_padrao,
            status,
            id_categoria
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Categoria de quarto atualizada com sucesso."
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({"erro": str(erro)}), 500

    finally:
        cursor.close()
        conexao.close()

@app.route("/categorias-quarto/<int:id_categoria>", methods=["DELETE"])
def delete_categoria_quarto(id_categoria):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_categoria
            FROM categorias_quarto
            WHERE id_categoria = %s
        """, (id_categoria,))

        if not cursor.fetchone():
            return jsonify({
                "erro": "Categoria de quarto não encontrada."
            }), 404

        cursor.execute("""
            SELECT COUNT(*)
            FROM quartos
            WHERE id_categoria = %s
        """, (id_categoria,))

        quantidade = cursor.fetchone()[0]

        if quantidade > 0:
            return jsonify({
                "erro": "Não é possível excluir esta categoria porque existem quartos vinculados a ela."
            }), 409

        cursor.execute("""
            DELETE FROM categorias_quarto
            WHERE id_categoria = %s
        """, (id_categoria,))

        conexao.commit()

        return jsonify({
            "mensagem": "Categoria de quarto excluída com sucesso."
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({"erro": str(erro)}), 500

    finally:
        cursor.close()
        conexao.close()

######### CRUD - CATEGORIAS DE QUARTO ############

######## CRUD - USUÁRIOS ###############
@app.route("/usuarios", methods=["GET"])
def get_usuarios():

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                u.id_usuario,
                u.nome,
                u.email,
                u.perfil,
                u.id_hotel,
                h.nome AS hotel,
                u.status,
                u.criado_em
            FROM usuarios u

            LEFT JOIN hoteis h
                ON u.id_hotel = h.id_hotel

            ORDER BY u.id_usuario DESC
        """)

        usuarios = cursor.fetchall()

        return jsonify(usuarios), 200

    except mysql.connector.Error as erro:
        return jsonify({"erro": str(erro)}), 500

    finally:
        cursor.close()
        conexao.close()

@app.route("/usuarios", methods=["POST"])
def post_usuario():

    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Nenhum dado foi enviado."}), 400

    nome = dados.get("nome")
    email = dados.get("email")
    senha = dados.get("senha")
    perfil = dados.get("perfil")
    id_hotel = dados.get("id_hotel")

    if not nome:
        return jsonify({"erro": "O nome é obrigatório."}), 400

    if not email:
        return jsonify({"erro": "O e-mail é obrigatório."}), 400

    if not senha:
        return jsonify({"erro": "A senha é obrigatória."}), 400

    if perfil not in ["ADMIN", "GERENTE", "RECEPCAO"]:
        return jsonify({
            "erro": "Perfil inválido."
        }), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            INSERT INTO usuarios
            (
                nome,
                email,
                senha,
                perfil,
                id_hotel
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            nome,
            email,
            senha,
            perfil,
            id_hotel
        ))

        id_usuario = cursor.lastrowid

        conexao.commit()

        return jsonify({
            "mensagem": "Usuário cadastrado com sucesso.",
            "id_usuario": id_usuario
        }), 201

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({"erro": str(erro)}), 500

    finally:
        cursor.close()
        conexao.close()

@app.route("/usuarios/<int:id_usuario>", methods=["PUT"])
def put_usuario(id_usuario):

    dados = request.get_json()

    if not dados:
        return jsonify({
            "erro": "Nenhum dado foi enviado."
        }), 400

    nome = dados.get("nome")
    email = dados.get("email")
    senha = dados.get("senha")
    perfil = dados.get("perfil")
    id_hotel = dados.get("id_hotel")

    if not nome:
        return jsonify({
            "erro": "O nome é obrigatório."
        }), 400

    if not email:
        return jsonify({
            "erro": "O e-mail é obrigatório."
        }), 400

    if not perfil:
        return jsonify({
            "erro": "O perfil é obrigatório."
        }), 400

    if perfil not in ["ADMIN", "GERENTE", "RECEPCAO"]:
        return jsonify({
            "erro": "Perfil inválido."
        }), 400

    conexao = conectar_banco()

    if conexao is None:
        return jsonify({
            "erro": "Não foi possível conectar ao banco de dados."
        }), 500

    cursor = conexao.cursor()

    try:

        # Verifica se o usuário existe
        cursor.execute("""
            SELECT id_usuario
            FROM usuarios
            WHERE id_usuario = %s
        """, (id_usuario,))

        if not cursor.fetchone():
            return jsonify({
                "erro": "Usuário não encontrado."
            }), 404

        # Verifica se o e-mail já pertence a outro usuário
        cursor.execute("""
            SELECT id_usuario
            FROM usuarios
            WHERE email = %s
            AND id_usuario <> %s
        """, (email, id_usuario))

        if cursor.fetchone():
            return jsonify({
                "erro": "Este e-mail já está cadastrado."
            }), 409

        # Se enviou senha, atualiza a senha
        if senha:

            cursor.execute("""
                UPDATE usuarios
                SET
                    nome = %s,
                    email = %s,
                    senha = %s,
                    perfil = %s,
                    id_hotel = %s
                WHERE id_usuario = %s
            """, (
                nome,
                email,
                senha,
                perfil,
                id_hotel,
                id_usuario
            ))

        else:

            cursor.execute("""
                UPDATE usuarios
                SET
                    nome = %s,
                    email = %s,
                    perfil = %s,
                    id_hotel = %s
                WHERE id_usuario = %s
            """, (
                nome,
                email,
                perfil,
                id_hotel,
                id_usuario
            ))

        conexao.commit()

        return jsonify({
            "mensagem": "Usuário atualizado com sucesso.",
            "id_usuario": id_usuario
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({
            "erro": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

@app.route("/usuarios/<int:id_usuario>", methods=["DELETE"])
def delete_usuario(id_usuario):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            SELECT id_usuario
            FROM usuarios
            WHERE id_usuario = %s
        """, (id_usuario,))

        if not cursor.fetchone():
            return jsonify({
                "erro": "Usuário não encontrado."
            }), 404

        cursor.execute("""
            DELETE FROM usuarios
            WHERE id_usuario = %s
        """, (id_usuario,))

        conexao.commit()

        return jsonify({
            "mensagem": "Usuário excluído com sucesso."
        }), 200

    except mysql.connector.Error as erro:

        conexao.rollback()

        return jsonify({"erro": str(erro)}), 500

    finally:
        cursor.close()
        conexao.close()
######## CRUD - USUÁRIOS ###############


# Rota Dashboard — Arapuã Hotéis
@app.route("/dashboard")
def dashboard():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexao = conectar_banco()

    if not conexao:
        return "Erro ao conectar ao banco de dados.", 500

    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM hoteis
            WHERE status = 'ATIVO'
        """)
        resultado = cursor.fetchone()
        total_hoteis = resultado["total"] if resultado else 0

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM quartos
            WHERE status <> 'MANUTENCAO'
        """)
        resultado = cursor.fetchone()
        total_quartos = resultado["total"] if resultado else 0

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM hospedes
        """)
        resultado = cursor.fetchone()
        total_hospedes = resultado["total"] if resultado else 0

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM reservas
        """)
        resultado = cursor.fetchone()
        total_reservas = resultado["total"] if resultado else 0

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM reservas
            WHERE status = 'PENDENTE'
        """)
        resultado = cursor.fetchone()
        reservas_pendentes = resultado["total"] if resultado else 0

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM reservas
            WHERE status = 'CONFIRMADA'
        """)
        resultado = cursor.fetchone()
        reservas_confirmadas = resultado["total"] if resultado else 0

        cursor.execute("""
            SELECT
                r.id_reserva,
                r.codigo_reserva,
                r.checkin_previsto,
                r.checkout_previsto,
                r.status,
                h.nome AS nome_hospede,
                q.numero AS numero_quarto,
                ht.nome AS nome_hotel
            FROM reservas r
            INNER JOIN hospedes h
                ON r.id_hospede = h.id_hospede
            INNER JOIN quartos q
                ON r.id_quarto = q.id_quarto
            INNER JOIN hoteis ht
                ON q.id_hotel = ht.id_hotel
            ORDER BY r.data_reserva DESC
            LIMIT 5
        """)

        reservas_recentes = cursor.fetchall()

        cursor.execute("""
            SELECT
                r.id_reserva,
                r.codigo_reserva,
                r.checkin_previsto,
                r.checkout_previsto,
                r.status,
                h.nome AS nome_hospede,
                q.numero AS numero_quarto,
                ht.nome AS nome_hotel
            FROM reservas r
            INNER JOIN hospedes h
                ON r.id_hospede = h.id_hospede
            INNER JOIN quartos q
                ON r.id_quarto = q.id_quarto
            INNER JOIN hoteis ht
                ON q.id_hotel = ht.id_hotel
            WHERE DATE(r.checkin_previsto)
                BETWEEN CURDATE()
                AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            ORDER BY r.checkin_previsto ASC
            LIMIT 7
        """)

        reservas_proximas_7_dias = cursor.fetchall()

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM checkin
            WHERE DATE(data_checkin) = CURDATE()
        """)

        resultado = cursor.fetchone()
        checkins_hoje = resultado["total"] if resultado else 0

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM checkout
            WHERE DATE(data_checkout) = CURDATE()
        """)

        resultado = cursor.fetchone()
        checkouts_hoje = resultado["total"] if resultado else 0

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM quartos
            WHERE status = 'OCUPADO'
        """)

        resultado = cursor.fetchone()
        quartos_ocupados = resultado["total"] if resultado else 0

        quartos_disponiveis = total_quartos - quartos_ocupados

        if quartos_disponiveis < 0:
            quartos_disponiveis = 0

        if total_quartos > 0:
            ocupacao = round(
                (quartos_ocupados / total_quartos) * 100
            )
        else:
            ocupacao = 0

        cursor.execute("""
            SELECT
                COALESCE(SUM(valor), 0) AS total
            FROM pagamentos
            WHERE status = 'PAGO'
            AND data_pagamento IS NOT NULL
            AND DATE(data_pagamento) = CURDATE()
        """)

        resultado = cursor.fetchone()

        faturamento_hoje = float(
            resultado["total"] or 0
        ) if resultado else 0.0

        cursor.execute("""
            SELECT
                COALESCE(SUM(valor), 0) AS total
            FROM pagamentos
            WHERE status = 'PAGO'
            AND data_pagamento IS NOT NULL
            AND DATE(data_pagamento)
                BETWEEN CURDATE()
                AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
        """)

        resultado = cursor.fetchone()

        faturamento_7_dias = float(
            resultado["total"] or 0
        ) if resultado else 0.0

        nome = session.get("nome", "Usuário")
        perfil = session.get("perfil", "Não informado")
        id_hotel = session.get("id_hotel")

        return render_template(
            "dashboard.html",
            nome=nome,
            perfil=perfil,
            id_hotel=id_hotel,
            total_hoteis=total_hoteis,
            total_quartos=total_quartos,
            total_hospedes=total_hospedes,
            total_reservas=total_reservas,
            reservas_pendentes=reservas_pendentes,
            reservas_confirmadas=reservas_confirmadas,
            reservas_recentes=reservas_recentes,
            reservas_proximas_7_dias=reservas_proximas_7_dias,
            checkins_hoje=checkins_hoje,
            checkouts_hoje=checkouts_hoje,
            quartos_ocupados=quartos_ocupados,
            quartos_disponiveis=quartos_disponiveis,
            ocupacao=ocupacao,
            faturamento_hoje=faturamento_hoje,
            faturamento_7_dias=faturamento_7_dias
        )

    except mysql.connector.Error as erro:

        print(f"Erro ao carregar dashboard: {erro}")

        return f"Erro ao carregar dashboard: {erro}", 500

    except Exception as erro:

        print(f"Erro inesperado no dashboard: {erro}")

        return f"Erro inesperado no dashboard: {erro}", 500

    finally:

        cursor.close()
        conexao.close()

###### ROTA HOTEL
@app.route("/pagina-hoteis")
def pagina_hoteis():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexao = conectar_banco()

    if not conexao:
        return "Erro ao conectar ao banco de dados."

    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                h.id_hotel,
                h.nome,
                h.cnpj,
                h.telefone,
                h.email,
                h.cep,
                h.rua,
                h.numero,
                h.bairro,
                h.cidade,
                h.estado,
                h.id_categoria,
                c.nome AS categoria,
                c.quantidade_estrelas,
                h.status,
                h.criado_em

            FROM hoteis h

            LEFT JOIN categorias_hotel c
                ON h.id_categoria = c.id_categoria

            ORDER BY h.nome ASC
        """)

        hoteis = cursor.fetchall()


        cursor.execute("""
            SELECT
                id_categoria,
                nome,
                quantidade_estrelas
            FROM categorias_hotel
            ORDER BY quantidade_estrelas ASC, nome ASC
        """)

        categorias = cursor.fetchall()


        return render_template(
            "pagina_hoteis.html",

            nome=session.get("nome", "Usuário"),

            perfil=session.get(
                "perfil",
                "Não informado"
            ),

            id_hotel=session.get("id_hotel"),

            hoteis=hoteis,

            categorias=categorias
        )


    except mysql.connector.Error as erro:

        print(
            f"Erro ao carregar página de hotéis: {erro}"
        )

        return (
            f"Erro ao carregar página de hotéis: {erro}"
        ), 500


    finally:

        cursor.close()
        conexao.close()

# PÁGINA DE QUARTOS
@app.route("/pagina-quartos")
def pagina_quartos():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexao = conectar_banco()

    if not conexao:
        return "Erro ao conectar ao banco de dados.", 500

    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                q.id_quarto,
                q.numero,
                q.andar,
                q.capacidade,
                q.status,
                q.id_categoria,
                cq.nome AS categoria,
                cq.valor_diaria,
                q.id_hotel,
                h.nome AS hotel,

                CASE
                    WHEN EXISTS (
                        SELECT 1
                        FROM checkin ci
                        LEFT JOIN checkout co
                            ON co.id_checkin = ci.id_checkin
                        WHERE ci.id_reserva IN (
                            SELECT r.id_reserva
                            FROM reservas r
                            WHERE r.id_quarto = q.id_quarto
                        )
                        AND co.id_checkout IS NULL
                    )
                    THEN 'OCUPADO'

                    WHEN q.status = 'MANUTENCAO'
                    THEN 'MANUTENCAO'

                    WHEN EXISTS (
                        SELECT 1
                        FROM reservas r
                        WHERE r.id_quarto = q.id_quarto
                        AND r.status IN ('PENDENTE', 'CONFIRMADA')
                        AND r.checkout_previsto >= CURDATE()
                    )
                    THEN 'RESERVADO'

                    ELSE 'LIVRE'
                END AS status_atual

            FROM quartos q

            LEFT JOIN categorias_quarto cq
                ON q.id_categoria = cq.id_categoria

            LEFT JOIN hoteis h
                ON q.id_hotel = h.id_hotel

            ORDER BY
                h.nome ASC,
                q.andar ASC,
                q.numero ASC
        """)

        quartos = cursor.fetchall()

        for quarto in quartos:
            quarto["status"] = quarto["status_atual"]

        cursor.execute("""
            SELECT
                id_hotel,
                nome
            FROM hoteis
            WHERE status = 'ATIVO'
            ORDER BY nome ASC
        """)

        hoteis = cursor.fetchall()

        cursor.execute("""
            SELECT
                id_categoria,
                nome,
                valor_diaria
            FROM categorias_quarto
            ORDER BY nome ASC
        """)

        categorias = cursor.fetchall()

        return render_template(
            "pagina_quartos.html",
            nome=session.get("nome", "Usuário"),
            perfil=session.get("perfil", "Não informado"),
            id_hotel=session.get("id_hotel"),
            quartos=quartos,
            hoteis=hoteis,
            categorias=categorias
        )

    except mysql.connector.Error as erro:

        print(f"Erro ao carregar página de quartos: {erro}")

        return f"Erro ao carregar página de quartos: {erro}", 500

    finally:

        cursor.close()
        conexao.close()
# PÁGINA DE HÓSPEDES
@app.route("/pagina-hospedes")
def pagina_hospedes():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexao = conectar_banco()

    if not conexao:
        return "Erro ao conectar ao banco de dados.", 500

    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                id_hospede,
                nome,
                cpf,
                telefone,
                email,
                data_nascimento
            FROM hospedes
            ORDER BY nome ASC
        """)

        hospedes = cursor.fetchall()

        return render_template(
            "pagina_hospedes.html",

            nome=session.get(
                "nome",
                "Usuário"
            ),

            perfil=session.get(
                "perfil",
                "Não informado"
            ),

            id_hotel=session.get(
                "id_hotel"
            ),

            hospedes=hospedes
        )

    except mysql.connector.Error as erro:

        print(
            f"Erro ao carregar página de hóspedes: {erro}"
        )

        return (
            f"Erro ao carregar página de hóspedes: {erro}"
        ), 500

    finally:

        cursor.close()
        conexao.close()


@app.route("/pagina-checkin")
def pagina_checkin():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexao = conectar_banco()

    if not conexao:
        return "Erro ao conectar ao banco de dados.", 500

    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                c.id_checkin,
                c.id_reserva,
                c.data_checkin,

                r.codigo_reserva,
                r.checkin_previsto,
                r.checkout_previsto,

                h.id_hospede,
                h.nome AS hospede,

                q.id_quarto,
                q.numero AS quarto,

                ht.id_hotel,
                ht.nome AS hotel

            FROM checkin c

            INNER JOIN reservas r
                ON c.id_reserva = r.id_reserva

            INNER JOIN hospedes h
                ON r.id_hospede = h.id_hospede

            INNER JOIN quartos q
                ON r.id_quarto = q.id_quarto

            LEFT JOIN hoteis ht
                ON q.id_hotel = ht.id_hotel

            ORDER BY c.data_checkin DESC
        """)

        checkins = cursor.fetchall()

        cursor.execute("""
            SELECT
                r.id_reserva,
                r.codigo_reserva,
                r.checkin_previsto,
                r.checkout_previsto,

                h.nome AS hospede,

                q.numero AS quarto,

                ht.nome AS hotel

            FROM reservas r

            INNER JOIN hospedes h
                ON r.id_hospede = h.id_hospede

            INNER JOIN quartos q
                ON r.id_quarto = q.id_quarto

            LEFT JOIN hoteis ht
                ON q.id_hotel = ht.id_hotel

            WHERE r.status IN ('PENDENTE', 'CONFIRMADA')

            ORDER BY r.checkin_previsto ASC
        """)

        reservas = cursor.fetchall()


        return render_template(
            "pagina_checkin.html",

            nome=session.get(
                "nome",
                "Usuário"
            ),

            perfil=session.get(
                "perfil",
                "Não informado"
            ),

            id_hotel=session.get(
                "id_hotel"
            ),

            checkins=checkins,

            reservas=reservas
        )


    except mysql.connector.Error as erro:

        print(
            f"Erro ao carregar página de check-in: {erro}"
        )

        return (
            f"Erro ao carregar página de check-in: {erro}"
        ), 500


    finally:

        cursor.close()
        conexao.close()


# PÁGINA DE RESERVAS
@app.route("/pagina-reservas")
def pagina_reservas():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexao = conectar_banco()

    if not conexao:
        return "Erro ao conectar ao banco de dados."

    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                r.id_reserva,
                r.codigo_reserva,
                r.data_reserva,
                r.checkin_previsto,
                r.checkout_previsto,
                r.quantidade_hospedes,
                r.observacao,
                r.status,

                r.id_hospede,
                h.nome AS hospede,

                r.id_quarto,
                q.numero AS numero_quarto,

                q.id_hotel,
                ho.nome AS hotel,

                r.id_usuario,
                u.nome AS usuario

            FROM reservas r

            LEFT JOIN hospedes h
                ON r.id_hospede = h.id_hospede

            LEFT JOIN quartos q
                ON r.id_quarto = q.id_quarto

            LEFT JOIN hoteis ho
                ON q.id_hotel = ho.id_hotel

            LEFT JOIN usuarios u
                ON r.id_usuario = u.id_usuario

            ORDER BY r.id_reserva DESC
        """)

        reservas = cursor.fetchall()


        cursor.execute("""
            SELECT
                id_hospede,
                nome
            FROM hospedes
            ORDER BY nome ASC
        """)

        hospedes = cursor.fetchall()

        cursor.execute("""
            SELECT
                q.id_quarto,
                q.numero,
                q.id_hotel,
                h.nome AS hotel
            FROM quartos q

            LEFT JOIN hoteis h
                ON q.id_hotel = h.id_hotel

            WHERE q.status <> 'MANUTENCAO'

            ORDER BY h.nome ASC, q.numero ASC
        """)

        quartos = cursor.fetchall()

        return render_template(

            "pagina_reservas.html",

            nome=session.get(
                "nome",
                "Usuário"
            ),

            perfil=session.get(
                "perfil",
                "Não informado"
            ),

            id_hotel=session.get(
                "id_hotel"
            ),

            reservas=reservas,

            hospedes=hospedes,

            quartos=quartos

        )


    except mysql.connector.Error as erro:

        print(
            f"Erro ao carregar página de reservas: {erro}"
        )

        return (
            f"Erro ao carregar página de reservas: {erro}"
        ), 500


    finally:

        cursor.close()
        conexao.close()

#pagina checkout
@app.route("/pagina-checkout")
def pagina_checkout():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexao = conectar_banco()

    if not conexao:
        return "Erro ao conectar ao banco de dados.", 500

    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                co.id_checkout,
                co.id_checkin,
                co.data_checkout,
                co.valor_diarias,
                co.valor_servicos,
                co.descontos,
                co.valor_total,

                ci.id_reserva,

                r.codigo_reserva,
                r.checkin_previsto,
                r.checkout_previsto,

                h.id_hospede,
                h.nome AS hospede,

                q.id_quarto,
                q.numero AS quarto,
                q.id_categoria,

                cq.nome AS categoria_quarto,
                cq.valor_diaria,

                ht.id_hotel,
                ht.nome AS hotel

            FROM checkout co

            INNER JOIN checkin ci
                ON co.id_checkin = ci.id_checkin

            INNER JOIN reservas r
                ON ci.id_reserva = r.id_reserva

            INNER JOIN hospedes h
                ON r.id_hospede = h.id_hospede

            INNER JOIN quartos q
                ON r.id_quarto = q.id_quarto

            INNER JOIN categorias_quarto cq
                ON q.id_categoria = cq.id_categoria

            LEFT JOIN hoteis ht
                ON q.id_hotel = ht.id_hotel

            ORDER BY co.data_checkout DESC
        """)

        checkouts = cursor.fetchall()

        cursor.execute("""
            SELECT
                ci.id_checkin,
                ci.id_reserva,
                ci.data_checkin,

                r.codigo_reserva,
                r.checkin_previsto,
                r.checkout_previsto,

                h.id_hospede,
                h.nome AS hospede,

                q.id_quarto,
                q.numero AS quarto,
                q.id_categoria,

                cq.nome AS categoria_quarto,
                cq.valor_diaria,

                ht.id_hotel,
                ht.nome AS hotel,

                DATEDIFF(
                    r.checkout_previsto,
                    r.checkin_previsto
                ) AS quantidade_diarias

            FROM checkin ci

            INNER JOIN reservas r
                ON ci.id_reserva = r.id_reserva

            INNER JOIN hospedes h
                ON r.id_hospede = h.id_hospede

            INNER JOIN quartos q
                ON r.id_quarto = q.id_quarto

            INNER JOIN categorias_quarto cq
                ON q.id_categoria = cq.id_categoria

            LEFT JOIN hoteis ht
                ON q.id_hotel = ht.id_hotel

            WHERE NOT EXISTS (
                SELECT 1
                FROM checkout co
                WHERE co.id_checkin = ci.id_checkin
            )

            ORDER BY r.checkout_previsto ASC
        """)

        checkins = cursor.fetchall()

        for checkin in checkins:

            cursor.execute("""
                SELECT
                    cs.id_consumo,
                    cs.quantidade,
                    cs.valor_unitario,
                    cs.valor_total,
                    cs.data_consumo,
                    cs.observacao,

                    s.id_servico,
                    s.nome AS servico,
                    s.preco

                FROM consumo_servicos cs

                INNER JOIN servicos s
                    ON cs.id_servico = s.id_servico

                WHERE cs.id_checkin = %s

                ORDER BY cs.data_consumo ASC
            """, (
                checkin["id_checkin"],
            ))

            consumos = cursor.fetchall()

            checkin["consumos"] = consumos

            quantidade_diarias = int(
                checkin["quantidade_diarias"] or 1
            )

            if quantidade_diarias <= 0:
                quantidade_diarias = 1

            valor_diaria = float(
                checkin["valor_diaria"] or 0
            )

            valor_diarias = (
                quantidade_diarias *
                valor_diaria
            )

            valor_servicos = 0.0

            for consumo in consumos:

                valor_consumo = float(
                    consumo["valor_total"] or 0
                )

                valor_servicos += valor_consumo

            descontos = 0.0

            valor_total = (
                valor_diarias
                + valor_servicos
                - descontos
            )

            if valor_total < 0:
                valor_total = 0.0

            checkin["quantidade_diarias"] = quantidade_diarias

            checkin["valor_diaria"] = valor_diaria

            checkin["valor_diarias"] = valor_diarias

            checkin["valor_servicos"] = valor_servicos

            checkin["descontos"] = descontos

            checkin["valor_total"] = valor_total

        cursor.execute("""
            SELECT
                id_servico,
                nome,
                descricao,
                preco,
                status

            FROM servicos

            WHERE status = 'ATIVO'

            ORDER BY nome ASC
        """)

        servicos = cursor.fetchall()

        for servico in servicos:

            servico["preco"] = float(
                servico["preco"] or 0
            )

        return render_template(
            "pagina_checkout.html",

            nome=session.get(
                "nome",
                "Usuário"
            ),

            perfil=session.get(
                "perfil",
                "Não informado"
            ),

            id_hotel=session.get(
                "id_hotel"
            ),

            checkouts=checkouts,

            checkins=checkins,

            servicos=servicos
        )

    except mysql.connector.Error as erro:

        print(
            f"ERRO MYSQL - PÁGINA CHECKOUT: {erro}"
        )

        return jsonify({
            "erro": "Erro ao carregar a página de checkout.",
            "detalhes": str(erro)
        }), 500

    except Exception as erro:

        print(
            f"ERRO GERAL - PÁGINA CHECKOUT: {erro}"
        )

        return jsonify({
            "erro": "Erro interno ao carregar o checkout.",
            "detalhes": str(erro)
        }), 500

    finally:

        cursor.close()
        conexao.close()

#pagina pagamentos
@app.route("/pagina-pagamentos")
def pagina_pagamentos():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexao = conectar_banco()

    if not conexao:
        return "Erro ao conectar ao banco de dados.", 500

    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.id_pagamento,
                p.valor,
                p.forma_pagamento,
                p.status,
                p.data_pagamento,
                co.id_checkout,
                ci.id_checkin,
                r.id_reserva,
                r.codigo_reserva,
                h.id_hospede,
                h.nome AS hospede,
                q.id_quarto,
                q.numero AS quarto,
                ht.id_hotel,
                ht.nome AS hotel
            FROM pagamentos p
            LEFT JOIN checkout co
                ON p.id_checkout = co.id_checkout
            LEFT JOIN checkin ci
                ON co.id_checkin = ci.id_checkin
            LEFT JOIN reservas r
                ON ci.id_reserva = r.id_reserva
            LEFT JOIN hospedes h
                ON r.id_hospede = h.id_hospede
            LEFT JOIN quartos q
                ON r.id_quarto = q.id_quarto
            LEFT JOIN hoteis ht
                ON q.id_hotel = ht.id_hotel
            ORDER BY p.data_pagamento DESC
        """)

        pagamentos = cursor.fetchall()

        cursor.execute("""
            SELECT
                co.id_checkout,
                co.data_checkout,
                co.valor_diarias,
                co.valor_servicos,
                co.descontos,
                co.valor_total,

                COALESCE(
                    SUM(
                        CASE
                            WHEN p.status = 'PAGO'
                            THEN p.valor
                            ELSE 0
                        END
                    ),
                    0
                ) AS valor_pago,

                (
                    co.valor_total -
                    COALESCE(
                        SUM(
                            CASE
                                WHEN p.status = 'PAGO'
                                THEN p.valor
                                ELSE 0
                            END
                        ),
                        0
                    )
                ) AS valor_disponivel,

                ci.id_checkin,
                r.id_reserva,
                r.codigo_reserva,
                h.nome AS hospede,
                q.numero AS quarto,
                ht.nome AS hotel

            FROM checkout co

            INNER JOIN checkin ci
                ON co.id_checkin = ci.id_checkin

            INNER JOIN reservas r
                ON ci.id_reserva = r.id_reserva

            INNER JOIN hospedes h
                ON r.id_hospede = h.id_hospede

            INNER JOIN quartos q
                ON r.id_quarto = q.id_quarto

            LEFT JOIN hoteis ht
                ON q.id_hotel = ht.id_hotel

            LEFT JOIN pagamentos p
                ON co.id_checkout = p.id_checkout

            GROUP BY
                co.id_checkout,
                co.data_checkout,
                co.valor_diarias,
                co.valor_servicos,
                co.descontos,
                co.valor_total,
                ci.id_checkin,
                r.id_reserva,
                r.codigo_reserva,
                h.nome,
                q.numero,
                ht.nome

            HAVING
                co.valor_total -
                COALESCE(
                    SUM(
                        CASE
                            WHEN p.status = 'PAGO'
                            THEN p.valor
                            ELSE 0
                        END
                    ),
                    0
                ) > 0

            ORDER BY co.data_checkout DESC
        """)

        checkouts = cursor.fetchall()

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM pagamentos
        """)

        resultado = cursor.fetchone()

        total_pagamentos = resultado["total"] if resultado else 0

        cursor.execute("""
            SELECT COALESCE(SUM(valor), 0) AS total
            FROM pagamentos
            WHERE status = 'PAGO'
        """)

        resultado = cursor.fetchone()

        total_recebido = resultado["total"] if resultado else 0

        return render_template(
            "pagina_pagamentos.html",
            nome=session.get("nome", "Usuário"),
            perfil=session.get("perfil", "Não informado"),
            id_hotel=session.get("id_hotel"),
            pagamentos=pagamentos,
            checkouts=checkouts,
            total_pagamentos=total_pagamentos,
            total_recebido=total_recebido
        )

    except mysql.connector.Error as erro:
        print(f"Erro ao carregar página de pagamentos: {erro}")
        return f"Erro ao carregar página de pagamentos: {erro}", 500

    except Exception as erro:
        print(f"Erro inesperado nos pagamentos: {erro}")
        return f"Erro inesperado nos pagamentos: {erro}", 500

    finally:
        cursor.close()
        conexao.close()

@app.route("/checkout/<int:id_checkout>/valor")
def valor_checkout(id_checkout):
    if "usuario_id" not in session:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    conexao = conectar_banco()

    if not conexao:
        return jsonify({"erro": "Erro ao conectar ao banco de dados."}), 500

    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                co.id_checkout,
                co.valor_total,
                COALESCE(
                    SUM(
                        CASE
                            WHEN p.status = 'PAGO' THEN p.valor
                            ELSE 0
                        END
                    ), 0
                ) AS valor_ja_pago
            FROM checkout co
            LEFT JOIN pagamentos p
                ON co.id_checkout = p.id_checkout
            WHERE co.id_checkout = %s
            GROUP BY
                co.id_checkout,
                co.valor_total
        """, (id_checkout,))

        checkout = cursor.fetchone()

        if not checkout:
            return jsonify({
                "erro": "Checkout não encontrado."
            }), 404

        valor_checkout = float(checkout["valor_total"] or 0)
        valor_ja_pago = float(checkout["valor_ja_pago"] or 0)
        valor_disponivel = max(
            valor_checkout - valor_ja_pago,
            0
        )

        return jsonify({
            "valor_checkout": round(valor_checkout, 2),
            "valor_ja_pago": round(valor_ja_pago, 2),
            "valor_disponivel": round(valor_disponivel, 2)
        })

    except mysql.connector.Error as erro:
        return jsonify({
            "erro": str(erro)
        }), 500

    finally:
        cursor.close()
        conexao.close()

@app.route("/pagina-consumos")
def pagina_consumos():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexao = conectar_banco()

    if not conexao:
        return "Erro ao conectar ao banco de dados.", 500

    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                id_servico,
                nome,
                descricao,
                preco,
                status,
                criado_em
            FROM servicos
            ORDER BY id_servico DESC
        """)

        servicos = cursor.fetchall()

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM servicos
        """)

        resultado = cursor.fetchone()
        total_servicos = resultado["total"] if resultado else 0

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM servicos
            WHERE status = 'ATIVO'
        """)

        resultado = cursor.fetchone()
        servicos_ativos = resultado["total"] if resultado else 0

        cursor.execute("""
            SELECT COALESCE(SUM(preco), 0) AS total
            FROM servicos
            WHERE status = 'ATIVO'
        """)

        resultado = cursor.fetchone()
        valor_servicos = resultado["total"] if resultado else 0

        return render_template(
            "pagina_consumos.html",
            nome=session.get("nome", "Usuário"),
            perfil=session.get("perfil", "Não informado"),
            id_hotel=session.get("id_hotel"),
            servicos=servicos,
            total_servicos=total_servicos,
            servicos_ativos=servicos_ativos,
            valor_servicos=valor_servicos
        )

    except mysql.connector.Error as erro:
        print(f"Erro ao carregar página de consumos: {erro}")
        return f"Erro ao carregar página de consumos: {erro}", 500

    except Exception as erro:
        print(f"Erro inesperado nos consumos: {erro}")
        return f"Erro inesperado nos consumos: {erro}", 500

    finally:
        cursor.close()
        conexao.close()


if __name__ == "__main__":
    app.run(debug=True)

