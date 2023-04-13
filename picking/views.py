import time
import requests
from bs4 import BeautifulSoup
from picking.models import Task
from random import randint
import schedule


def receiving_data():
    headers = {"Accept-Language": "ru-RU,ru;q=0.5"}
    list_tasks = []
    list_update =[]
    try:
        existing_tasks = {task.number: task for task in Task.objects.only("number", "solution").all()}
        print(existing_tasks)
        for n in range(1, 2):
            response = requests.get(f"https://codeforces.com/problemset/page/{n}?order=BY_SOLVED_DESC", headers=headers)
            time.sleep((randint(1, 2)))
            html_doc = response.content
            soup = BeautifulSoup(html_doc, 'html.parser')
            table = soup.find("table", class_="problems")
            try:

                for tr in table.findAll("tr")[1:]:
                    number = tr.find("td", class_="id").get_text().strip()
                    difficulty = tr.find("span", class_="ProblemRating")
                    if difficulty is not None:
                        difficulty = difficulty.get_text().strip()
                    else:
                        difficulty =1
                    topic = []
                    topics = tr.findAll("a", class_="notice")
                    for top in topics:
                        topic.append(top.get_text())
                    name = tr.findAll("a")[1].get_text().strip()
                    tag_content = tr.findAll("a")[1]
                    atribut_content = tag_content.get("href")
                    letter_index = atribut_content.split("/")[-1]
                    number_ind = atribut_content.split("/")[-2:-1]
                    number_index = int("".join(number_ind))

                    solution = tr.findAll("a")[-1]
                    if solution is not None:
                        solution= solution.get_text().strip()[1:]
                    else:
                        solution = 1
                    print(solution)
                    text_task = f"https://codeforces.com/problemset/problem/{number_index}/{letter_index}"
                    if number in existing_tasks:
                        existing_task = existing_tasks[number]
                        if solution != existing_task.solution:
                            existing_task.solution= solution
                            list_update.append(existing_task)
                    else:
                        list_tasks.append(Task(number=number,
                                               name=name,
                                               topic=','.join(topic),
                                               difficulty=difficulty,
                                               solution=solution,
                                               text_task=text_task
                                               ))


            except requests.HTTPError:
                print("ошибка данных при переборе тегов")
    except requests.HTTPError:
        print("ошибка данных при переборе страниц")
    Task.objects.bulk_create(list_tasks, ignore_conflicts=True)
    Task.objects.bulk_update(list_update, fields=("solution", ))

# schedule.every(60).minutes.do(receiving_data)
# while True:
#     schedule.run_pending()
#     time.sleep(1)


   # Вопросы к Леониду
#  Хотел уточнить по поводу ссылок в телеграмме на задачу (линк)
# Хотел уточнить как переписать обновление данных в новой редакции
#  Что происходит при повторном вызове функции по расписанию если функция еще не успела отработать первый проход
# может надо дождаться первичного прохода и затем только запускать по расприсанию
#  выводится ошибка связанная с незаполненными тегами диффикалти ради чего в прошлый раз писали is not None
#  Хотелось бы понять исправляет ли эту ситуацию то что я добавил else
#  Как правильно указать адрес по которому нужно склонировать репозиторий в readme
#  Уточнить про ошибки при сохранении в github