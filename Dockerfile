FROM openjdk:8-jre-slim

# Install wget and tar
RUN apt-get update && apt-get install -y wget tar && rm -rf /var/lib/apt/lists/*

# Set Launch4j version
ENV LAUNCH4J_VERSION=3.50

# Download and extract Launch4j
RUN wget -O /tmp/launch4j.tgz https://sourceforge.net/projects/launch4j/files/launch4j-${LAUNCH4J_VERSION}-linux-x64.tgz/download && \
    mkdir -p /opt/launch4j && \
    tar -xzf /tmp/launch4j.tgz -C /opt/launch4j --strip-components=1 && \
    rm /tmp/launch4j.tgz

ENV PATH="/opt/launch4j:${PATH}"

WORKDIR /work

# Default command (can be overridden)
ENTRYPOINT ["launch4j"]