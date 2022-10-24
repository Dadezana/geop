#!/bin/python
#/data/user/0/ru.iiec.pydroid3/files/aarch64-linux-android/bin/python
from requests import Session, utils, ConnectionError
from datetime import date, time, timedelta, datetime
from getpass import getpass
from sys import argv
from time import sleep
from termcolor import colored
import calendar, json, re
import sys, os
import colorama     # needed to display color windows's terminal

colorama.init()

MAIL_REGEX = "^[\w\-\.]+@itsrizzoli.it$"

# "info" is a list of json
def extract_info(info):

    WEEKDAY = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    SYMBOLS = {
        "ok": "✔",
        "cross": "x"
    }

    lessons = []    # list of dictionaries. used to sort the lessons before displaying them

    for _lesson in info:
        lesson = {}
        lesson["id"]      = int(_lesson["id"])
        lesson["subject"] = _lesson["tooltip"].split("<br>")[1].split(":")[1].strip().replace("Ã", "à")
        lesson["teacher"] = _lesson["tooltip"].split("<br>")[4].split(":")[1].strip()
        lesson["start"]   = _lesson["start"].split("T")[1][:-3].strip()
        lesson["end"]     = _lesson["end"].split("T")[1][:-3].strip()
        lesson["room"]    = _lesson["tooltip"].split("<br>")[2].split(":")[1].strip()
        lesson["day"]     = _lesson["start"].split("T")[0].split("-")
        lesson["month"]   = calendar.month_abbr[int(lesson["day"][1])]
        weekday_num       = calendar.weekday( int(lesson["day"][0]), int(lesson["day"][1]), int(lesson["day"][2]) )
        lesson["weekday"] = WEEKDAY[weekday_num]
        lesson["type"]    = _lesson["ClasseEvento"].lower()

        lesson_date = datetime(int(lesson["day"][0]), int(lesson["day"][1]), int(lesson["day"][2]), int(lesson["start"].split(":")[0]), int(lesson["start"].split(":")[1]))
        lesson["isDone"] = lesson_date < datetime.today()
        
        lesson["color"] = "white"
        lesson["symbol"] = SYMBOLS["cross"]
        if lesson["isDone"] == True:
            lesson["color"] = "white"
            lesson["symbol"] = SYMBOLS["ok"]
        
        if lesson["type"] == "esame":
            lesson["color"] = "magenta"
        
        lessons.append(lesson)

    return lessons

# todo: far si che il formato della data sia sempre di tipo "date"
def print_lessons(lessons):
    
    lessons.sort(key=lambda l: (int(l["day"][0]), int(l["day"][1]), int(l["day"][2]) ))

    for l in lessons:
        canPrintDay = True
        symbol, weekday, day, month, start, end, color = l["symbol"], l["weekday"], l["day"], l["month"], l["start"], l["end"], l["color"]
        teacher, subject, room = l["teacher"], l["subject"], l["room"]
        type_ = l["type"]

        previous_lesson_i = lessons.index(l) - 1
        if previous_lesson_i >= 0:
            previous_lesson = lessons[previous_lesson_i]
            if previous_lesson["day"] == day:
                canPrintDay = False

        if "sospensione didattica" in teacher.lower():
            print( colored(f"\n{symbol} {weekday[:3]} {day[2]} {month} {day[0]}, {start}-{end}", "red", attrs=["bold"]) )
            print( colored("-"*37, "red") )
            print( colored("Sospensione didattica", "red") )
            continue

        if not canPrintDay:
            print(" "*19, end="")
            print( colored(f"{start}-{end}", color, attrs=["bold"]) )
            print( colored(f"\t\t{teacher}\rTeacher: ", color) )
            print( colored(f"\t\t{subject}\rSubject: ", color) )
            print( colored(f"\t\t{room}\rRoom: ", color) )
            return

        print( colored(f"\n{symbol} {weekday[:3]} {day[2]} {month} {day[0]}, {start}-{end}", color, attrs=["bold"]), end="" )
        print( colored(f" [Esame]" if type_ == "esame" else "", "magenta", attrs=["bold"]) )
        print( colored("-"*37, color) )
        print( colored(f"\t\t{teacher}\rTeacher: ", color) )
        print( colored(f"\t\t{subject}\rSubject: ", color) )
        print( colored(f"\t\t{room}\rRoom: ", color) )

def swap(obj1, obj2):
    return obj2, obj1 

