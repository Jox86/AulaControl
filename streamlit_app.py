import streamlit as st
import pandas as pd
import json, csv, io
from datetime import date, timedelta

st.set_page_config(page_title='AulaControl · Gestión académica', page_icon='🎓', layout='wide')

# AulaControl full Streamlit adaptation of the included React MVP.
def seed():
    return {
      'students':[
        {'id':1,'name':'Ana Rodríguez','code':'IC-2401','group':'2A','attendance':92,'grades':[9,8,9,8],'published':True},
        {'id':2,'name':'Carlos Méndez','code':'IC-2402','group':'2A','attendance':78,'grades':[7,6,8,7],'published':True},
        {'id':3,'name':'Lucía Pérez','code':'IC-2403','group':'2A','attendance':48,'grades':[8,9,None,None],'published':False},
        {'id':4,'name':'Daniel Torres','code':'IC-2404','group':'2A','attendance':86,'grades':[6,7,7,None],'published':False},
        {'id':5,'name':'María Suárez','code':'IC-2405','group':'2A','attendance':96,'grades':[10,9,10,9],'published':True},
        {'id':6,'name':'Jorge Díaz','code':'IC-2406','group':'2A','attendance':61,'grades':[5,6,7,6],'published':True}],
      'sessions':[{'id':1,'date':str(date.today()),'topic':'Estructuras de datos: listas','type':'Clase','status':'Planificada'}, {'id':2,'date':str(date.today()+timedelta(days=1)),'topic':'Práctica de laboratorio','type':'Práctica','status':'Pendiente'}],
      'lessons':[{'id':1,'title':'Introducción a la asignatura','unit':'Unidad 1','date':'2026-10-20','notes':'Presentación, objetivos y entorno de trabajo.'}],
      'tasks':[{'id':1,'title':'Tarjeta de presentación con HTML y CSS','due':'2026-11-03','status':'Abierta'}],
      'resources':[{'title':'Documentación HTML','author':'MDN Web Docs','url':'https://developer.mozilla.org/es/docs/Web/HTML'}]
    }
if 'db' not in st.session_state: st.session_state.db=seed()
if 'subject' not in st.session_state: st.session_state.subject='Programación Web'
if 'term' not in st.session_state: st.session_state.term='2026 · Semestre 1'
if 'active' not in st.session_state: st.session_state.active='Resumen'
if 'dark' not in st.session_state: st.session_state.dark=True

db=st.session_state.db

def avg(nums):
    v=[float(n) for n in nums if n is not None and n!='']
    return sum(v)/len(v) if v else None
def metrics(s):
    sys=avg(s['grades'][:2]); c1=(sys+s['grades'][2])/2 if sys is not None and s['grades'][2] is not None else None; c2=(sys+s['grades'][3])/2 if sys is not None and s['grades'][3] is not None else None
    return {'Promedio sistemático':sys,'Corte 1':c1,'Corte 2':c2,'Final / 40':2*(c1+c2) if c1 is not None and c2 is not None else None}
def f(v): return '—' if v is None else f'{v:.2f}'
def next_id(items): return max([x.get('id',0) for x in items] or [0])+1
def students_df(rows):
    out=[]
    for s in rows:
        m=metrics(s); out.append({'Código':s['code'],'Estudiante':s['name'],'Grupo':s['group'],'Sistemática':f(m['Promedio sistemático']),'Parcial 1':s['grades'][2] if s['grades'][2] is not None else '—','Parcial 2':s['grades'][3] if s['grades'][3] is not None else '—','Corte 1':f(m['Corte 1']),'Corte 2':f(m['Corte 2']),'Final / 40':f(m['Final / 40']) if s['published'] else 'No publicada','Asistencia %':s['attendance'],'Publicada':'Sí' if s['published'] else 'No'})
    return pd.DataFrame(out)

with st.sidebar:
    st.markdown('# 🎓 AulaControl')
    st.caption('GESTIÓN ACADÉMICA · ESPACIO DOCENTE')
    st.divider()
    pages={'GENERAL':['Resumen','Libro de notas','Asistencia'],'DOCENCIA':['Cursos y grupos','Clases y temas','Bibliografía','Tareas'],'SEGUIMIENTO':['Analítica','Informes','Configuración']}
    for section,items in pages.items():
        st.caption(section)
        for p in items:
            label=f'⚠️ {p}' if p=='Asistencia' and sum(s['attendance']<50 for s in db['students']) else p
            if st.button(label, key='nav_'+p, use_container_width=True, type='primary' if st.session_state.active==p else 'secondary'):
                st.session_state.active=p; st.rerun()
    st.divider()
    st.write('**Docente Principal**')
    st.caption('Versión MVP · datos de demostración')

