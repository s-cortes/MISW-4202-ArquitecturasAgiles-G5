
FROM python:3
RUN mkdir /backend
WORKDIR /backend
ADD events.requirements.txt /backend/
RUN pip install -r events.requirements.txt
ADD * /backend/
EXPOSE 5000