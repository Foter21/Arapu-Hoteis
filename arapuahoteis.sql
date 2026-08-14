DROP DATABASE IF EXISTS Arapua_Hoteis;

CREATE DATABASE Arapua_Hoteis
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE Arapua_Hoteis;

CREATE TABLE categorias_hotel (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    descricao VARCHAR(255),
    quantidade_estrelas INT NOT NULL,
    CHECK (quantidade_estrelas BETWEEN 1 AND 5)
);

CREATE TABLE hoteis (
    id_hotel INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    cnpj CHAR(14) UNIQUE NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(100),
    cep CHAR(8),
    rua VARCHAR(120),
    numero VARCHAR(10),
    bairro VARCHAR(60),
    cidade VARCHAR(60),
    estado CHAR(2),
    id_categoria INT NOT NULL,
    status ENUM(
        'ATIVO',
        'INATIVO'
    ) DEFAULT 'ATIVO',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_categoria)
        REFERENCES categorias_hotel(id_categoria)
);

CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    perfil ENUM(
        'ADMIN',
        'GERENTE',
        'RECEPCAO'
    ) NOT NULL,

    id_hotel INT NULL,
    status ENUM(
        'ATIVO',
        'INATIVO'
    ) DEFAULT 'ATIVO',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_hotel)
        REFERENCES hoteis(id_hotel)
        ON DELETE SET NULL
);

