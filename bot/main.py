from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, 
    CallbackQueryHandler, CallbackContext, 
    MessageHandler, ConversationHandler, 
    filters)
import sqlite3
import logging
from functools import wraps
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)



# # States for the conversation
CHOOSING, SELECTING_QUANTITY = range(2)

TOKEN =os.getenv('TELEGRAM_TOKEN')
DB_PATH = "/app/data/"
DB = "{}/wine.db".format(DB_PATH)





def with_database_connection(func):
    @wraps(func)
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        try:
            conn = sqlite3.connect(DB)
            c = conn.cursor()
        except Exception as e:
            logger.error(e)
            return

        try:
            return await func(update, context, c, *args, **kwargs)
        finally:
            conn.commit()
            conn.close()

    return wrapper
    
async def aiuto(update: Update, context: CallbackContext) -> None:
    try:
        """Informa gli utenti su cosa può fare questo bot"""
        await update.message.reply_text(
            """Che devi da fà?:
            /segna pe segnà le bottije che te stai a fregà
            /controlla pe vedè quante ne so rimaste
            /cancella si te sei sbajato
            /ciucciatori pe vedè chi se sta a fregà le bottije
            /mischiatutto pe fatte da un consiglio, che non capisci un cazzo de come se fa il vino
            /se_semo_presi pe vedè quante bottije se preso ogni pisciacorgo per tipo di vino
            /me_so_sbajato pe cancellà l'ultima cazzata che hai fatto"""
        )
    except Exception as e:
        logger.error(e)
        return
    # funcs = {"Aiuto": "aiuto", "Segna": "segna_bottiglie", "Controlla": "controlla_bottigle"}
    
    # buttons = [[InlineKeyboardButton(key, callback_data=value)] for key, value in funcs.items()]
    # keyboard = InlineKeyboardMarkup(buttons)
    # await update.message.reply_text("Cosa vuoi fare?", reply_markup=keyboard)



@with_database_connection
async def controlla_bottiglie(update: Update, context: CallbackContext, c) -> None:
    try:
        await update.message.reply_text("Ve siete presi tutto mortacci vostra. Vedemo un po' che m'avete lasciato...")
    except Exception as e:
        logger.error(e)
        return
    
    try:
        # Query the database for the remaining bottles
        c.execute("SELECT type, quantity FROM wines")
        rows = c.fetchall()
    except Exception as e:
        logger.error(e)
        return
    
    try:
        # Format the data into a string
        message_text = "\n".join([f"{row[0]}:   {row[1]}" for row in rows])

        # Send the data to the chat
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
    except Exception as e:
        logger.error(e)
        return
    
    
@with_database_connection
async def lista_vini(update: Update, context: CallbackContext, c) -> None:
    try:
        # Query the database for the remaining bottles
        c.execute("SELECT type FROM wines")
        rows = c.fetchall()
        wines = [row[0] for row in rows]
    except Exception as e:
        logger.error(e)
        return
    return wines


@with_database_connection
async def check_user(update: Update, context: CallbackContext, c) -> None:
    logger.info('Update: {}'.format(update))
    try:
        user_id = context.user_data['user_id']
        user_name = context.user_data['user_name']
        logger.info('User ID: {}'.format(user_id))
        logger.info('User Name: {}'.format(user_name))
    except Exception as e:
        logger.error(e)
        return None
    
    try:
        # Execute the SELECT query
        c.execute("SELECT tid FROM users WHERE tid = ?", (user_id,))
        
        # Fetch the result of the SELECT query
        user_in = c.fetchone()
    except Exception as e:
        logger.error(e)
        return

    if not user_in:
        # User not found, insert a new row
        c.execute("INSERT INTO users(name, tid) VALUES(?, ?)", (user_name, user_id))
        logger.info('User inserted successfully')
    else:
        logger.info('User already exists')

    return user_id

