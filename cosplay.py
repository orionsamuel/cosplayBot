import re
import telegram
import pandas as pd

from telegram import User, InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, InlineQueryHandler, CallbackQueryHandler, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from telegram.utils.helpers import escape_markdown

botToken = "2014324973:AAEFIga73EHC2AdkG7nbnfLnxgS_d92bXg0"

cuscuzbot = telegram.Bot(botToken)

def listar(update, context):
    participantes = open("participantes.csv", "r+")
    for linha in participantes:
        competidor = linha.split(',')
        update.message.reply_text(str(competidor[0]) + " " + str(competidor[1]) + " " + str(competidor[2]))
    participantes.close()


def notas(update, context):
    participantes = open("participantes.csv", "r+")
    notasEscrita = open("notas.csv", "a+")
    notasLeitura = open("notas.csv", "r+")

    linhas = notasLeitura.readlines()

    numLinhas = sum(1 for linha in linhas)

    competidores = participantes.readlines()
    competidor = competidores[int(context.args[0]) -1 ]
    competidorChoosen = competidor.split(',')

    participantes.close()

    notasEscrita.write(str(numLinhas + 1) + "," + str(competidorChoosen[0]) + "," + str(competidorChoosen[1]) + "," +
                       str(competidorChoosen[2]) + "," + str(context.args[1]) + "," + str(context.args[2]) + "," +
                       str(context.args[3]) + "\n")

    notasLeitura.close()
    notasEscrita.close()


def resultado(update, context):
    notasLeitura = open("notas.csv", "r+")
    resultadoEscrita = open("resultado.csv", "w+")

    participantes = set()

    for linha in notasLeitura:
        participante = linha.split(',')
        participantes.add(participante[1])

    notasLeitura.close()

    for it in participantes:
        notasLeitura = open("notas.csv", "r+")
        totalParticipante = 0
        juriInd = 0
        for linha in notasLeitura:
            participante = linha.split(',')
            if(it == participante[1]):
                juriInd = (float(participante[4]) + float(participante[5]) + float(participante[6])) / 3
                totalParticipante = totalParticipante + juriInd

        notasLeitura.close()
        
        notasLeitura = open("notas.csv", "r+")
        escrita = 0
        for linha in notasLeitura:
            participante = linha.split(',')
            if(it == participante[1] and escrita == 0):
                resultadoEscrita.write(str(it) + "," + str(participante[2]) + "," + str(participante[3]) + "," + str(totalParticipante) + "\n")
                escrita = escrita + 1

        notasLeitura.close()

    resultadoEscrita.close()

    resultado = pd.read_csv('resultado.csv', header=None)
    resultado = resultado.sort_values([3], ascending=False)
    resultado.to_csv("resultado.csv", sep=',', header=None, index=False)

    resultado = open("resultado.csv", "r+")
    for linha in resultado:
        competidor = linha.split(',')
        update.message.reply_text(str(competidor[0]) + " " + str(competidor[1]) + " " + str(competidor[2]) + " " + str(competidor[3]))
    resultado.close()

def desempate(update, context):
    participantes = []
    
    for i in range(len(context.args)):
        notasLeitura = open("notas.csv", "r+")
        escrita = 0
        for linha in notasLeitura:
            participante = linha.split(',')
            if(context.args[i] == participante[1] and escrita == 0):
                participantes.append([context.args[i],participante[2],participante[3],participante[5]])
                escrita = escrita + 1
        notasLeitura.close()
        
    participanteDesempate = sorted(participantes, key = lambda x: x[3])
    update.message.reply_text(str(participanteDesempate[0][0]) + " " + str(participanteDesempate[0][1]) + " " +
                              str(participanteDesempate[0][2]) + " " + str(participanteDesempate[0][3]))


def foto(update, context):
    chat_id = update.message.chat_id
    cuscuzbot.send_photo(chat_id=chat_id, photo=open("images/"+str(context.args[0]+".png"), 'rb'))

def ajuda(update, context):
    update.message.reply_text("Esse bot foi criado para ajudar com a votação dos concursos de cosplay e cospobre. \n" +
                              "Abaixo se encontram os comandos disponíveis e suas formas de utilização. \n" + "\n" +
                              "/listar - Lista todos os participantes do concurso. Os participantes são listados com seu ID de participante, nome e personagem \n" + "\n" +
                              "/notas - Esse comando é utilizado para atribuir as notas de um determinado participante. Ele recebe como entrada o ID do participante e suas três notas, sempre separados por espaço. Ex: /notas 2 10 7.5 9.5 \n" + "\n" +
                              "/resultado - Lista os participantes em sua ordem de classificação. É recebido como resposta o ID do participante, nome, personagem e a média da notas. Os participantes já são listados ordenados do primeiro ao último colocado \n" + "\n" +
                              "/desempate - Comando utilizado quando ocorre empate em mais de um candidato. Deve ter como argumento de entrada os IDs dos participantes empatados. Ex: /desempate 2 5 6 \n" + "\n" +
                              "/foto - Exibe a foto do personagem de um determonado competidor. Recebe como entrada o ID do participante. Ex: /foto 2 \n" + "\n" +
                              "/help - Lista todos os comandos e suas descrições")

def main():
    updater = Updater(botToken, use_context=True)

    dp = updater.dispatcher
    
    #Comandos
    dp.add_handler(CommandHandler("listar", listar, pass_args=True))
    dp.add_handler(CommandHandler("notas", notas, pass_args=True))
    dp.add_handler(CommandHandler("resultado", resultado, pass_args=True))
    dp.add_handler(CommandHandler("desempate", desempate, pass_args=True))
    dp.add_handler(CommandHandler("foto", foto, pass_args=True))
    dp.add_handler(CommandHandler("help", ajuda, pass_args=True))

    
    # Start the Bot
    updater.start_polling()
    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