CREATE TABLE hospedes (
    id_hospede INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    cpf CHAR(11) UNIQUE NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(100),
    data_nascimento DATE,
    nacionalidade VARCHAR(60) DEFAULT 'Brasileira',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categorias_quarto (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(60) NOT NULL UNIQUE,
    descricao TEXT,
    valor_diaria DECIMAL(10,2) NOT NULL,
    capacidade_padrao INT NOT NULL,

    status ENUM(
        'ATIVO',
        'INATIVO'
    ) DEFAULT 'ATIVO',

    CHECK (valor_diaria >= 0),
    CHECK (capacidade_padrao > 0)
);

CREATE TABLE quartos (
    id_quarto INT AUTO_INCREMENT PRIMARY KEY,
    numero VARCHAR(10) NOT NULL,
    andar INT NOT NULL,
    capacidade INT NOT NULL,
    status ENUM(
        'LIVRE',
        'OCUPADO',
        'RESERVADO',
        'MANUTENCAO'
    ) DEFAULT 'LIVRE',
    id_categoria INT NOT NULL,
    id_hotel INT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (
        id_hotel,
        numero
    ),
    FOREIGN KEY (id_categoria)
        REFERENCES categorias_quarto(id_categoria),

    FOREIGN KEY (id_hotel)
        REFERENCES hoteis(id_hotel)
        ON DELETE CASCADE,

    CHECK (capacidade > 0)
);

CREATE TABLE reservas (
    id_reserva INT AUTO_INCREMENT PRIMARY KEY,
    codigo_reserva VARCHAR(20) UNIQUE NOT NULL,
    data_reserva DATETIME DEFAULT CURRENT_TIMESTAMP,
    checkin_previsto DATE NOT NULL,
    checkout_previsto DATE NOT NULL,
    quantidade_hospedes INT DEFAULT 1,
    observacao TEXT,
    status ENUM(
        'PENDENTE',
        'CONFIRMADA',
        'CANCELADA',
        'FINALIZADA'
    ) DEFAULT 'PENDENTE',
    id_hospede INT NOT NULL,
    id_quarto INT NOT NULL,
    id_usuario INT,
    FOREIGN KEY (id_hospede)
        REFERENCES hospedes(id_hospede),

    FOREIGN KEY (id_quarto)
        REFERENCES quartos(id_quarto),

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON DELETE SET NULL,

    CHECK (checkout_previsto > checkin_previsto),
    CHECK (quantidade_hospedes > 0)
);
CREATE TABLE checkin (
    id_checkin INT AUTO_INCREMENT PRIMARY KEY,
    data_checkin DATETIME DEFAULT CURRENT_TIMESTAMP,
    observacao TEXT,
    id_reserva INT NOT NULL UNIQUE,
    id_usuario INT,
    FOREIGN KEY (id_reserva)
        REFERENCES reservas(id_reserva),

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON DELETE SET NULL
);
CREATE TABLE checkout (
    id_checkout INT AUTO_INCREMENT PRIMARY KEY,
    data_checkout DATETIME DEFAULT CURRENT_TIMESTAMP,
    valor_diarias DECIMAL(10,2) DEFAULT 0.00,
    valor_servicos DECIMAL(10,2) DEFAULT 0.00,
    descontos DECIMAL(10,2) DEFAULT 0.00,
    valor_total DECIMAL(10,2) DEFAULT 0.00,
    observacao TEXT,
    id_checkin INT NOT NULL UNIQUE,
    id_usuario INT,
    FOREIGN KEY (id_checkin)
        REFERENCES checkin(id_checkin),

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON DELETE SET NULL,

    CHECK (valor_diarias >= 0),
    CHECK (valor_servicos >= 0),
    CHECK (descontos >= 0),
    CHECK (valor_total >= 0)
);
CREATE TABLE servicos (
    id_servico INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10,2) NOT NULL,
    status ENUM(
        'ATIVO',
        'INATIVO'
    ) DEFAULT 'ATIVO',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (preco >= 0)
);
CREATE TABLE consumo_servicos (
    id_consumo INT AUTO_INCREMENT PRIMARY KEY,
    quantidade INT NOT NULL DEFAULT 1,
    valor_unitario DECIMAL(10,2) NOT NULL,
    valor_total DECIMAL(10,2) NOT NULL,
    data_consumo DATETIME DEFAULT CURRENT_TIMESTAMP,
    observacao VARCHAR(255),
    id_servico INT NOT NULL,
    id_checkin INT NOT NULL,
    FOREIGN KEY (id_servico)
        REFERENCES servicos(id_servico),

    FOREIGN KEY (id_checkin)
        REFERENCES checkin(id_checkin),

    CHECK (quantidade > 0),
    CHECK (valor_unitario >= 0),
    CHECK (valor_total >= 0)
);
CREATE TABLE pagamentos (
    id_pagamento INT AUTO_INCREMENT PRIMARY KEY,
    valor DECIMAL(10,2) NOT NULL,
    forma_pagamento ENUM(
        'DINHEIRO',
        'PIX',
        'CARTAO_CREDITO',
        'CARTAO_DEBITO'
    ) NOT NULL,
    status ENUM(
        'PENDENTE',
        'PAGO',
        'CANCELADO'
    ) DEFAULT 'PENDENTE',
    data_pagamento DATETIME,
    observacao VARCHAR(255),
    id_checkout INT NOT NULL,
    FOREIGN KEY (id_checkout)
        REFERENCES checkout(id_checkout),

    CHECK (valor > 0)
);
INSERT INTO categorias_hotel
(id_categoria, nome, descricao, quantidade_estrelas)
VALUES
(1, 'Econômica', 'Categoria acessível para clientes que buscam conforto com valor acessível.', 2),
(2, 'Conforto', 'Categoria com bom conforto e estrutura básica para estadias curtas e médias.', 3),
(3, 'Executiva', 'Categoria para clientes que buscam qualidade, atendimento e conforto premium.', 4),
(4, 'Premium', 'Categoria de alto padrão com infraestrutura e serviços diferenciados.', 5);
INSERT INTO hoteis
(nome, cnpj, telefone, email, cep, rua, numero,
bairro, cidade, estado, id_categoria)
VALUES
('Arapuá Hotel Palmas','12345678000110','(63) 3215-1000','palmas@arapuahoteis.com.br','77001000','Avenida Tocantins','1000','Centro','Palmas','TO',3),
('Arapuá Hotel Goiânia','12345678000200','(62) 3250-2000','goiania@arapuahoteis.com.br','74000000','Avenida Goiás','1500','Setor Central','Goiânia','GO',3),
('Arapuá Hotel Brasília','12345678000390','(61) 3300-3000','brasilia@arapuahoteis.com.br','70000000','Eixo Monumental','2000','Asa Sul','Brasília','DF',4),
('Arapuá Hotel Imperatriz','12345678000470','(99) 3525-4000','imperatriz@arapuahoteis.com.br','65900000','Avenida Dorgival Pinheiro','800','Centro','Imperatriz','MA',2);
INSERT INTO usuarios
(nome, email, senha, perfil, id_hotel)
VALUES
('Lais Gabriela Basilio','lais@arapuahoteis.com.br','123456','ADMIN',NULL),
('Telê Santana','tele@arapuahoteis.com.br','123456','GERENTE',1),
('Joao Pedro','joao@arapuahoteis.com.br','123456','RECEPCAO',1);
INSERT INTO hospedes
(nome, cpf, telefone, email, data_nascimento, nacionalidade)
VALUES
('Lais Gabriela Basilio','11111111111','(63) 99111-1111','lais.gabriela@email.com','1998-04-15','Brasileira'),
('Telê Santana','22222222222','(63) 99222-2222','tele.santana@email.com','1995-08-20','Brasileira'),
('Joao Pedro','33333333333','(63) 99333-3333','joao.pedro@email.com','1997-03-10','Brasileira'),
('Mariana Oliveira','44444444444','(62) 99444-4444','mariana.oliveira@email.com','1992-11-25','Brasileira'),
('Carlos Henrique','55555555555','(61) 99555-5555','carlos.henrique@email.com','1989-01-18','Brasileira'),
('Ana Beatriz Santos','66666666666','(63) 99666-6666','ana.beatriz@email.com','1996-07-30','Brasileira'),
('Rafael Martins','77777777777','(62) 99777-7777','rafael.martins@email.com','1988-09-12','Brasileira'),
('Juliana Ferreira','88888888888','(61) 99888-8888','juliana.ferreira@email.com','1993-12-05','Brasileira');
INSERT INTO categorias_quarto
(nome, descricao, valor_diaria, capacidade_padrao)
VALUES
('Standard','Quarto confortável para uma ou duas pessoas.',180.00,2),
('Luxo','Quarto amplo com maior conforto e comodidades.',280.00,2),
('Premium','Quarto premium com espaço ampliado.',390.00,3),
('Suíte','Suíte completa com quarto, sala e banheiro privativo.',550.00,4),
('Família','Quarto amplo destinado a famílias.',450.00,5);
INSERT INTO quartos
(numero, andar, capacidade, status, id_categoria, id_hotel)
VALUES
('101',1,2,'LIVRE',1,1),
('102',1,2,'OCUPADO',1,1),
('103',1,3,'RESERVADO',2,1),
('201',2,2,'LIVRE',2,1),
('202',2,3,'OCUPADO',3,1),
('203',2,4,'MANUTENCAO',4,1),
('301',3,4,'LIVRE',4,1),
('302',3,5,'LIVRE',5,1),

