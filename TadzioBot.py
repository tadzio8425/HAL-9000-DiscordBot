#!/usr/bin/env python3
import discord
from discord.ext import tasks, commands
from RadarrAPI import RadarrAPI as radarr
from getSubs import get_subs
from ZoomPy import ZoomUs
import csv
import pandas as pd
import requests
import shutil
import logging
import requests, socket
import os

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP



client = discord.Client()

logging.basicConfig(filename='example.log', level=logging.DEBUG)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    await client.change_presence(activity=discord.Game(name="Utiliza '!ayuda' para ver mis comandos!"))


@client.event
async def on_message(message):

    
    with open("commands.csv", "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        command_list = next(csv_reader)
        print(command_list)


#!film -> Filmbot!
    flag_list = ["🇺🇸", "🇪🇸", "🇫🇷", "🇮🇹", "🇩🇪", "🇷🇺", "🇯🇵", "🇰🇷"]

    
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        await message.channel.send('Hello World!')

    
    if message.content.startswith('!film'):

        mensaje = message.content
        movie_name = mensaje.replace("!film ", "")

        embed=discord.Embed(title="Tadzio´s FilmBot", description="¿En que calidad deseas tu película?", color=0xe74c3c)
        embed.set_thumbnail(url="https://img.pngio.com/hal-icon-65700-free-icons-library-hal-png-1600_1600.jpg")

        #SELECTING QUALITY

        quality_settings = await message.channel.send(embed=embed)
        
        for emoji in ["<:720:763163748948508744>", "<:1080:763163336945958943>", "<:4k:763164907548966922>", "<:any:763181087794397194>"]:
            await quality_settings.add_reaction(emoji)


        def check(reaction, user):
            if user == message.author and str(reaction.emoji) in ["<:720:763163748948508744>", "<:1080:763163336945958943>", "<:4k:763164907548966922>", "<:any:763181087794397194>"]:
                return True, 
            else:
                return False

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60, check = check)
        except TimeoutError:
            await message.channel.send('Tiempo de espera agotado. Intentalo de nuevo!')
            exit
        else:
            print(type(reaction.emoji))

            if str(reaction.emoji) == "<:any:763181087794397194>":
                resolution = "ANY"

            elif str(reaction.emoji) == "<:720:763163748948508744>":
                resolution = "720"

            elif str(reaction.emoji) == "<:1080:763163336945958943>":
                resolution = "1080"

            elif str(reaction.emoji) == "<:4k:763164907548966922>":
                resolution = "4K"

            
    


        embed=discord.Embed(title="Tadzio´s FilmBot", description="¿En que idioma buscas tu película?", color=0xe74c3c)
        embed.set_thumbnail(url="https://img.pngio.com/hal-icon-65700-free-icons-library-hal-png-1600_1600.jpg")

        #SELECTING LANGUAGE

        language_settings = await message.channel.send(embed=embed)

        for emoji in flag_list:
            await language_settings.add_reaction(emoji)


        def check(reaction, user):
            if user == message.author and str(reaction.emoji) in flag_list:
                return True, 
            else:
                return False

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60, check = check)
        except TimeoutError:
            await message.channel.send('Tiempo de espera agotado. Intentalo de nuevo!')
            exit
        else:
            print(type(reaction.emoji))

            if str(reaction.emoji) == "🇺🇸":
                language = "english"

            elif str(reaction.emoji) == "🇪🇸":
                language = "spanish"

            elif str(reaction.emoji) == "🇫🇷":
                language = "french"

            elif str(reaction.emoji) == "🇮🇹":
                language = "italian"

            elif str(reaction.emoji) == "🇩🇪":
                language = "deutsch"

            elif str(reaction.emoji) == "🇷🇺":
                language = "russian"

            elif str(reaction.emoji) == "🇯🇵":
                language = "japanese"

            elif str(reaction.emoji) == "🇰🇷":
                language = "korean"


        #MENSAJE DE CONFIRMACION
        
        embed=discord.Embed(title="Tadzio´s FilmBot", description="Buscando películas que contengan \"{}\", en resolución {} y en el idioma  {}...".format(movie_name, resolution, str(reaction.emoji)), color=0xe74c3c)
        embed.set_thumbnail(url="https://img.pngio.com/hal-icon-65700-free-icons-library-hal-png-1600_1600.jpg")
        await message.channel.send(embed=embed)



        file2write=open("last_movie_id.txt",'r')
        past_film_id = str(file2write.read())
        file2write.close()
        
        
        print(resolution)
        print(past_film_id)
    
        radarr_initiate = radarr().get_torrent_public(movie_name = movie_name, past_film_id = past_film_id, resolution = resolution)

        if radarr_initiate is not None:

            magnet_link = radarr_initiate[0]
            past_film_id = radarr_initiate[1]
            movie_name = radarr_initiate[2]
            movie_image = radarr_initiate[3]
            size = radarr_initiate[4]
            hash_code = radarr_initiate[5]

            file2write=open("last_movie_id.txt",'w')
            file2write.write(str(past_film_id))
            file2write.close()

            embed = discord.Embed(
                title = movie_name,  
                description = magnet_link,
                colour = discord.Colour.red()
            )

            embed.set_image(url = movie_image)
            await message.channel.send(embed=embed)
            
            embed=discord.Embed(title="Tadzio´s FilmBot", description="Recuerda utilizar el comando '!subs' si deseas obtener subtitulos para tu película!", color=0xe74c3c)
            embed.set_thumbnail(url="https://img.pngio.com/hal-icon-65700-free-icons-library-hal-png-1600_1600.jpg")
            await message.channel.send(embed=embed)

            
        else:
            await message.channel.send("Película no encontrada. Intentalo de nuevo con una resolución diferente.")
    

