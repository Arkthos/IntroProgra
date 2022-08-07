#Importante, este programa necesita que proyectoFinal.py, usuarios.txt, facturas.txt y guias.txt esten descargads en la misma ubicacion para funcionar correctamente.
#para instalar el paquete de bcrypt cree un ambiente virtual "python -m venv venv", active el ambiente virtual ejectando "venv\Scripts\Activate.ps1" instale bcrypt "pip install bcrypt"
import bcrypt
import os
import numpy as np
import sqlite3
from sqlite3 import Error
from datetime import datetime as dt
from datetime import date
from prettytable import PrettyTable as pt

def create_connection(db_file):     #Crea conenccion a la db
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def main():  #define el formatod de la tbala y la crea si no existe
    database = r"paqueteria.db"
    sql_crea_tabla_paquetes = """CREATE TABLE IF NOT EXISTS paquetes (
                                    id integer PRIMARY KEY,
                                    envia text NOT NULL,
                                    enviaDireccion text NOT NULL,
                                    recibe text NOT NULL,
                                    recibeDireccion text NOT NULL,
                                    modoEnvio text NOT NULL,
                                    peso real NOT NULL,
                                    costo real NOT NULL,
                                    fecha datetime NOT NULL,
                                    orden text NOT NULL
                                );"""
    # create a database connection
    conn = create_connection(database)
    # create tables
    if conn is not None:
        create_table(conn, sql_crea_tabla_paquetes)
    else:
        print("Error! cannot create the database connection.")

def menuPrincipal():    #Esta funcion presenta al usuario con la seleccion basica de opciones para entrar a cada uno de los modulos
    controlmenu = "0"   # La siguiente estructura ejecuta el programa al menos una vez y continua ejecutando hasta que el usuario indique que quiere terminar la sesion.
    while controlmenu!= "4":
        controlMenu = str(input("Bienvenido, como le podems servir? Digite el numero correspondiente a cada opcion:\n1: Envios\n2: Facturacion\n3: Informes\n4: Salir\n"))
        if controlMenu == "1":
            moduloEnvios()
        elif controlMenu == "2":
            moduloFacturas()
        elif controlMenu == "3":
            moduloInformes()
        elif controlMenu == "4":
            break
        else:
            print("Esa no es una opcion valida")

