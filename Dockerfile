FROM python:3.7
MAINTAINER strautins.janis@gmail.com

ADD src/server.py /home/
ADD output/sample.json /home/output/

RUN pip install scrapy
RUN pip install pyramid
RUN pip install console-menu
RUN pip install numpy
RUN pip install matplotlib
RUN pip install pandas
RUN pip install flask

CMD [ "python", "./home/server.py" ]