#!subs -> Subs (Under development)
    if message.content.startswith('!subs'):
        requesting_user = message.author
        print(requesting_user)

         #SEARCHING FOR SUBS

        embed=discord.Embed(title="Tadzio´s SubsBot", description="¿En que idioma deseas obtener tus subtitulos?", color=0x19C5FF)
        embed.set_thumbnail(url="https://i.imgur.com/AyfoBv5.png")

        subtitles_settings = await message.channel.send(embed=embed)

        for emoji in flag_list:
            await subtitles_settings.add_reaction(emoji)


        def check(reaction, user):
            if user == message.author and str(reaction.emoji) in flag_list:
                return True, 
            else:
                return False

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60, check = check)
        except TimeoutError:
            await message.channel.send('Tiempo de espera agotado. Intentalo de nuevo!')
            exit
        else:
            print(type(reaction.emoji))

            if str(reaction.emoji) == "🇺🇸":
                language = "en"

            elif str(reaction.emoji) == "🇪🇸":
                language = "es"

            elif str(reaction.emoji) == "🇫🇷":
                language = "fr"

            elif str(reaction.emoji) == "🇮🇹":
                language = "it"

            elif str(reaction.emoji) == "🇩🇪":
                language = "ger"

            elif str(reaction.emoji) == "🇷🇺":
                language = "rus"

            elif str(reaction.emoji) == "🇯🇵":
                language = "jpn"

            elif str(reaction.emoji) == "🇰🇷":
                language = "kor"



            embed=discord.Embed(title="Tadzio´s SubsBot", description="Ingresa la dirección completa en la que está incluida tu película.", color=0x19C5FF)
            embed.add_field(name="Ejemplo:", value="D:\Películas\Pulp Fiction (1994) [1080p]\Pulp.Fiction.1994.1080p.BrRip.x264.YIFY.mp4", inline=False)
            embed.set_thumbnail(url="https://i.imgur.com/AyfoBv5.png")
            await message.channel.send(embed=embed)


            def check(user):
                if requesting_user == message.author:
                    print("Xd")
                    return True
                else:
                    print("Xdn´t")
                    return False


            try:
                message = await client.wait_for('message', timeout=120, check = check)
            except TimeoutError:
                await message.channel.send('Tiempo de espera agotado. Intentalo de nuevo!')
                exit
            else:
                print("checkcheck")
                direccion_filme = message.content

                subDb = get_subs(direccion_filme,language)

                if subDb.subs_found == True:


                        embed=discord.Embed(title="Tadzio´s SubsBot", description="Subtitulos encontrados y guardados en la dirección\n: " + subDb.path , color=0x19C5FF)
                        embed.set_thumbnail(url="https://i.imgur.com/AyfoBv5.png")
                        await message.channel.send(embed=embed)
            
                else:
                    await message.channel.send('Subtitulos no encontrados! Intenta cambiar el lenguaje o la dirección.')


#!zoom -> Creates or deletes a Zoom Call!
    if message.content.startswith("!zoom"):

        if  message.content.startswith("!zoom delete"):

            try:
                ZoomUs().delete_meeting()
                await message.channel.send('Todas las reuniones de Zoom han sido eliminadas exitosamente.')

            except:
                await message.channel.send('Ha ocurrido un error eliminando las reuniones de Zoom, intentalo nuevamente.')
                

        else:
            zoom_meeting_link = ZoomUs().create_meeting() 
            embed=discord.Embed(title="Reunión de Zoom", description="Aquí está el link para la reunión de Zoom.", url = zoom_meeting_link ,color=0x19C5FF)
            embed.add_field(name="Link", value=zoom_meeting_link, inline=False)
            embed.set_thumbnail(url = "https://seeklogo.com/images/Z/zoom-fondo-azul-vertical-logo-8246E36E95-seeklogo.com.png")
            await message.channel.send(embed=embed)





