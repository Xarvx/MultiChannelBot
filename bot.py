import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== CONFIGURACIÓN =====
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID'))
CANALES = os.environ.get('CANALES', '').split(',')

# ===== FUNCIONES =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ No tienes permiso para usar este bot.")
        return
    
    mensaje = (
        "🤖 *Bot Multi-Canal Activado*\n\n"
        "📤 Envíame cualquier mensaje y lo reenviaré a todos tus canales.\n\n"
        "*Tipos de contenido soportados:*\n"
        "• Texto\n"
        "• Imágenes\n"
        "• Videos\n"
        "• Documentos\n"
        "• Audio\n\n"
        "*Comandos:*\n"
        "/start - Ver este mensaje\n"
        "/canales - Ver canales configurados"
    )
    await update.message.reply_text(mensaje, parse_mode='Markdown')

async def mostrar_canales(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /canales - muestra los canales configurados"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ No tienes permiso para usar este bot.")
        return
    
    mensaje = "📺 *Canales configurados:*\n\n"
    for i, canal in enumerate(CANALES, 1):
        mensaje += f"{i}. {canal}\n"
    
    await update.message.reply_text(mensaje, parse_mode='Markdown')

async def reenviar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reenvía el mensaje a todos los canales"""
    user_id = update.effective_user.id
    
    # Verificar que sea el admin
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ No tienes permiso para usar este bot.")
        return
    
    mensaje = update.message
    exitosos = 0
    fallidos = 0
    errores = []
    
    # Intentar enviar a cada canal
    for canal in CANALES:
        try:
            # Detectar tipo de contenido y enviarlo
            if mensaje.text:
                await context.bot.send_message(chat_id=canal, text=mensaje.text)
            elif mensaje.photo:
                await context.bot.send_photo(
                    chat_id=canal,
                    photo=mensaje.photo[-1].file_id,
                    caption=mensaje.caption
                )
            elif mensaje.video:
                await context.bot.send_video(
                    chat_id=canal,
                    video=mensaje.video.file_id,
                    caption=mensaje.caption
                )
            elif mensaje.document:
                await context.bot.send_document(
                    chat_id=canal,
                    document=mensaje.document.file_id,
                    caption=mensaje.caption
                )
            elif mensaje.audio:
                await context.bot.send_audio(
                    chat_id=canal,
                    audio=mensaje.audio.file_id,
                    caption=mensaje.caption
                )
            elif mensaje.voice:
                await context.bot.send_voice(
                    chat_id=canal,
                    voice=mensaje.voice.file_id,
                    caption=mensaje.caption
                )
            
            exitosos += 1
            logger.info(f"Mensaje enviado exitosamente a {canal}")
            
        except Exception as e:
            fallidos += 1
            errores.append(f"{canal}: {str(e)}")
            logger.error(f"Error al enviar a {canal}: {e}")
    
    # Respuesta al admin
    respuesta = f"✅ Enviado a {exitosos}/{len(CANALES)} canales"
    if fallidos > 0:
        respuesta += f"\n❌ {fallidos} fallidos:\n"
        for error in errores:
            respuesta += f"• {error}\n"
    
    await update.message.reply_text(respuesta)

def main():
    """Función principal"""
    # Crear la aplicación
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("canales", mostrar_canales))
    
    # Handler para todos los tipos de mensajes (excepto comandos)
    application.add_handler(MessageHandler(
        filters.ALL & ~filters.COMMAND,
        reenviar_mensaje
    ))
    
    # Iniciar el bot
    logger.info("Bot iniciado...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    print("🚀 Iniciando bot...")
    print(f"📺 Canales configurados: {len(CANALES)}")
    main()
