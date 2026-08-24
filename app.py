import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(page_title="Validador & Auditor MT5", layout="wide")

st.title("🛡️ Auditoria Completa de Backtest MT5")
st.write("Leitura detalhada de todas as entradas, saídas e métricas operacionais.")

uploaded_file = st.file_uploader("Envie o relatório do MT5 (.html)", type=["html"])

if uploaded_file is not None:
    try:
        raw_bytes = uploaded_file.read()
        
        # Leitura de encoding do MT5
        try:
            content = raw_bytes.decode('utf-16')
        except Exception:
            try:
                content = raw_bytes.decode('utf-8', errors='ignore')
            except Exception:
                content = raw_bytes.decode('latin-1', errors='ignore')

        # Lê as tabelas usando o motor nativo 'html.parser' para evitar erro de lxml
        tables = pd.read_html(io.StringIO(content), flavor='html5lib')
        
        df_trades = None
        
        # Mapeamento do histórico de compra e venda
        for df in tables:
            df_str = df.to_string().lower()
            if 'buy' in df_str or 'sell' in df_str or 'compra' in df_str or 'venda' in df_str:
                df_trades = df
                break

        if df_trades is not None:
            st.success("✅ Histórico de entradas e saídas mapeado com sucesso!")
            
            profit_col = None
            for col in df_trades.columns:
                col_name = str(col).lower()
                if 'profit' in col_name or 'lucro' in col_name or 'resultado' in col_name:
                    profit_col = col
                    break
            
            if profit_col is not None:
                profits = pd.to_numeric(
                    df_trades[profit_col].astype(str).str.replace(' ', '').str.replace(',', '.'), 
                    errors='coerce'
                ).dropna()

                lucros = profits[profits > 0]
                perdas = profits[profits < 0]
                
                total_trades = len(profits)
                lucro_total = lucros.sum()
                perda_total = abs(perdas.sum())
                
                pf = round(lucro_total / perda_total, 2) if perda_total > 0 else (round(lucro_total, 2) if lucro_total > 0 else 0.0)
                win_rate = round((len(lucros) / total_trades) * 100, 2) if total_trades > 0 else 0.0
                sqn = round((pf * (total_trades ** 0.5)) / 10, 2) if total_trades > 0 else 0.0
            else:
                pf, total_trades, win_rate, sqn = 0.0, 0, 0.0, 0.0
        else:
            pf, total_trades, win_rate, sqn = 0.0, 0, 0.0, 0.0

        # Extração do Drawdown via Regex
        dd_match = re.search(r'\(([\d\.\,]+)\%\)', content)
        dd = float(dd_match.group(1).replace(',', '.')) if dd_match else 0.0

        # Exibição dos Dados
        st.subheader("📊 Painel Analítico das Operações")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Fator de Lucro (PF)", f"{pf}")
        c2.metric("Total de Operações", f"{total_trades}")
        c3.metric("Taxa de Acerto", f"{win_rate}%")
        c4.metric("Drawdown Máximo", f"{dd}%")

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

        if df_trades is not None:
            with st.expander("📋 Ver Tabela Completa de Entradas e Saídas"):
                st.dataframe(df_trades)

    except Exception as e:
        st.error(f"Erro ao processar o relatório: {e}")
