import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="ShopControl - Gestão & Monitoramento", layout="wide", page_icon="🛍️")

# --- INICIALIZAÇÃO DO BANCO DE DADOS EM MEMÓRIA ---
# Adicionado estoque inicial padrão com roupas, calçados e brinquedos
if 'produtos' not in st.session_state:
    estoque_inicial = [
        [1, 'Camisa Polo Básica', 'Roupas', 59.90, 20],
        [2, 'Calça Jeans Casual', 'Roupas', 119.90, 15],
        [3, 'Blusa de Frio Moletom', 'Roupas', 89.90, 10],
        [4, 'Tênis Esportivo Running', 'Calçados', 189.90, 8],
        [5, 'Sapato Social Couro', 'Calçados', 220.00, 5],
        [6, 'Carrinho de Controle Remoto', 'Brinquedos', 75.00, 12],
        [7, 'Boneca Articulada', 'Brinquedos', 49.90, 18]
    ]
    st.session_state.produtos = pd.DataFrame(
        estoque_inicial, 
        columns=['ID', 'Nome', 'Categoria', 'Preço Venda', 'Estoque Atual']
    )

if 'clientes' not in st.session_state:
    # Já deixei a Amanda criada como exemplo no sistema para você ver como fica!
    st.session_state.clientes = {
        'Amanda': {
            'compras': [{'data': '24/05/2026', 'itens': ['1x Calça Jeans Casual', '1x Blusa de Frio Moletom'], 'Total': 209.80}],
            'pagamentos': [{'data': '24/05/2026 às 14:30', 'valor': 50.00}]
        }
    }

if 'vendas' not in st.session_state:
    st.session_state.vendas = pd.DataFrame(columns=['Data', 'Cliente', 'Produtos', 'Total', 'Status'])

# --- FUNÇÕES AUXILIARES ---
def adicionar_produto(nome, categoria, preco, qtd):
    df = st.session_state.produtos
    if nome in df['Nome'].values:
        st.session_state.produtos.loc[st.session_state.produtos['Nome'] == nome, 'Estoque Atual'] += qtd
    else:
        novo_id = len(df) + 1
        novo_prod = pd.DataFrame([[novo_id, nome, categoria, preco, qtd]], columns=df.columns)
        st.session_state.produtos = pd.concat([st.session_state.produtos, novo_prod], ignore_index=True)

# --- interface principal ---
st.title("🛍️ ShopControl - Sistema de Monitoramento de Vendas")
st.markdown("---")

# Menu Lateral de Navegação
menu = st.sidebar.selectbox("Navegação", ["📊 Dashboard", "📦 Gestão de Estoque", "👥 Clientes & Crediário", "🛒 Registrar Venda"])

