from flask import Flask, render_template, request, redirect
import mysql.connector

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import Response
import io
import os

app = Flask(__name__)

#def get_db_connection():
#    return mysql.connector.connect(
       # host="localhost",
       # user="root",
       # password="a.0123456",
       # database="cursos_cedite"

#    )

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('MYSQLHOST'),
        user=os.environ.get('MYSQLUSER'),
        password=os.environ.get('MYSQLPASSWORD'),
        database=os.environ.get('MYSQLDATABASE'),
        port=int(os.environ.get('MYSQLPORT', 3306))
    )

@app.route("/")
def index():

    participantes = query_db(
        "SELECT COUNT(*) as total FROM participantes",
        fetch=True
    )[0]["total"]

    cursos = query_db(
        "SELECT COUNT(*) as total FROM cursos",
        fetch=True
    )[0]["total"]

    docentes = query_db(
        "SELECT COUNT(*) as total FROM docentes",
        fetch=True
    )[0]["total"]

    inscripciones = query_db(
        "SELECT COUNT(*) as total FROM inscripciones",
        fetch=True
    )[0]["total"]

    return render_template(
        "index.html",
        participantes=participantes,
        cursos=cursos,
        docentes=docentes,
        inscripciones=inscripciones
    )

@app.route("/participantes")
def participantes():

    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)

    buscar = request.args.get("buscar")

    if buscar:
        sql = """
        SELECT * FROM participantes
        WHERE apellido LIKE %s
        OR nombre LIKE %s
        OR dni LIKE %s
        OR email LIKE %s
        """
        valor = "%" + buscar + "%"
        cursor.execute(sql, (valor, valor, valor, valor))
    else:
        cursor.execute("SELECT * FROM participantes")

    participantes = cursor.fetchall()

    cursor.close()
    conexion.close()

    eliminado = request.args.get("eliminado")
    error = request.args.get("error")

    return render_template(
        "participantes.html",
        participantes=participantes,
        eliminado=eliminado,
        error=error
    )

@app.route("/nuevo_participante", methods=["GET", "POST"])
def nuevo_participante():
    if request.method == "POST":
        apellido = request.form["apellido"]
        nombre = request.form["nombre"]
        dni = request.form["dni"]
        email = request.form["email"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO participantes (apellido, nombre, dni, email)
            VALUES (%s, %s, %s, %s)
        """, (apellido, nombre, dni, email))
        conn.commit()
        conn.close()

        return redirect("/participantes")

    return render_template("nuevo_participante.html")
    
@app.route("/editar_participante/<int:id>", methods=["GET","POST"])
def editar_participante(id):

    participante = query_db(
        "SELECT * FROM participantes WHERE id_participante=%s",
        (id,),
        fetch=True
    )[0]

    if request.method == "POST":

        apellido = request.form["apellido"]
        nombre = request.form["nombre"]
        dni = request.form["dni"]
        email = request.form["email"]

        query_db("""
            UPDATE participantes
            SET apellido=%s, nombre=%s, dni=%s, email=%s
            WHERE id_participante=%s
        """,(apellido,nombre,dni,email,id))

        return redirect("/participantes")

    return render_template("editar_participante.html", participante=participante)
    
@app.route('/eliminar_participante/<int:id>')
def eliminar_participante(id):

    conexion = get_db_connection()
    cursor = conexion.cursor()

    try:
        cursor.execute("DELETE FROM participantes WHERE id_participante = %s", (id,))
        conexion.commit()

        cursor.close()
        conexion.close()

        return redirect("/participantes?eliminado=1")

    except mysql.connector.IntegrityError:

        cursor.close()
        conexion.close()

        return redirect("/participantes?error=1")

from flask import request

from flask import request, render_template

@app.route("/cursos")
def cursos():

    buscar = request.args.get("buscar", "")
    eliminado = request.args.get("eliminado")
    error = request.args.get("error")

    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT *
        FROM cursos
        WHERE nombre_curso LIKE %s
        OR descripcion LIKE %s
    """

    cursor.execute(query, (f"%{buscar}%", f"%{buscar}%"))

    data = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "cursos.html",
        cursos=data,
        eliminado=eliminado,
        error=error
    )
    