def check_argv():
    
    start_date = ""
    end_date = ""
    username = ""

    for arg in argv[1:]:
        if re.match("^(0?[1-9]|[12][0-9]|3[01])\-(0?[1-9]|1[012])\-\d{4}$", arg):   # [d]d-[m]m-yyyy

            if start_date != "" and end_date != "":
                print( colored("Error: Too much dates passed.\nOnly the first two will be taken into consideration", "red") )
                continue

            d = int(arg.split("-")[0])
            m = int(arg.split("-")[1])
            y = int(arg.split("-")[2])

            if start_date == "":
                start_date = date(y, m ,d)
                continue

            end_date = date(y, m, d)
            if end_date < start_date:
                start_date, end_date = swap(start_date, end_date)

            # the register doesn't count the last day provided when fetching the db
            end_date += timedelta(days=1)

            start_date = f"{start_date.year}-{start_date.month}-{start_date.day}"            
            end_date = f"{end_date.year}-{end_date.month}-{end_date.day}"
            

        elif re.match("^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$", arg):   # yyyy-[m]m-[d]d

            if start_date != "" and end_date != "":
                print( colored("Error: Too much dates passed.\nOnly the first two will be taken into consideration", "red") )
                continue

            d = int(arg.split("-")[2])
            m = int(arg.split("-")[1])
            y = int(arg.split("-")[0])

            if start_date == "":
                start_date = date(y, m ,d)
                continue

            end_date = date(y, m, d)
            if end_date < start_date:
                start_date, end_date = swap(start_date, end_date)

            # the register doesn't count the last day provided when fetching the db
            end_date += timedelta(days=1)
            
            start_date = f"{start_date.year}-{start_date.month}-{start_date.day}"            
            end_date = f"{end_date.year}-{end_date.month}-{end_date.day}"


        elif re.match(MAIL_REGEX, arg):
            username = arg
            write_to_file("email.txt", username)

        else:
            print(colored(f"Unrecognized option {arg}", "red"))

    return start_date, end_date, username

def get_file_content(file_name):
    username = ""

    exe_path = os.path.expanduser('~')
    file_name = f"{exe_path}/{file_name}"

    with open(file_name, "r") as f:
            username = f.readline()
    
    return username

def get_input_email():
    username = ""
    while True:
        username = input("Insert mail: ")

        if re.match(MAIL_REGEX, username) != None:
            break

        print( colored("Invalid mail", "red") )
        sleep(1)
    return username

def write_to_file(file_name, text):
    
    exe_path = os.path.expanduser('~')
    file_name = f"{exe_path}/{file_name}"

    with open(file_name, "w") as f:
            f.write(text) if not "dict" in str(type(text)) else json.dump(text, f) # write as json if the type is a dictionary (json is double quoted, dictionary not)

def get_cookies_of(session):
    cookies = json.loads(get_file_content("cookies.json"))
    utils.add_dict_to_cookiejar(session.cookies, cookies)

def is_cookie_valid_in(url, session):

    res = session.get(url)                          # no need to try-catch. Exceptions are handled externally from this function

    if res.status_code == 200:
        if "Sintassi non corretta" in res.text:     # cookie not valid anymore, asking for user's password
            return False
        return True
    else:
        raise Exception(colored(str(res.status) + " " + res.reason, "red"))

def can_login(username, psw, session, url):
    login_url = "/geopcfp2/update/login.asp?1=1&ajax_target=DIVHidden&ajax_tipotarget=login"
    body = {
        'username': username,
        'password': psw
    }

    url += login_url
    res = session.post(url, data=body)

    if res.status_code == 200:
        if "Username e password non validi" in res.text:    # valid password, ready to save cookies
            return False
        return True
    else:
        print( colored(str(res.status) + " " + res.reason, "red") )
    return False

def correct_dates(start_date, end_date):

    if start_date == "":
        start_date = date.today()
    if end_date == "":
        end_date = start_date + timedelta(days=8)  # default is +7, but the register doesn't count the last day provided when fetching the db
        
    if "date" in str(type(start_date)):
        start_date = f"{start_date.year}-{start_date.month}-{start_date.day}"
    if "date" in str(type(end_date)):    
        end_date = f"{end_date.year}-{end_date.month}-{end_date.day}"

    return start_date, end_date

