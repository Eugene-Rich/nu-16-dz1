from flask import Flask, render_template, request
from api_hh02 import getvkans
import sqlite3

app = Flask(__name__)
conn = sqlite3.connect('hh.db',check_same_thread=False)
cursor = conn.cursor()

@app.route("/")
def index():
   return render_template('index.html')

@app.route('/instrp/')
def instrp():
    return render_template('instrp.html')

@app.route('/ftbl/')
def results():
    return render_template('ftbl.html')


@app.route('/vvod/', methods=['GET', 'POST'])
def vvod():

    if request.method == 'GET':
        return render_template('vvod.html')
    else:

        # Обрабатываем регион
        reg = request.form['region']
        cursor.execute('SELECT * FROM region WHERE name = ?', (reg,))
        rezreg = cursor.fetchall()
        if len(rezreg) == 0: # Добавим в базу регион
            cursor.execute('INSERT INTO region (name) VALUES (?)', (reg,))
            conn.commit()
            cursor.execute('SELECT * FROM region WHERE name = ?', (reg,))
            rezreg = cursor.fetchall()
        k_region = rezreg[0][0]

        # Обрабатываем наименование вакансии
        naimvac = request.form['naimvac']
        cursor.execute('SELECT * FROM vacancy WHERE name = ?', (naimvac,))
        rezvac = cursor.fetchall()
        if len(rezvac) == 0: # Добавим в базу наименование вакансии
            cursor.execute('INSERT INTO vacancy (name) VALUES (?)', (naimvac,))
            conn.commit()
            cursor.execute('SELECT * FROM vacancy WHERE name = ?', (naimvac,))
            rezvac = cursor.fetchall()
        k_vacancy = rezvac[0][0]

        # Ищем запись в таблице поиска.
        cursor.execute('SELECT id FROM tseek WHERE k_region = ? and k_vacancy = ?', (k_region, k_vacancy,))
        rezts = cursor.fetchall()
        if len(rezts) == 0: # При отсутствии этой записи создаем ее.
            cursor.execute('INSERT INTO tseek (k_region, k_vacancy) VALUES (?,? )', (k_region, k_vacancy))
            conn.commit()
            cursor.execute('SELECT id FROM tseek WHERE k_region = ? and k_vacancy = ?', (k_region, k_vacancy,))
            rezts = cursor.fetchall()
        k_ts = rezts[0][0]

        # Ищем записи в таблице вакансий.
        cursor.execute('SELECT organiz, zarplata FROM listvac WHERE idzap = ?', (k_ts,))
        rezlsvc = cursor.fetchall()
        if len(rezlsvc) == 0: # Не найден такой запрос в нашей базе. Будем запрашивать с hh.
            lstvac = getvkans(naimvac, reg)

            # Сохраним в нашей базе ответ HH
            for vac in lstvac:
                cursor.execute('INSERT INTO listvac (idzap, organiz, zarplata) VALUES (?,?,?)', (k_ts, vac[0], vac[1]))
                conn.commit()

            print('Выполнен запрос к НН')

        else:
            lstvac = []
            for rz in rezlsvc:
                print(rz)
                stls = [rz[0], rz[1]]
                lstvac.append(stls)

            print('Выданы данные из нашей базы.')


        return render_template('ftbl.html', msvac = lstvac, reg=reg, naimvac=naimvac)


if __name__ == "__main__":
    app.run(debug=True)
