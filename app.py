import streamlit as st
import unicodedata

st.set_page_config(page_title="Manejo Antitrombótico", page_icon="🩸", layout="centered")

# --- MENÚ LATERAL DE CONFIGURACIÓN ---
with st.sidebar:
    st.header("⚙️ Configuración")
    st.write("Ajuste la interfaz a su pantalla:")
    tamano_texto = st.radio("Tamaño de letra:", ["Pequeño", "Mediano", "Grande"], index=1)

if tamano_texto == "Pequeño":
    css_font_size = "0.95rem"
    css_radio_pad = "0.8rem"
elif tamano_texto == "Mediano":
    css_font_size = "1.1rem"
    css_radio_pad = "1.2rem"
else:
    css_font_size = "1.3rem"
    css_radio_pad = "1.5rem"

# --- INYECCIÓN CSS (INCLUYE ARREGLO DEL TEXTO CORTADO) ---
st.markdown(f"""
<style>
    /* Ajuste general de tamaño de texto */
    html, body, [class*="st-"] {{
        font-size: {css_font_size} !important;
    }}
    
    /* Separación ampliada para botones táctiles */
    div.stRadio > div[role="radiogroup"] > label {{ 
        padding-top: {css_radio_pad}; 
        padding-bottom: {css_radio_pad}; 
        margin-bottom: 0.5rem;
    }}
    
    div[data-testid="stCheckbox"] > label {{ 
        padding-top: 1rem; 
        padding-bottom: 1rem; 
        margin-bottom: 0.3rem;
    }}
    
    div.stButton > button {{ 
        min-height: 4rem; 
        border-radius: 8px; 
    }}
    
    /* Forzar salto de línea en el recuadro gris final para que no se coma el texto */
    pre, code {{
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown("<div style='text-align: right; font-size: 0.8em; color: #888;'>v0.17.6 (Corrección texto cortado)</div>", unsafe_allow_html=True)

st.title("Manejo Perioperatorio")
st.caption("Herramienta de soporte clínico basada en el Consenso SEC 2025")
st.divider()

# --- ESTADO INICIAL SEGURO ---
if 'chads_score' not in st.session_state: st.session_state.chads_score = None
if 'crcl_val' not in st.session_state: st.session_state.crcl_val = None
if 'riesgo_qx' not in st.session_state: st.session_state.riesgo_qx = None
if 'proc_nombre' not in st.session_state: st.session_state.proc_nombre = None
if 'mostrar_calc' not in st.session_state: st.session_state.mostrar_calc = False
if 'mostrar_calc_renal' not in st.session_state: st.session_state.mostrar_calc_renal = False
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

def aplicar_riesgo_qx(riesgo, nombre):
    st.session_state.riesgo_qx = riesgo
    st.session_state.proc_nombre = nombre
    st.session_state.mostrar_cat_qx = False

def quitar_tildes(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

# --- PASO 1 ---
st.subheader("1. Tratamiento actual")
tipo_farmaco = st.radio("Familia farmacológica:", ["Antiagregantes", "Anticoagulantes (AVK / ACOD)"], label_visibility="collapsed")

farmaco_p2y12 = None
if tipo_farmaco == "Antiagregantes":
    farmaco = st.selectbox("Seleccione fármaco:", ["AAS", "Clopidogrel", "Prasugrel", "Ticagrelor", "Doble Antiagregación (TAPD)"])
    if farmaco == "Doble Antiagregación (TAPD)":
        farmaco_p2y12 = st.selectbox("Inhibidor P2Y12 asociado a la Aspirina:", ["Clopidogrel", "Ticagrelor", "Prasugrel"])
else:
    farmaco = st.selectbox("Seleccione fármaco:", ["Acenocumarol (Sintrom)", "Warfarina (Aldocumar)", "Dabigatrán", "Rivaroxabán", "Apixabán", "Edoxabán"])

st.divider()

# --- PASO 2 ---
st.subheader("2. Riesgo Trombótico del Paciente")
riesgo_tromb = "No evaluado"

if tipo_farmaco == "Anticoagulantes (AVK / ACOD)":
    indicacion = st.radio("Motivo de la anticoagulación:", ["Fibrilación Auricular (FA)", "Prótesis Valvular Mecánica", "Enfermedad Tromboembólica Venosa (ETEV)"])
    
    if indicacion == "Fibrilación Auricular (FA)":
        st.write("Escala CHA₂DS₂-VA (Consenso 2025)")
        if st.session_state.chads_score is not None:
            st.success(f"Puntuación confirmada: **{st.session_state.chads_score}**")
            riesgo_tromb = "Alto" if st.session_state.chads_score >= 7 else "Bajo / Moderado"
        else:
            st.warning("⚠️ Requiere calcular puntuación.")
            
        st.button("🧮 Abrir Calculadora CHA₂DS₂-VA", on_click=toggle_calc)
        
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

    elif indicacion == "Prótesis Valvular Mecánica":
        tipo_valvula = st.selectbox("Tipo/Localización:", ["Aórtica sin factores de riesgo", "Mitral", "Aórtica con factores de riesgo"])
        riesgo_tromb = "Bajo / Moderado" if tipo_valvula == "Aórtica sin factores de riesgo" else "Alto"
        
    elif indicacion == "Enfermedad Tromboembólica Venosa (ETEV)":
        tiempo_etev = st.radio("Tiempo desde el evento ETEV:", ["Más de 3 meses", "Menos de 3 meses (o trombofilia grave)"])
        riesgo_tromb = "Bajo / Moderado" if tiempo_etev == "Más de 3 meses" else "Alto"

elif tipo_farmaco == "Antiagregantes":
    indicacion = st.radio("Escenario clínico:", ["Prevención Primaria o SC Crónico (>12 meses)", "ICP/Stent reciente (<1 a 3 meses)", "SCA reciente (<1 mes)"])
    riesgo_tromb = "Alto" if "reciente" in indicacion else "Bajo / Moderado"

if riesgo_tromb != "No evaluado":
    if riesgo_tromb == "Alto": st.error(f"⚠️ Riesgo Trombótico: **{riesgo_tromb}**")
    else: st.success(f"✅ Riesgo Trombótico: **{riesgo_tromb}**")

st.divider()

# --- PASO 3 ---
st.subheader("3. Riesgo Hemorrágico de la Intervención")

catalogo = [
  {"categoria": "Cardiología e Intervencionismo", "nombre": "Cateterismo cardíaco diagnóstico", "riesgo": "Bajo", "sinonimos": ["cateterismo", "coronariografia"]},
  {"categoria": "Cardiología e Intervencionismo", "nombre": "Intervención coronaria percutánea (ICP / Angioplastia)", "riesgo": "Bajo", "sinonimos": ["pci", "icp", "stent", "angioplastia"]},
  {"categoria": "Cardiología e Intervencionismo", "nombre": "Implante de marcapasos o DAI", "riesgo": "Bajo", "sinonimos": ["marcapasos", "dai", "desfibrilador"]},
  {"categoria": "Cardiología e Intervencionismo", "nombre": "Ablación de fibrilación auricular", "riesgo": "Alto", "sinonimos": ["ablacion", "fa"]},
  {"categoria": "Radiología", "nombre": "Biopsia de órgano profundo", "riesgo": "Alto", "sinonimos": ["bag", "biopsia hepatica", "biopsia renal"]},
  {"categoria": "Cirugía Digestiva y General", "nombre": "Endoscopia digestiva diagnóstica", "riesgo": "Bajo", "sinonimos": ["gastroscopia", "colonoscopia", "endoscopia"]},
  {"categoria": "Cirugía Digestiva y General", "nombre": "Endoscopia con polipectomía", "riesgo": "Alto", "sinonimos": ["polipectomia", "resecion mucosa"]},
  {"categoria": "Cirugía Digestiva y General", "nombre": "Cirugía herniaria", "riesgo": "Alto", "sinonimos": ["hernia", "herniorrafia", "eventracion", "inguinal"]},
  {"categoria": "Cirugía Digestiva y General", "nombre": "Cirugía biliar o colorrectal mayor", "riesgo": "Alto", "sinonimos": ["vesicula", "colelap", "colecistectomia", "colectomia"]},
  {"categoria": "Traumatología", "nombre": "Infiltraciones articulares", "riesgo": "Bajo", "sinonimos": ["infiltracion", "artrocentesis"]},
  {"categoria": "Traumatología", "nombre": "Artroscopia diagnóstica o cirugía menor", "riesgo": "Bajo", "sinonimos": ["artroscopia", "menisco", "tunel carpiano"]},
  {"categoria": "Traumatología", "nombre": "Cirugía ortopédica mayor (prótesis cadera/rodilla)", "riesgo": "Alto", "sinonimos": ["ptg", "ptc", "rodilla", "cadera", "protesis"]},
  {"categoria": "Urología", "nombre": "Cistoscopia diagnóstica", "riesgo": "Bajo", "sinonimos": ["cistoscopia"]},
  {"categoria": "Urología", "nombre": "Biopsia prostática", "riesgo": "Alto", "sinonimos": ["prp", "biopsia prostata"]},
  {"categoria": "Urología", "nombre": "Resección transuretral (RTU)", "riesgo": "Alto", "sinonimos": ["rtu", "rtup", "rtuv"]},
  {"categoria": "Ginecología", "nombre": "Histeroscopia diagnóstica o biopsia cervical", "riesgo": "Bajo", "sinonimos": ["histeroscopia", "conizacion", "biopsia cervix"]},
  {"categoria": "Ginecología", "nombre": "Histerectomía o cirugía pélvica", "riesgo": "Alto", "sinonimos": ["histerectomia", "anexectomia"]},
  {"categoria": "Mama", "nombre": "Cirugía de mama (biopsia o tumorectomía simple)", "riesgo": "Bajo", "sinonimos": ["mama biopsia", "tumorectomia mama"]},
  {"categoria": "Mama", "nombre": "Cirugía de mama mayor (mastectomía)", "riesgo": "Alto", "sinonimos": ["mastectomia", "ganglio centinela", "mama"]},
  {"categoria": "Oftalmología", "nombre": "Cirugía de cataratas o segmento anterior", "riesgo": "Bajo", "sinonimos": ["cataratas", "faco"]},
  {"categoria": "Odontología", "nombre": "Extracción dental (1-3 piezas)", "riesgo": "Bajo", "sinonimos": ["diente", "muela", "extraccion simple", "empaste"]},
  {"categoria": "Odontología", "nombre": "Extracción dental múltiple", "riesgo": "Alto", "sinonimos": ["cordal", "muela juicio", "extraccion multiple"]}
]

if st.session_state.riesgo_qx is not None:
    st.success(f"Procedimiento: **{st.session_state.proc_nombre}** (Riesgo **{st.session_state.riesgo_qx}**)")
else:
    st.warning("⚠️ Requiere seleccionar un procedimiento clínico.")

st.button("📖 Abrir catálogo de procedimientos", on_click=toggle_cat_qx)

if st.session_state.mostrar_cat_qx:
    with st.container(border=True):
        st.write("🔎 **Buscador rápido (por sinónimos o jerga):**")
        busqueda = st.text_input("Escriba el procedimiento:", placeholder="Buscar...", label_visibility="collapsed").lower()
        
        if busqueda:
            busqueda_limpia = quitar_tildes(busqueda)
            coincidencias = []
            
            for proc in catalogo:
                match_nombre = busqueda_limpia in quitar_tildes(proc["nombre"].lower())
                match_sinonimos = any(busqueda_limpia in quitar_tildes(sin.lower()) for sin in proc["sinonimos"])
                if match_nombre or match_sinonimos:
                    coincidencias.append(proc)
            
            if coincidencias:
                st.markdown("*Resultados sugeridos:*")
                for i, proc in enumerate(coincidencias):
                    icono = "🟢" if proc["riesgo"] == "Bajo" else "🔴"
                    col_res1, col_res2 = st.columns([3, 1])
                    with col_res1:
                        st.write(f"{icono} **{proc['nombre']}**")
                        st.caption(f"({proc['categoria']})")
                    with col_res2:
                        st.button("Aplicar", key=f"btn_apply_search_{i}", on_click=aplicar_riesgo_qx, args=(proc["riesgo"], proc["nombre"]))
                st.divider()

        st.write("📂 **O seleccione manualmente:**")
        categorias_unicas = sorted(list(set(p["categoria"] for p in catalogo)))
        cat_seleccionada = st.selectbox("1. Especialidad:", categorias_unicas)
        procs_filtrados = [p for p in catalogo if p["categoria"] == cat_seleccionada]
        nombres_procs = [p["nombre"] for p in procs_filtrados]
        proc_elegido_nombre = st.selectbox("2. Procedimiento:", nombres_procs)
        proc_elegido = next(p for p in procs_filtrados if p["nombre"] == proc_elegido_nombre)
        
        col_bq1, col_bq2 = st.columns(2)
        with col_bq1: st.button("Aplicar procedimiento", type="primary", on_click=aplicar_riesgo_qx, args=(proc_elegido["riesgo"], proc_elegido["nombre"]), key="btn_apply_manual")
        with col_bq2: st.button("Cerrar sin aplicar", on_click=toggle_cat_qx, key="btn_cerrar_qx")

st.divider()

# --- PASO 4 ---
st.subheader("4. Función Renal")

if tipo_farmaco == "Anticoagulantes (AVK / ACOD)":
    st.info("Para el ajuste de ACOD se debe utilizar el **Aclaramiento de Creatinina (Cockcroft-Gault)**, no el Filtrado Glomerular estimado (CKD-EPI).")
    st.button("🧮 Mostrar Calculadora", on_click=toggle_calc_renal)

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
            with col_btn_r1: st.button("Aplicar", type="primary", on_click=aplicar_aclaramiento, args=(calc_crcl,))
            with col_btn_r2: st.button("Cerrar", on_click=toggle_calc_renal, key="btn_cerrar_renal2")

    crcl_input = st.number_input("Aclaramiento (ml/min):", min_value=0, max_value=200, value=st.session_state.crcl_val, step=5)
    
    if crcl_input is not None and crcl_input != st.session_state.crcl_val:
        st.session_state.crcl_val = crcl_input
        st.rerun()

    if st.session_state.crcl_val is not None:
        if st.session_state.crcl_val < 30: st.error(f"Aclaramiento: {st.session_state.crcl_val} ml/min (Severa)")
        elif st.session_state.crcl_val <= 50: st.warning(f"Aclaramiento: {st.session_state.crcl_val} ml/min (Moderada)")
        else: st.success(f"Aclaramiento: {st.session_state.crcl_val} ml/min (Conservada)")
    else:
        st.warning("⚠️ Requiere confirmar función renal.")
else:
    st.write("El ajuste renal no es estrictamente necesario para antiagregantes aquí.")

st.divider()

# --- VALIDACIÓN ---
listo_para_recomendar = True
if riesgo_tromb == "No evaluado": listo_para_recomendar = False
if st.session_state.riesgo_qx is None: listo_para_recomendar = False
if tipo_farmaco != "Antiagregantes" and st.session_state.crcl_val is None: listo_para_recomendar = False

# --- PASO 5 ---
if listo_para_recomendar:
    st.subheader("5. Recomendación Clínica (SEC 2025)")
    with st.container(border=True):
        r_sangrado = st.session_state.riesgo_qx
        
        texto_resumen = f"📋 MANEJO PERIOPERATORIO (SEC 2025)\n"
        if farmaco == "Doble Antiagregación (TAPD)":
            texto_resumen += f"Fármaco: {farmaco} (AAS + {farmaco_p2y12})\n"
        else:
            texto_resumen += f"Fármaco: {farmaco}\n"
        texto_resumen += f"Riesgo Trombótico: {riesgo_tromb}\n"
        texto_resumen += f"Procedimiento: {st.session_state.proc_nombre} (Riesgo {r_sangrado})\n"
        if tipo_farmaco == "Anticoagulantes (AVK / ACOD)":
            texto_resumen += f"Aclaramiento Creatinina: {st.session_state.crcl_val} ml/min\n"
        texto_resumen += f"---\n"
        
        if farmaco == "Dabigatrán" and st.session_state.crcl_val < 30:
            st.error(f"🚨 **ALERTA CLÍNICA:** El uso de {farmaco} está **contraindicado** con CrCl < 30 ml/min. Valorar riesgo/beneficio o consultar nefrología/hematología.")
            texto_resumen += f"- ALERTA: {farmaco} CONTRAINDICADO con CrCl < 30 ml/min.\n- ACCIÓN: Reevaluar tratamiento basal.\n"
            
        else:
            if farmaco in ["Acenocumarol (Sintrom)", "Warfarina (Aldocumar)"]:
                st.markdown("### 🛑 Preoperatorio")
                if farmaco == "Acenocumarol (Sintrom)":
                    st.write("- **Sintrom**: Suspender 3 días antes de la intervención.")
                    texto_resumen += "PREOPERATORIO:\n- Acenocumarol: Suspender 3 días antes.\n"
                else:
                    st.write("- **Aldocumar**: Suspender 5 días antes de la intervención.")
                    texto_resumen += "PREOPERATORIO:\n- Warfarina: Suspender 5 días antes.\n"
                
                st.write("- Objetivo: INR < 1.5 (riesgo alto) o < 2.0 (riesgo bajo).")
                texto_resumen += "- Objetivo INR < 1.5 (riesgo alto) o < 2.0 (riesgo bajo).\n"
                
                st.markdown("### 🌉 Terapia Puente con HBPM")
                if riesgo_tromb == "Alto":
                    st.warning("⚠️ **SÍ INDICADA**. Iniciar HBPM a dosis terapéuticas cuando el INR < 2.0.")
                    texto_resumen += "- Puente HBPM: SÍ INDICADA. Iniciar con INR < 2.0. Última dosis 24h antes.\n"
                else:
                    st.success("✅ **NO INDICADA**. El consenso desaconseja el puente sistemático en riesgo bajo/moderado.")
                    texto_resumen += "- Puente HBPM: NO INDICADA.\n"
                    
                st.markdown("### 🟢 Postoperatorio (Reinicio)")
                st.write("- Reiniciar AVK la misma noche de la cirugía.")
                texto_resumen += "POSTOPERATORIO:\n- Reiniciar AVK misma noche de cirugía (hemostasia adecuada).\n"
                
                if riesgo_tromb == "Alto":
                    horas = "24 horas" if r_sangrado == "Bajo" else "48 - 72 horas"
                    st.write(f"- Reiniciar HBPM puente a las **{horas}** de la intervención.")
                    texto_resumen += f"- Reiniciar HBPM puente a las {horas}.\n"

            elif farmaco in ["Dabigatrán", "Rivaroxabán", "Apixabán", "Edoxabán"]:
                st.markdown("### 🛑 Preoperatorio")
                texto_resumen += "PREOPERATORIO:\n"
                    
                dias = "24 horas antes (Omitir 1 día)" if r_sangrado == "Bajo" else "48 horas antes (Omitir 2 días)"
                st.write(f"- Suspender {farmaco} **{dias}**.")
                texto_resumen += f"- Suspender {farmaco} {dias}.\n"
                
                if farmaco == "Dabigatrán" and st.session_state.crcl_val <= 50:
                    st.write("- *Atención:* Por su farmacocinética renal y CrCl ≤ 50, considerar prolongar suspensión.")
                    texto_resumen += "- Atención: (Dabigatrán + CrCl ≤ 50) Prolongar suspensión.\n"
                
                st.markdown("### 🌉 Terapia Puente con HBPM")
                st.success("✅ **NO INDICADA EN NINGÚN CASO** para los ACOD.")
                texto_resumen += "- Puente HBPM: NO INDICADA (ACOD).\n"
                
                st.markdown("### 🟢 Postoperatorio (Reinicio)")
                horas_reinicio = "24 horas" if r_sangrado == "Bajo" else "48 - 72 horas"
                st.write(f"- Reiniciar ACOD a las **{horas_reinicio}** tras la intervención.")
                texto_resumen += f"POSTOPERATORIO:\n- Reiniciar ACOD a las {horas_reinicio} (si hemostasia adecuada).\n"

            elif tipo_farmaco == "Antiagregantes":
                st.markdown("### 🛑 Manejo de la Antiagregación")
                texto_resumen += "MANEJO ANTIAGREGACIÓN:\n"
                
                if farmaco == "Doble Antiagregación (TAPD)":
                    dias_p2y12 = 7 if farmaco_p2y12 == "Prasugrel" else 5
                    if riesgo_tromb == "Alto":
                        st.error("⚠️ **Riesgo Trombótico Muy Alto**")
                        st.write("- Cirugía electiva **DEBE POSPONERSE** si es posible.")
                        st.write(f"- Si inaplazable: **MANTENER AAS** y suspender {farmaco_p2y12} ({dias_p2y12} días antes).")
                        texto_resumen += "- ALERTA: Riesgo Trombótico Muy Alto. Posponer electiva.\n"
                        texto_resumen += f"- Si inaplazable: MANTENER AAS y suspender {farmaco_p2y12} ({dias_p2y12} días).\n"
                    else:
                        st.write(f"- **Suspender {farmaco_p2y12}** ({dias_p2y12} días antes) y **MANTENER AAS**.")
                        texto_resumen += f"- Suspender {farmaco_p2y12} ({dias_p2y12} días antes) y MANTENER AAS.\n"
                else:
                    if farmaco == "AAS":
                        if r_sangrado == "Bajo":
                            st.write("- **MANTENER AAS** perioperatoriamente.")
                            texto_resumen += "- MANTENER AAS perioperatoriamente.\n"
                        else:
                            st.write("- Riesgo cruzado: Evaluar riesgo/beneficio individualizado. Tendencia a mantener AAS.")
                            texto_resumen += "- Riesgo cruzado: Evaluar riesgo/beneficio. Tendencia a mantener AAS.\n"
                    elif farmaco in ["Clopidogrel", "Ticagrelor"]:
                        st.write(f"- **Suspender {farmaco} 5 DÍAS antes**.")
                        texto_resumen += f"- Suspender {farmaco} 5 días antes.\n"
                    elif farmaco == "Prasugrel":
                        st.write("- **Suspender Prasugrel 7 DÍAS antes**.")
                        texto_resumen += "- Suspender Prasugrel 7 días antes.\n"
                
                st.markdown("### 🟢 Postoperatorio (Reinicio)")
                st.write("- Reiniciar antiagregante al asegurar hemostasia (idealmente 24h).")
                texto_resumen += "POSTOPERATORIO:\n- Reiniciar antiagregante al asegurar hemostasia.\n"

        st.divider()
        st.markdown("#### 📝 Resumen para Historia Clínica")
        st.caption("Pasa el ratón sobre el recuadro gris y pulsa el icono de 'Copiar' (arriba a la derecha) para luego poder pegarlo directamente en la Historia Clínica Electrónica.")
        st.code(texto_resumen, language="text")