active=st.session_state.active
st.markdown(f"<div style='padding:4px 0 0;color:#64748b;font-size:0.9rem'>ESPACIO DOCENTE　/　{active.upper()}</div>",unsafe_allow_html=True)
st.title('Buenos días, profesor' if active=='Resumen' else active)
st.caption('Administra y consulta la información de tu actividad académica.')
col1,col2,col3=st.columns([2,2,3])
with col1: st.session_state.subject=st.selectbox('Asignatura activa',['Programación Web','Introducción a la Informática','Bases de Datos'],index=['Programación Web','Introducción a la Informática','Bases de Datos'].index(st.session_state.subject))
with col2: st.session_state.term=st.selectbox('Período académico',['2026 · Semestre 1','2026 · Semestre 2','2027 · Semestre 1'],index=['2026 · Semestre 1','2026 · Semestre 2','2027 · Semestre 1'].index(st.session_state.term))
with col3: st.write(''); st.write(''); st.caption('Los cambios se conservan durante la sesión activa de Streamlit. Para persistencia multiusuario se necesita una base de datos.')
st.divider()
students=db['students']; at_risk=[s for s in students if s['attendance']<50]; course_avg=avg([metrics(s)['Promedio sistemático'] for s in students]); published=sum(s['published'] for s in students)

if active=='Resumen':
    st.markdown('## Tu aula, organizada. Tu progreso, visible.')
    st.write('Gestiona evaluaciones, asistencia y contenidos desde un solo lugar.')
    a,b,c,d=st.columns(4); a.metric('Estudiantes',len(students)); b.metric('Promedio del grupo',f(course_avg)+'/10' if course_avg is not None else '—'); c.metric('Publicaciones',f'{published}/{len(students)}'); d.metric('Alertas de asistencia',len(at_risk))
    st.subheader('Próximas actividades')
    upcoming=sorted(db['sessions'],key=lambda x:x['date'])
    if upcoming: st.dataframe(pd.DataFrame(upcoming),use_container_width=True,hide_index=True)
    else: st.info('No hay actividades planificadas.')
    left,right=st.columns(2)
    with left:
        st.subheader('Accesos rápidos')
        for p in ['Libro de notas','Asistencia','Clases y temas','Tareas','Analítica']:
            if st.button('Abrir '+p,key='quick_'+p,use_container_width=True): st.session_state.active=p; st.rerun()
    with right:
        st.subheader('Distribución de notas sistemáticas')
        vals=[metrics(s)['Promedio sistemático'] for s in students if metrics(s)['Promedio sistemático'] is not None]
        if vals: st.bar_chart(pd.Series(vals,name='Promedio sistemático').value_counts().sort_index())

elif active=='Libro de notas':
    st.write('Edita las sistemáticas y parciales. Los cortes y la nota final se calculan automáticamente.')
    query=st.text_input('Buscar por estudiante, código o grupo')
    rows=[s for s in students if query.lower() in f"{s['name']} {s['code']} {s['group']}".lower()]
    for s in rows:
        m=metrics(s)
        with st.expander(f"{s['name']} · {s['code']} · Grupo {s['group']}",expanded=True):
            x1,x2,x3,x4=st.columns(4)
            labels=['Sistemática 1','Sistemática 2','Parcial 1','Parcial 2']
            for i,(col,label) in enumerate(zip([x1,x2,x3,x4],labels)):
                with col:
                    value=st.number_input(label,0.0,10.0,step=0.5,value=float(s['grades'][i] or 0),key=f"grade_{s['id']}_{i}")
                    s['grades'][i]=value
            m=metrics(s); a,b,c,d=st.columns(4)
            a.metric('Promedio S',f(m['Promedio sistemático'])+'/10'); b.metric('Corte 1',f(m['Corte 1'])); c.metric('Corte 2',f(m['Corte 2'])); d.metric('Final / 40',f(m['Final / 40']) if s['published'] else 'Oculta')
            s['published']=st.checkbox('Marcar resultado como publicado (solo estado de demostración)',value=s['published'],key=f"pub_{s['id']}")
    with st.expander('➕ Añadir estudiante'):
        with st.form('add_student'):
            name=st.text_input('Nombre completo'); code=st.text_input('Código'); group=st.text_input('Grupo','2A'); ok=st.form_submit_button('Guardar estudiante')
        if ok:
            if name.strip() and code.strip(): db['students'].append({'id':next_id(db['students']),'name':name.strip(),'code':code.strip(),'group':group or '2A','attendance':100,'grades':[None,None,None,None],'published':False}); st.success('Estudiante añadido.'); st.rerun()
            else: st.error('Nombre y código son obligatorios.')
    st.download_button('⬇️ Exportar libro de notas CSV',students_df(students).to_csv(index=False).encode('utf-8-sig'),'aulacontrol-libro-notas.csv','text/csv')