async def segna_bottiglie(update: Update, context: CallbackContext) -> None:
    try:
        # Get user_id and username to store them in the context user_data
        context.user_data['user_id'] = update.effective_user.id
        context.user_data['user_name'] = update.effective_user.first_name
    except Exception as e:
        logger.error(e)
        return
    try:
        # Parse the message text to get the wine type and number of bottles
        avail_wines = await lista_vini(update, context)
        logger.info('Lista vini: {}'.format(' '.join(map(str, avail_wines))))
    except Exception as e:
        logger.error(e)
        return
    
    try:
        # Use the available wines to create a list of buttons
        buttons = [[InlineKeyboardButton(wine, callback_data=wine)] for wine in avail_wines]
        keyboard = InlineKeyboardMarkup(buttons)
    except Exception as e:
        logger.error(e)
        return
            
    try:
        # Allow the user to select the wine types from the list of buttons (multiple selection)
        await update.message.reply_text("Che te stai a portà via, maledetto?", reply_markup=keyboard)
    except Exception as e:
        logger.error(e)
        return

    return CHOOSING

async def button(update: Update, context: CallbackContext) -> int:
    try:
        query = update.callback_query
        await query.answer()
    except Exception as e:
        logger.error(e)
        return
    
    try:
        wtype = query.data
        context.user_data['choice'] = wtype
        logger.info('ButtonSelected User Data: {}'.format(context.user_data))
    except Exception as e:
        logger.error(e)
        return
    
    try:
        # Create a list of buttons for the user to select the quantity
        buttons = [[InlineKeyboardButton(str(i), callback_data=str(i))] for i in range(1, 11)]
        keyboard = InlineKeyboardMarkup(buttons)
    except Exception as e:
        logger.error(e)
        return
    
    try:
        # Ask the user to select the quantity
        await query.edit_message_text(
            text=f"{query.data} dici? E quante te ne porti via?",
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(e)
        return
    
    return SELECTING_QUANTITY


@with_database_connection
async def received_quantity(update: Update, context: CallbackContext, c) -> int:
    # logger.info('Received Chat Data: {}'.format(context.chat_data))
    logger.info('Received User Data: {}'.format(context.user_data))
    try:
        # Get current user id
        user_id = await check_user(update, context)

        logger.info('Checked User ID: {}'.format(user_id))
    except Exception as e:
        logger.error(e)
        return
    
    try:
        # quantity = update.message.text
        quantity = update.callback_query.data
        wtype = context.user_data['choice'] 
        # context.user_data[wtype] = quantity

        logger.info('Selected Wine Type {}'.format(wtype))
        logger.info('Selected Quantity: {}'.format(quantity))
    except Exception as e:
        logger.error(e)
        return
    
    try:
        # Get wine id
        c.execute("SELECT id FROM wines WHERE type = ?", (wtype,))
        wine_id = c.fetchone()[0]
    except Exception as e:
        logger.error(e)
        return
    
    try:
        # Update the database
        c.execute("UPDATE users SET picked = picked + ? WHERE tid = ?", (quantity, user_id))
        c.execute("UPDATE wines SET quantity = quantity - ? WHERE type = ?", (quantity, wtype))
        c.execute("INSERT INTO transactions(quantity, user_id, wine_id) VALUES(?, ?, ?)", (quantity, user_id, wine_id))
        
        await update.callback_query.message.reply_text(
            text=f"Te sei preso {quantity} bottije de {wtype}. Pisciacorgo!"
        )

        return ConversationHandler.END
    except Exception as e:
        logger.error(e)
        return
    
    

    

async def cancel(update: Update, context: CallbackContext) -> int:
    try:
        await update.message.reply_text('C\'hai ripensato come i cornuti?')
        await update.message.reply_text('Allora ciao, spero de non rivedette verticale.')
    except Exception as e:
        logger.error(e)
        
    return ConversationHandler.END


async def mischiatutto(update: Update, context: CallbackContext) -> None:
    try:
        await update.message.reply_text('Mischia tutto, e senti che te bevi!')
    except Exception as e:
        logger.error(e)
        return
    
    
@with_database_connection
async def ciucciatori(update: Update, context: CallbackContext, c) -> None:
    try:
        c.execute(
            """ 
                SELECT name, picked
                FROM users
                ORDER BY picked DESC
            """
            )
    
        rows = c.fetchall()
    except Exception as e:
        logger.error(e)
        return
    
    if not rows:
        await update.message.reply_text('Nessuno se sta a fregà le bottije. Me fate schifo.')
        return
    else:
        try:
            await update.message.reply_text('Ecco la classifica de chi se sta a fregà più bottije:')
            message_text = "\n".join([f"{row[0]}:   {row[1]}" for row in rows])

            # Send the data to the chat
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
            await update.message.reply_text('{} è il più grande ciucciatore di tutti i tempi!'.format(rows[0][0]))
        except Exception as e:
            logger.error(e)
            return


@with_database_connection
async def se_semo_presi(update: Update, context: CallbackContext, c) -> None:
    try:
        c.execute('''
            SELECT users.name, wines.type, SUM(transactions.quantity) as total_bottles
            FROM transactions
            INNER JOIN users ON transactions.user_id = users.tid
            INNER JOIN wines ON transactions.wine_id = wines.id
            GROUP BY users.name, wines.type
        ''')
    
        rows = c.fetchall()
    except Exception as e:
        logger.error(e)
        return
    
    if not rows:
        await update.message.reply_text('Non ve siete presi manco na bottija. Ma n\'è che ve piace o pesce?')
        return
    else:
        try:
            update.message.reply_text('Guarda quanta roba ve siete presi! M\'avete rovinato!!')
            message_text = "\n".join([f"{row[0]}:   {row[1]} -> {row[2]}" for row in rows])

            # Send the data to the chat
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
        except Exception as e:
            logger.error(e)
            return

@with_database_connection
async def me_so_sbajato(update: Update, context: CallbackContext, c) -> None:
    try:
        context.user_data['user_id'] = update.effective_user.id
        context.user_data['user_name'] = update.effective_user.first_name
    except Exception as e:
        logger.error(e)
        return
    
    try:
        # Get current user id
        user_id = await check_user(update, context)
    except Exception as e:
        logger.error(e)
        return
    
    try:
        c.execute('SELECT id, quantity, wine_id FROM transactions WHERE user_id = ? ORDER BY id DESC LIMIT 1', (user_id,))
        last_transaction = c.fetchone()
        if last_transaction is None:
            print("No transactions to delete.")
        else:
            last_transaction_id, last_transaction_quantity, last_transaction_wine_id = last_transaction

            c.execute('DELETE FROM transactions WHERE id = ?', (last_transaction_id,))
            c.execute('UPDATE wines SET quantity = quantity + ? WHERE id = ?', (last_transaction_quantity, last_transaction_wine_id))
            c.execute('UPDATE users SET picked = picked - ? WHERE tid = ?', (last_transaction_quantity, context.user_data['user_id']))
            await update.message.reply_text('Bene, hai cancellato st\'ultima cazzata. Mo ridamme ste bottije!')
    except Exception as e:
        logger.error(e)
        return
    
def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("aiuto", aiuto))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('segna', segna_bottiglie)],
        states={
            CHOOSING: [CallbackQueryHandler(button)],
            # SELECTING_QUANTITY: [MessageHandler(filters.Text() & ~filters.Command(), received_quantity)],
            SELECTING_QUANTITY: [CallbackQueryHandler(received_quantity)]
        },
        fallbacks=[CommandHandler('cancella', cancel)],
    )
    application.add_handler(conv_handler)
    
    application.add_handler(CommandHandler("controlla", controlla_bottiglie))
    application.add_handler(CommandHandler("cancella", cancel))
    application.add_handler(CommandHandler("mischiatutto", mischiatutto))
    application.add_handler(CommandHandler("ciucciatori", ciucciatori))
    application.add_handler(CommandHandler("se_semo_presi", se_semo_presi))
    application.add_handler(CommandHandler("me_so_sbajato", me_so_sbajato))
    

    application.run_polling(allowed_updates=Update.ALL_TYPES)






if __name__ == '__main__':
    main()