from flask import Flask, request, render_template
from db import Database
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
app = Flask('sensors-db')

@app.route("/request/", methods=["POST", "GET"])
def request_site():
    data = request.get_json(force=True)
    db = Database('database.db')
    db.insert('sensors', None, data['temperature'], data['humidity'], datetime.now().timestamp())
    db.delete('sensors', f'timestamp < {datetime.now().timestamp() - 60*60*24}')
    return "Nice"

@app.route('/')
def main_site():
    db = Database('database.db')
    result = db.fetch_all('temperature, humidity, timestamp', 'sensors').fetchall()
    result.sort(key=lambda x: x[2])
    ref = datetime.now().timestamp()

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
        while j < 100:
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
    plt.savefig('static/img.jpg')
    plt.close()
    
    return render_template('template.html', image='static/img.jpg')

if __name__ == '__main__':
    app.run(host='192.168.100.36', port=5000, debug=True, threaded=False)