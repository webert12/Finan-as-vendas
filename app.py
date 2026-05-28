import streamlit as st
import pandas as pd
from datetime import datetime
import pytz  # Biblioteca profissional para controle de fuso horário

# Configuração da página profissional
st.set_page_config(
    page_title="Ademir Trovão Azul - Gestão & Monitoramento", 
    layout="wide", 
    page_icon="⚡"
)

# --- CONFIGURAÇÃO DO HORÁRIO DE BRASÍLIA ---
def obter_data_hora_brasilia():
    fuso_brasilia = pytz.timezone('America/Sao_Paulo')
    return datetime.now(fuso_brasilia)

# --- INICIALIZAÇÃO DO BANCO DE DADOS EM MEMÓRIA ---
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
        novo_id = int(df['ID'].max() + 1) if not df.empty else 1
        novo_prod = pd.DataFrame([[novo_id, nome, categoria, preco, qtd]], columns=df.columns)
        st.session_state.produtos = pd.concat([st.session_state.produtos, novo_prod], ignore_index=True)

def gerar_relatorio_consolidado():
    vendas_produtos = {}
    for cliente, dados in st.session_state.clientes.items():
        for compra in dados['compras']:
            for item in compra['itens']:
                try:
                    partes = item.split("x ", 1)
                    if len(partes) == 2:
                        qtd = int(partes[0])
                        prod = partes[1]
                        vendas_produtos[prod] = vendas_produtos.get(prod, 0) + qtd
                except:
                    pass
    if vendas_produtos:
        return pd.DataFrame(list(vendas_produtos.items()), columns=["📦 Produto", "🔢 Total Vendido"])
    return pd.DataFrame(columns=["📦 Produto", "🔢 Total Vendido"])

# --- INTERFACE PRINCIPAL ---
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>⚡ Ademir Trovão Azul</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold; color: #4B5563;'>Sistema Comercial de Monitoramento de Vendas & Estoque</p>", unsafe_allow_html=True)
st.markdown("---")

