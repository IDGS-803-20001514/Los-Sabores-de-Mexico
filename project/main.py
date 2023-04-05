from flask import Blueprint, render_template, request, redirect, url_for
from flask_security import login_required, current_user
from flask_security.decorators import roles_required, roles_accepted
from . import db
from . models import Productos
from werkzeug.utils import secure_filename
import os
import logging

main = Blueprint('main',__name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'jfif'])

@main.route('/')
def index():
    return render_template('inicio.html')

@main.route('/sobreNosotros')
def sobreNosotros():
    return render_template('sobreNosotros.html')

@main.route('/contacto')
def contacto():
    return render_template('contacto.html')

@main.route('/menu')
@login_required
def menu():

    productos = Productos.query.all()

    return render_template('menu.html', productos = productos)

@main.route('/profile')
@login_required
# @roles_required('admin') #Autorización para rol admin
@roles_accepted('admin', 'user') #Autorización para cualquier rol
def profile():

    # Verificar si el usuario es un administrador
    if 'admin' in current_user.roles:

        productos = Productos.query.all()

        return render_template('productos.html', productos = productos)
    
    elif 'user' in current_user.roles:

        productos = Productos.query.all()

        return render_template('menu.html', productos = productos)
    
    else:
        
        return render_template('error.html', message='Tienes que estar registrado para acceder al demas contenido.')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route('/registrarProducto', methods=['POST'])
@login_required
@roles_required('admin')
def registrarProducto():

    if request.method == 'POST':
            
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            precio = request.form['precio']
            tipo = request.form['tipo']

            imagen = request.files['imagen']

            file = secure_filename(imagen.filename)

            if file and allowed_file(file):
                filename = os.path.join('project/static/img/productos/', file)
                imagen.save(filename)
    
            nuevoProducto = Productos(nombre = nombre, descripcion = descripcion, precio = precio,tipo = tipo, imagen = file)
    
            db.session.add(nuevoProducto)
            db.session.commit()
    
            return redirect(url_for('main.profile'))
    

@main.route('/editarProducto', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def editarProducto():
         
        if request.method == 'POST':
    
            id = request.form['id']
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            precio = request.form['precio']
            tipo = request.form['tipo']

            if request.files['imagen'].filename != '':
                imagen = request.files['imagen']
                file = secure_filename(imagen.filename)
                if file and allowed_file(file):
                    filename = os.path.join('project/static/img/productos/', file)
                    imagen.save(filename)
    
                #Eliminar imagen anterior

                image_path = 'project/static/img/productos/'+request.form['imagenRes']

                # Verificar si la imagen existe
                if os.path.exists(image_path):
                # Eliminar la imagen
                    os.remove(image_path)
                    print(f"La imagen en {image_path} ha sido eliminada.")
                else:
                    print(f"La imagen en {image_path} no existe.")

                producto = db.session.query(Productos).filter(Productos.id == id).first()
                producto.nombre = nombre
                producto.descripcion = descripcion
                producto.precio = precio
                producto.imagen = file
                producto.tipo = tipo
        
                db.session.add(producto)
                db.session.commit()
        
                return redirect(url_for('main.profile'))
            
            else:
                 
                producto = db.session.query(Productos).filter(Productos.id == id).first()
                producto.nombre = nombre
                producto.descripcion = descripcion
                producto.precio = precio
                producto.tipo = tipo
        
                db.session.add(producto)
                db.session.commit()
        
                return redirect(url_for('main.profile'))
        
        else:
    
            id = request.args.get('id')
    
            producto = db.session.query(Productos).filter(Productos.id == id).first()
    
            return render_template('editarProducto.html', producto = producto)

@main.route('/eliminarProducto', methods=['GET'])
@login_required
@roles_required('admin')
def eliminarProducto():
    
        id = request.args.get('id')

        producto = db.session.query(Productos).filter(Productos.id == id).first()
    
        try:
            db.session.delete(producto)
            db.session.commit()
            return redirect(url_for('main.profile'))
        except:
            return 'Hubo un problema al eliminar el producto'
        

@main.route('/buscarProducto', methods=['GET'])
@login_required
@roles_required('admin')
def buscarProducto():
    
        busqueda = request.args.get('busqueda')
    
        productos = Productos.query.filter(Productos.id.like(busqueda) | 
                                           Productos.nombre.like('%'+busqueda+'%') |
                                           Productos.descripcion.like('%'+busqueda+'%') |
                                           Productos.precio.like(busqueda) |
                                           Productos.tipo.like('%'+busqueda+'%')).all()
    
        return render_template('productos.html', productos = productos)