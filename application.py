from flask import Flask, render_template, request, url_for, redirect
import datetime
import sqlite3

import functions

app = Flask(__name__)


@app.route('/', methods=['GET'])
@app.route('/USD', methods=['GET'])
def redirect_homepage():
    
    now = datetime.date.today().strftime('%Y-%m-%d')
    past = (datetime.date.today() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    return redirect(url_for('.homepage', waluta = 'USD', start = past, stop = now))

@app.route('/<waluta>/<start>/<stop>', methods=['GET'])
def homepage(waluta, start, stop):

    now = datetime.date.today().strftime('%Y-%m-%d')
    past = (datetime.date.today() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    start = datetime.datetime.strptime(start, '%Y-%m-%d')
    stop = datetime.datetime.strptime(stop, '%Y-%m-%d')

    data, curr = functions.get_data_from_db(waluta, str(start), str(stop))

    if len(data) == 0:
        functions.get_data_from_nbp_max('A', waluta, start, stop)
        data, curr = functions.get_data_from_db(waluta, start, stop)
        chart_name = functions.chart(data, waluta)
        data = reversed(data)
        return render_template("index.html", cur = waluta, lista = data, start = past, stop = now, zapytanie = '/'+waluta, chart = '../../../static/'+chart_name)
    elif start == data[0][0] and stop == data[len(data)-1][0]:
        chart_name = functions.chart(data, waluta)
        data = reversed(data)
        return render_template("index.html", cur = waluta, lista = data, start = past, stop = now, zapytanie = '/'+waluta, chart = '../../../static/'+chart_name)
    elif start == data[0][0]:
        new_start_date = datetime.datetime.strptime(data[len(data)-1][0], '%Y-%m-%d') + datetime.timedelta(days=1)
        functions.get_data_from_nbp_max('A', waluta, new_start_date, stop)
        data, curr = functions.get_data_from_db(waluta, str(start), str(stop))
        chart_name = functions.chart(data, waluta)
        data = reversed(data)
        return render_template("index.html", cur = waluta, lista = data, start = past, stop = now, zapytanie = '/'+waluta, chart = '../../../static/'+chart_name)
    else:
        new_stop_date = datetime.datetime.strptime(data[0][0], '%Y-%m-%d') - datetime.timedelta(days=1)
        functions.get_data_from_nbp_max('A', waluta, start, new_stop_date)
        data, curr = functions.get_data_from_db(waluta, start, stop)
        chart_name = functions.chart(data, waluta)
        data = reversed(data)
        return render_template("index.html", cur = waluta, lista = data, start = past, stop = now, zapytanie = '/'+waluta, chart = '../../../static/'+chart_name)

@app.route('/<waluta>', methods=['POST'])
@app.route('/<waluta>/<start>/<stop>/', methods=['POST'])
def homepage_change(waluta):

    start = request.form['text_od']
    stop = request.form['text_do']

    return redirect(url_for('.homepage', waluta = waluta, start = start, stop = stop))

@app.route('/table/<waluta>/<start>/<stop>/', methods=['GET'])
def table(waluta, start, stop):
    data, curr = functions.get_data_from_db(waluta, str(start), str(stop))
    return render_template("table.html", cur = waluta, lista = data, start = start, stop = stop)

@app.route('/table/<waluta>/<chart_name>', methods=['GET'])
def chart(waluta, chart_name):
    
    return render_template("chart.html", cur = waluta, chart = chart_name)

@app.route('/clear_cache', methods=['GET'])
def clear_cache():
    con = sqlite3.connect('nbp.db')
    cur = con.cursor() 
    cur.execute("DELETE FROM currency") 
    con.commit()
    con.close()
    con = sqlite3.connect('charts.db')
    cur = con.cursor() 
    cur.execute("DELETE FROM pictures") 
    con.commit()
    con.close()

    now = datetime.date.today().strftime('%Y-%m-%d')
    past = (datetime.date.today() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    return redirect(url_for('.homepage', waluta = 'USD', start = past, stop = now))


if __name__ == "__main__":
    app.run()
