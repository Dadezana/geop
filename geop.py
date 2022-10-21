#!/bin/python
from requests import Session, utils
from datetime import date, time, timedelta
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
        weekday_num = calendar.weekday( int(lesson["day"][0]), int(lesson["day"][1]), int(lesson["day"][2]) )
        lesson["weekday"] = WEEKDAY[weekday_num]
        lesson["type"] = _lesson["ClasseEvento"].lower()
        
        lesson["color"] = "green"
        lesson["symbol"] = "✔"
        if _lesson["backgroundColor"] == "#B7B7B7":
            lesson["color"] = "white"
            lesson["symbol"] = "x"
        
        if lesson["type"] == "esame":
            lesson["color"] = "magenta"
        
        lessons.append(lesson)

    return lessons

def print_lessons(lessons):
    
    lessons.sort(key=lambda l: (int(l["day"][0]), int(l["day"][1]), int(l["day"][2]) ))

    for l in lessons:
        symbol, weekday, day, month, start, end, color = l["symbol"], l["weekday"], l["day"], l["month"], l["start"], l["end"], l["color"]
        teacher, subject, room = l["teacher"], l["subject"], l["room"]
        type = l["type"]

        if "sospensione didattica" in teacher.lower():
            print( colored(f"\n{symbol} {weekday[:3]} {day[2]} {month} {day[0]}, {start}-{end}", "red", attrs=["bold"]) )
            print( colored("-"*37, "red") )
            print( colored("Sospensione didattica", "red") )
            continue

        print( colored(f"\n{symbol} {weekday[:3]} {day[2]} {month} {day[0]}, {start}-{end}", color, attrs=["bold"]), end="" )
        print( colored(f" [Esame]" if type == "esame" else "", "magenta", attrs=["bold"]) )
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
    body = {
        'username': username,
        'password': psw
    }

    try: res = session.post(url, data=body)
    except: 
        # print(colored("Can't connect to url", "red"))
        return True             # Connection exception will be handled by the lessons request

    if res.status_code == 200:
        if "Username e password non validi" in res.text:    # valid password, ready to save cookies
            return False
        return True
    else:
        print( colored(str(res.status) + " " + res.reason, "red") )

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
    login_url = "/geopcfp2/update/login.asp?1=1&ajax_target=DIVHidden&ajax_tipotarget=login"
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
    except:
        while True:
            psw = getpass()
            url = site + login_url
            if can_login(username, psw, session, url):
                break
            print(colored("Wrong password", "red"))
            sleep(1)

        cookies = session.cookies.get_dict()
        write_to_file("cookies.json", cookies)
            
    # LESSONS
    url = site + lessons_url
    
    try: res = session.get(url)
    except: 
        print(colored("Can't connect to url", "red"))
        sys.exit(1)

    if res.status_code == 200:
        lessons = extract_info(res.json())
        print_lessons(lessons)
    else:
        print( colored(str(res.status_code) + " " + res.reason, "red") )
        sys.exit(1)
    

if __name__ == '__main__':
    main()