('101',1,2,'OCUPADO',1,2),
('102',1,2,'LIVRE',1,2),
('201',2,3,'RESERVADO',2,2),
('202',2,4,'LIVRE',3,2),
('301',3,4,'OCUPADO',4,2),

('101',1,2,'LIVRE',1,3),
('102',1,2,'OCUPADO',2,3),
('201',2,3,'LIVRE',3,3),
('202',2,4,'RESERVADO',4,3),
('301',3,5,'LIVRE',5,3),

('101',1,2,'LIVRE',1,4),
('102',1,2,'OCUPADO',1,4),
('201',2,3,'LIVRE',2,4);


INSERT INTO servicos
(nome, descricao, preco)
VALUES
('Café da manhã','Café da manhã completo servido no hotel.',35.00),
('Estacionamento','Diária de estacionamento.',25.00),
('Lavanderia','Serviço de lavagem de roupas.',40.00),
('Room Service','Serviço de alimentação no quarto.',60.00);
INSERT INTO reservas
(codigo_reserva, checkin_previsto, checkout_previsto,quantidade_hospedes, observacao, status,
id_hospede, id_quarto, id_usuario)
VALUES
('ARAP000001','2026-08-08','2026-08-11',2,'Reserva para viagem de negócios.','CONFIRMADA',1,2,3),
('ARAP000002','2026-08-09','2026-08-12',2,'Hospedagem de lazer.','CONFIRMADA',2,3,3),
('ARAP000003','2026-08-10','2026-08-15',3,'Reserva para família.','PENDENTE',3,11,2),
('ARAP000004','2026-08-07','2026-08-10',2,'Hospedagem corporativa.','CONFIRMADA',4,9,2),
('ARAP000005','2026-08-06','2026-08-09',2,'Reserva finalizada.','FINALIZADA',5,20,3),
('ARAP000006','2026-08-12','2026-08-16',3,'Hospedagem de férias.','CONFIRMADA',6,17,2),
('ARAP000007','2026-08-15','2026-08-18',4,'Reserva familiar.','PENDENTE',7,13,2),
('ARAP000008','2026-08-20','2026-08-23',4,'Hospedagem programada.','CONFIRMADA',8,21,3);
INSERT INTO checkin
(data_checkin, observacao, id_reserva, id_usuario)
VALUES
('2026-08-08 14:05:00','Check-in realizado normalmente.',1,3),
('2026-08-07 14:30:00','Documento conferido no momento do check-in.',4,3),
('2026-08-06 14:10:00','Check-in realizado antecipadamente.',5,3);
INSERT INTO checkout
(data_checkout, valor_diarias, valor_servicos,
descontos, valor_total, observacao,
id_checkin, id_usuario)
VALUES
('2026-08-10 11:30:00',840.00,145.00,0.00,985.00,'Checkout realizado normalmente.',2,3),
('2026-08-09 10:45:00',540.00,70.00,70.00,540.00,'Desconto aplicado na hospedagem.',3,3);
INSERT INTO consumo_servicos
(quantidade, valor_unitario, valor_total,
data_consumo, observacao, id_servico, id_checkin)
VALUES
(2,35.00,70.00,'2026-08-08 08:30:00','Café da manhã',1,1),
(1,25.00,25.00,'2026-08-08 09:00:00','Estacionamento',2,1),
(1,60.00,60.00,'2026-08-08 20:15:00','Room Service',4,1),
(3,35.00,105.00,'2026-08-07 08:20:00','Café da manhã',1,2),
(1,40.00,40.00,'2026-08-08 10:00:00','Lavanderia',3,2),
(2,35.00,70.00,'2026-08-06 08:30:00','Café da manhã',1,3);
INSERT INTO pagamentos
(valor, forma_pagamento, status,
data_pagamento, observacao, id_checkout)
VALUES
(985.00,'CARTAO_CREDITO','PAGO','2026-08-10 11:35:00','Pagamento integral da hospedagem.',1),
(540.00,'PIX','PAGO','2026-08-09 10:50:00','Pagamento realizado via PIX.',2);
SELECT
    id_checkin,
    id_reserva,
    data_checkin
FROM checkin
ORDER BY id_checkin;
SELECT
    id_checkout,
    id_checkin,
    valor_total
FROM checkout
ORDER BY id_checkout;

UPDATE usuarios
SET senha = '123456'
WHERE status = 'ATIVO';


