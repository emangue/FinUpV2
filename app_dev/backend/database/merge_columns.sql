-- Backup da tabela
CREATE TABLE preview_transacoes_backup AS SELECT * FROM preview_transacoes;

-- Recriar tabela com apenas colunas antigas (CamelCase)
DROP TABLE preview_transacoes;

CREATE TABLE preview_transacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    banco TEXT,
    cartao TEXT,
    nome_arquivo TEXT,
    mes_fatura TEXT,
    data TEXT,
    lancamento TEXT,
    valor REAL,
    created_at TEXT,
    IdTransacao TEXT,
    IdParcela TEXT,
    EstabelecimentoBase TEXT,
    ValorPositivo REAL,
    TipoTransacao TEXT,
    GRUPO TEXT,
    SUBGRUPO TEXT,
    TipoGasto TEXT,
    CategoriaGeral TEXT,
    origem_classificacao TEXT,
    ValidarIA TEXT,
    MarcacaoIA TEXT,
    ParcelaAtual INTEGER,
    TotalParcelas INTEGER,
    TemParcela INTEGER,
    IgnorarDashboard INTEGER DEFAULT 0,
    tipo_documento VARCHAR(50),
    nome_cartao VARCHAR(255),
    data_criacao TIMESTAMP,
    is_duplicate BOOLEAN DEFAULT 0,
    duplicate_reason TEXT,
    updated_at DATETIME,
    padrao_buscado TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Restaurar dados
INSERT INTO preview_transacoes (
    id, session_id, user_id, banco, cartao, nome_arquivo, mes_fatura,
    data, lancamento, valor, created_at, IdTransacao, IdParcela,
    EstabelecimentoBase, ValorPositivo, TipoTransacao, GRUPO, SUBGRUPO,
    TipoGasto, CategoriaGeral, origem_classificacao, ValidarIA, MarcacaoIA,
    ParcelaAtual, TotalParcelas, TemParcela, IgnorarDashboard,
    tipo_documento, nome_cartao, data_criacao, is_duplicate, duplicate_reason,
    updated_at, padrao_buscado
)
SELECT 
    id, session_id, user_id, banco, cartao, nome_arquivo, mes_fatura,
    data, lancamento, valor, created_at, IdTransacao, IdParcela,
    EstabelecimentoBase, ValorPositivo, TipoTransacao, GRUPO, SUBGRUPO,
    TipoGasto, CategoriaGeral, origem_classificacao, ValidarIA, MarcacaoIA,
    ParcelaAtual, TotalParcelas, TemParcela, IgnorarDashboard,
    tipo_documento, nome_cartao, data_criacao, is_duplicate, duplicate_reason,
    updated_at, padrao_buscado
FROM preview_transacoes_backup;

-- Recriar índices
CREATE INDEX idx_preview_session ON preview_transacoes(session_id);
CREATE INDEX idx_preview_user ON preview_transacoes(user_id);
CREATE INDEX idx_preview_id_transacao ON preview_transacoes(IdTransacao);
CREATE INDEX idx_preview_id_parcela ON preview_transacoes(IdParcela);
CREATE INDEX idx_preview_origem ON preview_transacoes(origem_classificacao);

-- Limpar backup
DROP TABLE preview_transacoes_backup;

SELECT 'Tabela recriada. Total de registros: ' || COUNT(*) FROM preview_transacoes;