#!lola -> Impedida

    if message.content.startswith("!lola"):
        await message.channel.send(file = discord.File("./imagenes/lola.jpg"))


#!sech -> Embed con el Ete Sech 
    if message.content.startswith("!sech"):
        embed=discord.Embed(title="ete sech 😎", description="ete sech")
        embed.set_image(url = "https://i.redd.it/hfta4w753mo51.jpg")
        embed.set_thumbnail(url = "https://i.redd.it/hfta4w753mo51.jpg")
        embed.set_footer(text = "ete sech")
        await message.channel.send(embed=embed)



#!ayuda -> Embed con los comandos del server
    if message.content.startswith("!ayuda"):
        
        embed=discord.Embed(title="Lista de commandos de HAL-9000:", color = 0xe74c3c)
        embed.set_thumbnail(url = "https://img.pngio.com/hal-icon-65700-free-icons-library-hal-png-1600_1600.jpg")

        embed.add_field(name="!zoom", value="Crea una llamada en Zoom y retorna el link de esta misma.", inline=False)
        embed.add_field(name="!zoom delete", value="Elimina todas las llamadas creadas en Zoom.", inline=False)
        embed.add_field(name="!film + nombre del filme", value="Busca una película y retorna el link del torrent para su descarga. Ej: !film A Clockwork Orange", inline=False)
        embed.add_field(name="!create", value="Abre el asistente para crear un comando personalizado", inline=False)
        embed.add_field(name="!custom", value="Retorna la lista de cutom commands ya creados.", inline=False)


        await message.channel.send(embed=embed)


