FROM registry.access.redhat.com/ubi9/ubi-minimal:latest
USER root
RUN curl -sSL https://raw.githubusercontent.com/codeuh/customize-bash/main/customize-bash.sh | bash
RUN microdnf install -y python3.12 python3.12-pip \
    && microdnf clean all \
    && python3.12 -m venv /venv \
    && /venv/bin/python3.12 -m pip install --upgrade pip \
    && ln -s /venv/bin/python3.12 /usr/bin/python \
    && ln -s /venv/bin/pip3.12 /usr/bin/pip 
COPY /app/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
ENV _ZO_DOCTOR=0 \
    PATH="/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_WARN_SCRIPT_LOCATION=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POSH_THEME="/root/.posh-themes/powerlevel10k_lean.omp.json" 