# Menu Lateral Comercial
st.sidebar.markdown("<h2 style='color: #1E3A8A; text-align:center;'>Menu de Controle</h2>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("Escolha a tela:", ["📊 Dashboard", "📦 Gestão de Estoque", "👥 Clientes & Crediário", "🛒 Registrar Venda"])

# ================= RECURSO 1: DASHBOARD =================
if menu == "📊 Dashboard":
    st.subheader("📊 Faturamento e Saúde Financeira")
    
    total_faturado = sum(v['Total'] for c in st.session_state.clientes.values() for v in c['compras'])
    total_recebido = sum(sum(p['valor'] for p in c['pagamentos']) for c in st.session_state.clientes.values())
    total_a_receber = total_faturado - total_recebido
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.container(border=True).metric("Total Faturado", f"R$ {total_faturado:,.2f}")
    with col2:
        st.container(border=True).metric("Total Recebido (Caixa)", f"R$ {total_recebido:,.2f}")
    with col3:
        st.container(border=True).metric("Total em Aberto (Dívidas)", f"R$ {total_a_receber:,.2f}", delta="- Devedores", delta_color="inverse")
    
    # [REQUISITO AMALELO/VERMELHO] - Relatório consolidado oculto
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🟡 CLIQUE AQUI PARA VER O RELATÓRIO OCULTO DE SAÍDAS (Apenas Produtos e Qtds)"):
        st.markdown("<h4 style='color: #1E3A8A;'>📋 Produtos mais Saídos</h4>", unsafe_allow_html=True)
        df_consolidado = gerar_relatorio_consolidado()
        if not df_consolidado.empty:
            st.dataframe(df_consolidado, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma venda registrada para processar o relatório.")
            
    st.markdown("### 📦 Visão Visual do Estoque Atual")
    if not st.session_state.produtos.empty:
        st.data_editor(
            st.session_state.produtos,
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Preço Venda": st.column_config.NumberColumn("Preço de Venda", format="R$ %.2f"),
                "Estoque Atual": st.column_config.ProgressColumn("Nível de Estoque", help="Quantidade disponível", min_value=0, max_value=100, format="%d un")
            },
            disabled=True,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhum produto cadastrado no estoque ainda.")

# ================= RECURSO 2: GESTÃO DE ESTOQUE =================
elif menu == "📦 Gestão de Estoque":
    st.subheader("📦 Controle e Alteração de Estoque")
    
    aba_unitario, aba_massa, aba_gerenciar = st.tabs(["🆕 Adicionar Novo", "📋 Carga em Massa", "🛠️ Alterar / Excluir Existente"])
    
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
            st.success(f"Estoque updated: +{qtd_entrada} unidades de '{nome_prod}'!")
            st.rerun()
            
    with aba_massa:
        st.markdown("""
        **Modelo exigido:** `Nome, Categoria, Preço, Quantidade`
```text
        Calça Moletom, Roupas, 89.90, 15
        Tênis Corrida, Calçados, 199.00, 8
        ```
""")
texto_colado = st.text_area("Cole as linhas do seu estoque aqui:", height=150, placeholder="Nome, Categoria, Preço, Quantidade")

if st.button("Processar e Salvar Lista"):
    if texto_colado.strip():
        linhas = texto_colado.strip().split("\n")
        sucessos = 0
        for linha in linhas:
            try:
                partes = [p.strip() for p in linha.split(",")]
                if len(partes) == 4:
                    nome = partes[0]
                    cat = partes[1] if partes[1] in ["Roupas", "Calçados", "Brinquedos"] else "Roupas"
                    preco = float(partes[2])
                    qtd = int(partes[3])
                    adicionar_produto(nome, cat, preco, qtd)
                    sucessos += 1
            except Exception:
                pass
        if sucessos > 0:
            st.success(f"Sucesso! {sucessos} produtos processados.")
            st.rerun()

with aba_gerenciar:
if st.session_state.produtos.empty:
    st.info("Não há produtos no estoque para gerenciar.")
else:
    st.markdown("#### Selecione um item cadastrado para modificar:")
    lista_nomes_produtos = st.session_state.produtos['Nome'].tolist()
    prod_selecionado = st.selectbox("Escolha o Produto:", lista_nomes_produtos)
    
    linha_produto = st.session_state.produtos.loc[st.session_state.produtos['Nome'] == prod_selecionado].iloc[0]
    estoque_atual = int(linha_produto['Estoque Atual'])
    preco_atual = float(linha_produto['Preço Venda'])
    
    st.warning(f"Status Atual de **{prod_selecionado}**: {estoque_atual} unidades em estoque | Preço atual: R$ {preco_atual:.2f}")
    
    col_alt1, col_alt2 = st.columns(2)
    
    # Caixa da esquerda: Ajuste de estoque
    with col_alt1:
        st.markdown("##### ➕ Entrada / Ajuste Positivo")
        qtd_mais = st.number_input("Adicionar quantas unidades ao estoque?", min_value=0, step=1, value=0, key="add_qtd_mais")
        novo_preco = st.number_input("Alterar preço de venda para: (R$)", min_value=0.0, value=preco_atual, step=5.0, key="up_novo_preco")
        
        if st.button("Salvar Alterações de Estoque/Preço"):
            if qtd_mais > 0 or novo_preco != preco_atual:
                st.session_state.produtos.loc[st.session_state.produtos['Nome'] == prod_selecionado, 'Estoque Atual'] += qtd_mais
                st.session_state.produtos.loc[st.session_state.produtos['Nome'] == prod_selecionado, 'Preço Venda'] = novo_preco
                st.success(f"Ajuste realizado! {prod_selecionado} agora tem {estoque_atual + qtd_mais} unidades.")
                st.rerun()
    
    # Caixa da direita: Exclusão de itens
    with col_alt2:
        st.markdown("##### ❌ Exclusão de Mercadoria")
        st.write("Deseja retirar esse item permanentemente?")
        confirmar_exclusao = st.checkbox("Sim, quero apagar este produto.")
        
        if st.button("Remover Produto do Sistema", type="primary"):
            if confirmar_exclusao:
                st.session_state.produtos = st.session_state.produtos[st.session_state.produtos['Nome'] != prod_selecionado]
                st.success(f"O produto '{prod_selecionado}' foi deletado.")
                st.rerun()
            else:
                st.error("Marque a caixa de confirmação para prosseguir.")

# ================= RECURSO 3: REGISTRAR VENDA =================
elif menu == "🛒 Registrar Venda":
st.subheader("🛒 Venda Direta e Cadastro Automático")

if st.session_state.produtos.empty:
st.warning("Cadastre produtos no estoque antes de realizar uma venda.")
else:
# [REQUISITO AZUL/VERDE] - Zona de Limpar Tela Integrada
with st.container(border=True):
    col_b1, col_b2 = st.columns([4, 1])
    with col_b1:
        st.markdown("<p style='margin:0; font-weight:bold; color:#1E3A8A;'>Painel de Registro</p>", unsafe_allow_html=True)
    with col_b2:
        if st.button("🧹 Limpar Tela", use_container_width=True, type="secondary"):
            st.rerun()
            
clientes_existentes = list(st.session_state.clientes.keys())

with st.container(border=True):
    nome_cliente = st.text_input("👤 Nome do Cliente (Se for novo, cadastraremos ao finalizar)").strip()
    if clientes_existentes:
        st.caption(f"**Clientes ativos no sistema:** {', '.join(clientes_existentes)}")

st.markdown("<br>", unsafe_allow_html=True)

produtos_disponiveis = st.session_state.produtos['Nome'].tolist()
produtos_selecionados = st.multiselect("🛍️ Selecione as mercadorias vendidas", produtos_disponiveis)

carrinho = {}
total_venda = 0.0

if produtos_selecionados:
    st.markdown("#### 🔢 Defina as quantidades:")
    for prod in produtos_selecionados:
        estoque_max = int(st.session_state.produtos.loc[st.session_state.produtos['Nome'] == prod, 'Estoque Atual'].values[0])
        preco_un = float(st.session_state.produtos.loc[st.session_state.produtos['Nome'] == prod, 'Preço Venda'].values[0])
        
        if estoque_max <= 0:
            st.error(f"Produto '{prod}' está esgotado no estoque!")
            continue
        
        with st.container(border=True):
            qtd = st.number_input(f"{prod} — Preço: R$ {preco_un:.2f} (Estoque atual: {estoque_max})", min_value=1, max_value=estoque_max, key=f"qtd_{prod}")
            carrinho[prod] = {'qtd': qtd, 'preco': preco_un}
            total_venda += (preco_un * qtd)
    
    st.markdown(f"<h2 style='color:#1E3A8A;'>Total Geral: R$ {total_venda:,.2f}</h2>", unsafe_allow_html=True)
    
    if st.button("🚀 Confirmar Venda e Lançar Débito"):
        if not nome_cliente:
            st.error("Insira o nome do cliente para salvar.")
        elif not carrinho:
            st.error("O carrinho não possui itens válidos.")
        else:
            for prod, info in carrinho.items():
                st.session_state.produtos.loc[st.session_state.produtos['Nome'] == prod, 'Estoque Atual'] -= info['qtd']
            
            if nome_cliente not in st.session_state.clientes:
                st.session_state.clientes[nome_cliente] = {'compras': [], 'pagamentos': []}
            
            data_atual = obter_data_hora_brasilia().strftime("%d/%m/%Y")
            st.session_state.clientes[nome_cliente]['compras'].append({
                'data': data_atual,
                'itens': [f"{info['qtd']}x {prod}" for prod, info in carrinho.items()],
                'Total': total_venda
            })
            
            st.success(f"Venda concluída com sucesso para {nome_cliente}!")
            st.rerun()

# ================= RECURSO 4: CLIENTES & CREDIÁRIO =================
elif menu == "👥 Clientes & Crediário":
st.subheader("👥 Painel de Controle de Clientes e Recebimentos")

if not st.session_state.clientes:
st.info("Nenhuma movimentação de clientes registrada.")
else:
st.markdown("### 📋 Painel Geral de Contas")
lista_geral_clientes = []
for nome, dados in st.session_state.clientes.items():
    total_comprado = sum(c['Total'] for c in dados['compras'])
    total_pago = sum(p['valor'] for p in dados['pagamentos'])
    saldo_devedor = total_comprado - total_pago
    lista_geral_clientes.append({
        "Nome do Cliente": nome,
        "Total Comprado": total_comprado,
        "Total Pago": total_pago,
        "Saldo Devedor": saldo_devedor
    })
df_geral_clientes = pd.DataFrame(lista_geral_clientes)

st.data_editor(
    df_geral_clientes,
    column_config={
        "Total Comprado": st.column_config.NumberColumn("Total Comprado", format="R$ %.2f"),
        "Total Pago": st.column_config.NumberColumn("Total Já Pago", format="R$ %.2f"),
        "Saldo Devedor": st.column_config.NumberColumn("Saldo Devedor Atual", format="R$ %.2f"),
    },
    disabled=True, use_container_width=True, hide_index=True
)

st.markdown("---")
st.markdown("### 🔍 Ficha e Histórico Individual")
cliente_sel = st.selectbox("Selecione o cliente para gerenciar:", list(st.session_state.clientes.keys()))

dados_cliente = st.session_state.clientes[cliente_sel]
total_comprado = sum(c['Total'] for c in dados_cliente['compras'])
total_pago = sum(p['valor'] for p in dados_cliente['pagamentos'])
saldo_devedor = total_comprado - total_pago

c1, c2, c3 = st.columns(3)
c1.metric("Total Comprado", f"R$ {total_comprado:,.2f}")
c2.metric("Total Pago", f"R$ {total_pago:,.2f}")
c3.metric("Dívida Restante", f"R$ {saldo_devedor:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("#### 💰 Registrar Novo Abatimento")
    if saldo_devedor > 0:
        with st.form("form_pagamento"):
            valor_pago = st.number_input("Valor entregue pelo cliente (R$)", min_value=0.01, max_value=float(saldo_devedor), step=5.0)
            btn_pagar = st.form_submit_button("Confirmar e Dar Desconto na Dívida")
            
            if btn_pagar:
                data_pagto = obter_data_hora_brasilia().strftime("%d/%m/%Y às %H:%M")
                dados_cliente['pagamentos'].append({
                    'data': data_pagto,
                    'valor': valor_pago
                })
                st.success(f"Excelente! R$ {valor_pago:.2f} descontados da conta de {cliente_sel}!")
                st.rerun()
    else:
        st.success("🎉 Ótimo! Este cliente não possui pendências financeiras.")
    
# [REQUISITO HISTÓRICO CONDICIONAL E EXCLUSÃO] 
st.markdown("### 📋 Histórico Detalhado & Remoções")
aba1, aba2 = st.tabs(["📋 Saídas (O que comprou e Detalhes)", "💵 Entradas (Pagamentos feitos)"])

with aba1:
    if dados_cliente['compras']:
        df_compras = pd.DataFrame(dados_cliente['compras'])
        st.dataframe(
            df_compras,
            column_config={"Total": st.column_config.NumberColumn("Valor Total", format="R$ %.2f")},
            use_container_width=True, hide_index=True
        )
        
        # Interface para remover item do histórico de compras
        with st.expander("❌ Remover Compra do Histórico"):
            opcoes_compras = [f"{i} - Data: {c['data']} | Total: R${c['Total']:.2f}" for i, c in enumerate(dados_cliente['compras'])]
            compra_remover = st.selectbox("Escolha a compra para excluir:", opcoes_compras, key="del_compra_sel")
            if st.button("Excluir Registro de Compra Selecionado", type="primary"):
                idx = int(compra_remover.split(" - ")[0])
                dados_cliente['compras'].pop(idx)
                st.success("Compra removida do histórico com sucesso!")
                st.rerun()
    else:
        st.write("Sem registros de compras.")
        
with aba2:
    if dados_cliente['pagamentos']:
        df_pagos = pd.DataFrame(dados_cliente['pagamentos'])
        st.dataframe(
            df_pagos,
            column_config={"valor": st.column_config.NumberColumn("Valor Pago", format="R$ %.2f")},
            use_container_width=True, hide_index=True
        )
        
        # Interface para remover item do histórico de pagamentos
        with st.expander("❌ Remover Pagamento do Histórico"):
            opcoes_pagos = [f"{i} - Data: {p['data']} | Valor: R${p['valor']:.2f}" for i, p in enumerate(dados_cliente['pagamentos'])]
            pago_remover = st.selectbox("Escolha o pagamento para excluir:", opcoes_pagos, key="del_pago_sel")
            if st.button("Excluir Registro de Pagamento Selecionado", type="primary"):
                idx = int(pago_remover.split(" - ")[0])
                dados_cliente['pagamentos'].pop(idx)
                st.success("Pagamento removido do histórico com sucesso!")
                st.rerun()
    else:
        st.write("Nenhum pagamento registrado.")