elif active=='Asistencia':
    st.write('Control de asistencia y planificación de clases. Las alertas se activan por debajo del 50%.')
    st.metric('Estudiantes bajo el 50%',len(at_risk))
    for s in students:
        with st.container(border=True):
            c1,c2,c3=st.columns([3,2,2]); c1.write(f"**{s['name']}** · {s['code']}");
            with c2: s['attendance']=st.slider('Asistencia %',0,100,int(s['attendance']),key=f"att_{s['id']}")
            with c3: st.write('⚠️ Seguimiento' if s['attendance']<50 else '✅ En rango')
    st.subheader('Clases y actividades')
    if db['sessions']: st.dataframe(pd.DataFrame(db['sessions']),use_container_width=True,hide_index=True)
    with st.expander('➕ Nueva clase o actividad'):
        with st.form('new_session'):
            topic=st.text_input('Tema / actividad'); dt=st.date_input('Fecha',value=date.today()); typ=st.selectbox('Tipo',['Clase','Práctica','Seminario','Evaluación']); ok=st.form_submit_button('Guardar actividad')
        if ok and topic.strip(): db['sessions'].append({'id':next_id(db['sessions']),'date':str(dt),'topic':topic.strip(),'type':typ,'status':'Planificada'}); st.success('Actividad añadida.'); st.rerun()

elif active=='Cursos y grupos':
    st.subheader('Configuración del curso')
    st.write(f"**Asignatura:** {st.session_state.subject}　|　**Período:** {st.session_state.term}")
    groups=sorted(set(s['group'] for s in students)); st.metric('Grupos registrados',len(groups)); st.metric('Estudiantes matriculados',len(students))
    for g in groups:
        with st.expander(f'Grupo {g} · {sum(s["group"]==g for s in students)} estudiantes'):
            st.dataframe(students_df([s for s in students if s['group']==g]),use_container_width=True,hide_index=True)
    with st.expander('Añadir estudiante al curso'):
        with st.form('course_student'):
            n=st.text_input('Nombre'); code=st.text_input('Código de matrícula'); group=st.text_input('Grupo','2A'); ok=st.form_submit_button('Añadir')
        if ok and n.strip() and code.strip(): db['students'].append({'id':next_id(students),'name':n.strip(),'code':code.strip(),'group':group,'attendance':100,'grades':[None,None,None,None],'published':False}); st.rerun()

elif active=='Clases y temas':
    st.write('Planifica contenidos, unidades temáticas y apuntes.')
    with st.expander('➕ Añadir tema o clase',expanded=not db['lessons']):
        with st.form('new_lesson'):
            title=st.text_input('Título del tema'); unit=st.text_input('Unidad temática','Unidad 1'); dt=st.date_input('Fecha',value=date.today()); notes=st.text_area('Apuntes de la clase'); ok=st.form_submit_button('Guardar tema')
        if ok and title.strip(): db['lessons'].append({'id':next_id(db['lessons']),'title':title.strip(),'unit':unit,'date':str(dt),'notes':notes}); st.success('Tema guardado.'); st.rerun()
    for lesson in db['lessons']:
        with st.expander(f"{lesson['title']} · {lesson['date']}"):
            st.caption(lesson.get('unit','')); st.write(lesson.get('notes','') or 'Sin apuntes.');
            if st.button('Eliminar tema',key=f"del_lesson_{lesson['id']}"): db['lessons']=[x for x in db['lessons'] if x['id']!=lesson['id']]; st.rerun()

elif active=='Bibliografía':
    st.write('Recursos de apoyo para la asignatura.')
    for r in db['resources']:
        st.markdown(f"**{r['title']}** · {r.get('author','')}  \n[{r['url']}]({r['url']})")
    with st.expander('➕ Añadir recurso'):
        with st.form('new_resource'):
            title=st.text_input('Título'); author=st.text_input('Autor o institución'); url=st.text_input('URL'); ok=st.form_submit_button('Guardar recurso')
        if ok and title.strip() and url.startswith(('http://','https://')): db['resources'].append({'title':title.strip(),'author':author,'url':url}); st.success('Recurso añadido.'); st.rerun()
        elif ok: st.error('Indica un título y una URL válida que empiece por http:// o https://.')

