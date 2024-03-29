FROM python:3.10-alpine

ADD Pipfile.lock .
RUN pip install pipenv
RUN pipenv requirements > requirements.txt
RUN pip uninstall pipenv -y
RUN pip install -r requirements.txt

ADD app.py .
ADD templates/ templates/

ENTRYPOINT ["python"]

CMD ["app.py"] 