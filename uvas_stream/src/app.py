from datetime import date
import sqlalchemy
import streamlit as st
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database import Base, DATABASE_URL, engine, session_scope
from models import GrapeVariety, HarvestLot, Producer


st.set_page_config(page_title="Uva Viva", page_icon="🍇", layout="wide")
Base.metadata.create_all(bind=engine)

st.markdown(
    """
    <style>
    :root { --ink: #25342c; --leaf: #385b45; --wine: #8e3f52; --paper: #f7f5ef; }
    .stApp { background: var(--paper); color: var(--ink); }
    [data-testid="stSidebar"] { background: #e9eee7; border-right: 1px solid #d5ddd3; }
    .hero { padding: 1.5rem 0 1rem; border-bottom: 1px solid #d5ddd3; margin-bottom: 1.5rem; }
    .hero-kicker { color: var(--wine); text-transform: uppercase; font-size: .76rem; font-weight: 700; letter-spacing: .08em; }
    .hero h1 { color: var(--ink); font-size: 2.45rem; line-height: 1.1; margin: .35rem 0; }
    .hero p { color: #536258; max-width: 760px; margin-bottom: .2rem; }
    div[data-testid="stMetric"] { background: #fff; padding: 1rem; border: 1px solid #dfe4dc; border-radius: 6px; }
    div[data-testid="stMetricLabel"] { color: #536258; }
    .grape-note { border-left: 4px solid var(--wine); padding: .5rem 1rem; background: #fff; }
    h2, h3 { color: var(--leaf); }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_records(model):
    with session_scope() as session:
        return list(session.scalars(select(model).order_by(model.id)))


def show_table(records, columns):
    if not records:
        st.info("Ainda não há registros. Use o formulário abaixo para adicionar o primeiro.")
        return
    st.dataframe(
        [{label: getter(record) for label, getter in columns.items()} for record in records],
        use_container_width=True,
        hide_index=True,
    )


def perform_mutation(operation, success_message):
    try:
        with session_scope() as session:
            operation(session)
        st.success(success_message)
        st.rerun()
    except IntegrityError:
        st.error("Não foi possível salvar: confira campos únicos e vínculos usados por outros registros.")
    except Exception as error:
        st.error(f"Não foi possível concluir a operação: {error}")


def variety_page():
    st.title("Variedades")
    st.caption("Registre castas, características e usos comuns das uvas.")
    records = load_records(GrapeVariety)
    show_table(
        records,
        {
            "Nome": lambda item: item.name,
            "Cor": lambda item: item.color,
            "Origem": lambda item: item.origin,
            "Doçura": lambda item: item.sweetness,
            "Descrição": lambda item: item.description,
        },
    )

    with st.expander("Adicionar variedade", expanded=not records):
        with st.form("create_variety", clear_on_submit=True):
            name = st.text_input("Nome da variedade")
            color = st.selectbox("Cor", ["Branca", "Rosada", "Tinta", "Outra"])
            origin = st.text_input("Origem")
            sweetness = st.selectbox("Perfil de sabor", ["Seca", "Equilibrada", "Doce"])
            description = st.text_area("Descrição e usos", placeholder="Ex.: consumo in natura, suco ou vinho")
            submitted = st.form_submit_button("Criar variedade", type="primary")
        if submitted:
            if not name.strip() or not origin.strip():
                st.warning("Informe o nome e a origem.")
            else:
                perform_mutation(
                    lambda session: session.add(
                        GrapeVariety(name=name.strip(), color=color, origin=origin.strip(), sweetness=sweetness, description=description.strip())
                    ),
                    "Variedade criada.",
                )

    if records:
        with st.expander("Editar variedade"):
            selected = st.selectbox("Escolha a variedade", records, format_func=lambda item: item.name, key="edit_variety")
            with st.form("update_variety"):
                name = st.text_input("Nome", selected.name)
                color_options = ["Branca", "Rosada", "Tinta", "Outra"]
                color = st.selectbox("Cor", color_options, index=color_options.index(selected.color) if selected.color in color_options else 0)
                origin = st.text_input("Origem", selected.origin)
                sweetness_options = ["Seca", "Equilibrada", "Doce"]
                sweetness = st.selectbox("Perfil de sabor", sweetness_options, index=sweetness_options.index(selected.sweetness) if selected.sweetness in sweetness_options else 0)
                description = st.text_area("Descrição e usos", selected.description)
                submitted = st.form_submit_button("Salvar alterações", type="primary")
            if submitted:
                if not name.strip() or not origin.strip():
                    st.warning("Informe o nome e a origem.")
                else:
                    def update(session):
                        item = session.get(GrapeVariety, selected.id)
                        item.name, item.color, item.origin = name.strip(), color, origin.strip()
                        item.sweetness, item.description = sweetness, description.strip()
                    perform_mutation(update, "Variedade atualizada.")

        with st.expander("Excluir variedade"):
            selected = st.selectbox("Variedade para excluir", records, format_func=lambda item: item.name, key="delete_variety")
            if st.button("Excluir variedade", key="delete_variety_button", type="secondary"):
                with session_scope() as session:
                    used = session.scalar(select(HarvestLot.id).where(HarvestLot.variety_id == selected.id).limit(1))
                if used:
                    st.error("Esta variedade está vinculada a lotes. Exclua ou edite esses lotes primeiro.")
                else:
                    perform_mutation(lambda session: session.delete(session.get(GrapeVariety, selected.id)), "Variedade excluída.")


def producer_page():
    st.title("Produtores")
    st.caption("Conheça as pessoas e propriedades que cultivam as uvas cadastradas.")
    records = load_records(Producer)
    show_table(
        records,
        {
            "Produtor": lambda item: item.name,
            "Município": lambda item: item.municipality,
            "País": lambda item: item.country,
            "E-mail": lambda item: item.email,
            "Telefone": lambda item: item.phone,
            "Cultivo sustentável": lambda item: "Sim" if item.sustainable else "Não informado",
        },
    )

    with st.expander("Adicionar produtor", expanded=not records):
        with st.form("create_producer", clear_on_submit=True):
            name = st.text_input("Nome do produtor ou propriedade")
            municipality = st.text_input("Município")
            country = st.text_input("País", value="Brasil")
            email = st.text_input("E-mail")
            phone = st.text_input("Telefone")
            sustainable = st.checkbox("Informou práticas de cultivo sustentável")
            submitted = st.form_submit_button("Criar produtor", type="primary")
        if submitted:
            if not name.strip() or not municipality.strip():
                st.warning("Informe o nome e o município.")
            else:
                perform_mutation(
                    lambda session: session.add(
                        Producer(name=name.strip(), municipality=municipality.strip(), country=country.strip() or "Brasil", email=email.strip(), phone=phone.strip(), sustainable=sustainable)
                    ),
                    "Produtor criado.",
                )

    if records:
        with st.expander("Editar produtor"):
            selected = st.selectbox("Escolha o produtor", records, format_func=lambda item: item.name, key="edit_producer")
            with st.form("update_producer"):
                name = st.text_input("Nome do produtor ou propriedade", selected.name)
                municipality = st.text_input("Município", selected.municipality)
                country = st.text_input("País", selected.country)
                email = st.text_input("E-mail", selected.email)
                phone = st.text_input("Telefone", selected.phone)
                sustainable = st.checkbox("Informou práticas de cultivo sustentável", selected.sustainable)
                submitted = st.form_submit_button("Salvar alterações", type="primary")
            if submitted:
                if not name.strip() or not municipality.strip():
                    st.warning("Informe o nome e o município.")
                else:
                    def update(session):
                        item = session.get(Producer, selected.id)
                        item.name, item.municipality = name.strip(), municipality.strip()
                        item.country, item.email, item.phone = country.strip() or "Brasil", email.strip(), phone.strip()
                        item.sustainable = sustainable
                    perform_mutation(update, "Produtor atualizado.")

        with st.expander("Excluir produtor"):
            selected = st.selectbox("Produtor para excluir", records, format_func=lambda item: item.name, key="delete_producer")
            if st.button("Excluir produtor", key="delete_producer_button"):
                with session_scope() as session:
                    used = session.scalar(select(HarvestLot.id).where(HarvestLot.producer_id == selected.id).limit(1))
                if used:
                    st.error("Este produtor está vinculado a lotes. Exclua ou edite esses lotes primeiro.")
                else:
                    perform_mutation(lambda session: session.delete(session.get(Producer, selected.id)), "Produtor excluído.")


def harvest_page():
    st.title("Lotes de colheita")
    st.caption("Acompanhe origem, volume e valor estimado de cada lote de uvas.")
    with session_scope() as session:
        records = list(session.scalars(select(HarvestLot).order_by(HarvestLot.harvest_date.desc())))
        varieties = list(session.scalars(select(GrapeVariety).order_by(GrapeVariety.name)))
        producers = list(session.scalars(select(Producer).order_by(Producer.name)))
        rows = [
            {
                "Código": item.code,
                "Variedade": item.variety.name,
                "Produtor": item.producer.name,
                "Colheita": item.harvest_date.strftime("%d/%m/%Y"),
                "Quantidade (kg)": item.quantity_kg,
                "Preço/kg (R$)": item.price_per_kg,
                "Valor estimado (R$)": item.quantity_kg * item.price_per_kg,
                "Observações": item.notes,
            }
            for item in records
        ]
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("Ainda não há lotes. Cadastre ao menos uma variedade e um produtor antes de criar um lote.")

    if varieties and producers:
        with st.expander("Adicionar lote", expanded=not records):
            with st.form("create_harvest", clear_on_submit=True):
                code = st.text_input("Código do lote")
                variety = st.selectbox("Variedade", varieties, format_func=lambda item: item.name)
                producer = st.selectbox("Produtor", producers, format_func=lambda item: item.name)
                harvest_date = st.date_input("Data da colheita", value=date.today())
                quantity = st.number_input("Quantidade (kg)", min_value=0.01, step=1.0)
                price = st.number_input("Preço por kg (R$)", min_value=0.0, step=0.5, format="%.2f")
                notes = st.text_area("Observações")
                submitted = st.form_submit_button("Criar lote", type="primary")
            if submitted:
                if not code.strip():
                    st.warning("Informe um código para o lote.")
                else:
                    perform_mutation(
                        lambda session: session.add(
                            HarvestLot(code=code.strip(), variety_id=variety.id, producer_id=producer.id, harvest_date=harvest_date, quantity_kg=quantity, price_per_kg=price, notes=notes.strip())
                        ),
                        "Lote criado.",
                    )

    if records:
        with st.expander("Editar lote"):
            selected = st.selectbox("Escolha o lote", records, format_func=lambda item: item.code, key="edit_harvest")
            with st.form("update_harvest"):
                code = st.text_input("Código", selected.code)
                variety = st.selectbox("Variedade", varieties, index=next(i for i, item in enumerate(varieties) if item.id == selected.variety_id), format_func=lambda item: item.name, key="update_harvest_variety")
                producer = st.selectbox("Produtor", producers, index=next(i for i, item in enumerate(producers) if item.id == selected.producer_id), format_func=lambda item: item.name, key="update_harvest_producer")
                harvest_date = st.date_input("Data da colheita", selected.harvest_date)
                quantity = st.number_input("Quantidade (kg)", min_value=0.01, value=float(selected.quantity_kg), step=1.0)
                price = st.number_input("Preço por kg (R$)", min_value=0.0, value=float(selected.price_per_kg), step=0.5, format="%.2f")
                notes = st.text_area("Observações", selected.notes)
                submitted = st.form_submit_button("Salvar alterações", type="primary")
            if submitted:
                if not code.strip():
                    st.warning("Informe um código para o lote.")
                else:
                    def update(session):
                        item = session.get(HarvestLot, selected.id)
                        item.code, item.variety_id, item.producer_id = code.strip(), variety.id, producer.id
                        item.harvest_date, item.quantity_kg, item.price_per_kg = harvest_date, quantity, price
                        item.notes = notes.strip()
                    perform_mutation(update, "Lote atualizado.")

        with st.expander("Excluir lote"):
            selected = st.selectbox("Lote para excluir", records, format_func=lambda item: item.code, key="delete_harvest")
            if st.button("Excluir lote", key="delete_harvest_button"):
                perform_mutation(lambda session: session.delete(session.get(HarvestLot, selected.id)), "Lote excluído.")


def dashboard_page():
    st.markdown(
        """
        <div class="hero">
          <div class="hero-kicker">Caderno de viticultura</div>
          <h1>Uva Viva</h1>
          <p>Um catálogo para descobrir variedades, conhecer quem cultiva e acompanhar cada colheita da videira à mesa.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with session_scope() as session:
        variety_count = session.query(GrapeVariety).count()
        producer_count = session.query(Producer).count()
        harvests = list(session.scalars(select(HarvestLot)))
    total_kg = sum(item.quantity_kg for item in harvests)
    estimated_value = sum(item.quantity_kg * item.price_per_kg for item in harvests)
    metrics = st.columns(4)
    metrics[0].metric("Variedades", variety_count)
    metrics[1].metric("Produtores", producer_count)
    metrics[2].metric("Uvas registradas", f"{total_kg:,.1f} kg".replace(",", "X").replace(".", ",").replace("X", "."))
    metrics[3].metric("Valor estimado", f"R$ {estimated_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.subheader("Um fruto, muitas expressões")
    st.write(
        "A uva ( *Vitis vinifera* e espécies aparentadas) está entre as frutas cultivadas há mais tempo. "
        "As variedades diferem em cor, acidez, doçura, textura e adaptação ao clima; por isso, uma mesma fruta "
        "pode ser apreciada fresca, transformada em suco, passa ou vinho."
    )
    st.markdown(
        """
        <div class="grape-note"><strong>Para observar no catálogo:</strong> castas de mesa costumam valorizar tamanho,
        textura e resistência da casca; uvas destinadas à vinificação são escolhidas também pelo equilíbrio
        entre açúcares, acidez, aromas e taninos. Origem e manejo completam a história de cada lote.</div>
        """,
        unsafe_allow_html=True,
    )
    st.subheader("Comece por aqui")
    st.write("Cadastre uma variedade e um produtor; depois, relacione os dois em um lote de colheita para acompanhar volume e preço.")
    st.caption(f"Banco conectado: {'MySQL' if DATABASE_URL.startswith('mysql+') else 'SQLite/local'}")


with st.sidebar:
    st.markdown("## Uva Viva")
    page = st.radio("Navegação", ["Visão geral", "Variedades", "Produtores", "Lotes de colheita"], label_visibility="collapsed")
    st.divider()
    st.caption("Caderno digital da viticultura")

if page == "Visão geral":
    dashboard_page()
elif page == "Variedades":
    variety_page()
elif page == "Produtores":
    producer_page()
else:
    harvest_page()
