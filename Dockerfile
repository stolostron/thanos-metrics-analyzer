FROM python:3
RUN mkdir /thanos-metrics-anlytics
RUN chmod a+rwx -R /tmp
RUN chmod a+rwx -R  /thanos-metrics-anlytics
COPY ./requirements.txt /thanos-metrics-anlytics/requirements.txt
WORKDIR /thanos-metrics-anlytics 
RUN pip install -r requirements.txt
COPY ./*.py /thanos-metrics-anlytics 
CMD [ "python", "start.py" ]
