import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Global dictionary to store the to-do list for each user
user_todos = {}

# Define states for the conversation handler
ADDING_TODO = 1

# /start command handler
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! I am your Task bot. Use /addtask to add tasks.")

# /addtask command handler - starts the process of adding tasks
async def addtask(update: Update, context: CallbackContext):
    await update.message.reply_text("Please send me your tasks, one per message. Send /donetask when you're done.")
    user_id = update.message.from_user.id
    user_todos[user_id] = []  # Initialize an empty task list for the user
    return ADDING_TODO

# Handler to accept a task item
async def add_todo_item(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    todo_item = update.message.text
    
    # Add the task item to the user's list
    user_todos[user_id].append(todo_item)
    await update.message.reply_text(f"Added: {todo_item}")

    return ADDING_TODO  # Continue accepting more tasks

# /donetask command handler - stops the process and shows the list
async def donetask(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    # If the user has a list, display it
    if user_id in user_todos and user_todos[user_id]:
        todos = "\n".join(user_todos[user_id])
        await update.message.reply_text(f"Here is your task list:\n{todos}")
    else:
        await update.message.reply_text("You don't have any tasks.")
    
    # End the conversation
    return ConversationHandler.END

# /showtask command handler - shows the current tasks
async def showtask(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # If the user has a task list, display it
    if user_id in user_todos and user_todos[user_id]:
        todos = "\n".join(user_todos[user_id])
        await update.message.reply_text(f"Here are your current tasks:\n{todos}")
    else:
        await update.message.reply_text("You don't have any tasks yet. Use /addtask to add some.")

# /deletetask command handler - delete specific task or entire list
async def deletetask(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # If user has tasks, check for task number argument
    if user_id in user_todos and user_todos[user_id]:
        if context.args:
            try:
                # Get the task number from the command argument
                task_number = int(context.args[0]) - 1
                
                # Check if the task number is valid
                if 0 <= task_number < len(user_todos[user_id]):
                    deleted_task = user_todos[user_id].pop(task_number)
                    await update.message.reply_text(f"Deleted task: {deleted_task}")
                else:
                    await update.message.reply_text("Invalid task number.")
            except ValueError:
                await update.message.reply_text("Please provide a valid task number.")
        else:
            # No argument provided: delete the entire task list
            user_todos[user_id].clear()
            await update.message.reply_text("Deleted the entire task list.")
    else:
        await update.message.reply_text("You don't have any tasks to delete.")

# Handler for unknown commands
async def unknown(update: Update, context: CallbackContext):
    await update.message.reply_text("Sorry, I didn't understand that command.")

# Main function to set up the bot
def main():
    # Get the bot token from the environment variable
    bot_token = os.getenv("BOT_TOKEN")

    # Check if the bot token is retrieved successfully
    if bot_token is None:
        print("Error: Bot token not found in environment variables.")
        return

    # Create the bot application
    app = Application.builder().token(bot_token).build()

    # ConversationHandler to manage the flow of adding tasks
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("addtask", addtask)],
        states={
            ADDING_TODO: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_todo_item)],
        },
        fallbacks=[CommandHandler("donetask", donetask)]
    )

    app.add_handler(conv_handler)  # Register the conversation handler
    app.add_handler(CommandHandler("showtask", showtask))  # Register /showtask command
    app.add_handler(CommandHandler("deletetask", deletetask))  # Register /deletetask command
    app.add_handler(CommandHandler("start", start))  # Register /start command
    app.add_handler(MessageHandler(filters.COMMAND, unknown))  # Register unknown command handler

    # Start polling for updates (this starts the bot)
    app.run_polling()

if __name__ == "__main__":
    main()