def main():
    start_date, end_date, username = check_argv()
    
    start_date, end_date = correct_dates(start_date, end_date)  # if no dates are provided. Default is today +7 days

    site = "https://itsar.registrodiclasse.it"
    lessons_url = f"/geopcfp2/json/fullcalendar_events_alunno.asp?Oggetto=idAlunno&idOggetto=2672&editable=false&z=1665853136739&start={start_date}&end={end_date}&_=1665853136261"
    # used to get presence of the student from website
    presence_url = "https://itsar.registrodiclasse.it/geopcfp2/json/data_tables_ricerca_registri.asp"
    presence_body = "columns%5B0%5D%5Bdata%5D=idRegistroAlunno&columns%5B0%5D%5Bname%5D=idRegistroAlunno&columns%5B1%5D%5Bdata%5D=Giorno&columns%5B1%5D%5Bname%5D=Giorno&columns%5B2%5D%5Bdata%5D=Data&columns%5B2%5D%5Bname%5D=Data&columns%5B3%5D%5Bdata%5D=DataOraInizio&columns%5B3%5D%5Bname%5D=DataOraInizio&columns%5B4%5D%5Bdata%5D=DataOraFine&columns%5B4%5D%5Bname%5D=DataOraFine&columns%5B5%5D%5Bdata%5D=MinutiPresenza&columns%5B5%5D%5Bname%5D=MinutiPresenza&columns%5B6%5D%5Bdata%5D=MinutiAssenza&columns%5B6%5D%5Bname%5D=MinutiAssenza&columns%5B7%5D%5Bdata%5D=CodiceMateria&columns%5B7%5D%5Bname%5D=CodiceMateria&columns%5B8%5D%5Bdata%5D=Materia&columns%5B8%5D%5Bname%5D=Materia&columns%5B9%5D%5Bdata%5D=CognomeDocente&columns%5B9%5D%5Bname%5D=CognomeDocente&columns%5B10%5D%5Bdata%5D=Docente&columns%5B10%5D%5Bname%5D=Docente&columns%5B11%5D%5Bdata%5D=DataGiustificazione&columns%5B11%5D%5Bname%5D=DataGiustificazione&columns%5B12%5D%5Bdata%5D=Note&columns%5B12%5D%5Bname%5D=Note&columns%5B13%5D%5Bdata%5D=idLezione&columns%5B13%5D%5Bname%5D=idLezione&columns%5B14%5D%5Bdata%5D=idAlunno&columns%5B14%5D%5Bname%5D=idAlunno&columns%5B15%5D%5Bdata%5D=DeveGiustificare&columns%5B15%5D%5Bname%5D=DeveGiustificare&order%5B0%5D%5Bcolumn%5D=2&order%5B0%5D%5Bdir%5D=desc&order%5B1%5D%5Bcolumn%5D=3&order%5B1%5D%5Bdir%5D=desc&start=0&length=10000&search%5Bregex%5D=false&NumeroColonne=15&idAnnoAccademicoFiltroRR=13&MateriePFFiltroRR=0&RisultatiPagina=10000&SuffissoCampo=FiltroRR&NumeroPagina=1&OrderBy=DataOraInizio&ajax_target=DIVRisultati&ajax_tipotarget=elenco_ricerca_registri&z=1666466657560"
    canGetCookie = True

    try:
        file_username = get_file_content("email.txt")
        if re.match(MAIL_REGEX, file_username) == None:
            raise Exception()
    except:
        file_username = ""

    if username == "":
        try:
            username = get_file_content("email.txt")
            if re.match(MAIL_REGEX, username) == None:
                raise Exception()
        except:
            username = get_input_email()
            write_to_file("email.txt", username)

    if username != file_username:   # if the username passed is different from the one saved, there is no point checking the cookie's validity
        canGetCookie = False

    #* Getting cookie
    session = Session()
    try:
        if not canGetCookie:
            raise Exception()

        cookies = get_cookies_of(session)

        if not is_cookie_valid_in(site + lessons_url, session):
            raise Exception()

    except ConnectionError as e:
        print(colored("Failed to connect. Check your internet connection", "red"))

    except:
        while True:
            psw = getpass()
            try:
                if can_login(username, psw, session, site):
                    break
            except ConnectionError as e:
                print(colored("Failed to connect. Check your internet connection", "red"))
                sys.exit(1)
            except:
                print(colored("Something went wrong", "red"))
                sys.exit(1)
            else:
                print(colored("Wrong password", "red"))
            sleep(1)

        cookies = session.cookies.get_dict()
        write_to_file("cookies.json", cookies)
            
    # LESSONS
    url = site + lessons_url
    try:
        res = session.get(url)
        lessons = extract_info(res.json())
        print_lessons(lessons)
    except ConnectionError as e:
        print(colored("Failed to connect. Check your internet connection", "red"))
    except Exception as e:
        print(e)
        sys.exit(1)
    

if __name__ == '__main__':
    main()

