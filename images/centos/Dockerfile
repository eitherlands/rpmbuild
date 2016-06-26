FROM centos:7

RUN yum upgrade -y
RUN yum groupinstall -y "Development Tools"
RUN yum install -y yum-utils git rpm-build spectool coreutils findutils bc gnupg git
RUN mkdir /root/rpmbuild /artifacts

ENV DOCKER=true
VOLUME /artifacts
WORKDIR /root/rpmbuild

COPY ./SOURCES /root/rpmbuild/SOURCES
COPY ./SPECS /root/rpmbuild/SPECS
COPY ./vendor/manage /root/rpmbuild/manage
COPY ./.manage.yml /root/rpmbuild/.manage.yml
COPY ./scripts /root/rpmbuild/scripts

ENTRYPOINT ["/root/rpmbuild/manage/bin/manage"]
CMD ["build"]

