FROM python:3.12


WORKDIR /code

RUN pip install  requests  rich pytz jinja2  pymongo  Jinja2 datetime  flask flask_httpauth flask_session flask-socketio qrcode Pillow

COPY . .

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "7860"]
