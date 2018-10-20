FROM python:3.7
MAINTAINER strautins.janis@gmail.com

ADD src/server.py /home/
ADD output/sample.json /home/output/

RUN pip install scrapy
RUN pip install pyramid

CMD [ "python", "./home/server.py" ]

