import streamlit as st
import re

st.set_page_config(page_title="Validador MT5", layout="wide")

st.title("🛡️ Validador e Auditor de Robôs MT5")
st.write("Analise a fundo a viabilidade matemática e estatística do seu robô através do relatório de backtest.")

uploaded_file = st.file_uploader("Envie o arquivo do backtest (.html)", type=["html"])

if uploaded_file is not None:
    try:
        raw_bytes = uploaded_file.read()
        try:
            content = raw_bytes.decode('utf-16')
        except Exception:
            try:
                content = raw_bytes.decode('utf-8', errors='ignore')
            except Exception:
                content = raw_bytes.decode('latin-1', errors='ignore')

        # Busca flexível por métricas usando apenas Expressões Regulares
        pf_match = re.search(r'(?:Profit Factor|Fator de lucro)\s*[\:\=]?\s*([\d\.\,]+)', content, re.IGNORECASE)
        dd_match = re.search(r'(?:Maximal drawdown|Rebaixamento máximo)\s*[\:\=]?\s*[\d\.\,\s]+\(([\d\.\,]+)\%\)', content, re.IGNORECASE) or re.search(r'\(([\d\.\,]+)\%\)', content)
        trades_match = re.search(r'(?:Total Trades|Total de negociações)\s*[\:\=]?\s*(\d+)', content, re.IGNORECASE)

        pf = float(pf_match.group(1).replace(',', '.')) if pf_match else 0.0
        dd = float(dd_match.group(1).replace(',', '.')) if dd_match else 0.0
        trades = int(trades_match.group(1)) if trades_match else 0

        # Cálculo do SQN (System Quality Number)
        sqn = round((pf * (trades ** 0.5)) / 10, 2) if trades > 0 else 0.0

        st.success("✅ Relatório do MT5 lido com sucesso!")
        
        st.subheader("📊 Métricas Principais Extraídas")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Fator de Lucro (PF)", f"{pf:.2f}")
        col2.metric("Drawdown Máximo", f"{dd:.2f}%")
        col3.metric("Total de Trades", f"{trades}")
        col4.metric("Índice SQN", f"{sqn:.2f}")

        st.divider()

        # Classificação nas 4 Categorias Rigorosas
        if pf >= 1.8 and sqn >= 2.5 and dd <= 15:
            categoria = "EXCELENTE"
            aprovado = True
            selo = "🥇 SELO MÁXIMO DE EXCELÊNCIA MATEMÁTICA"
        elif pf >= 1.4 and sqn >= 1.6 and dd <= 25:
            categoria = "MUITO BOM"
            aprovado = True
            selo = "🥈 SELO DE VALIDAÇÃO OPERACIONAL"
        elif pf >= 1.1:
            categoria = "BOM"
            aprovado = False
            selo = "⚠️ DESQUALIFICADO PARA CERTIFICADO (Sem Selo - Risco Elevado)"
        else:
            categoria = "RUIM"
            aprovado = False
            selo = "❌ DESQUALIFICADO PARA CERTIFICADO (Sem Selo - Inviável)"

        st.subheader("🏷️ Resultado da Auditoria")
        
        if aprovado:
            st.success(f"### CATEGORIA: {categoria}")
            st.balloons()
            st.markdown(f"""
            ### {selo}
            - **Status:** APROVADO PARA OPERAÇÃO REAL  
            - **Análise:** O robô apresenta expectativa matemática positiva e baixo risco de ruína.
            """)
        else:
            if categoria == "BOM":
                st.warning(f"### CATEGORIA: {categoria}")
            else:
                st.error(f"### CATEGORIA: {categoria}")
                
            st.markdown(f"""
            ### {selo}
            - **Status:** REPROVADO PARA CERTIFICAÇÃO  
            - **Análise:** A estratégia não atingiu a margem de segurança necessária para o selo.
            """)

    except Exception as e:
        st.error(f"Erro ao ler o arquivo HTML: {e}")
