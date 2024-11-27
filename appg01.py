from flask import Flask, request, url_for, redirect, render_template, abort, flash
from flask import send_file
app = Flask(__name__)

app.secret_key = 'jesus1804'

from datetime import datetime
import mysql.connector

#IMPORTAR EL CONECTOR DE MYSQL
import mysql.connector

import pandas as pd
import os

'''#CONECTAR LA BD
midb = mysql.connector.connect(    
    host='localhost',
    user='JepeJepe',
    password='EPEJjesus4081',
    database='prueba'
    ) 

cursor = midb.cursor(dictionary=True) #Le indica al sistema que convierta la tabla en un diccionario en vez de una tupla
'''

sql_listar="""
SELECT 
    idg, 
    monto, 
    cuenta, 
    detalle, 
    Previsto,
    DATE_FORMAT(fecha, '%d/%m/%y') AS f_f 
FROM 
    appg01;
"""

@app.route('/')
def index():
    #return 'segundo mensaje de la app Gastos 01'
    return render_template('plantilla.html')

#@app.route('/ingreso')
#def ingreso():
#    return render_template('registro.html')
    
@app.route('/mensaje', methods=['GET'])
def mensaje():
    return render_template('mensaje.html', mensaje='Hola Jepecito')

sql_totalizar="""
WITH NumberedRecords AS (
  SELECT 
    monto, 
    ROW_NUMBER() OVER (ORDER BY idg) AS row_num
  FROM appg01
)
SELECT SUM(monto) as page_total
FROM NumberedRecords
WHERE row_num BETWEEN {start_row} AND {end_row};
"""

#########################  funciones para revisión de datos

def get_data(page, records_per_page):
    
    midb = mysql.connector.connect(    
    host='localhost',
    user='JepeJepe',
    password='EPEJjesus4081',
    database='prueba'
    ) 

    cursor = midb.cursor(dictionary=True)  
    
    offset = (page - 1) * records_per_page
    
    # Query to get the records with pagination
    query = f"""
        SELECT idg, fecha, monto, cuenta, detalle, CASE WHEN Previsto = 1 THEN 'Sí' ELSE 'No' END AS Previsto
        FROM (
            SELECT idg, fecha, monto, cuenta, detalle, Previsto,
                   ROW_NUMBER() OVER (ORDER BY idg DESC) AS row_num
            FROM appg01
        ) AS numbered_rows
        WHERE row_num > {offset} AND row_num <= {offset + records_per_page}
    """
    cursor.execute(query)
    records = cursor.fetchall()
    
    # Query to get the total of the current page
    cursor.execute(f"""
        SELECT SUM(monto) AS page_total
        FROM (
            SELECT monto,
                   ROW_NUMBER() OVER (ORDER BY idg DESC) AS row_num
            FROM appg01
        ) AS numbered_rows
        WHERE row_num > {offset} AND row_num <= {offset + records_per_page}
    """)
    page_total = cursor.fetchone()['page_total'] or 0
    
    # Query to get the total general
    cursor.execute("SELECT SUM(monto) AS total_general FROM appg01")
    total_general = cursor.fetchone()['total_general'] or 0
    
    midb.close()
    
    return records, page_total, total_general
    
################################# fin funcoines de revisión de datos #################################


@app.route('/revision', methods=['GET'])
def revision():
    
    midb = mysql.connector.connect(    
        host='localhost',
        user='JepeJepe',
        password='EPEJjesus4081',
        database='prueba'
        ) 

    cursor = midb.cursor(dictionary=True)   
   
  
    # Convertir los valores booleanos (1 o 0) a "Sí" o "No"
    #for registro in records:
    #    registro['Previsto'] = "Sí" if registro['Previsto'] == 1 else "No"
    
    page = request.args.get('page', 1, type=int)  # Obtener número de página, por defecto 1
    records_per_page = 10
    offset = (page - 1) * records_per_page

    # Get the data for the current page
    records, page_total, total_general = get_data(page, records_per_page)
    
    
    
    cursor.execute("SELECT COUNT(*) AS total_records FROM appg01")
        
    total_records = cursor.fetchone()['total_records']
    total_pages = (total_records + records_per_page - 1) // records_per_page

    #offset = records_per_page / total_records
        
    # Consulta para obtener el total de la página actual
    cursor.execute(f"""
        SELECT SUM(monto) as page_total
        FROM (
            SELECT monto, ROW_NUMBER() OVER (ORDER BY idg) AS row_num
            FROM appg01
        ) AS numbered_rows
        WHERE row_num > {offset} AND row_num <= {offset + records_per_page}
    """)
    
    page_total = cursor.fetchone()['page_total'] or 0

    # Consulta para obtener el total general
    cursor.execute("SELECT SUM(monto) as total_general FROM appg01")
    total_general = cursor.fetchone()['total_general'] or 0

    midb.close()

    return render_template(
        'review.html',
        records=records,
        page_total=page_total,
        total_general=total_general,
        current_page=page,
        total_pages=total_pages
    )