@app.route("/nuevo_curso", methods=["GET", "POST"])
def nuevo_curso():
    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        duracion = request.form["duracion"]

        query_db("""
            INSERT INTO cursos (nombre_curso, descripcion, duracion_horas)
            VALUES (%s, %s, %s)
        """, (nombre, descripcion, duracion))

        return redirect("/cursos")

    return render_template("nuevo_curso.html")
    
@app.route("/editar_curso/<int:id>", methods=["GET","POST"])
def editar_curso(id):

    curso = query_db(
        "SELECT * FROM cursos WHERE id_curso=%s",
        (id,),
        fetch=True
    )[0]

    if request.method == "POST":

        nombre = request.form["nombre_curso"]
        descripcion = request.form["descripcion"]
        duracion = request.form["duracion_horas"]

        query_db("""
            UPDATE cursos
            SET nombre_curso=%s,
                descripcion=%s,
                duracion_horas=%s
            WHERE id_curso=%s
        """,(nombre,descripcion,duracion,id))

        return redirect("/cursos")

    return render_template("editar_curso.html", curso=curso)
    
from flask import flash, redirect, url_for
import mysql.connector

@app.route('/eliminar_curso/<int:id>')
def eliminar_curso(id):

    conexion = get_db_connection()
    cursor = conexion.cursor()

    try:
        cursor.execute("DELETE FROM cursos WHERE id_curso = %s", (id,))
        conexion.commit()

        cursor.close()
        conexion.close()

        return redirect("/cursos?eliminado=1")

    except mysql.connector.IntegrityError:

        cursor.close()
        conexion.close()

        return redirect("/cursos?error=1")
        
from flask import request

@app.route("/docentes")
def docentes():

    buscar = request.args.get("buscar", "")
    eliminado = request.args.get("eliminado")
    error = request.args.get("error")

    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT *
        FROM docentes
        WHERE apellido LIKE %s OR nombre LIKE %s
    """

    cursor.execute(query, (f"%{buscar}%", f"%{buscar}%"))

    data = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "docentes.html",
        docentes=data,
        buscar=buscar,
        eliminado=eliminado,
        error=error
    )
    
@app.route("/nuevo_docente", methods=["GET", "POST"])
def nuevo_docente():
    if request.method == "POST":
        apellido = request.form["apellido"]
        nombre = request.form["nombre"]
        email = request.form["email"]
        telefono = request.form["telefono"]
        especialidad = request.form["especialidad"]

        query_db("""
            INSERT INTO docentes (apellido, nombre, email, telefono, especialidad)
            VALUES (%s, %s, %s, %s, %s)
        """, (apellido, nombre, email, telefono, especialidad))

        return redirect("/docentes")

    return render_template("nuevo_docente.html")
    
@app.route("/editar_docente/<int:id>", methods=["GET","POST"])
def editar_docente(id):

    docente = query_db(
        "SELECT * FROM docentes WHERE id_docente=%s",
        (id,),
        fetch=True
    )[0]

    if request.method == "POST":

        apellido = request.form["apellido"]
        nombre = request.form["nombre"]
        email = request.form["email"]

        query_db("""
            UPDATE docentes
            SET apellido=%s,
                nombre=%s,
                email=%s
            WHERE id_docente=%s
        """,(apellido,nombre,email,id))

        return redirect("/docentes")

    return render_template("editar_docente.html", docente=docente)
    
@app.route('/eliminar_docente/<int:id>')
def eliminar_docente(id):

    conexion = get_db_connection()
    cursor = conexion.cursor()

    try:
        cursor.execute("DELETE FROM docentes WHERE id_docente = %s", (id,))
        conexion.commit()

        cursor.close()
        conexion.close()

        return redirect("/docentes?eliminado=1")

    except mysql.connector.IntegrityError:

        cursor.close()
        conexion.close()

        return redirect("/docentes?error=1")
        
@app.route("/ediciones")
def ediciones():
    data = query_db("""
        SELECT e.*, c.nombre_curso, d.apellido
        FROM ediciones e
        JOIN cursos c ON e.id_curso = c.id_curso
        LEFT JOIN docentes d ON e.id_docente = d.id_docente
    """, fetch=True)
    
    return render_template("ediciones.html", ediciones=data)


@app.route("/nueva_edicion", methods=["GET", "POST"])
def nueva_edicion():

    cursos = query_db("SELECT * FROM cursos", fetch=True)
    docentes = query_db("SELECT * FROM docentes", fetch=True)

    if request.method == "POST":

        id_curso = request.form["id_curso"]
        id_docente = request.form.get("id_docente")
        anio = request.form["anio"]
        fecha_inicio = request.form.get("fecha_inicio")
        fecha_fin = request.form.get("fecha_fin")
        cupo_maximo = request.form.get("cupo_maximo")

        query_db("""
            INSERT INTO ediciones
            (id_curso, id_docente, anio, fecha_inicio, fecha_fin, cupo_maximo)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (id_curso, id_docente, anio, fecha_inicio, fecha_fin, cupo_maximo))

        return redirect("/ediciones")

    return render_template(
        "nueva_edicion.html",
        cursos=cursos,
        docentes=docentes
    )
    