def creaPaquete(conn, paquete):
    sql = '''INSERT INTO paquetes(envia,enviaDireccion,recibe,recibeDireccion,modoEnvio,peso,costo,fecha,orden)
              VALUES(?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql,paquete)
    conn.commit()
    return cur.lastrowid

#esta funcion presenta la instrucciones para generar una guia de envio
def moduloEnvios():
    conn = create_connection(r"paqueteria.db")
    PESOBASE = float(1)
    PRECIOBASE = float(1000)
    PRECIOEXPRESS = float(200)
    PRECIOBAJOCOSTO = float(100)
    PRECIOINTERNACIONAL = float(300)
    PESOMAXIMO = float(45)
    navegacion = "1"
    fechaHora = dt.now()
    ordenId = str(fechaHora)
    ordenId = ordenId.split('.',1)[0]
    ordenId = ordenId.replace("-", "")
    ordenId = ordenId.replace(" ", "")
    ordenId = ordenId.replace(":", "")
    
    while navegacion == "1":
        print("Para realizar un envio, enter los siguientes valores")
        pqtPeso = input("Peso del paque te en Kg usando . para los decimales: ")
        try:
            pqtPeso = float(pqtPeso)
        except ValueError or (len(pqtPeso) == 0):
            print("Ese no es un peso valido. Por favor  digite el peso de su paquete en Kg, use . para decimales")
            moduloEnvios()
        if pqtPeso <= 0:
            print("El peso del envio no puede ser igual o menor que 0")
            moduloEnvios()
        if pqtPeso >= PESOMAXIMO:
            print("En este momento el peso maximo de los paqetes debe ser menor a 45 Kg.")
            moduloEnvios()
        destinatario = input("Cual es el nombre del destinatario? ")
        destinatarioDireccion = input("Cual es la direccion del destinatario? ")
        remitente = input("Nombre de quien envia: ")
        remitenteDireccion = input("Direccion de origen:  ")
        metodoEnvio = input("Que metodo de envio va a utilizar, digite el numero correspondiente a cada opcion:\n1: Express\n2: Bajo Costo\n3: Internacional\n")
        
        if pqtPeso > 0 and pqtPeso <=1:
            costo = PRECIOBASE
        elif metodoEnvio == "1":
            costo = ((pqtPeso - PESOBASE) * PRECIOEXPRESS) + PRECIOBASE
        elif metodoEnvio == "2":
            costo = ((pqtPeso - PESOBASE) * PRECIOBAJOCOSTO) + PRECIOBASE
        elif metodoEnvio =="3":
            costo = ((pqtPeso - PESOBASE) * PRECIOINTERNACIONAL) + PRECIOBASE
        else:
            print("Esa no es una opcion valida")
            moduloEnvios()
        
        if metodoEnvio == "1":
            metodoEnvio = "Express"
        elif metodoEnvio == "2":
            metodoEnvio = "Bajo Costo"
        else:
            metodoEnvio = "Internacional"                

        #confirmacion de los detalles de cada paquete          
        print("Envia: "+remitente)
        print("Direccion de origen: "+remitenteDireccion)        
        print("Recibe: "+destinatario)   
        print("Direccion de entrega: "+destinatarioDireccion)
        print("Metodo de envio : "+metodoEnvio)
        pqtPeso = pqtPeso
        print("Peso: ",pqtPeso)
        costostr = str(costo)
        print("Costo: "+costostr)       

        #si la informacion es correcta guarda a DB de lo contrario
        confirma = input("Si los detalles del paquete son correctos digite 1 o cualquier otra tecla para volver a empezar: ")    
        if confirma == "1":
            with conn:             
                paquete = (remitente,remitenteDireccion,destinatario,destinatarioDireccion,metodoEnvio,pqtPeso,costo,fechaHora,ordenId)
                creaPaquete(conn, paquete)
        else:
            pass

        #opcion de agregar otros paquetes a la misma orden
        navegacion = input("Digite 1 agregar otro paquete a esta orden o cualquier otra tecla para volver al menu principal ")
    try:
        paquetes = selectPaquetesPorOrdenid(conn, ordenId)
        orden = pt(['Paquete','Remitente','Direccion de origen','Destinatario','Direccion de entrega','Tipo Envio','Peso','Costo'])
        for paquete in paquetes:
            orden.add_row([paquete[0],paquete[1],paquete[2],paquete[3],paquete[4],paquete[5],paquete[6],paquete[7]])  
        print("\nOrden de envio: "+ordenId+" IMPORTANTE: CONSERVE SU NUMERO DE ORDEN SI NECESITA GENERAR SU FACTURA")
        print(orden)     
    except:
        print("no se confirmo ninguna orden")        
    print("Gracias, que tenga un buen dia!")
    menuPrincipal()

def selectPaquetesPorOrdenid(conn, orden):
    cur = conn.cursor()
    result = None    
    cur.execute("SELECT * FROM paquetes WHERE orden =?", (orden,))
    rows = cur.fetchall()
    return rows

def moduloFacturas():
    conn = create_connection("paqueteria.db")
    IVA = 0.13
    ordenId = input("Pasa generar la factura, digite el numero de orden: ")
    nombre = input("digite su nombre completo: ")
    cedula = input("digite su numero de cedula: ")  
    paquetes = selectPaquetesPorOrdenid(conn, ordenId)
    fechaDeFacturacion = dt.now()
    fechaDeFacturacion = str(fechaDeFacturacion)
    fechaDeFacturacion = fechaDeFacturacion.split('.',1)[0]
    subtotal = 0
    factura = pt(['Paquete','Tipo Envio','Peso','Costo'])
    for paquete in paquetes:
        factura.add_row([paquete[0],paquete[5],paquete[6],paquete[7]])
        subtotal += float(paquete[7])
    subtotalIVA = (subtotal * IVA)
    total = str(subtotal +subtotalIVA)
    subtotalIVA = str(subtotal * IVA)
    subtotal = str(subtotal)
    print("\nMensajeria el Cachiflin")
    print("Cedula juridica: 3-111-999999_________________________________________")
    print("Cliente: "+nombre)
    print("Cedula: "+cedula)
    print("Fecha de facturacion: "+fechaDeFacturacion)
    print("Numero de orden: "+ordenId+"\n____________________________________________")
    print(factura)
    print("Subtotal: "+subtotal)
    print("Impuesto de ventas: "+subtotalIVA)
    print("Total: "+total+"\n")

def selectPaquetesPorFecha(conn, fecha):
    cur = conn.cursor()
    result = None    
    query = (str(date.today())+"%")
    cur.execute("SELECT * FROM paquetes WHERE fecha LIKE ?", (query,))
    rows = cur.fetchall()
    return rows

def informesPaquetesCreadosDiario():
    conn = create_connection("paqueteria.db")
    fecha = date.today()
    paquetes = selectPaquetesPorFecha(conn, fecha)
    informe = pt(['Paquete','Modo de Envio','Peso','Costo'])
    for paquete in paquetes:
        informe.add_row([paquete[0],paquete[5],paquete[6],paquete[7]])
    fecha = str(fecha)
    print("Mensajeria el Cachiflin")
    print("Cedula juridica: 3-111-999999\n\n_________________________________________")
    print("Paquetes creados el "+fecha)
    print(informe)

def informesGananciaDiario():
    conn = create_connection("paqueteria.db")
    fecha = date.today()
    paquetes = selectPaquetesPorFecha(conn, fecha)
    informe = pt(['Modo de Envio','Ganancia'])
    gananciaExpress = 0
    gananciaBajoCosto = 0
    gananciaInternacional = 0
    for paquete in paquetes:
        if paquete[5] == "Express":
            gananciaExpress += paquete[7]
        elif paquete[5] == "Bajo Costo":            
            gananciaBajoCosto += paquete[7]
        else:            
            gananciaInternacional += paquete[7]
    informe.add_row(["Express",gananciaExpress])
    informe.add_row(["Bajo Costo",gananciaBajoCosto])
    informe.add_row(["Internacional",gananciaInternacional])
    fecha = str(fecha)
    print("Mensajeria el Cachiflin")
    print("Cedula juridica: 3-111-999999\n\n_________________________________________")
    print("Paquetes creados el "+fecha)
    print(informe)

def informesPaquetesPorPesoDiario():
    conn = create_connection("paqueteria.db")
    fecha = date.today()
    paquetes = selectPaquetesPorFecha(conn, fecha)
    informe = pt(['De 0 a 9 Kg','De 10 a 19 Kg','De 20 a 29 Kg','De 30 a 39 Kg','De 40 a 45 Kg'])
    hastaDiez = 0
    hastaVeinte = 0
    hastaTreinta = 0
    hastaCuarenta = 0
    hastaCuarentaycinco = 0
    for paquete in paquetes:        
        if paquete[6] > 0 and paquete[6] <= 10:
            hastaDiez += 1
        elif paquete[6] > 10 and paquete[6] <= 20:
            hastaVeinte += 1
        elif paquete[6] > 20 and paquete[6] <= 30:
            hastaTreinta += 1
        elif paquete[6] > 30 and paquete[6] <= 40:
            hastaCuarenta += 1
        else:
            hastaCuarentaycinco += 1
    informe.add_row([hastaDiez,hastaVeinte,hastaTreinta,hastaCuarenta,hastaCuarentaycinco])        
    fecha = str(fecha)
    print("Mensajeria el Cachiflin")
    print("Cedula juridica: 3-111-999999\n\n_________________________________________")
    print("Paquetes creados el "+fecha)
    print(informe)

def moduloInformes(): #genera informes diarios, es decir, basados en registros de la fecha presente
    opt = 9
    while opt != "4":
        opt = input("Digite el numero correspondiente a cada opcion:\n1. Paquetes Creados\n2. Ganancia por envio\n3. Paquetes por peso\n4. Menu principal\n")
        if opt == "1":
            informesPaquetesCreadosDiario()
        elif opt == "2":
            informesGananciaDiario()
        elif opt == "3":
            informesPaquetesPorPesoDiario()            
        else:
            print("Opcion invalida intente de nuevo")
        opt = input("para generar otro reporte digite 1 o 4 para volver al menu procipal.\n")

#esta funcion detalla los pasos para registrar un nuevo envio y calcula el costo del envio
def gainAccess(Username=None, Password=None):
    Username = input("Nombre de usuario:")
    Password = input("Contraseña:")
    
    if not len(Username or Password) < 1:
        if True:
            db = open("usuarios.txt", "r")
            d = []
            f = []
            for i in db:
                a,b = i.split(",")
                b = b.strip()
                c = a,b
                d.append(a)
                f.append(b)
                data = dict(zip(d, f))
            try:
                if Username in data:
                    hashed = data[Username].strip('b')
                    hashed = hashed.replace("'", "")
                    hashed = hashed.encode('utf-8')
                    
                    try:
                        if bcrypt.checkpw(Password.encode(), hashed):
                        
                            print("Bienvenido!")
                            print("Hola", Username)
                            menuPrincipal()
                        else:
                            print("Contraseña incorrecta")
                            gainAccess()
                        
                    except:
                        print("usuario o contraseña incorrectos")
                        gainAccess()
                else:
                    print("Nombre de usuario no existe")
                    gainAccess()
            except:
                print("Nombre de usuario o contraseña no existe")
                gainAccess()
        else:
            print("Error de autenticacion")
            gainAccess()
            
    else:
        print("Intente de nuevo")
        gainAccess()

#Esta funcion crea usuarios nuevos para acceder al sistema
def register(Username=None, Password1=None, Password2=None):
    Username = input("Cree su nombre de usuario:")
    Password1 = input("Cree su contraseña:")
    Password2 = input("Confirme la contraseña:")    
    db = open("usuarios.txt", "r")
    d = []
    for i in db:
        a,b = i.split(",")
        b = b.strip()
        c = a,b
        d.append(a)
    db.close()
    if not len(Password1)<8:
        db = open("usuarios.txt", "r")
        if not Username ==None:
            if len(Username) <1:
                print("Digite un nombre de usuario")
                register()
            elif Username in d:
                print("Usuario previamente regstrado")
                register()		
            else:
                if Password1 == Password2:
                    Password1 = Password1.encode('utf-8')
                    Password1 = bcrypt.hashpw(Password1, bcrypt.gensalt())                                 
                    db = open("usuarios.txt", "a+")
                    add = (Username+", "+str(Password1)+"\n")
                    db.write(add)
                    db.close()
                    print("Usuario creado exitosamente!")
                    print("Proceda a autenticarse para acceder:")
                    home()                    
                    # print(texts)
                else:
                    print("Las contraseñas no concuerdan")
                    register()
    else:
        print("Contraseña es muy corta")

#Presenta los modulos de registro y autenticacion como primera opcion.
def home(option=None):
    print("Bienvenido, Si ya tiene una cuenta digite 1 para acceder, si no digite 2 para registrarse o 3 para salir")
    option = input("1: Acceder | 2: Registrase | 3: Salir\n")
    if option == "1":
        gainAccess()
    elif option == "2":
        register()
    elif option == "3":
        pass
    else:
        print("Esa no es una opcion valida")
        home()

#if __name__ == '__main__': #Para crear la DB
#    create_connection(r"paqueteria.db")
#main() para crear la tabla de paqueteria
menuPrincipal()