#!create -> Crea comandos
    if message.content.startswith("!create"):

            requesting_user = message.author

            mensaje_comando = "None"
            command_image = "None"
            og_path = "None"

            embed=discord.Embed(title="HAL-9000 Command Creator", description="Seguido de '!', escribe el nombre del comando que desees crear:", color=0xe74c3c)
            embed.set_thumbnail(url="https://img.pngio.com/hal-icon-65700-free-icons-library-hal-png-1600_1600.jpg")
            await message.channel.send(embed=embed)

            def check(user):
                if requesting_user == message.author:
                    print("Xd")
                    return True
                else:
                    print("Xdn´t")
                    return False


            try:
                message = await client.wait_for('message', timeout=60, check = check)
            except TimeoutError:
                await message.channel.send('Tiempo de espera agotado. Intentalo de nuevo!')
                exit
            else:
                print("checkcheck")
                nombre_comando = message.content

            if nombre_comando[0] == "!" and nombre_comando not in command_list:
                #Pregunta si desea añadir un mensaje
                embed=discord.Embed(title="HAL-9000 Command Creator", description="¿Deseas añadir un mensaje?", color=0xe74c3c)
                embed.set_thumbnail(url="https://img.pngio.com/hal-icon-65700-free-icons-library-hal-png-1600_1600.jpg")

                message_settings = await message.channel.send(embed=embed)

                for emoji in ["✅","⛔"]:
                    await message_settings.add_reaction(emoji)


                def check(reaction, user):
                    if user == message.author and str(reaction.emoji) in ["✅","⛔"]:
                        return True, 
                    else:
                        return False

                try:
                    reaction, user = await client.wait_for('reaction_add', timeout=60, check = check)
                except TimeoutError:
                    await message.channel.send('Tiempo de espera agotado. Intentalo de nuevo!')
                    exit
                else:
                    print(type(reaction.emoji))

                    if str(reaction.emoji) == "✅":
                        add_message = True

                    elif str(reaction.emoji) == "⛔":
                        add_message = False


                if add_message:
                    embed=discord.Embed(title="HAL-9000 Command Creator", description="Escribe el mensaje que deseas añadir al comando:", color=0xe74c3c)
                    embed.set_thumbnail(url="https://img.pngio.com/hal-icon-65700-free-icons-library-hal-png-1600_1600.jpg")
                    await message.channel.send(embed=embed)

                    def check(user):
                        if requesting_user == message.author:
                            print("Xd")
                            return True
                        else:
                            print("Xdn´t")
                            return False


                    try:
                        message = await client.wait_for('message', timeout=60, check = check)
                    except TimeoutError:
                        await message.channel.send('Tiempo de espera agotado. Intentalo de nuevo!')
                        exit
                    else:
                        print("checkcheck")
                        mensaje_comando = message.content
                        

        #Pregunta si desea añadir una imagen

                embed=discord.Embed(title="HAL-9000 Command Creator", description="¿Deseas añadir un archivo multimedia?", color=0xe74c3c)
                embed.set_thumbnail(url="https://img.pngio.com/hal-icon-65700-free-icons-library-hal-png-1600_1600.jpg")

                image_settings = await message.channel.send(embed=embed)

                for emoji in ["✅","⛔"]:
                    await image_settings.add_reaction(emoji)


                def check(reaction, user):
                    if user == message.author and str(reaction.emoji) in ["✅","⛔"]:
                        return True, 
                    else:
                        return False

                try:
                    reaction, user = await client.wait_for('reaction_add', timeout=60, check = check)
                except TimeoutError:
                    await message.channel.send('Tiempo de espera agotado. Intentalo de nuevo!')
                    exit
                else:
                    print(type(reaction.emoji))

                    if str(reaction.emoji) == "✅":
                        add_image = True

                    elif str(reaction.emoji) == "⛔":
                        add_image = False

                if add_image:

                    embed=discord.Embed(title="HAL-9000 Command Creator", description="Sube la imagen/video/gif que desees añadir al comando:", color=0xe74c3c)
                    embed.set_thumbnail(url="https://img.pngio.com/hal-icon-65700-free-icons-library-hal-png-1600_1600.jpg")
                    await message.channel.send(embed=embed)

                    def check(user):
                        if requesting_user == message.author:
                            print("Xd")
                            return True
                        else:
                            print("Xdn´t")
                            return False


                    try:
                        message = await client.wait_for('message', timeout=60, check = check)
                    except TimeoutError:
                        await message.channel.send('Tiempo de espera agotado. Intentalo de nuevo!')
                        exit
                    else:
                        print("checkcheck")
                        command_image = message.attachments[0].url
                        print(command_image)

                        r = requests.get(command_image, stream=True, headers={'User-agent': 'Mozilla/5.0'})

                    embed=discord.Embed(title="HAL-9000 Command Creator", description="¿Que tipo de archivo estas subiendo? (Video, imagen o gif)", color=0xe74c3c)
                    embed.set_thumbnail(url="https://img.pngio.com/hal-icon-65700-free-icons-library-hal-png-1600_1600.jpg")
                    await message.channel.send(embed=embed)

                    def check(user):
                        if requesting_user == message.author:
                            print("Xd")
                            return True
                        else:
                            print("Xdn´t")
                            return False


                    try:
                        message = await client.wait_for('message', timeout=60, check = check)
                    except TimeoutError:
                        await message.channel.send('Tiempo de espera agotado. Intentalo de nuevo!')
                        exit
                    else:

                        if message.content.lower() == "video":
                            extension_archivo = ".mp4"

                        elif message.content.lower() == "imagen":
                            extension_archivo = ".png"

                        elif message.content.lower() == "gif":
                            extension_archivo = ".gif"

                        if r.status_code == 200:
                            image_path = "./imagenes/{}{}".format(nombre_comando, extension_archivo)
                            og_path = image_path
                            with open(image_path, 'wb') as f:
                                r.raw.decode_content = True
                                shutil.copyfileobj(r.raw, f)

                print(nombre_comando)
                print(mensaje_comando)
                print(og_path)

                df = pd.read_csv("commands.csv")
                df[nombre_comando] = [mensaje_comando, og_path]
                df.to_csv("commands.csv", index=False)
                
                embed=discord.Embed(title="HAL-9000 Command Creator", description="Has creado del comando '{}' exitosamente!".format(nombre_comando), color=0xe74c3c)
                embed.set_thumbnail(url="https://img.pngio.com/hal-icon-65700-free-icons-library-hal-png-1600_1600.jpg")
                await message.channel.send(embed=embed)

            
            else:
                await message.channel.send('No has ingresado un nombre de comando válido!')
            
#!commands_created -> Iterates over the created commands!
    if message.content in command_list:
        
        command_name = [message.content]

        df = pd.read_csv("commands.csv", usecols=command_name)

        message_text = df[command_name].iloc[0].values[0]
        message_image = df[command_name].iloc[1].values[0]


        if message_text != "None":
            await message.channel.send(message_text)

        if message_image != "None":
            await message.channel.send(file = discord.File(message_image))


        print(message_text)
        print(message_image)


#!custom -> Abre la lista de custom commands
    if message.content.startswith('!custom'):
        await message.channel.send(command_list)

#!ip -> Envía la IP local 
    if message.content.startswith('!ip'):
        local_ip = get_ip()

        embed=discord.Embed(title=local_ip, color=0xe74c3c)

        await message.channel.send("This is Hal's current local IP address: ")
        await message.channel.send(embed=embed)


client.run(os.getenv('DISCORD'))