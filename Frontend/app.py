from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

mock_messages = [
    {"role": "bot", "content": "สวัสดีครับ! ผมคือ MitrPhol RAG Assistant ผู้ช่วยค้นหาข้อมูลเทคนิคของคุณ..."},
    {"role": "user", "content": "ค่าความขุ่น (Turbidity) ของน้ำอ้อยใสมีผลต่อกระบวนการเคี่ยวอย่างไร?"},
    {"role": "bot", "content": "ค่าความขุ่นของน้ำอ้อยใสหมายถึงการมีสิ่งเจือปนต่างๆ เช่น กัม (gums), แว็กซ์ (waxes)..."}
]

@app.route('/')
def index():
    return render_template('index.html', messages=mock_messages)

@app.route('/community')
def community():
    return render_template('community.html')

@app.route('/logbook')
def logbook():
    return render_template('logbook.html')

if __name__ == '__main__':
    app.run(debug=True)