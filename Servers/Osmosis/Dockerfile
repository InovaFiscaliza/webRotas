FROM openjdk:8-jdk-alpine
RUN apk add --no-cache bash
ADD https://bretth.dev.openstreetmap.org/osmosis-build/osmosis-latest.tgz /osmosis.tgz
RUN tar -xzf /osmosis.tgz -C / && rm /osmosis.tgz
ENV PATH="/bin/osmosis/bin:$PATH"
