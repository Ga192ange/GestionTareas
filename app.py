from flask import Flask, render_template, request, redirect
from firebase_config import db

app = Flask(__name__)


@app.route("/")
def inicio():
    return redirect("/registro")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        correo = request.form["correo"]
        password = request.form["password"]

        usuarios = db.collection("usuarios").stream()

        for usuario in usuarios:

            datos = usuario.to_dict()

            if datos["correo"] == correo and datos["password"] == password:

                return redirect("/dashboard")

        return render_template("login.html", error="Correo o contraseña incorrectos")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    # PROYECTOS
    proyectos = list(db.collection("proyectos").stream())

    total_proyectos = len(proyectos)

    activos = 0
    finalizados = 0

    for proyecto in proyectos:

        datos = proyecto.to_dict()

        if datos["estado"] == "Activo":
            activos += 1

        elif datos["estado"] == "Finalizado":
            finalizados += 1

    # TAREAS
    tareas = list(db.collection("tareas").stream())

    total_tareas = len(tareas)

    pendientes = 0
    progreso = 0
    completadas = 0

    for tarea in tareas:

        datos = tarea.to_dict()

        if datos["estado"] == "Pendiente":
            pendientes += 1

        elif datos["estado"] == "En Progreso":
            progreso += 1

        elif datos["estado"] == "Completada":
            completadas += 1

    return render_template(
        "dashboard.html",
        total_proyectos=total_proyectos,
        activos=activos,
        finalizados=finalizados,
        total_tareas=total_tareas,
        pendientes=pendientes,
        progreso=progreso,
        completadas=completadas,
    )


# PROYECTOS
@app.route("/proyectos")
def proyectos():

    proyectos_ref = db.collection("proyectos").stream()

    lista_proyectos = []

    for proyecto in proyectos_ref:

        datos = proyecto.to_dict()

        datos["id"] = proyecto.id

        lista_proyectos.append(datos)

    return render_template("proyectos.html", proyectos=lista_proyectos)


@app.route("/tareas")
def tareas():

    filtro_estado = request.args.get("estado")

    tareas_ref = db.collection("tareas").stream()

    lista_tareas = []

    for tarea in tareas_ref:

        datos = tarea.to_dict()

        datos["id"] = tarea.id

        if filtro_estado:

            if datos["estado"] == filtro_estado:
                lista_tareas.append(datos)

        else:
            lista_tareas.append(datos)

    return render_template("tareas.html", tareas=lista_tareas)


@app.route("/nuevo-proyecto", methods=["GET", "POST"])
def nuevo_proyecto():

    if request.method == "POST":

        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        estado = request.form["estado"]

        db.collection("proyectos").add(
            {"nombre": nombre, "descripcion": descripcion, "estado": estado}
        )

        return redirect("/proyectos")

    return render_template("proyecto_form.html")


@app.route("/nueva-tarea", methods=["GET", "POST"])
def nueva_tarea():

    if request.method == "POST":

        titulo = request.form["titulo"]
        descripcion = request.form["descripcion"]
        usuario = request.form["usuario"]
        proyecto = request.form["proyecto"]
        prioridad = request.form["prioridad"]
        fecha_limite = request.form["fecha_limite"]
        estado = request.form["estado"]

        db.collection("tareas").add(
            {
                "titulo": titulo,
                "descripcion": descripcion,
                "usuario": usuario,
                "proyecto": proyecto,
                "prioridad": prioridad,
                "fecha_limite": fecha_limite,
                "estado": estado,
            }
        )

        return redirect("/tareas")

    return render_template("tarea_form.html")


@app.route("/eliminar-proyecto/<id>")
def eliminar_proyecto(id):

    db.collection("proyectos").document(id).delete()

    return redirect("/proyectos")


@app.route("/eliminar-tarea/<id>")
def eliminar_tarea(id):

    db.collection("tareas").document(id).delete()

    return redirect("/tareas")


@app.route("/editar-proyecto/<id>", methods=["GET", "POST"])
def editar_proyecto(id):

    proyecto_ref = db.collection("proyectos").document(id)

    if request.method == "POST":

        proyecto_ref.update(
            {
                "nombre": request.form["nombre"],
                "descripcion": request.form["descripcion"],
                "estado": request.form["estado"],
            }
        )

        return redirect("/proyectos")

    proyecto = proyecto_ref.get().to_dict()

    return render_template("editar_proyecto.html", proyecto=proyecto)


@app.route("/editar-tarea/<id>", methods=["GET", "POST"])
def editar_tarea(id):

    tarea_ref = db.collection("tareas").document(id)

    if request.method == "POST":

        tarea_ref.update(
            {
                "titulo": request.form["titulo"],
                "descripcion": request.form["descripcion"],
                "usuario": request.form["usuario"],
                "proyecto": request.form["proyecto"],
                "prioridad": request.form["prioridad"],
                "estado": request.form["estado"],
            }
        )

        return redirect("/tareas")

    tarea = tarea_ref.get().to_dict()

    return render_template("editar_tarea.html", tarea=tarea)


@app.route("/usuarios")
def usuarios():

    usuarios_ref = db.collection("usuarios").stream()

    lista_usuarios = []

    for usuario in usuarios_ref:

        datos = usuario.to_dict()

        lista_usuarios.append(datos)

    return render_template("usuarios.html", usuarios=lista_usuarios)


@app.route("/registro", methods=["GET", "POST"])
def registro():

    if request.method == "POST":

        db.collection("usuarios").add(
            {
                "nombre": request.form["nombre"],
                "correo": request.form["correo"],
                "password": request.form["password"],
                "rol": "usuario",
            }
        )

        return redirect("/login")

    return render_template("registro.html")


@app.route("/cerrar-sesion")
def cerrar_sesion():
    return redirect("/registro")


if __name__ == "__main__":
    app.run(debug=True)
