# Use the UBI minimal base image
FROM registry.access.redhat.com/ubi8/ubi-minimal:latest

LABEL name="thanos-metrics-analyzer" \
      description="thanos metrics analyzer docker file" \
      target-file="Dockerfile"

# Set environment variables
ENV PYTHON_VERSION=3.9 \
    PATH=$HOME/.local/bin/:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8

# Install Python 3.9
RUN microdnf update -y && \
    microdnf install -y python39 && \
    microdnf -y clean all && rm -rf /var/cache/yum

# Install pipenv and setuptools
RUN pip3.9 install --no-cache-dir --upgrade pip && \
    pip3.9 install --no-cache-dir --upgrade pipenv && \
    pip3.9 install --no-cache-dir 'setuptools>=65.5.1'

RUN mkdir /thanos-metrics-anlytics
RUN chmod a+rwx -R  /thanos-metrics-anlytics
COPY ./requirements.txt /thanos-metrics-anlytics/requirements.txt
WORKDIR /thanos-metrics-anlytics 
RUN pip install -r requirements.txt
COPY ./*.py /thanos-metrics-anlytics 
ENTRYPOINT [ "python", "start.py" ]
