FROM python

WORKDIR /home/app

COPY . .

RUN pip install -r requirements.txt
COPY . /home/app
EXPOSE 8503

CMD streamlit run --server.port $PORT app.py