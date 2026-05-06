import streamlit as st

st.set_page_config(page_title="Recipe Generator", layout="centered")

# -------------------------
# INIT NAVIGATION
# -------------------------
if "page" not in st.session_state:
    st.session_state.page = "main"


# -------------------------
# PAGE PRINCIPALE
# -------------------------
def main_page():
    st.title("🍳 Recipe Generator")

    st.write("Page principale")

    st.markdown("<div style='text-align:left'>", unsafe_allow_html=True)
    if st.button("⚙️ Détails avancés"):
        st.session_state.page = "advanced"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------
# PAGE AVANCÉE
# -------------------------
def advanced_page():
    st.title("🔧 Détails avancés")

    st.write("Réglages et paramètres fins de l'algorithme")

    mutation_rate = st.slider("Mutation rate", 0.0, 1.0, 0.2)
    elitism = st.checkbox("Elitism activé", value=True)
    diversity = st.slider("Diversité population", 0, 100, 50)

    st.divider()

    if st.button("⬅ Retour"):
        st.session_state.page = "main"
        st.rerun()


# -------------------------
# ROUTING
# -------------------------
if st.session_state.page == "main":
    main_page()
else:
    advanced_page()