@app.route("/inscripciones")
def inscripciones():

    buscar = request.args.get("buscar")

    if buscar:
        data = query_db("""
            SELECT i.*, p.apellido, p.nombre, c.nombre_curso, e.anio
            FROM inscripciones i
            JOIN participantes p ON i.id_participante = p.id_participante
            JOIN ediciones e ON i.id_edicion = e.id_edicion
            JOIN cursos c ON e.id_curso = c.id_curso
            WHERE p.apellido LIKE %s
            OR p.nombre LIKE %s
            OR c.nombre_curso LIKE %s
        """,(f"%{buscar}%",f"%{buscar}%",f"%{buscar}%"),fetch=True)

    else:
        data = query_db("""
            SELECT i.*, p.apellido, p.nombre, c.nombre_curso, e.anio
            FROM inscripciones i
            JOIN participantes p ON i.id_participante = p.id_participante
            JOIN ediciones e ON i.id_edicion = e.id_edicion
            JOIN cursos c ON e.id_curso = c.id_curso
        """,fetch=True)

    return render_template("inscripciones.html", inscripciones=data)
    
@app.route("/nueva_inscripcion", methods=["GET", "POST"])
def nueva_inscripcion():
    participantes = query_db("SELECT * FROM participantes", fetch=True)
    ediciones = query_db("""
        SELECT e.id_edicion, c.nombre_curso, e.anio
        FROM ediciones e
        JOIN cursos c ON e.id_curso = c.id_curso
    """, fetch=True)

    if request.method == "POST":
        id_participante = request.form["id_participante"]
        id_edicion = request.form["id_edicion"]

        query_db("""
            INSERT INTO inscripciones (id_participante, id_edicion, fecha_inscripcion)
            VALUES (%s, %s, CURDATE())
        """, (id_participante, id_edicion))

        return redirect("/inscripciones")

    return render_template("nueva_inscripcion.html",
                           participantes=participantes,
                           ediciones=ediciones)
                           
@app.route("/editar_inscripcion/<int:id>", methods=["GET","POST"])
def editar_inscripcion(id):

    inscripcion = query_db(
        "SELECT * FROM inscripciones WHERE id_inscripcion=%s",
        (id,),
        fetch=True
    )[0]

    participantes = query_db("SELECT * FROM participantes", fetch=True)
    ediciones = query_db("""
        SELECT e.id_edicion, c.nombre_curso, e.anio
        FROM ediciones e
        JOIN cursos c ON e.id_curso = c.id_curso
    """, fetch=True)

    if request.method == "POST":

        participante = request.form["id_participante"]
        edicion = request.form["id_edicion"]

        query_db("""
            UPDATE inscripciones
            SET id_participante=%s,
                id_edicion=%s
            WHERE id_inscripcion=%s
        """,(participante,edicion,id))

        return redirect("/inscripciones")

    return render_template(
        "editar_inscripcion.html",
        inscripcion=inscripcion,
        participantes=participantes,
        ediciones=ediciones
    )
    
@app.route("/eliminar_inscripcion/<int:id>")
def eliminar_inscripcion(id):

    query_db(
        "DELETE FROM inscripciones WHERE id_inscripcion=%s",
        (id,)
    )

    return redirect("/inscripciones")
                           
                        
                        
