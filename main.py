from flask import Flask, render_template, request
from api_hh02 import getvkans

app = Flask(__name__)

kash = {} # Словарь для хранения кэша запросов

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

    print(request.method)

    if request.method == 'GET':
        return render_template('vvod.html')
    else:

        reg = request.form['region']
        print(reg)

        naimvac = request.form['naimvac']
        print(naimvac)

        lstvac = kash.get(reg + " " + naimvac)
        if lstvac == None:  # Не нашли такой запрос в кэше. Будем формировать запрос и выполнять его.
            lstvac = getvkans(naimvac, reg)
            print('Выполнен запрос к НН')

            # Сохраним в кэше запрос и ответ на него
            kash[reg + " " + naimvac] = lstvac  # Сохраним в кэше запрос и ответ на него
        else:
            print('Выданы данные из кэша.')

        return render_template('ftbl.html', msvac = lstvac, reg=reg, naimvac=naimvac)


if __name__ == "__main__":
    app.run(debug=True)
