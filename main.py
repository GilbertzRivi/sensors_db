from flask import Flask, request, render_template
from db import Database
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

app = Flask('sensors-db')
bg_color = "#373737"
plt.rcParams['axes.facecolor'] = bg_color

def generate_image_sensor(start, finish, path):

    def normalize_x(input, val):
        output = []
        for i in input:
            x = int(((ref - i[2])/60))
            y = int(i[val])
            output.append((x, y))

        return output[::-1 ]
    db = Database('database.db')
    result = db.fetch('temperature, humidity, timestamp', 'sensors', f'timestamp>{start} and timestamp<{finish}').fetchall()
    result.sort(key=lambda x: x[2])
    no_data = False
    try:
        ref = result[-1][2]
    except IndexError:
        no_data = True

    if not no_data:
        values_h = normalize_x(result, 1)
        y_h = [i[1] for i in values_h]
        x_h = [i[0] for i in values_h]

        x_h = [datetime.fromtimestamp(ref-(60*i)) for i in x_h]
        plt.plot(x_h,y_h, color='b', label="humidity")

        values_t = normalize_x(result, 0)
        y_t = [i[1] for i in values_t]
        x_t = [i[0] for i in values_t]

        x_t = [datetime.fromtimestamp(ref-(60*i)) for i in x_t]
        plt.plot(x_t,y_t, color='r', label="temperature")
    else:
        x_h = 0
        y_h = 0
        x_t = 0
        y_t = 0

    plt.grid()
    plt.legend()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.gcf().autofmt_xdate()
    plt.gcf().set_facecolor(bg_color)
    plt.ylim(ymin=0)
    plt.savefig(path)
    plt.close()

def generate_image_pc(start, finish, path):

    def normalize_x(input, val):
        output = []
        for i in input:
            x = int(((ref - i[4])/60))
            y = int(i[val])
            output.append((x, y))

        return output[::-1 ]
    db = Database('database.db')
    result = db.fetch('cpu_load, cpu_temp, gpu_load, memory, timestamp', 'pc', f'timestamp>{start} and timestamp<{finish}').fetchall()
    result.sort(key=lambda x: x[4])
    no_data = False
    try:
        ref = result[-1][4]
    except IndexError:
        no_data = True

    if not no_data:
        values_cpu_load = normalize_x(result, 0)
        y_cl = [i[1] for i in values_cpu_load]
        x_cl = [i[0] for i in values_cpu_load]

        print(x_cl)
        x_cl = [datetime.fromtimestamp(ref-(60*i)) for i in x_cl]
        print(x_cl)
        plt.plot(x_cl,y_cl, color='r', label="cpu load")

        values_cpu_temp = normalize_x(result, 1)
        y_ct = [i[1] for i in values_cpu_temp]
        x_ct = [i[0] for i in values_cpu_temp]

        x_ct = [datetime.fromtimestamp(ref-(60*i)) for i in x_ct]
        plt.plot(x_ct,y_ct, color='g', label="cpu temp")

        values_gpu_load = normalize_x(result, 2)
        y_gl = [i[1] for i in values_gpu_load]
        x_gl = [i[0] for i in values_gpu_load]

        x_gl = [datetime.fromtimestamp(ref-(60*i)) for i in x_gl]
        plt.plot(x_gl,y_gl, color='b', label="gpu load")

        values_mem = normalize_x(result, 3)
        y_mem = [i[1] for i in values_mem]
        x_mem = [i[0] for i in values_mem]

        x_mem = [datetime.fromtimestamp(ref-(60*i)) for i in x_mem]
        plt.plot(x_mem,y_mem, color='m', label="memory")
    else:
        y_cl = 0
        x_cl = 0
        y_ct = 0
        x_ct = 0
        y_gl = 0
        x_gl = 0
        y_mem = 0
        x_mem = 0

    plt.grid()
    plt.legend()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.gcf().autofmt_xdate()
    plt.gcf().set_facecolor(bg_color)
    plt.ylim(ymin=0)
    plt.savefig(path)
    plt.close()

@app.route("/pc_request", methods=["POST"])
def pc_request_site():
    data = request.get_json(force=True)
    db = Database('database.db')
    db.insert('pc', None, data['cpu_load'], data['cpu_temp'], data['gpu_load'], data['memory'], datetime.now().timestamp())
    db.delete('pc', f'timestamp < {datetime.now().timestamp() - 60*60*24}')
    return "Nice"

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
    num = (int(data['finish']) - int(data['start']))/60
    generate_image_sensor(data['start'], data['finish'], 'static/img.jpg')
    generate_image_pc(data['start'], data['finish'], 'static/img_pc.jpg')
    return "Nice"

@app.route('/', methods=["POST"])
def main_request():
    start = datetime.strptime(request.form['start'], '%Y-%m-%dT%H:%M').timestamp()
    finish = datetime.strptime(request.form['finish'], '%Y-%m-%dT%H:%M').timestamp()
    num = (finish-start)/60
    generate_image_sensor(start, finish, 'static/img.jpg')
    generate_image_pc(start, finish, 'static/img_pc.jpg')
    
    return render_template('template.html', image='static/img.jpg', image_pc='static/img_pc.jpg', dynamicrefresh=0)

@app.route('/')
def main_site():
    generate_image_sensor(datetime.now().timestamp()-60*60*2, datetime.now().timestamp(), 'static/img.jpg')
    generate_image_pc(datetime.now().timestamp()-60*60*2, datetime.now().timestamp(), 'static/img_pc.jpg')
    
    return render_template('template.html', image='static/img.jpg', image_pc='static/img_pc.jpg', dynamicrefresh=1)

if __name__ == '__main__':
    app.run(host='192.168.2.211', port=5000, debug=True, threaded=False)
        