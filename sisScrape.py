from bs4 import BeautifulSoup
import requests
import cred

#change this
email = cred.email
password = cred.password
mailTarget = cred.te

#don't change this
mailUser = cred.ee
mailPass = cred.epass


website = 'https://eng.asu.edu.eg/login'
target = 'https://eng.asu.edu.eg/dashboard/my_courses'
mode = 1
final = {}
temp = []
codes = []
ind = 0


with requests.session() as s:
    print('Logging in...')
    res = s.get(website)
    content = res.text
    soup = BeautifulSoup(content, 'lxml')
    token = content[3343:3383]
    payload = {
        '_token':token,
        'email': email,
        'password': password
        }
    s.post(website, data=payload)
    print('Log in done...')
    r0 = s.get('https://eng.asu.edu.eg/dashboard')
    someData = BeautifulSoup(r0.text,'lxml')
    scrapingD = someData.find_all('h3', class_='text-white')
    gpa = str(scrapingD[0]).split('>')[1].split('<')[0]
    trainingWeeks = str(scrapingD[1]).split('>')[1].split('<')[0]
    hoursPassed = str(scrapingD[2]).split('>')[1].split('<')[0]
    r = s.get(target)
    courses = BeautifulSoup(r.text,'lxml')
    cards = courses.find_all('div', class_='card-header')
    for card in cards:
        e = str(card.find('a')).split('>')
        code = e[1][:-3]
        codes.append(code)
    print(f'[*]Detected {len(codes)} courses!')
    for card in cards:
        ind = ind +1
        print(f'Checking {ind}/{len(codes)}')
        e = str(card.find('a')).split('>')
        code = e[1][:-3]
        final[code[0:7]] = {}
        t = e[0][9:-1]
        c = BeautifulSoup(s.get(t).text, 'lxml')
        data = c.find_all('div', class_='col-lg-3')
        for mark in data:
            gs = mark.find_all('li')
            for g in gs:
                temp.append(str(g)[-13:-5].strip('> () ;">'))
            for j in range(0,len(temp)):
                if mode > 0:
                    if temp[j] == 'Midterm':
                        final[code[0:7]]['Midterm'] = temp[j+1]
                    elif temp[j] == 'tivities':
                        final[code[0:7]]['Activities'] = temp[j+1]
                    else:
                        final[code[0:7]]['GPA'] = temp[j+1]
                    mode = mode*-1
                elif mode < 0:
                    mode = mode*-1
            temp.clear()

print('preparing E-mail')
          
tempmsg = []
for key in list(final.keys()):
    K = list(final[key].keys())
    tempmsg.append(codes[list(final.keys()).index(key)]+":\n")
    for gra in K:
        tempmsg.append(f'{gra}:{final[key][gra]}\n')
    tempmsg.append('\n')

footer = f'\nGPA:{gpa} | Training Weeks: {trainingWeeks} | Credit Hours Passed: {hoursPassed}'
msg = 'Grades report.\n\n\n' +''.join(tempmsg) + footer

import smtplib

smtp_username = mailUser
smtp_password = mailPass

# creates SMTP session
S = smtplib.SMTP('smtp.gmail.com', 587)
# start TLS for security
S.starttls()
# Authentication
S.login(smtp_username, smtp_password)
# sending the mail
print("Sending E-Mail to you...")
S.sendmail(smtp_username, mailTarget, msg)

print("Sending short E-Mail...")
import pandas as pd

data = pd.DataFrame(final).transpose()
msg2 = str(data) + '\n' + footer
S.sendmail(smtp_username, mailTarget, msg2)

# terminating the session
S.quit()

print('Done...')
