FROM python:3.10

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
#RUN pip3 install --update setuptools - ошибка доступа, нет прав

COPY . .

CMD ["python", "-u", "src/main.py"]