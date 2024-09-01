FROM --platform=linux/amd64 python:3.11.5

COPY . .
RUN pip install -r requirements.txt


EXPOSE 8080
ENTRYPOINT ["streamlit","run","streamlit_app.py"]