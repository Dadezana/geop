# Geop<br>![Cocoapods platforms](https://img.shields.io/badge/Platform-Windows-blue) ![Cocoapods platforms](https://img.shields.io/badge/Platform-Linux-yellow) ![Cocoapods platforms](https://img.shields.io/badge/Platform-Android-green) ![Cocoapods platforms](https://img.shields.io/badge/Platform-MacOS-red)
Cross-platform program tested on Windows, Linux and Android<br>
I made it to speed up the access to my school's register, so i don't have, every time, to open the browser, search for the register and so on...

# How to use it
>Install packages: `pip -r requirements.txt`<br>
## <img src="https://1000marcas.net/wp-content/uploads/2019/12/Windows-Logo-1.png" width=40> **Windows**
1. Install python from the [website](https://www.python.org/downloads/) or from the microsoft store (suggested)
2. Open terminal and install the required packages
3. Move the file in a handy position in your pc (i suggest your home directory)
4. Open the terminal, navigate to the directory you moved your file (by default terminal opens in your home dir)
5. Run the file

## <img src="https://logos-world.net/wp-content/uploads/2020/09/Linux-Logo.png" width=40> **Linux and MacOS**
1. Install python and the required packages
2. Move the file in `~/.local/bin/` and rename it as `geop` *(or whatever you like)*
3. Give the file execution permission `chmod +x <file_name>`
4. Now you can run the file in every directory of your pc, using a terminal

## <img src="https://cdn.freebiesupply.com/logos/thumbs/2x/android-logo.png" width=33> **Android**
1. Download a python interpreter *(I used Pydroid3)*
2. Open the file and put the `!` in the first line to the second one after the `#`
3. Place the file wherever in your phone
4. Open it with your python interpreter and run it
<br>
 
>Syntax: `geop [email] [start_date] [end_date]`
## Examples
> If no year specified, the current one will be used
```bash
geop 21-11-2022 27-11-2022  # range set from 21-11-2022 to 27-11-2022
geop 21-11 27-11            # range set from 21-11-2022 to 27-11-2022
```
```bash
geop 21-11-2022  # range set from 21-11-2022 to 28-11-2022
geop 21-11       # range set from 21-11-2022 to 28-11-2022
```
```bash
geop yesterday 15-12 # range set from yesterday to 15-12-2022
```
```bash
geop today tomorrow # range set from today to tomorrow
```
> The number can be positive or negative and it's always referred to the start date
```bash
geop +3         # range set from today to 3 days later
geop 21-12 +5   # range set from 21-12-2022 to 5 days later (26-12-2022)
```

### What to know
- All the arguments are optional
- You can pass the arguments in every order you like and you can mix various type of telling the date
- Date format can be "dd-mm-yyyy" or "yyyy-mm-dd". If only one date is passed, it will be considered as *start_date* exception for `+x` numbers

# <img src="https://cdn.icon-icons.com/icons2/317/PNG/512/key-icon_34404.png" width=20>  License
You are free to modify and share the program as you like.<br>
If you change it I'd like to know, maybe you had a good idea and I can implement it!