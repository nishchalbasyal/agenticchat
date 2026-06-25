FROM python:3.12-slim

WORKDIR /code

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

CMD streamlit run src/frontend.py --server.port=$PORT --server.address=0.0.0.0