@app.route('/labd', methods=['GET', 'POST'])
def labd():

    midb = mysql.connector.connect(    
    host='localhost',
    user='JepeJepe',
    password='EPEJjesus4081',
    database='prueba'
    ) 

    cursor = midb.cursor(dictionary=True)  
    
    page = request.args.get('page', 1, type=int)  # Obtener número de página, por defecto 1
    records_per_page = 10
    offset = (page - 1) * records_per_page

    # Get the data for the current page
    records, page_total, total_general = get_data(page, records_per_page)
    
    cursor.execute("SELECT COUNT(*) AS total_records FROM appg01")
    total_records = cursor.fetchone()['total_records']
    total_pages = (total_records + records_per_page - 1) // records_per_page

    #offset = records_per_page / total_records
        
    # Consulta para obtener el total de la página actual
    cursor.execute(f"""
        SELECT SUM(monto) as page_total
        FROM (
            SELECT monto, ROW_NUMBER() OVER (ORDER BY idg) AS row_num
            FROM appg01
        ) AS numbered_rows
        WHERE row_num > {offset} AND row_num <= {offset + records_per_page}
    """)
    page_total = cursor.fetchone()['page_total'] or 0

    # Consulta para obtener el total general
    cursor.execute("SELECT SUM(monto) as total_general FROM appg01")
    total_general = cursor.fetchone()['total_general'] or 0

    midb.close()

    return render_template(
        'review.html',
        records=records,
        page_total=page_total,
        total_general=total_general,
        current_page=page,
        total_pages=total_pages
    )

#CREAR NUEVOS REGISTROS
@app.route('/ingreso', methods=['GET', 'POST'])
def ingreso():

    midb = mysql.connector.connect(    
    host='localhost',
    user='JepeJepe',
    password='EPEJjesus4081',
    database='prueba'
    ) 

    cursor = midb.cursor(dictionary=True)  
    
    if request.method == "POST":
        fecha = request.form['fecha']
        monto = request.form['monto'] 
        cuenta = request.form['cuenta']
        detalle = request.form['detalle']
        previsto = request.form.get('Previsto') =='on'
        sql = "insert into appg01 (fecha, monto, cuenta, detalle, previsto) values (%s, %s, %s, %s, %s)"
        values = (fecha, monto, cuenta, detalle, previsto)

#        sql = "insert into appg01 (fecha, monto, cuenta, detalle) values (%s, %s, %s, %s)"
#        values = (fecha, monto, cuenta, detalle)
        

        cursor.execute (sql, values)
        midb.commit()    

        midb.close()
        
        return redirect(url_for('labd')) #una vez cargados los datos envía a revisión del listado total con el nuevo registro
    
    return render_template('registro.html') # return es un comando que envía una respuesta HTML puede ser una cadena de texto o una acción

#MODIFICAR | EDITAR un registro con su ID

### inicio Editar old
@app.route('/editar/<int:idg>', methods=['GET', 'POST'])
def editar_registro(idg):
#    midb = mysql.connector.connect(**db_config)
    midb = mysql.connector.connect(    
    host='localhost',
    user='JepeJepe',
    password='EPEJjesus4081',
    database='prueba'
    ) 
    
    cursor = midb.cursor(dictionary=True)

    if request.method == 'POST':
        
        fecha = request.form['fecha']
        monto = request.form['monto']
        cuenta = request.form['cuenta']
        detalle = request.form['detalle']
        previsto = 1 if 'previsto' in request.form else 0

        # Actualiza el registro en la base de datos
        consulta = """
            UPDATE appg01
            SET fecha = %s, monto = %s, cuenta = %s, detalle = %s, Previsto = %s
            WHERE idg = %s
        """
        valores = (fecha, monto, cuenta, detalle, previsto, idg)

        cursor.execute(consulta, valores)
        midb.commit()
        midb.close()
        return redirect(url_for('labd')) # Envía a revisión de registros

    else:
        cursor.execute("SELECT idg, fecha, FORMAT(monto, 2) AS monto, cuenta, detalle, previsto FROM appg01 WHERE idg = %s", (idg,))
        registro = cursor.fetchone()
        cursor.close()
        midb.close()
        registro['fecha'] = registro['fecha'].strftime('%Y-%m-%d')
        registro['previsto']=registro['previsto']
        previsto_checked = 'checked' if registro['previsto'] == 1 else ''
        #return render_template('editar.html', registro=registro)
    
        return render_template('editar.html', registro=registro, 
                               previsto_checked=previsto_checked)
