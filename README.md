# 🏖️ Balneabilidade das Praias de Alagoas

Visualizador interativo dos dados de balneabilidade das praias do estado de Alagoas, Brasil.

Os dados são extraídos automaticamente do [relatório REAB do IMA/AL](https://www2.ima.al.gov.br/laboratorio/relatorios-de-balneabilidade/balneabilidade-de-praias/).

## 🌐 Demo

Acesse: [https://SEU-USUARIO.github.io/playas-brasil/](https://SEU-USUARIO.github.io/playas-brasil/)

## 📊 Funcionalidades

- **Mapa interativo** com marcadores coloridos (verde = própria, vermelho = imprópria)
- **Tabela** com todas as praias organizadas por região (Litoral Norte, Maceió, Litoral Sul)
- **Busca** de endereços no mapa
- **Responsivo** - funciona em desktop e mobile
- **Atualização automática** a cada 3 dias via GitHub Actions

## 🔄 Atualização dos dados

Os dados são atualizados automaticamente a cada 3 dias através de um GitHub Action que:

1. Acessa a página do IMA/AL
2. Baixa o PDF mais recente
3. Extrai os dados das praias
4. Atualiza os arquivos CSV e JSON
5. Faz commit das mudanças

Para atualizar manualmente, execute:

```bash
pip install -r requirements.txt
python scraper.py
```

## 📁 Estrutura

```
├── index.html          # Página principal
├── scraper.py          # Script de extração de dados
├── DatosPlaya.csv      # Dados em formato simples
├── DatosPlaya_completo.csv  # Dados com todas as colunas
├── metadata.json       # Metadados (data, contagens)
├── requirements.txt    # Dependências Python
└── .github/workflows/  # GitHub Actions
```

## 📜 Licença

Os dados são de domínio público, fornecidos pelo [Instituto do Meio Ambiente de Alagoas (IMA/AL)](https://www2.ima.al.gov.br/).
