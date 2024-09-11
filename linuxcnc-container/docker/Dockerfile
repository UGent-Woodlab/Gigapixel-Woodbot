FROM debian:buster-backports

ARG HTTP_PROXY

# Configure & update apt
# - Silence some Apt warnings
ENV DEBIAN_FRONTEND noninteractive
RUN echo 'APT::Install-Recommends "0";\nAPT::Install-Suggests "0";' > \
    /etc/apt/apt.conf.d/01norecommend

# # - Upgrade packages
RUN apt-get update
RUN apt-get upgrade -y && \
    apt-get clean
# - Silence more Apt warnings
RUN apt-get install -y \
#    software-properties-common \
    libfile-fcntllock-perl \
    && apt-get clean

# Install and configure sudo, passwordless for everyone
RUN apt-get install -y \
    sudo && \
    apt-get clean
RUN echo "ALL	ALL=(ALL:ALL) NOPASSWD: ALL" >> /etc/sudoers

# Cookie variable for container build environment
ENV ENV_COOKIE docker-build

# HTTP proxy for wget, etc.
ENV http_proxy ${HTTP_PROXY}

###########################################
# Install packages
#
# Customize the following for building/running targeted software

# Install misc. packages
ARG EXTRA_PACKAGES
RUN apt-get install -y \
    ccache \
    gnupg2 \
    ${EXTRA_PACKAGES} \
    && apt-get clean

# Copy install scripts; only copy modular parts on demand so they can
# be fixed without dirtying the Docker cache
COPY env.sh /tmp/install/

# Update system & install general dependencies
COPY 1-system.sh /tmp/install/
RUN /tmp/install/1-system.sh

# Install LCNC deps
COPY 2-lcnc-deps.sh /tmp/install/
RUN /tmp/install/2-lcnc-deps.sh

# Install LCNC
COPY 3-lcnc-install.sh /tmp/install/
RUN /tmp/install/3-lcnc-install.sh

# Install python dependencies
COPY 4-python-config.sh /tmp/install/
RUN /tmp/install/4-python-config.sh

# Final cleanup
RUN rm -rf /tmp/install

# Image version for adding to the environment
ARG IMAGE_VERSION

ENV \
    # Speed builds with ccache
    PATH=/usr/lib/ccache:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin \
    # Set image version for internal sanity checks
    IMAGE_VERSION=${IMAGE_VERSION}
    # disable Pythons .local import path
    #PYTHONNOUSERSITE=True

# Cookie variable for container run environment
ENV ENV_COOKIE docker-run

# Set the locale
RUN locale-gen en_US.UTF-8 && dpkg-reconfigure locales

###########################################
# Set up user
#

# This shell script adds passwd and group entries for the user
COPY entrypoint.sh /usr/bin/entrypoint
ENTRYPOINT ["/usr/bin/entrypoint"]

# Add python files to home
RUN mkdir /usr/src/server
COPY py-websocket-server /usr/src/server/

# If no args to `docker run`, start an interactive shell
CMD ["/bin/bash", "--login", "-i"]
