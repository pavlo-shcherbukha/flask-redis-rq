FROM registry.fedoraproject.org/f33/python3
# Add application sources to a directory that the assemble script expects them
# and set permissions so that the container runs without root access

USER 0
RUN git config --global url."https://${GIT_USER}:${GIT_PSW}@github.com/".insteadOf "https://github.com/"
RUN git clone ${GIT_URL} /tmp/src -b ${GIT_BRANCH}



RUN /usr/bin/fix-permissions /tmp/src

# Remote debug run
#RUN echo "export PYTHONDONTWRITEBYTECODE=1 ; export PYTHONUNBUFFERED=1 ; python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m flask run -h 0.0.0.0 -p 8080" > /opt/app-root/etc/xapp.sh

RUN echo "PYTHONUNBUFFERED=1" >> /opt/app-root/etc/xapp.sh
RUN echo "PYTHONDONTWRITEBYTECODE=1" >> /opt/app-root/etc/xapp.sh
RUN echo "python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m flask run -h 0.0.0.0 -p 8080" >> /opt/app-root/etc/xapp.sh
RUN chmod 777 /opt/app-root/etc/xapp.sh

RUN echo "========= PRINT DEBUG SH-FILE=========="
RUN cat /opt/app-root/etc/xapp.sh
RUN echo "=========********************=========="

# Put self signed CA into trust store
# RUN cp /tmp/src/sh_app/tlscert/ca-crt.pem /usr/share/pki/ca-trust-source/anchors/
# RUN ls /usr/share/pki/ca-trust-source/anchors/
# RUN update-ca-trust

USER 1001


# Install the dependencies
RUN python3.9 -m pip install --upgrade pip
RUN /usr/libexec/s2i/assemble
EXPOSE 8080

# Remote debug run: packages
# RUN pip install ptvsd debugpy
# Remote debug run: Keeps Python from generating .pyc files in the container
#ENV PYTHONDONTWRITEBYTECODE=1
# Remote debug run: Turns off buffering for easier container logging
#ENV PYTHONUNBUFFERED=1
# Remote debug run
EXPOSE 5678

# Set the default command for the resulting image
CMD /usr/libexec/s2i/run
