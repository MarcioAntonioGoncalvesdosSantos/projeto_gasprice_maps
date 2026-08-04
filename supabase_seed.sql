-- Seed inicial para o projeto GasPrice

insert into public.postos (nome, bandeira, cidade, endereco, bairro)
values
  ('Auto Posto Estrela', 'Shell', 'São Paulo', 'Rua das Flores, 50', 'Centro'),
  ('Posto Econômico', 'Bandeira Branca', 'São Paulo', 'Rodovia Sul, KM 12', 'Vila Nova'),
  ('Posto Central', 'Petrobras', 'São Paulo', 'Av. Principal, 100', 'Jardins'),
  ('Posto Ipiranga Express', 'Ipiranga', 'São Paulo', 'Av. Brasil, 1500', 'Pinheiros'),
  ('Posto Ale Cidade', 'ALE', 'Campinas', 'Av. Francisco Glicério, 800', 'Centro'),
  ('Posto Anhanguera', 'Bandeira Branca', 'Campinas', 'Rod. Anhanguera, KM 98', 'Industrial'),
  ('Posto Beira Mar', 'Shell', 'Santos', 'Av. Bartolomeu de Gusmão, 45', 'Aparecida');

insert into public.precos (posto_id, tipo_combustivel, preco)
values
  (1, 'gasolina', 5.35),
  (1, 'etanol', 3.65),
  (1, 'diesel', 5.89),
  (2, 'gasolina', 5.29),
  (2, 'etanol', 3.59),
  (2, 'diesel', 5.75),
  (2, 'gnv', 4.39),
  (3, 'gasolina', 5.49),
  (3, 'etanol', 3.79),
  (3, 'diesel', 5.95),
  (4, 'gasolina', 5.42),
  (4, 'etanol', 3.72),
  (4, 'diesel', 5.85),
  (4, 'gnv', 4.49),
  (5, 'gasolina', 5.39),
  (5, 'etanol', 3.69),
  (5, 'diesel', 5.80),
  (6, 'gasolina', 5.25),
  (6, 'etanol', 3.55),
  (6, 'diesel', 5.70),
  (7, 'gasolina', 5.45),
  (7, 'etanol', 3.75),
  (7, 'diesel', 5.90),
  (7, 'gnv', 4.59);

-- ============================================================
-- Ajusta as sequences de identidade.
-- Como os ids foram inseridos explicitamente acima, o Postgres
-- não avança as sequences sozinho. Sem isso, o próximo INSERT
-- via app tentaria id=1 e daria erro de chave duplicada.
-- ============================================================
select setval(
    pg_get_serial_sequence('public.postos', 'id'),
    (select coalesce(max(id), 1) from public.postos)
);
select setval(
    pg_get_serial_sequence('public.precos', 'id'),
    (select coalesce(max(id), 1) from public.precos)
);