#FIN editar old

@app.route('/editar2/<int:idg>', methods=['GET', 'POST'])
def editar_registro2(idg):

    midb = mysql.connector.connect(    
    host='localhost',
    user='JepeJepe',
    password='EPEJjesus4081',
    database='prueba'
    ) 

    cursor = midb.cursor(dictionary=True)
    
    if request.method == 'POST':

        fecha = request.form['fecha']   
        monto = request.form['monto']
        cuenta = request.form['cuenta']
        detalle = request.form['detalle']
        previsto = 1 if 'previsto' in request.form else 0 
            
        # Actualiza el registro en la base de datos
        consulta = """
            UPDATE appg01
            SET fecha = %s, monto = %s, cuenta = %s, detalle = %s, Previsto = %s
            WHERE idg = %s
        """
        valores = (fecha, monto, cuenta, detalle, previsto, idg)
            
        cursor.execute(consulta, valores)
        midb.commit()

        midb.close() #ojo con esto#
        
        return redirect(url_for('labd')) # Envía a revisión de registros
        #else:
        #    print('no se encontró registro')
        #    return redirect(url_for('labd'))    
    
    else:

        cursor.execute("SELECT idg, fecha, FORMAT(monto, 2) AS monto, cuenta, detalle, previsto FROM appg01 WHERE idg = %s", (idg,))
        registro = cursor.fetchone()
        #cursor.close()
        #midb.close()
        
        registro['fecha'] = registro['fecha'].strftime('%Y-%m-%d')
        registro['previsto']=registro['previsto']
        previsto_checked = 'checked' if registro['previsto'] == 1 else ''   
                       
        midb.close()
        
        return render_template('editar.html', registro=registro, 
                               previsto_checked=previsto_checked)

@app.route('/borrar/<int:idg>', methods=['GET', 'POST'])
def borrar_registro(idg):
    
    midb = mysql.connector.connect(    
    host='localhost',
    user='JepeJepe',
    password='EPEJjesus4081',
    database='prueba'
    ) 

    cursor = midb.cursor(dictionary=True)
    if request.method == 'POST':
        # Si el método es POST, se procede a borrar el registro
        consulta = "DELETE FROM appg01 WHERE idg = %s"
        cursor.execute(consulta, (idg,))
        midb.commit()
        midb.close()
        return redirect(url_for('labd'))  # Redirige a la página 'labd'
    else:
        cursor.execute("SELECT idg, DATE_FORMAT(fecha, '%d/%m/%y') AS fecha, CAST(FORMAT(monto, 2) AS DOUBLE) AS monto, cuenta, detalle, previsto FROM appg01 WHERE idg = %s", (idg,))
        registro = cursor.fetchone()
        midb.close()
        return render_template('borrar.html', registro=registro)
    
@app.route('/vermes', methods=['GET', 'POST'])
def vermes():

    midb = mysql.connector.connect(    
    host='localhost',
    user='JepeJepe',
    password='EPEJjesus4081',
    database='prueba'
    ) 

    cursor = midb.cursor(dictionary=True)  
    
    cursor.execute(sql_listar, )
    rows = cursor.fetchall() #Se graban los registros de 'usuario' en una variable
    
    cursor.execute("SELECT idg, fecha, monto, cuenta, detalle, previsto FROM appg01")
    registros = cursor.fetchall()
    
    cursor.execute("SELECT SUM(monto) AS total_monto FROM appg01")
    total_monto = cursor.fetchone()['total_monto']

    midb.close()

    return render_template('pormes.html', gastos=rows, registros=registros, total_monto=total_monto)

@app.route('/resultados')

