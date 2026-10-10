import streamlit as st
import unicodedata

st.set_page_config(page_title="Manejo Antitrombótico", page_icon="🩸", layout="centered")

st.markdown("""
<style>
    div.stButton > button { min-height: 3.5rem; font-size: 1.1rem !important; border-radius: 8px; }
    div.stRadio > div[role="radiogroup"] > label { padding-top: 0.8rem; padding-bottom: 0.8rem; font-size: 1.1rem; }
    p, .st-bb { font-size: 1.1rem; }
    div[data-testid="stCheckbox"] > label { padding-top: 0.5rem; padding-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# Marcador de versión
st.markdown("<div style='text-align: right; font-size: 0.8em; color: #888;'>v0.17 (10 Oct - 16:38)</div>", unsafe_allow_html=True)

st.title("Manejo Perioperatorio")
st.caption("Herramienta de soporte clínico basada en el Consenso SEC 2025")
st.divider()

if 'chads_score' not in st.session_state: st.session_state.chads_score = 0
if 'mostrar_calc' not in st.session_state: st.session_state.mostrar_calc = False
if 'crcl_val' not in st.session_state: st.session_state.crcl_val = 87
if 'mostrar_calc_renal' not in st.session_state: st.session_state.mostrar_calc_renal = False
if 'riesgo_qx' not in st.session_state: st.session_state.riesgo_qx = "Bajo"
if 'mostrar_cat_qx' not in st.session_state: st.session_state.mostrar_cat_qx = False

def aplicar_puntuacion(score):
    st.session_state.chads_score = score
    st.session_state.mostrar_calc = False

def toggle_calc(): st.session_state.mostrar_calc = not st.session_state.mostrar_calc
def toggle_calc_renal(): st.session_state.mostrar_calc_renal = not st.session_state.mostrar_calc_renal
def toggle_cat_qx(): st.session_state.mostrar_cat_qx = not st.session_state.mostrar_cat_qx

def aplicar_aclaramiento(valor):
    st.session_state.crcl_val = int(valor)
    st.session_state.mostrar_calc_renal = False

def aplicar_riesgo_qx(riesgo):
    st.session_state.riesgo_qx = riesgo
    st.session_state.mostrar_cat_qx = False

def quitar_tildes(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

st.subheader("1. Tratamiento actual")
tipo_farmaco = st.radio("Familia farmacológica:", ["Antiagregantes", "Anticoagulantes (AVK / ACOD)"], label_visibility="collapsed")

if tipo_farmaco == "Antiagregantes":
    farmaco = st.selectbox("Seleccione fármaco:", ["AAS", "Clopidogrel", "Prasugrel", "Ticagrelor", "Doble Antiagregación (TAPD)"])
else:
    farmaco = st.selectbox("Seleccione fármaco:", ["Sintrom / Aldocumar", "Dabigatrán", "Rivaroxabán", "Apixabán", "Edoxabán"])

st.divider()

st.subheader("2. Riesgo Trombótico del Paciente")
riesgo_tromb = "No evaluado"

if tipo_farmaco == "Anticoagulantes (AVK / ACOD)":
    indicacion = st.radio("Motivo de la anticoagulación:", ["Fibrilación Auricular (FA)", "Prótesis Valvular Mecánica", "Enfermedad Tromboembólica Venosa (ETEV)"])
    
    if indicacion == "Fibrilación Auricular (FA)":
        st.write("Escala CHA₂DS₂-VA (Consenso 2025)")
        st.radio("Selección directa de puntuación:", options=[0, 1, 2, 3, 4, 5, 6, 7, 8], horizontal=True, key="chads_score")
        
        st.button("🧮 Mostrar CHA₂DS₂-VA", on_click=toggle_calc)
        
        if st.session_state.mostrar_calc:
            with st.container(border=True):
                c = st.checkbox("Insuficiencia Congestiva / Disfunción VI (+1)")
                h = st.checkbox("Hipertensión Arterial (+1)")
                a2 = st.checkbox("Edad ≥ 75 años (+2)")
                a1 = st.checkbox("Edad 65-74 años (+1)", disabled=a2)
                d = st.checkbox("Diabetes Mellitus (+1)")
                s2 = st.checkbox("Ictus / AIT / Tromboembolismo previo (+2)")
                v = st.checkbox("Enfermedad Vascular (Infarto, EAP, placa aórtica) (+1)")
                
                calc_score = sum([c, h, a2*2, a1 if not a2 else 0, d, s2*2, v])
                st.markdown(f"**Puntuación calculada: {calc_score}**")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1: st.button("Aplicar este resultado", type="primary", on_click=aplicar_puntuacion, args=(calc_score,))
                with col_btn2: st.button("Cerrar", on_click=toggle_calc)

        riesgo_tromb = "Alto" if st.session_state.chads_score >= 7 else "Bajo / Moderado"
        
    elif indicacion == "Prótesis Valvular Mecánica":
        tipo_valvula = st.selectbox("Tipo/Localización:", ["Aórtica sin factores de riesgo", "Mitral", "Aórtica con factores de riesgo"])
        riesgo_tromb = "Bajo / Moderado" if tipo_valvula == "Aórtica sin factores de riesgo" else "Alto"
        
    elif indicacion == "Enfermedad Tromboembólica Venosa (ETEV)":
        tiempo_etev = st.radio("Tiempo desde el evento ETEV:", ["Más de 3 meses", "Menos de 3 meses (o trombofilia grave)"])
        riesgo_tromb = "Bajo / Moderado" if tiempo_etev == "Más de 3 meses" else "Alto"

elif tipo_farmaco == "Antiagregantes":
    indicacion = st.radio("Escenario clínico:", ["Prevención Primaria o SC Crónico (>12 meses)", "ICP/Stent reciente (<1 a 3 meses)", "SCA reciente (<1 mes)"])
    riesgo_tromb = "Alto" if "reciente" in indicacion else "Bajo / Moderado"

if riesgo_tromb == "Alto": st.error(f"⚠️ Riesgo Trombótico: **{riesgo_tromb}**")
else: st.success(f"✅ Riesgo Trombótico: **{riesgo_tromb}**")

st.divider()

st.subheader("3. Riesgo Hemorrágico de la Intervención")

diccionario_qx = {
    "Cardiología y Radiología Intervencionista": {
        "Cateterismo cardíaco diagnóstico": "Bajo",
        "Intervención coronaria percutánea (ICP / Angioplastia)": "Bajo",
        "Implante de marcapasos o DAI": "Bajo",
        "Estudio electrofisiológico simple": "Bajo",
        "Ablación de fibrilación auricular o taquicardia ventricular": "Alto",
        "Radiología: Punciones superficiales o drenajes simples": "Bajo",
        "Radiología: Biopsia de órgano profundo o embolización": "Alto"
    },
    "Cirugía Cardiovascular, Torácica y Vascular": {
        "Cirugía cardíaca (bypass, recambio valvular)": "Alto",
        "Cirugía vascular mayor (aneurisma aorta, bypass periférico)": "Alto",
        "Cirugía torácica mayor (resección pulmonar, mediastino)": "Alto",
        "Toracocentesis / Drenaje pleural simple": "Bajo"
    },
    "Cirugía General y del Aparato Digestivo": {
        "Endoscopia digestiva diagnóstica (con o sin biopsia)": "Bajo",
        "CPRE sin esfinterotomía": "Bajo",
        "Endoscopia con resección mucosa o polipectomía": "Alto",
        "CPRE con esfinterotomía": "Alto",
        "Biopsia hepática": "Alto",
        "Cirugía herniaria": "Alto",
        "Cirugía biliar, gástrica o colorrectal mayor": "Alto",
        "Cirugía de mama (biopsia o tumorectomía simple)": "Bajo",
        "Cirugía de mama mayor (mastectomía)": "Alto"
    },
    "Cirugía Ortopédica y Traumatología": {
        "Infiltraciones articulares o de partes blandas": "Bajo",
        "Artroscopia diagnóstica o cirugía menor": "Bajo",
        "Cirugía ortopédica mayor (prótesis cadera/rodilla)": "Alto",
        "Cirugía de columna": "Alto"
    },
    "Urología": {
        "Cistoscopia diagnóstica": "Bajo",
        "Biopsia prostática o renal": "Alto",
        "Resección transuretral de próstata (RTU) o vejiga": "Alto",
        "Litotricia extracorpórea": "Alto",
        "Nefrectomía o cirugía urológica mayor": "Alto"
    },
    "Obstetricia y Ginecología": {
        "Histeroscopia diagnóstica o biopsia cervical": "Bajo",
        "Cirugía de mama (biopsia o tumorectomía simple)": "Bajo",
        "Cirugía de mama mayor (mastectomía)": "Alto",
        "Histerectomía o cirugía pélvica mayor": "Alto",
        "Cesárea o parto vaginal": "Alto",
        "Cirugía oncológica ginecológica": "Alto"
    },
    "Neurología, Neurocirugía y Anestesiología": {
        "Bloqueos nerviosos periféricos superficiales": "Bajo",
        "Anestesia neuroaxial (epidural/raquídea)": "Alto",
        "Bloqueos nerviosos profundos": "Alto",
        "Neurocirugía (craneal o espinal)": "Alto"
    },
    "ORL, Maxilofacial y Cirugía Plástica": {
        "Biopsia ORL superficial o endoscopia nasal": "Bajo",
        "Cirugía de oído medio (timpanoplastia)": "Bajo",
        "Amigdalectomía o adenoidectomía": "Alto",
        "Cirugía endoscópica nasosinusal (CENS)": "Alto",
        "Cirugía maxilofacial mayor o reconstructiva": "Alto",
        "Cirugía plástica mayor, mamoplastia o reconstrucción": "Alto"
    },
    "Dermatología, Oftalmología y Odontología": {
        "Cirugía menor cutánea (ej. extirpación nevus)": "Bajo",
        "Cirugía de cataratas o segmento anterior": "Bajo",
        "Extracción dental (1-3 piezas) o limpieza": "Bajo",
        "Cirugía de glaucoma o retina (compleja)": "Alto",
        "Extracción dental múltiple": "Alto"
    },
    "Cirugía Pediátrica": {
        "Cirugía pediátrica menor (fimosis, hernias simples)": "Bajo",
        "Cirugía pediátrica mayor (tórax, abdomen, ortopedia)": "Alto"
    }
}

sinonimos = {
    "pci": ("Cardiología y Radiología Intervencionista", "Intervención coronaria percutánea (ICP / Angioplastia)"),
    "icp": ("Cardiología y Radiología Intervencionista", "Intervención coronaria percutánea (ICP / Angioplastia)"),
    "stent": ("Cardiología y Radiología Intervencionista", "Intervención coronaria percutánea (ICP / Angioplastia)"),
    "angioplastia": ("Cardiología y Radiología Intervencionista", "Intervención coronaria percutánea (ICP / Angioplastia)"),
    "vesicula": ("Cirugía General y del Aparato Digestivo", "Cirugía biliar, gástrica o colorrectal mayor"),
    "colelap": ("Cirugía General y del Aparato Digestivo", "Cirugía biliar, gástrica o colorrectal mayor"),
    "colecistectomia": ("Cirugía General y del Aparato Digestivo", "Cirugía biliar, gástrica o colorrectal mayor"),
    "cataratas": ("Dermatología, Oftalmología y Odontología", "Cirugía de cataratas o segmento anterior"),
    "faco": ("Dermatología, Oftalmología y Odontología", "Cirugía de cataratas o segmento anterior"),
    "prp": ("Urología", "Biopsia prostática o renal"),
    "rtu": ("Urología", "Resección transuretral de próstata (RTU) o vejiga"),
    "rodilla": ("Cirugía Ortopédica y Traumatología", "Cirugía ortopédica mayor (prótesis cadera/rodilla)"),
    "cadera": ("Cirugía Ortopédica y Traumatología", "Cirugía ortopédica mayor (prótesis cadera/rodilla)"),
    "ptg": ("Cirugía Ortopédica y Traumatología", "Cirugía ortopédica mayor (prótesis cadera/rodilla)"),
    "ptc": ("Cirugía Ortopédica y Traumatología", "Cirugía ortopédica mayor (prótesis cadera/rodilla)"),
    "diente": ("Dermatología, Oftalmología y Odontología", "Extracción dental (1-3 piezas) o limpieza"),
    "muela": ("Dermatología, Oftalmología y Odontología", "Extracción dental (1-3 piezas) o limpieza"),
    "cordal": ("Dermatología, Oftalmología y Odontología", "Extracción dental múltiple"),
    "herniorrafia": ("Cirugía General y del Aparato Digestivo", "Cirugía herniaria"),
    "eventracion": ("Cirugía General y del Aparato Digestivo", "Cirugía herniaria"),
    "hernia": ("Cirugía General y del Aparato Digestivo", "Cirugía herniaria"),
    "marcapasos": ("Cardiología y Radiología Intervencionista", "Implante de marcapasos o DAI"),
    "dai": ("Cardiología y Radiología Intervencionista", "Implante de marcapasos o DAI"),
    "mama biopsia": ("Cirugía General y del Aparato Digestivo", "Cirugía de mama (biopsia o tumorectomía simple)"),
    "mama mastectomia": ("Cirugía General y del Aparato Digestivo", "Cirugía de mama mayor (mastectomía)"),
    "mama reconstruccion": ("ORL, Maxilofacial y Cirugía Plástica", "Cirugía plástica mayor, mamoplastia o reconstrucción"),
    "mama reduccion": ("ORL, Maxilofacial y Cirugía Plástica", "Cirugía plástica mayor, mamoplastia o reconstrucción"),
    "mamoplastia": ("ORL, Maxilofacial y Cirugía Plástica", "Cirugía plástica mayor, mamoplastia o reconstrucción"),
    "mastectomia": ("Cirugía General y del Aparato Digestivo", "Cirugía de mama mayor (mastectomía)")
}

st.radio("Nivel de sangrado (selección manual o automática):", ["Bajo", "Alto"], horizontal=True, key="riesgo_qx")

st.button("📖 Abrir catálogo de procedimientos", on_click=toggle_cat_qx)

if st.session_state.mostrar_cat_qx:
    with st.container(border=True):
        st.write("🔎 **Buscador rápido (por sinónimos o jerga):**")
        busqueda = st.text_input("Escriba el procedimiento (ej. colelap, stent, mama...)", placeholder="Buscar...", label_visibility="collapsed").lower()
        
        if busqueda:
            busqueda_limpia = quitar_tildes(busqueda)
            coincidencias = []
            for sin, (cat, proc) in sinonimos.items():
                if sin in busqueda_limpia or busqueda_limpia in sin:
                    if (cat, proc) not in coincidencias:
                        coincidencias.append((cat, proc))
            
            if coincidencias:
                st.markdown("*Resultados sugeridos:*")
                for i, (cat_match, proc_match) in enumerate(coincidencias):
                    r_match = diccionario_qx[cat_match][proc_match]
                    icono = "🟢" if r_match == "Bajo" else "🔴"
                    col_res1, col_res2 = st.columns([3, 1])
                    with col_res1:
                        st.write(f"{icono} **{proc_match}**")
                        st.caption(f"({cat_match}) - Riesgo: {r_match}")
                    with col_res2:
                        st.button("Aplicar", key=f"btn_apply_search_{i}", on_click=aplicar_riesgo_qx, args=(r_match,))
                st.divider()
            else:
                st.warning("No se encontraron sinónimos exactos. Utilice el catálogo manual a continuación.")
                st.divider()

        st.write("📂 **O seleccione manualmente por especialidad:**")
        categoria = st.selectbox("1. Especialidad:", list(diccionario_qx.keys()))
        proc_elegido = st.selectbox("2. Procedimiento:", list(diccionario_qx[categoria].keys()))
        
        r_calculado = diccionario_qx[categoria][proc_elegido]
        
        if r_calculado == "Bajo":
            st.success(f"Riesgo asociado a este procedimiento: **{r_calculado}**")
        else:
            st.error(f"Riesgo asociado a este procedimiento: **{r_calculado}**")
        
        col_bq1, col_bq2 = st.columns(2)
        with col_bq1: st.button("Aplicar procedimiento", type="primary", on_click=aplicar_riesgo_qx, args=(r_calculado,), key="btn_apply_manual")
        with col_bq2: st.button("Cerrar sin aplicar", on_click=toggle_cat_qx, key="btn_cerrar_qx")

st.divider()

# --- PASO 4: FUNCIÓN RENAL ---
st.subheader("4. Función Renal")

if tipo_farmaco == "Anticoagulantes (AVK / ACOD)":
    st.info("Para el ajuste de ACOD se debe utilizar el **Aclaramiento de Creatinina (Cockcroft-Gault)**, no el Filtrado Glomerular estimado (CKD-EPI).")

st.button("🧮 Mostrar Calculadora Cockcroft-Gault", on_click=toggle_calc_renal)

if st.session_state.mostrar_calc_renal:
    with st.container(border=True):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            sexo = st.radio("Sexo:", ["Hombre", "Mujer"], horizontal=True)
            edad = st.number_input("Edad:", min_value=18, max_value=120, value=70)
        with col_c2:
            peso = st.number_input("Peso (kg):", min_value=30.0, max_value=200.0, value=75.0)
            creat = st.number_input("Creatinina (mg/dL):", min_value=0.1, max_value=15.0, value=1.0, step=0.1)
        
        calc_crcl = ((140 - edad) * peso) / (72 * creat)
        if sexo == "Mujer": calc_crcl *= 0.85
            
        st.markdown(f"#### Resultado: **{calc_crcl:.1f} ml/min**")
        
        col_btn_r1, col_btn_r2 = st.columns(2)
        with col_btn_r1: st.button("Aplicar Aclaramiento", type="primary", on_click=aplicar_aclaramiento, args=(calc_crcl,))
        with col_btn_r2: st.button("Cerrar", on_click=toggle_calc_renal, key="btn_cerrar_renal2")

crcl = st.number_input("Aclaramiento de Creatinina (ml/min):", min_value=0, max_value=200, key="crcl_val", step=5)

if crcl < 30:
    st.error("Insuficiencia Renal Severa")
elif crcl <= 50:
    st.warning("Insuficiencia Renal Moderada")
else:
    st.success("Función Renal Conservada")

st.divider()

# --- PASO 5: RECOMENDACIÓN FINAL Y EXPORTACIÓN ---
st.subheader("5. Recomendación Clínica (SEC 2025)")
with st.container(border=True):
    r_sangrado = st.session_state.riesgo_qx
    
    texto_resumen = f"📋 MANEJO PERIOPERATORIO (Consenso SEC 2025)\n"
    texto_resumen += f"Fármaco: {farmaco}\n"
    texto_resumen += f"Riesgo Trombótico: {riesgo_tromb}\n"
    texto_resumen += f"Riesgo Hemorrágico (Cirugía): {r_sangrado}\n"
    if tipo_farmaco == "Anticoagulantes (AVK / ACOD)":
        texto_resumen += f"Aclaramiento Creatinina: {st.session_state.crcl_val} ml/min\n"
    texto_resumen += f"---\n"
    
    if farmaco == "Sintrom / Aldocumar":
        st.markdown("### 🛑 Preoperatorio")
        st.write("- **Acenocumarol (Sintrom)**: Suspender 3 días antes de la intervención.")
        st.write("- **Warfarina (Aldocumar)**: Suspender 5 días antes de la intervención.")
        st.write("- Objetivo: INR < 1.5 el día previo o el mismo día del procedimiento (riesgo sangrado alto) o < 2.0 (riesgo bajo).")
        
        texto_resumen += "PREOPERATORIO:\n- Acenocumarol: Suspender 3 días antes / Warfarina: 5 días antes.\n- Objetivo INR < 1.5 (riesgo alto) o < 2.0 (riesgo bajo).\n"
        
        st.markdown("### 🌉 Terapia Puente con HBPM")
        if riesgo_tromb == "Alto":
            st.warning("⚠️ **SÍ INDICADA**. Iniciar HBPM a dosis terapéuticas cuando el INR < 2.0. Administrar última dosis 24h antes del procedimiento (a mitad de dosis).")
            texto_resumen += "- Puente HBPM: SÍ INDICADA. Iniciar con INR < 2.0. Última dosis 24h antes (mitad de dosis).\n"
        else:
            st.success("✅ **NO INDICADA**. El consenso desaconseja el puente con HBPM sistemático en pacientes de riesgo bajo/moderado por aumento de sangrado sin beneficio trombótico.")
            texto_resumen += "- Puente HBPM: NO INDICADA (Riesgo trombótico no alto).\n"
            
        st.markdown("### 🟢 Postoperatorio (Reinicio)")
        st.write("- Reiniciar AVK la misma noche de la cirugía a dosis habitual (si se asegura hemostasia).")
        texto_resumen += "POSTOPERATORIO:\n- Reiniciar AVK la misma noche de la cirugía a dosis habitual.\n"
        
        if riesgo_tromb == "Alto":
            if r_sangrado == "Bajo":
                st.write("- Reiniciar HBPM puente a las **24 horas** de la intervención, hasta alcanzar INR terapéutico (>2.0).")
                texto_resumen += "- Reiniciar HBPM puente a las 24 horas hasta alcanzar INR >2.0.\n"
            else:
                st.write("- Reiniciar HBPM puente a las **48 - 72 horas** de la intervención, hasta alcanzar INR terapéutico (>2.0).")
                texto_resumen += "- Reiniciar HBPM puente a las 48-72 horas hasta alcanzar INR >2.0.\n"

    elif farmaco in ["Dabigatrán", "Rivaroxabán", "Apixabán", "Edoxabán"]:
        st.markdown("### 🛑 Preoperatorio")
        texto_resumen += "PREOPERATORIO:\n"
        if st.session_state.crcl_val < 30 and farmaco == "Dabigatrán":
            st.error(f"🚨 **ALERTA CLÍNICA:** El uso de {farmaco} está **contraindicado** con CrCl < 30 ml/min. Valorar el riesgo/beneficio individualmente o consultar a nefrología/hematología.")
            texto_resumen += f"- ALERTA: {farmaco} CONTRAINDICADO con CrCl < 30 ml/min.\n"
            
        if r_sangrado == "Bajo":
            st.write(f"- Suspender {farmaco} **24 horas antes** del procedimiento (Omitir 1 día).")
            texto_resumen += f"- Suspender {farmaco} 24 horas antes (Omitir 1 día).\n"
            if farmaco == "Dabigatrán" and st.session_state.crcl_val < 50:
                st.write("- *Atención:* Por su farmacocinética renal y CrCl < 50, considerar aumentar a **48 horas**.")
                texto_resumen += "- Atención: (Dabigatrán + CrCl < 50) Considerar aumentar a 48 horas.\n"
        else:
            st.write(f"- Suspender {farmaco} **48 horas antes** del procedimiento (Omitir 2 días).")
            texto_resumen += f"- Suspender {farmaco} 48 horas antes (Omitir 2 días).\n"
            if farmaco == "Dabigatrán" and st.session_state.crcl_val < 50:
                st.write("- *Atención:* Por su farmacocinética renal y CrCl < 50, prolongar suspensión a **72 - 96 horas**.")
                texto_resumen += "- Atención: (Dabigatrán + CrCl < 50) Prolongar a 72-96 horas.\n"
        
        st.markdown("### 🌉 Terapia Puente con HBPM")
        st.success("✅ **NO INDICADA EN NINGÚN CASO**. Nunca se usa heparina puente para los ACOD.")
        texto_resumen += "- Puente HBPM: NO INDICADA (ACOD).\n"
        
        st.markdown("### 🟢 Postoperatorio (Reinicio)")
        texto_resumen += "POSTOPERATORIO:\n"
        if r_sangrado == "Bajo":
            st.write("- Reiniciar ACOD a las **24 horas** tras la intervención (si hemostasia adecuada).")
            texto_resumen += "- Reiniciar ACOD a las 24 horas tras la intervención.\n"
        else:
            st.write("- Reiniciar ACOD a las **48 - 72 horas** tras la intervención (si hemostasia adecuada).")
            texto_resumen += "- Reiniciar ACOD a las 48-72 horas tras la intervención.\n"

    elif tipo_farmaco == "Antiagregantes":
        st.markdown("### 🛑 Manejo de la Antiagregación")
        texto_resumen += "MANEJO ANTIAGREGACIÓN:\n"
        
        if farmaco == "Doble Antiagregación (TAPD)":
            if riesgo_tromb == "Alto":
                st.error("⚠️ **Riesgo Trombótico Muy Alto (Stent o SCA reciente)**")
                st.write("- La cirugía electiva **DEBE POSPONERSE** si es posible.")
                st.write("- Si la cirugía es inaplazable: **MANTENER AAS** y suspender el inhibidor P2Y12 (Clopidogrel/Ticagrelor 5 días, Prasugrel 7 días antes).")
                texto_resumen += "- ALERTA: Riesgo Trombótico Muy Alto. Posponer cirugía electiva si es posible.\n"
                texto_resumen += "- Si inaplazable: MANTENER AAS y suspender inhibidor P2Y12 (Clopid/Ticag 5d, Prasugrel 7d).\n"
            else:
                st.write("- **Suspender el inhibidor P2Y12** (Clopidogrel/Ticagrelor 5 días, Prasugrel 7 días) y **MANTENER AAS** perioperatorio si el riesgo de sangrado lo permite.")
                texto_resumen += "- Suspender inhibidor P2Y12 (Clopid/Ticag 5d, Prasugrel 7d) y MANTENER AAS.\n"
        else:
            if farmaco == "AAS":
                if r_sangrado == "Bajo":
                    st.write("- **MANTENER AAS** perioperatoriamente (≤ 100 mg).")
                    texto_resumen += "- MANTENER AAS perioperatoriamente.\n"
                else:
                    if riesgo_tromb == "Bajo / Moderado":
                        st.write("- **Suspender AAS** 3-5 días antes de la intervención (riesgo hemorrágico alto y trombótico bajo).")
                        texto_resumen += "- Suspender AAS 3-5 días antes de la intervención.\n"
                    else:
                        st.write("- Evaluar riesgo/beneficio individualizado. Tendencia a mantener AAS por riesgo trombótico alto.")
                        texto_resumen += "- Riesgo cruzado: Evaluar riesgo/beneficio individualizado. Tendencia a mantener AAS.\n"
            elif farmaco in ["Clopidogrel", "Ticagrelor"]:
                st.write(f"- **Suspender {farmaco} 5 DÍAS antes** de la intervención.")
                texto_resumen += f"- Suspender {farmaco} 5 días antes.\n"
            elif farmaco == "Prasugrel":
                st.write("- **Suspender Prasugrel 7 DÍAS antes** de la intervención.")
                texto_resumen += "- Suspender Prasugrel 7 días antes.\n"
        
        st.markdown("### 🟢 Postoperatorio (Reinicio)")
        st.write("- Reiniciar el fármaco antiagregante en cuanto la hemostasia sea segura, idealmente a las **24 horas**.")
        texto_resumen += "POSTOPERATORIO:\n- Reiniciar antiagregante al asegurar hemostasia (idealmente 24h).\n"
    
    st.divider()
    st.markdown("#### 📝 Resumen para Historia Clínica")
    st.caption("Pasa el ratón sobre el recuadro gris y pulsa el icono de 'Copiar' (arriba a la derecha) para luego poder pegarlo directamente en la Historia Clínica Electrónica.")
    st.code(texto_resumen, language="text")
