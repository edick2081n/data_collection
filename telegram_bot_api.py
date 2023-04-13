import os
import sys
import django
from core.settings import BASE_DIR
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from picking.models import Task
from asgiref.sync import sync_to_async
from django.db.models.functions import StrIndex
from django.db.models import Value


TELEGRAM_TOKEN=os.environ['TELEGRAM_TOKEN']

topic = None
topics_tasks = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="выберите тему задач")
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global topic
    if topic is None:
        topic = update.message.text
        message = "введите сложность задачи"
    else:
        difficulty = int(update.message.text)
        if topic not in topics_tasks:
            topics_tasks[topic]= []
        tasks_numbers = []
        for numbers in await sync_to_async(topics_tasks.values)():
            tasks_numbers+=numbers
        tasks = Task.objects.filter(difficulty=difficulty).annotate(topic_index=StrIndex('topic', Value(topic)))\
        .filter(topic_index__gt=0).exclude(number__in=tasks_numbers)[:10]
        print(tasks.query)
        tasks_data=await sync_to_async(tasks.values)("name", "text_task")
        tasks_numbers = await sync_to_async(tasks.values_list)('number', flat=True)
        topics_tasks[topic] += await sync_to_async(list)(tasks_numbers)
        task_names=[]
        tasks_data = await sync_to_async(list)(tasks_data)
        for task in tasks_data:
            task_names.append(f"[{task['name']}]({task['text_task']})")
        tasks_data = await sync_to_async(", ".join)(task_names)
        message = f"подходящие задачи: {tasks_data}"
        topic = None
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="MarkdownV2")
if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(echo_handler)

    application.run_polling()