elif active=='Tareas':
    st.write('Gestiona actividades y fechas límite.')
    with st.expander('➕ Nueva tarea'):
        with st.form('new_task'):
            title=st.text_input('Título de la tarea'); due=st.date_input('Fecha límite',value=date.today()+timedelta(days=7)); ok=st.form_submit_button('Crear tarea')
        if ok and title.strip(): db['tasks'].append({'id':next_id(db['tasks']),'title':title.strip(),'due':str(due),'status':'Abierta'}); st.success('Tarea creada.'); st.rerun()
    for t in db['tasks']:
        with st.container(border=True):
            c1,c2,c3=st.columns([4,2,2]); c1.write(f"**{t['title']}**"); c2.write(f"Fecha límite: {t.get('due','—')}");
            with c3:
                if st.button('Cerrar' if t['status']=='Abierta' else 'Reabrir',key=f"toggle_task_{t['id']}"): t['status']='Cerrada' if t['status']=='Abierta' else 'Abierta'; st.rerun()
                if st.button('Eliminar',key=f"del_task_{t['id']}"): db['tasks']=[x for x in db['tasks'] if x['id']!=t['id']]; st.rerun()
            st.caption('Estado: '+t['status'])

elif active=='Analítica':
    vals=[metrics(s)['Promedio sistemático'] for s in students if metrics(s)['Promedio sistemático'] is not None]
    a,b,c,d=st.columns(4); a.metric('Promedio del grupo',f(avg(vals))); b.metric('Mejor sistemática',f(max(vals) if vals else None)); c.metric('Alertas de asistencia',len(at_risk)); d.metric('Estudiantes con notas',len(vals))
    st.subheader('Distribución del promedio sistemático')
    if vals: st.bar_chart(pd.Series(vals,name='Promedio').value_counts().sort_index())
    st.subheader('Seguimiento de asistencia')
    st.dataframe(pd.DataFrame([{'Estudiante':s['name'],'Asistencia %':s['attendance'],'Promedio S':f(metrics(s)['Promedio sistemático']),'Seguimiento':'Revisar causas' if s['attendance']<50 else 'Sin alerta'} for s in students]),use_container_width=True,hide_index=True)

elif active=='Informes':
    st.subheader('Exportaciones')
    st.download_button('⬇️ Descargar libro de notas CSV',students_df(students).to_csv(index=False).encode('utf-8-sig'),'aulacontrol-libro-notas.csv','text/csv')
    backup={'version':1,'subject':st.session_state.subject,'term':st.session_state.term,**db}
    st.download_button('⬇️ Descargar respaldo JSON',json.dumps(backup,ensure_ascii=False,indent=2).encode('utf-8'),'aulacontrol-respaldo.json','application/json')
    uploaded=st.file_uploader('Restaurar respaldo AulaControl (JSON)',type=['json'])
    if uploaded:
        if st.button('Importar y reemplazar datos'):
            try:
                data=json.load(uploaded)
                if not isinstance(data.get('students'),list): raise ValueError('No contiene una lista de estudiantes.')
                for k in ['students','sessions','lessons','tasks','resources']:
                    if isinstance(data.get(k),list): db[k]=data[k]
                st.success('Respaldo importado.'); st.rerun()
            except Exception as e: st.error(f'No se pudo importar: {e}')
    st.subheader('Resumen del informe'); a,b,c,d=st.columns(4); a.metric('Estudiantes',len(students)); b.metric('Notas capturadas',sum(sum(g is not None for g in s['grades']) for s in students)); c.metric('Publicaciones',published); d.metric('Alertas',len(at_risk))
    st.warning('El respaldo puede contener información académica. Esta versión no cifra el JSON.')

elif active=='Configuración':
    st.subheader('Preferencias de la aplicación')
    st.toggle('Preferir tema oscuro (visualización)',key='dark')
    st.write('**Asignatura activa:**',st.session_state.subject); st.write('**Período:**',st.session_state.term)
    st.subheader('Reglas académicas')
    a,b,c=st.columns(3); a.metric('Sistemática','Promedio simple'); b.metric('Cortes','(S + Pᵢ) / 2'); c.metric('Final','2 × (C₁ + C₂) · /40')
    st.info('Versión MVP: no tiene autenticación real, roles, base de datos compartida ni sincronización multiusuario. Los datos de esta versión viven en la sesión de Streamlit y pueden perderse al reiniciar. No introduzcas datos personales o académicos reales hasta añadir almacenamiento persistente y controles de acceso.')

st.divider()
st.caption('© 2026 AulaControl · Adaptación completa de la interfaz MVP a Streamlit. No usar aún como sistema oficial de publicación de notas.')
