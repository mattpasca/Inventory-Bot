import asyncio
from telegram import Update
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    CallbackContext
)
# Custom fcts
import callbacks as cb

# -------------------------
# Command handlers
# -------------------------

CHOOSE_PLANT, INSERT_DETAILS, CONFIRM_INSERTION = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    print(user_id)
    await update.message.reply_text(
        text=(
        "Ciao! Sono il bot per l'inventario colleghi di Gorini.\n"
        "\nPer iniziare inserisci il nome del <b>collega</b> da cui si trovano le piante dopo /c\n"
        "\n /c Nome_collega\n"
        "\nPer salvare una <b>nuova voce</b>, inizia selezionando una pianta.\n"
        "Scrivi il nome dopo /n, per esempio:\n\n/n Acer Palmatum"
        ),
        parse_mode='HTML'
    )

async def find_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text.replace("/n\n", "")
    try:
        suggestions = cb.suggestions(user_text)
    except:
        await update.message.reply_text(
            text=(
                "L'operazione non è andata a buon fine. <b>Inserimento annulato.<b>"
            ),
            parse_mode="HTML"
        )
        return ConversationHandler.END
    keyboard = [[InlineKeyboardButton(name, callback_data=name)] for name in suggestions]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Seleziona una voce:", reply_markup=reply_markup)
    return CHOOSE_PLANT

# Button press handler
async def name_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()  # Acknowledge callback
        selected_plant = query.data
        context.user_data["plant_name"] = selected_plant  # store user choice
        await query.edit_message_text(
            text=(
                f"Hai scelto: <b>{selected_plant}</b>.\n"
                "Ora inserisci i dettagli nel seguente ordine:\n\nFormato\nTipo C\nMis.\nAltezza\nAlt.Tronco\nCirconf.\nChioma\nQlt\nPRZ1\nPRZ2\nPRZ3\nqta\nST\nDisp.\nnote"
            ),
            parse_mode="HTML"
        )
        return INSERT_DETAILS
    
async def insert_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Try to fit user input into inventary structure
    if "collega" in context.user_data:
        colleague = context.user_data["collega"]
    else:
        colleague = ""
    if update.message.voice:
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)
        await file.download_to_drive("voice_note.ogg")
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, cb.transcribe)
        print(text)
        details_dict = cb.parse_message(colleague, text, "v")
    else:
        try:
            details_dict = cb.parse_message(colleague, update.message.text, "t")
        except:
            await update.message.reply_text(
                text=(
                    "L'operazione non è andata a buon fine. <b>Inserimento annulato.</b>"
                ),
                parse_mode="HTML"
            )
            return ConversationHandler.END
    context.user_data["details_dict"] = details_dict
    
    keyboard = [
        [InlineKeyboardButton("✅ Conferma", callback_data="y")],
        [InlineKeyboardButton("✏️ Modifica", callback_data="c")],
        [InlineKeyboardButton("❌ Annulla", callback_data="n")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    buf = cb.generate_preview_image(details_dict, context.user_data["plant_name"])
    await update.message.reply_photo(
        photo=buf,
        caption="Confermi di salvare questa voce?",
        reply_markup=reply_markup
    )
    return CONFIRM_INSERTION

async def confirm_insertion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        if query.data == "y":
            details_dict = context.user_data.get("details_dict")
            plant_name = context.user_data.get("plant_name")
            filename = update.effective_user.first_name + ".json"
            cb.save_json(plant_name, details_dict, filename)
            await query.edit_message_caption(caption="✅ Voce salvata.")
        elif query.data == "n":
            await query.edit_message_caption("❌ Annullato.")
        elif query.data == "c":
                details = context.user_data["details_dict"]
                values_text = "\n".join(str(v) for k, v in details.items() if k != "collega")
                await query.message.reply_text(
                    text = f"{values_text}",
                    parse_mode = 'HTML'
                )
                return INSERT_DETAILS


    return ConversationHandler.END

async def change_colleague(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.replace("/c", "")
    context.user_data["collega"] = user_text
    await update.message.reply_text(
        text = f"<b>Collega:</b>{user_text}",
        parse_mode = 'HTML'
    )
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Inserzione annullata.")
    return ConversationHandler.END

async def update_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cb.update_inventory()

# -------------------------
# Main function
# -------------------------

def main() -> None:
    """Start the bot."""
    # Replace 'YOUR_TOKEN_HERE' with your actual bot token
    app = ApplicationBuilder().token("8297051995:AAFr1Gnly_F1g5U3olc9zMALs8Vqr3xDV_g").build()

    # Add command handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("n", find_name)],
        states={
            CHOOSE_PLANT: [CallbackQueryHandler(name_button)],
            INSERT_DETAILS: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, insert_details)],
            CONFIRM_INSERTION: [CallbackQueryHandler(confirm_insertion)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("n", find_name) # let user arbitrarily begin from start 
            ],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("c", change_colleague))
    # Add a message handler for all text messages (optional)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: u.message.reply_text("I received your message!")))

    # Run the bot
    app.run_polling()

# -------------------------
# Entry point
# -------------------------
if __name__ == "__main__":
    main()
