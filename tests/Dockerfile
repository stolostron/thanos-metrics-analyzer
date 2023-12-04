FROM registry.access.redhat.com/ubi8/python-39

LABEL name="thanos-metrics-analyzer-ci" \
      description="thanos-metrics-analyzer CI docker file" \
      target-file="Dockerfile"

# Install pip & pipenv
RUN pip install --upgrade --no-cache-dir pip && \
    pip install --upgrade --no-cache-dir pipenv

# Setup work directory
WORKDIR /opt/app-root/

RUN pip install -r requirements.txt
