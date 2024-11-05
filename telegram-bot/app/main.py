import telebot
from telebot import types
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN_BOT = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN_BOT)

db_host = os.getenv("DATABASE_HOST")
db_port = os.getenv("DATABASE_PORT")
db_name = os.getenv("DATABASE_NAME")
db_user = os.getenv("DATABASE_USER")
db_password = os.getenv("DATABASE_PASSWORD")

# Conectar a la base de datos

db = mysql.connector.connect(
    host=db_host,
    port=db_port,
    user=db_user,
    password=db_password
)

cursor = db.cursor()
sql_query = "CREATE DATABASE IF NOT EXISTS `{}`".format(db_name)
cursor.execute(sql_query)

db = mysql.connector.connect(
    host=db_host,
    port=db_port,
    user=db_user,
    database = db_name,
    password=db_password
)
db.database = db_name
cursor = db.cursor()
cursor.execute("""
        CREATE TABLE `bot-telegram` (
        `id` int NOT NULL AUTO_INCREMENT,
        `user_id` varchar(100)  NULL,
        `nombre_usuario` varchar(100)  NULL,
        `nombre_colaborador` varchar(100) NULL,
        `genero_colaborador` varchar(100) NULL,
        `correo_colaborador` varchar(100) NULL,
        `imagen_url` varchar(100) NULL,
        PRIMARY KEY (`id`)
        );""")



datos_colaborador = {}


#Rergistro Colaboardores
@bot.message_handler(commands=['registrocolaborador'])
def inicio_registro_colaboardor(message):
	#bot.reply_to(message, "Bienvenido, Soy tu BOT de RH, A continucion te realizare algunas prguntas para tu resgitro")
    bot.reply_to(message, "¿Cual es tu nombre?")
    datos_colaborador[message.chat.id] ={'state':'nombre_colaborador'}
    print(datos_colaborador)

@bot.message_handler(func=lambda message:datos_colaborador.get(message.chat.id, {}).get('state') == 'nombre_colaborador')
def registro_nombre_colaboardor(message):
    nombre = str(message.text)
    datos_colaborador[message.chat.id]['nombre'] = str(message.text)

    print(datos_colaborador)

    datos_colaborador[message.chat.id]['state'] ='genero_colaborador'

    print(datos_colaborador)

    botones_genero = types.InlineKeyboardMarkup()
    botones_genero.add(types.InlineKeyboardButton("Masculino", callback_data="genero_Masculino"))
    botones_genero.add(types.InlineKeyboardButton("Femenino", callback_data="genero_Femenino"))
    botones_genero.add(types.InlineKeyboardButton("Otro", callback_data="genero_Otro"))
    bot.send_message(message.chat.id, "¿Cual es tu genero?",reply_markup=botones_genero)
    
@bot.callback_query_handler(func=lambda datos_genero_colaborador:datos_genero_colaborador.data.startswith("genero_"))
def registro_genero_colaborador(datos_genero_colaborador):
    genero = datos_genero_colaborador.data.split('_')[1]
    datos_colaborador[datos_genero_colaborador.message.chat.id]['genero'] = str(genero)
    print(datos_colaborador)
    datos_colaborador[datos_genero_colaborador.message.chat.id]['state'] ='correo_colaborador'
    bot.send_message(datos_genero_colaborador.message.chat.id, "¿Cual es tu correo electronico?")

@bot.message_handler(func=lambda message:datos_colaborador.get(message.chat.id, {}).get('state') == 'correo_colaborador')
def registro_correo_colaborador(message):
    datos_colaborador[message.chat.id]['mail'] = message.text
    print(datos_colaborador)
    datos_colaborador[message.chat.id]['state'] ='ubicacion_colaborador'
    bot.reply_to(message, "¿Cual es tu ubicacion?")

@bot.message_handler(func=lambda message:datos_colaborador.get(message.chat.id, {}).get('state') == 'ubicacion_colaborador')
def registro_correo_colaboardor(message):
    datos_colaborador[message.chat.id]['ubicacion'] = message.text
    print(datos_colaborador)
    datos_colaborador[message.chat.id]['state'] ='ubicacion_gps'

    gps = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    botones_gps = types.KeyboardButton('comparte tu ubicacion', request_location=True)
    gps.add(botones_gps)
    bot.send_message(message.chat.id, "¿comparte tu ubicacion gps?",reply_markup=gps)

@bot.message_handler(content_types=['location'], func=lambda message:datos_colaborador.get(message.chat.id, {}).get('state') == 'ubicacion_gps')
def registro_ubicaciongps_colaboardor(message):
    datos_colaborador[message.chat.id]['ubicacion'] ={
        'latitud':message.location.latitude,
        'longitud':message.location.longitude
    }
    datos_colaborador[message.chat.id]['state'] ='Foto_colaborador'
    bot.send_message(message.chat.id, "ingresar un foto 4x4")

@bot.message_handler(content_types=['photo'], func=lambda message:datos_colaborador.get(message.chat.id, {}).get('state') == 'Foto_colaborador')
def registro_foto_colaboardor(message):
    id_foto = message.photo[-1].file_id
    info_foto= bot.get_file(id_foto)
    ruta_foto = info_foto.file_path
    url_foto = f'https://api.telegram.org/file/bot/{TOKEN_BOT}/{ruta_foto}'
    datos_colaborador[message.chat.id]['imagen'] = url_foto
    print(message.from_user.username)
    print(datos_colaborador)

    cursor.execute(
    "INSERT INTO `bot-telegram` (user_id, nombre_usuario, nombre_colaborador, genero_colaborador, correo_colaborador, imagen_url) VALUES(%s,%s,%s,%s,%s,%s);",
        (
                    message.from_user.id,
                    message.from_user.username,
                    datos_colaborador[message.chat.id]['nombre'],
                    datos_colaborador[message.chat.id]['genero'],
                    datos_colaborador[message.chat.id]['mail'],
                    datos_colaborador[message.chat.id]['imagen']
        )
    )

    db.commit()
    bot.reply_to(message, "se registro colaborador")
    print(datos_colaborador)
    datos_colaborador.pop(message.chat.id, None)
    
    
"""
@bot.message_handler(content_types=['text'])
def inicio_conversacion(message):
    chat_bienvenida = f'''
        <b>ProSystemTools</b>\n
        <a href='https://adguard.prosystemtools.com'>Da click</a>
    '''
    if message.text.startswith('Hola'):
	    bot.send_message(message.chat.id, "Hola, en que te puedo ayudar")
    elif message.text.startswith('Chao'):
        bot.send_message(message.chat.id, str(chat_bienvenida) , parse_mode="html")
"""

if __name__ == "__main__":
    bot.set_my_commands([
        telebot.types.BotCommand("/registrocolaborador","Registra Colaboradores"),
        telebot.types.BotCommand("/cuscacolaborador","Busca Colaboradores"),
    ])
    bot.infinity_polling()