def resultados():

    midb = mysql.connector.connect(    
    host='localhost',
    user='JepeJepe',
    password='EPEJjesus4081',
    database='prueba'
    ) 

    cursor = midb.cursor(dictionary=True)  
    
    # Obtener mes, año y página de los parámetros
    mes = request.args.get('mes', type=int)
    anio = request.args.get('anio', type=int)
    page = request.args.get('page', 1, type=int)
    
    records_per_page = 10
    offset = (page - 1) * records_per_page
  
    # Obtener los registros paginados usando ROW_NUMBER()
    query = f"""
        SELECT idg, fecha, monto, cuenta, detalle, CASE WHEN Previsto = 1 THEN 'Sí' ELSE 'No' END AS Previsto
        FROM (
            SELECT idg, fecha, monto, cuenta, detalle, previsto,
                   ROW_NUMBER() OVER (ORDER BY idg) AS row_num
            FROM appg01
            WHERE MONTH(fecha) = {mes} AND YEAR(fecha) = {anio}
        ) AS numbered_rows
        WHERE row_num > {offset} AND row_num <= {offset + records_per_page}
    """
    cursor.execute(query)
    registros = cursor.fetchall()
    
    # Obtener el total de la página
    query_total_pagina = f"""
        SELECT SUM(monto) as total_pagina
        FROM (
            SELECT monto, ROW_NUMBER() OVER (ORDER BY idg) AS row_num
            FROM appg01
            WHERE MONTH(fecha) = {mes} AND YEAR(fecha) = {anio}
        ) AS numbered_rows
        WHERE row_num > {offset} AND row_num <= {offset + records_per_page}
    """
    cursor.execute(query_total_pagina)
    total_pagina = cursor.fetchone()['total_pagina'] or 0

    # Obtener el total general
    query_total_general = f"SELECT SUM(monto) as total_general FROM appg01 WHERE MONTH(fecha) = {mes} AND YEAR(fecha) = {anio}"
    cursor.execute(query_total_general)
    total_general = cursor.fetchone()['total_general'] or 0
    
    # Obtener el número total de páginas
    query_count = f"SELECT COUNT(*) as total_registros FROM appg01 WHERE MONTH(fecha) = {mes} AND YEAR(fecha) = {anio}"
    cursor.execute(query_count)
    total_registros = cursor.fetchone()['total_registros']
    total_pages = (total_registros + records_per_page - 1) // records_per_page
    
    midb.close()
    
    return render_template('resultados.html',
                           mes = mes,
                           anio = anio, 
                           registros=registros, 
                           total_pagina=total_pagina,
                           total_general=total_general,
                           page=page, 
                           total_pages=total_pages)

@app.route('/exportar', methods=['GET', 'POST'])
def exportar():
    if request.method == 'POST':
        # Obtener las fechas del formulario
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        
        # Formatear las fechas para la consulta SQL
        #fecha_inicio = datetime.strptime(fecha_inicio, "%d/%m/%y").strftime("%Y-%m-%d")
        #fecha_fin = datetime.strptime(fecha_fin, "%d/%m/%y").strftime("%Y-%m-%d")
        
        # Conexión a la base de datos MySQL
        midb = mysql.connector.connect(    
        host='localhost',
        user='JepeJepe',
        password='EPEJjesus4081',
        database='prueba'
        ) 
        
        cursor = midb.cursor(dictionary=True)  
        
        # Consulta SQL para obtener los registros en el rango de fechas
        query = """
            SELECT idg, fecha, monto, cuenta, detalle, Previsto 
            FROM appg01 
            WHERE fecha BETWEEN %s AND %s
        """
        cursor.execute(query, (fecha_inicio, fecha_fin))
        registros = cursor.fetchall()
        
        # Cerrar la conexión
        cursor.close()
        midb.close()

        # Si hay registros, crear archivo Excel
        if registros:
            df = pd.DataFrame(registros)
            df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%d/%m/%Y')
            df['Previsto'] = df['Previsto'].apply(lambda x: 'Sí' if x == 1 else 'No')
            
            # Formatear el nombre del archivo Excel
            #nombre_archivo = f"gastos_del_{request.form['fecha_inicio']}_al_{request.form['fecha_final']}.xlsx"
            nombre_archivo = f"gastos_APG01.xlsx"
            ruta_archivo = os.path.join('C:\\Users\\PC\\Downloads', nombre_archivo)
            #ruta_archivo = os.path.join('C:\\Users\\PC\\OneDrive\\Documentos', nombre_archivo)
                    
            # Guardar el archivo Excel
            df.to_excel(ruta_archivo, index=False)

            # Descargar el archivo
            #archivo_resultado = os.path.join(ruta_archivo, nombre_archivo)
            #registros.to_excel(archivo_resultado, index=False)
            return send_file(ruta_archivo, as_attachment=True)
        else:
            return "No hay registros en el rango de fechas seleccionado."
    
    # Renderizar el formulario
    return render_template('exportar.html')


if __name__ == '__main__':
    app.run(debug=True)