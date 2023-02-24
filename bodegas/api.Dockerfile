
FROM python:3
RUN mkdir /backend
WORKDIR /backend
ADD api.requirements.txt /backend/
RUN pip install -r api.requirements.txt
ADD * /backend/
EXPOSE 5000