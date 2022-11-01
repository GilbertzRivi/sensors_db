from flask import Flask, request, render_template
from db import Database
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

app = Flask('sensors-db')

def generate_image(start, finish, num, path):
    db = Database('database.db')
    result = db.fetch('temperature, humidity, timestamp', 'sensors', f'timestamp>{start} and timestamp<{finish}').fetchall()
    result.sort(key=lambda x: x[2])
    ref = result[-1][2]

    def normalize_x(input, val):
        output = []
        for i in input:
            x = int(((ref - i[2])/60))
            y = int(i[val])
            output.append((x, y))
            
        input = output[::-1 ]
        output = []
        j = 0
        i = 0
        while j < num:
            if input[i][0] == j:
                output.append((input[i][1], j))
                i += 1
                j += 1
            elif input[i][0] < j:
                i += 1
            elif j < input[i][0]:
                output.append((0, j))
                j += 1

        return output

    values_h = normalize_x(result, 1)
    y_h = [i[0] for i in values_h]
    x_h = [i[1] for i in values_h]

    x_h = [datetime.fromtimestamp(ref-(60*i)) for i in x_h]
    plt.plot(x_h,y_h, color='b')

    values_t = normalize_x(result, 0)
    y_t = [i[0] for i in values_t]
    x_t = [i[1] for i in values_t]

    x_t = [datetime.fromtimestamp(ref-(60*i)) for i in x_t]

    plt.plot(x_t,y_t, color='r')
    plt.grid()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.gcf().autofmt_xdate()
    plt.ylim(ymin=0)
    plt.savefig(path)
    plt.close()

@app.route("/request/", methods=["POST", "GET"])
def request_site():
    data = request.get_json(force=True)
    db = Database('database.db')
    db.insert('sensors', None, data['temperature'], data['humidity'], datetime.now().timestamp())
    db.delete('sensors', f'timestamp < {datetime.now().timestamp() - 60*60*24}')
    return "Nice"

@app.route("/render_image/", methods=["POST"])
def render_image():
    data = request.get_json(force=True)
    print(data['start'], data['stop'], data['num'])
    generate_image(data['start'], data['stop'], data['num'], 'static/img.jpg')
    return "Nice"

@app.route('/', methods=["POST"])
def main_request():
    print(request.form['start'])
    start = datetime.strptime(request.form['start'], '%Y-%m-%dT%H:%M').timestamp()
    finish = datetime.strptime(request.form['finish'], '%Y-%m-%dT%H:%M').timestamp()
    generate_image(start, finish, int(request.form['num']), 'static/img.jpg')
    
    return render_template('template.html', image='static/img.jpg')

@app.route('/')
def main_site():
    generate_image(datetime.now().timestamp()-60*60*2, datetime.now().timestamp(), 100, 'static/img.jpg')
    
    return render_template('template.html', image='static/img.jpg')

if __name__ == '__main__':
    app.run(host='192.168.100.36', port=5000, debug=True, threaded=False)
        