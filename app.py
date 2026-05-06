"""Application Streamlit - Concours Fonction Publique Maroc."""
import streamlit as st
from config import MINISTERES, SPECIALITES, GRADES
from scrapers import search_concours
from scrapers.pdf_extractor import download_and_extract
from scrapers.image_scraper import scrape_page_images, download_image_as_base64, get_image_mime_type
from ai_solver import generer_solution, resumer_concours, lire_image_concours

# --- Configuration de la page ---
st.set_page_config(
    page_title="Concours Fonction Publique Maroc",
    page_icon="🇲🇦",
    layout="wide",
)

# --- En-tête ---
st.title("🇲🇦 Concours de la Fonction Publique - Maroc")
st.markdown("""
Trouvez les concours de la fonction publique marocaine et obtenez des **solutions générées par IA** 
pour vous aider dans votre préparation.
""")

st.divider()

# --- Filtres dans la sidebar ---
with st.sidebar:
    st.header("🔍 Filtres de recherche")

    ministere = st.selectbox(
        "📋 Ministère",
        options=["Tous"] + MINISTERES,
        index=0,
    )

    specialite = st.selectbox(
        "🎓 Spécialité",
        options=["Toutes"] + SPECIALITES,
        index=0,
    )

    grade = st.selectbox(
        "📊 Grade",
        options=["Tous"] + GRADES,
        index=0,
    )

    st.divider()

    annee = st.slider("📅 Année", min_value=2018, max_value=2026, value=(2022, 2026))

    rechercher = st.button("🔎 Rechercher des concours", type="primary", use_container_width=True)

# --- Recherche et affichage ---
if rechercher:
    min_str = ministere if ministere != "Tous" else ""
    spec_str = specialite if specialite != "Toutes" else ""
    grade_str = grade if grade != "Tous" else ""

    if not any([min_str, spec_str, grade_str]):
        st.warning("⚠️ Veuillez sélectionner au moins un critère de recherche.")
    else:
        with st.spinner("🔄 Recherche des sujets d'épreuves..."):
            tous_resultats = search_concours(min_str, spec_str, grade_str)

        if not tous_resultats:
            st.info("ℹ️ Aucun concours trouvé pour ces critères. Essayez d'élargir votre recherche.")
        else:
            st.success(f"✅ {len(tous_resultats)} concours trouvé(s)")

            for i, concours in enumerate(tous_resultats):
                with st.expander(f"📄 {concours.titre}", expanded=(i == 0)):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown(f"**Ministère:** {concours.ministere or 'Non spécifié'}")
                        st.markdown(f"**Spécialité:** {concours.specialite or 'Non spécifiée'}")
                        st.markdown(f"**Grade:** {concours.grade or 'Non spécifié'}")

                    with col2:
                        st.markdown(f"**Année:** {concours.annee}")
                        if concours.url_source and concours.url_source.startswith("http"):
                            st.markdown(f"[🔗 Lien externe ↗]({concours.url_source})")

                    # Bouton pour charger et afficher le contenu directement
                    pdf_url = concours.url_pdf or (concours.url_source if concours.url_source and concours.url_source.endswith(".pdf") else None)
                    if pdf_url:
                        if st.button("📄 Afficher l'énoncé (PDF)", key=f"pdf_{i}"):
                            with st.spinner("⏳ Téléchargement et extraction du PDF..."):
                                contenu_pdf = download_and_extract(pdf_url, f"concours_{i}.pdf")
                                if contenu_pdf:
                                    st.success("✅ Énoncé chargé avec succès")
                                    st.text_area("📝 Contenu de l'épreuve", contenu_pdf, height=400, key=f"txt_{i}")
                                else:
                                    st.error("❌ Impossible de charger le PDF.")

                    # Bouton pour extraire les images de la page (sujets en images)
                    if concours.url_source and not pdf_url:
                        if st.button("🖼️ Extraire le sujet (images)", key=f"img_{i}"):
                            with st.spinner("⏳ Extraction des images du sujet..."):
                                images = scrape_page_images(concours.url_source)
                                if images:
                                    st.success(f"✅ {len(images)} image(s) trouvée(s)")
                                    all_text = ""
                                    for j, img_url in enumerate(images):
                                        st.image(img_url, caption=f"Page {j+1}", use_container_width=True)
                                        # Lire le contenu avec l'IA vision
                                        img_b64 = download_image_as_base64(img_url)
                                        if img_b64:
                                            with st.spinner(f"🧠 Lecture IA de l'image {j+1}..."):
                                                mime = get_image_mime_type(img_url)
                                                texte = lire_image_concours(img_b64, mime)
                                                all_text += texte + "\n\n"
                                                st.text_area(f"📝 Texte extrait - Image {j+1}", texte, height=200, key=f"imgtxt_{i}_{j}")
                                    # Stocker le contenu pour la génération de solution
                                    if all_text:
                                        st.session_state[f"contenu_{i}"] = all_text
                                else:
                                    st.warning("❌ Aucune image de sujet trouvée sur cette page.")

                    st.divider()

                    # Bouton pour générer la solution IA
                    if st.button(f"🤖 Générer la solution IA", key=f"solve_{i}"):
                        with st.spinner("🧠 L'IA génère la solution..."):
                            # Récupérer le contenu depuis différentes sources
                            contenu = st.session_state.get(f"contenu_{i}", "") or concours.contenu_epreuve or ""
                            if not contenu and concours.url_pdf:
                                contenu = download_and_extract(
                                    concours.url_pdf,
                                    f"concours_{i}.pdf"
                                )
                            # Si toujours pas de contenu, extraire depuis les images
                            if not contenu and concours.url_source:
                                images = scrape_page_images(concours.url_source)
                                for img_url in images[:3]:
                                    img_b64 = download_image_as_base64(img_url)
                                    if img_b64:
                                        mime = get_image_mime_type(img_url)
                                        contenu += lire_image_concours(img_b64, mime) + "\n\n"

                            if not contenu:
                                contenu = f"Concours: {concours.titre}\nGrade: {concours.grade}\nSpécialité: {concours.specialite}"

                            solution = generer_solution(contenu, concours.specialite, concours.grade)
                            st.markdown("### 💡 Solution générée par IA")
                            st.markdown(solution)

# --- Footer ---
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.8em;">
    🛠️ Propulsé par Streamlit, Groq AI & Open Source | 
    Les solutions sont générées par IA et sont indicatives uniquement.
</div>
""", unsafe_allow_html=True)
