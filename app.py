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
        
        # Encoding do MT5
        try:
            content = raw_bytes.decode('utf-16')
        except Exception:
            try:
                content = raw_bytes.decode('utf-8', errors='ignore')
            except Exception:
                content = raw_bytes.decode('latin-1', errors='ignore')

        # --- EXTRAÇÃO DIRETA DAS MÉTRICAS OFICIAIS DO MT5 ---
        
        # 1. Fator de Lucro
        pf_match = re.search(r'(?:Profit Factor|Fator de Lucro)\s*</td>\s*<td[^>]*><b>?\s*([\d\.\,]+)', content, re.IGNORECASE)
        pf = float(pf_match.group(1).replace(',', '.')) if pf_match else 0.0

        # 2. Total de Negociações Reais (Trades)
        trades_match = re.search(r'(?:Total Trades|Total de Negociações)\s*</td>\s*<td[^>]*><b>?\s*(\d+)', content, re.IGNORECASE)
        total_trades = int(trades_match.group(1)) if trades_match else 0

        # 3. Drawdown Máximo do Saldo (ou Capital Líquido)
        dd_match = re.search(r'(?:Maximal drawdown|Rebaixamento Máximo do Saldo).*?\(([\d\.\,]+)\%\)', content, re.DOTALL | re.IGNORECASE)
        dd = float(dd_match.group(1).replace(',', '.')) if dd_match else 0.0

        # 4. Negociações com Lucro para calcular a Taxa de Acerto Exata
        win_match = re.search(r'(?:Profit Trades|Negociações com Lucro).*?\(\s*([\d\.\,]+)\%', content, re.DOTALL | re.IGNORECASE)
        if win_match:
            win_rate = float(win_match.group(1).replace(',', '.'))
        else:
            win_rate = 0.0

        # Cálculo do SQN baseado nas negociações reais
        sqn = round((pf * (total_trades ** 0.5)) / 10, 2) if total_trades > 0 else 0.0

        st.success("✅ Relatório do MT5 lido com sucesso!")
        
        # Exibição das Métricas Oficiais
        st.subheader("📊 Painel Analítico das Operações")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Fator de Lucro (PF)", f"{pf:.2f}")
        c2.metric("Total de Trades", f"{total_trades}")
        c3.metric("Taxa de Acerto", f"{win_rate:.2f}%")
        c4.metric("Drawdown Máximo", f"{dd:.2f}%")

        st.divider()

        # Regras da Auditoria
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

    except Exception as e:
        st.error(f"Erro ao processar o relatório: {e}")
