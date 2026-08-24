import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Validador & Auditor MT5", layout="wide")

st.title("🛡️ Auditoria Completa de Backtest MT5")
st.write("Leitura detalhada de todas as entradas, saídas e métricas operacionais.")

uploaded_file = st.file_uploader("Envie o relatório do MT5 (.html)", type=["html"])

if uploaded_file is not None:
    try:
        raw_bytes = uploaded_file.read()
        
        # Leitura de encoding do MT5 (UTF-16, UTF-8 ou Latin-1)
        try:
            content = raw_bytes.decode('utf-16')
        except Exception:
            try:
                content = raw_bytes.decode('utf-8', errors='ignore')
            except Exception:
                content = raw_bytes.decode('latin-1', errors='ignore')

        # --- PARSER NATIVO VIA REGEX (DISPENSA LXML E HTML5LIB) ---
        
        # Extração de métricas de resumo
        pf_match = re.search(r'(?:Profit Factor|Fator de lucro)\s*</td>\s*<td[^>]*><b>?\s*([\d\.\,]+)', content, re.IGNORECASE)
        trades_match = re.search(r'(?:Total Trades|Total de negociações)\s*</td>\s*<td[^>]*><b>?\s*(\d+)', content, re.IGNORECASE)
        dd_match = re.search(r'\(([\d\.\,]+)\%\)', content)
        
        pf = float(pf_match.group(1).replace(',', '.')) if pf_match else 0.0
        total_trades = int(trades_match.group(1)) if trades_match else 0
        dd = float(dd_match.group(1).replace(',', '.')) if dd_match else 0.0

        # Extração das linhas da tabela de Histórico de Operações (Deals/Orders)
        # Busca por linhas de tabelas com valores numéricos de lucro
        row_pattern = re.compile(r'<tr[^>]*>\s*<td[^>]*>(.*?)</td>\s*</tr>', re.DOTALL | re.IGNORECASE)
        cells_pattern = re.compile(r'<td[^>]*>(.*?)</td>', re.DOTALL | re.IGNORECASE)
        
        trades_data = []
        for match in row_pattern.finditer(content):
            row_html = match.group(0)
            cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells_pattern.findall(row_html)]
            if len(cells) >= 6:
                # Procura por linhas que contenham indicação de compra/venda
                row_str = " ".join(cells).lower()
                if any(k in row_str for k in ['buy', 'sell', 'compra', 'venda', 'in', 'out']):
                    trades_data.append(cells)

        # Monta DataFrame das Operações se encontradas
        df_trades = None
        win_rate = 0.0
        
        if trades_data:
            df_trades = pd.DataFrame(trades_data)
            
            # Tenta encontrar a coluna de Lucro/Profit (geralmente a última ou penúltima)
            for col_idx in reversed(range(df_trades.shape[1])):
                series_clean = df_trades[col_idx].astype(str).str.replace(' ', '').str.replace(',', '.')
                numeric_series = pd.to_numeric(series_clean, errors='coerce').dropna()
                
                # Se encontrou valores numéricos positivos e negativos
                if len(numeric_series) > 0 and (numeric_series < 0).any():
                    lucros = numeric_series[numeric_series > 0]
                    perdas = numeric_series[numeric_series < 0]
                    
                    if total_trades == 0:
                        total_trades = len(numeric_series)
                    
                    win_rate = round((len(lucros) / len(numeric_series)) * 100, 2) if len(numeric_series) > 0 else 0.0
                    
                    if pf == 0.0 and abs(perdas.sum()) > 0:
                        pf = round(lucros.sum() / abs(perdas.sum()), 2)
                    break

        # Cálculo do SQN (System Quality Number)
        sqn = round((pf * (total_trades ** 0.5)) / 10, 2) if total_trades > 0 else 0.0

        st.success("✅ Relatório do MT5 lido com sucesso!")
        
        # Exibição dos Dados
        st.subheader("📊 Painel Analítico das Operações")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Fator de Lucro (PF)", f"{pf:.2f}")
        c2.metric("Total de Operações", f"{total_trades}")
        c3.metric("Taxa de Acerto", f"{win_rate}%")
        c4.metric("Drawdown Máximo", f"{dd:.2f}%")

        st.divider()

        # Classificação por Categorias
        if pf >= 1.8 and sqn >= 2.5 and dd <= 15 and total_trades >= 50:
            categoria = "EXCELENTE"
            aprovado = True
            selo = "🥇 SELO MÁXIMO DE EXCELÊNCIA OPERACIONAL"
        elif pf >= 1.4 and sqn >= 1.6 and dd <= 25 and total_trades >= 30:
            categoria = "MUITO BOM"
            aprovado = True
            selo = "🥈 SELO DE VALIDAÇÃO OPERACIONAL"
        elif pf >= 1.1:
            categoria = "BOM"
            aprovado = False
            selo = "⚠️ DESQUALIFICADO (Risco Elevado)"
        else:
            categoria = "RUIM"
            aprovado = False
            selo = "❌ DESQUALIFICADO (Expectativa Negativa)"

        st.subheader("🏷️ Veredito da Auditoria")
        if aprovado:
            st.success(f"### CATEGORIA: {categoria}")
            st.balloons()
            st.markdown(f"**{selo}**\n\nRobô aprovado estatisticamente com histórico comprovado.")
        else:
            if categoria == "BOM":
                st.warning(f"### CATEGORIA: {categoria}")
            else:
                st.error(f"### CATEGORIA: {categoria}")
            st.markdown(f"**{selo}**\n\nRobô desqualificado pelos parâmetros de segurança.")

        if df_trades is not None and not df_trades.empty:
            with st.expander("📋 Ver Tabela de Operações Extraídas"):
                st.dataframe(df_trades)

    except Exception as e:
        st.error(f"Erro ao processar o relatório: {e}")
