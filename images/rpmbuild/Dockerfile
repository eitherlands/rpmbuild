FROM centos:8

ENV DOCKER=true
RUN yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm && \
    yum -y --setopt="tsflags=nodocs" upgrade && \
    yum -y --setopt="tsflags=nodocs" install --allowerasing bc \
                                             coreutils \
                                             epel-release \
                                             expect \
                                             findutils \
                                             git \
                                             gnupg \
                                             mock \
                                             rpm-build \
                                             rpm-sign \
                                             spectool \
                                             sudo \
                                             yum-utils && \
    yum clean all && \
    rm -rf /var/cache/yum/

RUN adduser -u 1000 -G mock -U -m centos && \
    echo 'centos ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    mkdir -p /home/centos/cache /home/centos/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS} && \
    echo '%_topdir %(echo $HOME)/rpmbuild' > ~/.rpmmacros && \
    chmod g+w /etc/mock/*.cfg && \
    echo "config_opts['use_nspawn'] = False" >> /etc/mock/site-defaults.cfg && \
    echo "config_opts['cache_topdir'] = '/home/centos/cache/mock'" >> /etc/mock/site-defaults.cfg


WORKDIR /home/centos/rpmbuild
VOLUME /tmp/repository
VOLUME /home/centos/cache

COPY ./manage /home/centos/rpmbuild/manage
COPY ./.manage.yml /home/centos/rpmbuild/.manage.yml
COPY ./scripts /home/centos/rpmbuild/scripts

RUN chown centos:centos -R /home/centos && install -g mock -m 2775 -d /home/centos/cache/mock

USER centos
RUN /home/centos/rpmbuild/manage trust-escapace
ENTRYPOINT ["/home/centos/rpmbuild/manage"]
CMD ["build"]
