FROM quay.io/centos/centos:stream9

LABEL maintainer="jccy016@gmail.com"
LABEL description="Ansible control node based on CentOS Stream 9"
LABEL ansible.version="ansible-core==2.17.*"

RUN dnf update -y && \
    dnf install -y \
        python3 \
        python3-pip \
        openssh-clients \
        git \
        sshpass \
    && dnf clean all \
    && rm -rf /var/cache/dnf

RUN pip3 install --no-cache-dir "ansible-core==2.17.*"

RUN mkdir -p /ansible/playbooks /ansible/inventory /ansible/roles

WORKDIR /ansible

CMD ["ansible", "--version"]