# ================= RECURSO 1: DASHBOARD =================
if menu == "📊 Dashboard":
    st.subheader("Faturamento e Saúde Financeira")
    
    # Cálculos de métricas
    total_faturado = sum(v['Total'] for c in st.session_state.clientes.values() for v in c['compras'])
    total_recebido = sum(sum(p['valor'] for p in c['pagamentos']) for c in st.session_state.clientes.values())
    total_a_receber = total_faturado - total_recebido
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Faturado", f"R$ {total_faturado:,.2f}")
    col2.metric("Total Recebido (Caixa)", f"R$ {total_recebido:,.2f}", delta_color="normal")
    col3.metric("Total em Aberto (Dívidas)", f"R$ {total_a_receber:,.2f}", delta="- Devedores")
    
    st.markdown("### 📦 Visão Geral do Estoque Atual")
    if not st.session_state.produtos.empty:
        st.dataframe(st.session_state.produtos, use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado no estoque ainda.")

# ================= RECURSO 2: GESTÃO DE ESTOQUE =================
elif menu == "📦 Gestão de Estoque":
    st.subheader("Controle de Entradas (Compras) de Produtos")
    
    aba_unitario, aba_massa = st.tabs(["🆕 Adicionar Um por Um", "📋 Colar Lista (Carga em Massa)"])
    
    with aba_unitario:
        with st.form("form_produto"):
            col1, col2 = st.columns(2)
            nome_prod = col1.text_input("Nome do Produto (Ex: Vestido Florido)")
            categoria = col2.selectbox("Categoria", ["Roupas", "Calçados", "Brinquedos"], key="cat_unitario")
            
            col3, col4 = st.columns(2)
            preco_venda = col3.number_input("Preço de Venda (R$)", min_value=0.0, step=1.0, key="preco_unitario")
            qtd_entrada = col4.number_input("Quantidade Comprada (Entrada)", min_value=1, step=1, key="qtd_unitario")
            
            btn_produto = st.form_submit_button("Cadastrar / Adicionar Estoque")
            
        if btn_produto and nome_prod:
            adicionar_produto(nome_prod, categoria, preco_venda, qtd_entrada)
            st.success(f"Estoque atualizado: +{qtd_entrada} unidades de '{nome_prod}'!")
            st.rerun()
            
    with aba_massa:
        st.markdown("""
        **Como usar:** Cole sua lista abaixo separando as informações por vírgula. Siga exatamente este modelo:
```text
        Calça Moletom, Roupas, 89.90, 15
        Tênis Corrida, Calçados, 199.00, 8
        Boneca de Pano, Brinquedos, 45.00, 20
        ```
        """)
        texto_colado = st.text_area("Cole as linhas do seu estoque aqui:", height=200, placeholder="Nome, Categoria, Preço, Quantidade")
        
        if st.button("Processar e Salvar Lista"):
            if texto_colado.strip():
                linhas = texto_colado.strip().split("\n")
                sucessos = 0
                erros = 0
                
                for linha in hashtags:
                    try:
                        partes = [p.strip() for p in linha.split(",")]
                        if len(partes) == 4:
                            nome = partes[0]
                            cat = partes[1] if partes[1] in ["Roupas", "Calçados", "Brinquedos"] else "Roupas"
                            preco = float(partes[2])
                            qtd = int(partes[3])
                            
                            adicionar_produto(nome, cat, preco, qtd)
                            sucessos += 1
                        else:
                            erros += 1
                    except Exception:
                        erros += 1
                
                if sucessos > 0:
                    st.success(f"Sucesso! {sucessos} produtos foram adicionados/atualizados no estoque.")
                if erros > 0:
                    st.error(f"Aviso: {erros} linhas estavam fora do padrão e foram puladas.")
                if sucessos > 0:
                    st.rerun()

# ================= RECURSO 3: REGISTRAR VENDA (CADASTRO DIRETO) =================
elif menu == "🛒 Registrar Venda":
    st.subheader("Venda Direta e Cadastro de Cliente")
    
    if st.session_state.produtos.empty:
        st.warning("Cadastre produtos no estoque antes de realizar uma venda.")
    else:
        # Aqui o lojista digita ou escolhe um cliente existente
        clientes_existentes = list(st.session_state.clientes.keys())
        
        col_c1, col_c2 = st.columns([2, 1])
        nome_cliente = col_c1.text_input("Nome do Cliente (Se não existir, será cadastrado na hora)").strip()
        
        if clientes_existentes:
            col_c2.markdown("<br>", unsafe_allow_html=True) # Alinhamento visual
            st.info(f"Clientes já cadastrados: {', '.join(clientes_existentes)}")

        st.markdown("---")
        
        # Seleção de múltiplos produtos do estoque padrão
        produtos_disponiveis = st.session_state.produtos['Nome'].tolist()
        produtos_selecionados = st.multiselect("Selecione os produtos comprados", produtos_disponiveis)
        
        carrinho = {}
        total_venda = 0.0
        
        if produtos_selecionados:
            st.markdown("#### Ajuste as Quantidades:")
            for prod in produtos_selecionados:
                estoque_max = int(st.session_state.produtos.loc[st.session_state.produtos['Nome'] == prod, 'Estoque Atual'].values[0])
                preco_un = float(st.session_state.produtos.loc[st.session_state.produtos['Nome'] == prod, 'Preço Venda'].values[0])
                
                if estoque_max <= 0:
                    st.error(f"Produto '{prod}' está sem estoque disponível!")
                    continue
                
                # Input de quantidade que você pediu
                qtd = st.number_input(f"{prod} (R$ {preco_un:.2f} cada | Disp: {estoque_max})", min_value=1, max_value=estoque_max, key=f"qtd_{prod}")
                carrinho[prod] = {'qtd': qtd, 'preco': preco_un}
                total_venda += (preco_un * qtd)
            
            st.markdown(f"### **Total da Compra: R$ {total_venda:,.2f}**")
            
            if st.button("Finalizar Venda e Registrar"):
                if not nome_cliente:
                    st.error("Por favor, digite o nome do cliente para prosseguir.")
                elif not carrinho:
                    st.error("Selecione produtos válidos e com estoque disponível.")
                else:
                    # Dar baixa automática no estoque
                    for prod, info in carrinho.items():
                        st.session_state.produtos.loc[st.session_state.produtos['Nome'] == prod, 'Estoque Atual'] -= info['qtd']
                    
                    # Criação automática do cliente no sistema se ele for novo
                    if nome_cliente not in st.session_state.clientes:
                        st.session_state.clientes[nome_cliente] = {'compras': [], 'pagamentos': []}
                    
                    # Registrar a compra no histórico
                    data_atual = datetime.now().strftime("%d/%m/%Y")
                    st.session_state.clientes[nome_cliente]['compras'].append({
                        'data': data_atual,
                        'itens': [f"{info['qtd']}x {prod}" for prod, info in carrinho.items()],
                        'Total': total_venda
                    })
                    
                    st.success(f"Sucesso! Cliente '{nome_cliente}' registrado e compra computada!")
                    st.rerun()

# ================= RECURSO 4: CLIENTES & CREDIÁRIO =================
elif menu == "👥 Clientes & Crediário":
    st.subheader("Histórico de Clientes e Amortização de Dívidas")
    
    if not st.session_state.clientes:
        st.info("Nenhuma venda realizada até o momento.")
    else:
        st.markdown("### 📋 Painel Geral de Clientes (Controle de Dívidas e Valores Pagos)")
        lista_geral_clientes = []
        for nome, dados in st.session_state.clientes.items():
            total_comprado = sum(c['Total'] for c in dados['compras'])
            total_pago = sum(p['valor'] for p in dados['pagamentos'])
            saldo_devedor = total_comprado - total_pago
            lista_geral_clientes.append({
                "Nome do Cliente": nome,
                "Total Comprado (R$)": total_comprado,
                "Total Pago (R$)": total_pago,
                "Saldo Devedor (R$)": saldo_devedor
            })
        df_geral_clientes = pd.DataFrame(lista_geral_clientes)
        st.dataframe(df_geral_clientes, use_container_width=True)
        st.markdown("---")
        
        st.markdown("### 🔍 Gerenciamento Individual")
        cliente_sel = st.selectbox("Selecione o Cliente para detalhar ou dar baixa", list(st.session_state.clientes.keys()))
        
        dados_cliente = st.session_state.clientes[cliente_sel]
        
        total_comprado = sum(c['Total'] for c in dados_cliente['compras'])
        total_pago = sum(p['valor'] for p in dados_cliente['pagamentos'])
        saldo_devedor = total_comprado - total_pago
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Comprado", f"R$ {total_comprado:,.2f}")
        c2.metric("Total Pago", f"R$ {total_pago:,.2f}", delta_color="inverse")
        c3.metric("Saldo Devedor Atual", f"R$ {saldo_devedor:,.2f}", delta="- Restante")
        
        st.markdown("### 💰 Registrar Pagamento / Abatimento")
        if saldo_devedor > 0:
            with st.form("form_pagamento"):
                valor_pago = st.number_input("Valor pago pelo cliente (R$)", min_value=0.01, max_value=float(saldo_devedor), step=10.0)
                btn_pagar = st.form_submit_button("Confirmar Recebimento")
                
                if btn_pagar:
                    data_pagto = datetime.now().strftime("%d/%m/%Y às %H:%M")
                    dados_cliente['pagamentos'].append({
                        'data': data_pagto,
                        'valor': valor_pago
                    })
                    st.success(f"Abatimento de R$ {valor_pago:.2f} processado para {cliente_sel}!")
                    st.rerun()
        else:
            st.success("🎉 Este cliente está com as contas em dia!")
            
        aba1, aba2 = st.tabs(["📋 Extrato de Compras (Saídas)", "💵 Histórico de Pagamentos (Entradas)"])
        
        with aba1:
            if dados_cliente['compras']:
                df_compras = pd.DataFrame(dados_cliente['compras'])
                st.dataframe(df_compras, use_container_width=True)
            else:
                st.write("Sem compras registradas.")
                
        with aba2:
            if dados_cliente['pagamentos']:
                df_pagos = pd.DataFrame(dados_cliente['pagamentos'])
                st.dataframe(df_pagos, use_container_width=True)
            else:
                st.write("Nenhum pagamento efetuado ainda.")