@app.route("/calificaciones")
def calificaciones():
    data = query_db("""
        SELECT cal.*, p.apellido, p.nombre, c.nombre_curso, e.anio
        FROM calificaciones cal
        JOIN inscripciones i ON cal.id_inscripcion = i.id_inscripcion
        JOIN participantes p ON i.id_participante = p.id_participante
        JOIN ediciones e ON i.id_edicion = e.id_edicion
        JOIN cursos c ON e.id_curso = c.id_curso
    """, fetch=True)

    return render_template("calificaciones.html", calificaciones=data)
    
@app.route("/nueva_calificacion", methods=["GET", "POST"])
def nueva_calificacion():
    inscripciones = query_db("""
        SELECT i.id_inscripcion, p.apellido, p.nombre, c.nombre_curso
        FROM inscripciones i
        JOIN participantes p ON i.id_participante = p.id_participante
        JOIN ediciones e ON i.id_edicion = e.id_edicion
        JOIN cursos c ON e.id_curso = c.id_curso
    """, fetch=True)

    if request.method == "POST":
        id_inscripcion = request.form["id_inscripcion"]
        nota = request.form["nota"]
        aprobado = float(nota) >= 6

        query_db("""
            INSERT INTO calificaciones (id_inscripcion, nota_final, aprobado)
            VALUES (%s, %s, %s)
        """, (id_inscripcion, nota, aprobado))

        return redirect("/calificaciones")

    return render_template("nueva_calificacion.html", inscripciones=inscripciones)
    
@app.route("/reporte_inscripciones")
def reporte_inscripciones():

    data = query_db("""
        SELECT p.apellido, p.nombre, c.nombre_curso, e.anio, i.fecha_inscripcion
        FROM inscripciones i
        JOIN participantes p ON i.id_participante = p.id_participante
        JOIN ediciones e ON i.id_edicion = e.id_edicion
        JOIN cursos c ON e.id_curso = c.id_curso
        ORDER BY p.apellido
    """, fetch=True)

    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=letter)
    y = 750

    pdf.setFont("Helvetica-Bold",16)
    pdf.drawString(200,800,"Reporte de Inscripciones")

    pdf.setFont("Helvetica",10)

    y -= 40

    for row in data:

        linea = f"{row['apellido']} {row['nombre']}  |  {row['nombre_curso']} ({row['anio']})  |  {row['fecha_inscripcion']}"

        pdf.drawString(50,y,linea)

        y -= 20

        if y < 50:
            pdf.showPage()
            y = 750

    pdf.save()

    buffer.seek(0)

    return Response(
        buffer,
        mimetype="application/pdf",
        headers={"Content-Disposition":"inline; filename=inscripciones.pdf"}
    )    

@app.route("/reporte_calificaciones")
def reporte_calificaciones():

    data = query_db("""
        SELECT p.apellido, p.nombre, c.nombre_curso, e.anio, cal.nota_final, cal.aprobado
        FROM calificaciones cal
        JOIN inscripciones i ON cal.id_inscripcion = i.id_inscripcion
        JOIN participantes p ON i.id_participante = p.id_participante
        JOIN ediciones e ON i.id_edicion = e.id_edicion
        JOIN cursos c ON e.id_curso = c.id_curso
        ORDER BY p.apellido
    """, fetch=True)

    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=letter)

    y = 750

    pdf.setFont("Helvetica-Bold",16)
    pdf.drawString(200,800,"Reporte de Calificaciones")

    pdf.setFont("Helvetica",10)

    y -= 40

    for row in data:

        estado = "Aprobado" if row["aprobado"] else "No aprobado"

        linea = f"{row['apellido']} {row['nombre']} | {row['nombre_curso']} ({row['anio']}) | Nota: {row['nota_final']} | {estado}"

        pdf.drawString(50,y,linea)

        y -= 20

        if y < 50:
            pdf.showPage()
            y = 750

    pdf.save()

    buffer.seek(0)

    return Response(
        buffer,
        mimetype="application/pdf",
        headers={"Content-Disposition":"inline; filename=calificaciones.pdf"}
    )

    
def query_db(query, params=None, fetch=False):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    
    if fetch:
        result = cursor.fetchall()
        conn.close()
        return result
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    app.run(debug=True)