# FROM nvidia/cuda:11.6.1-devel-ubuntu20.04

# FROM nvidia/cuda:9.0-devel-ubuntu16.04

# # SET TIMEZONE
# ENV TZ=Europe/Brussels
# RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# ARG EXEC_DIR="/opt/executables"
# ARG DATA_DIR="/data"

# # Create folders
# RUN mkdir -p ${EXEC_DIR} \
#     && mkdir -p ${EXEC_DIR}/lib/jcuda \
#     && mkdir -p ${DATA_DIR}/inputs \
#     && mkdir ${DATA_DIR}/outputs
    
# # Copy MIST CUDA lib
# COPY lib/jcuda/*.ptx ${EXEC_DIR}/lib/jcuda/

# # Copy MIST JAR
# COPY target/MIST_*-jar-with-dependencies.jar ${EXEC_DIR}/MIST.jar

# # Set working directory
# WORKDIR ${EXEC_DIR}

FROM wipp/mist:2.0.6

# insall maven
ARG MAVEN_VERSION=3.8.8
ARG USER_HOME_DIR="/root"
ARG BASE_URL=https://apache.osuosl.org/maven/maven-3/${MAVEN_VERSION}/binaries

RUN apt-get update \
    && apt-get install -y libfftw3-dev \
    && apt-get install -y openjdk-8-jdk \
    && apt-get install -y curl \
    && update-alternatives --set java /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java

RUN mkdir -p /usr/share/maven /usr/share/maven/ref \
 && curl -fsSL -o /tmp/apache-maven.tar.gz ${BASE_URL}/apache-maven-${MAVEN_VERSION}-bin.tar.gz \
 && tar -xzf /tmp/apache-maven.tar.gz -C /usr/share/maven --strip-components=1 \
 && rm -f /tmp/apache-maven.tar.gz \
 && ln -s /usr/share/maven/bin/mvn /usr/bin/mvn

ENV MAVEN_HOME /usr/share/maven
ENV MAVEN_CONFIG "$USER_HOME_DIR/.m2"

# Define working directory.
WORKDIR /data
COPY lib/ /data/lib/

# Define commonly used JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/

# install python
RUN apt-get -y update && apt-key adv --refresh-keys --keyserver keyserver.ubuntu.com
RUN apt-get -y install software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa
RUN apt-get -y update
RUN apt-get -y install \
    python3 python3-pip

# RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
#     python3 get-pip.py && \
#     rm get-pip.py
RUN python3 -m pip install --upgrade pip==20.3.4
RUN python3 -m pip install flask==1.1.4

# ENV JAVA_HOME /usr/lib/jvm/default-jvm/

# Define default command.
# CMD ["mvn", "--version"]

# Default command. Additional arguments are provided through the command line
# ENTRYPOINT ["/usr/bin/java", "-jar", "MIST.jar"]
ENTRYPOINT ["/bin/bash"]

# find / -type f -regex '\/.*.tif'
# /usr/bin/java -d64 -Xmx4g -jar target/MIST_-2.1-jar-with-dependencies.jar --gridHeight 24 --gridWidth 78 -startTileRow 24 --startTileCol 0 --extentHeight 24 --extentWidth 78 --horizontalOverlap 49 --verticalOverlap 49 --overlapUncertainty 10 --outputPath /image-document-store/db/08_03_2023_11_49_48/fiji/ --startTileCol 0 --startTileRow 0 --filenamePatternType "ROWCOL" --filenamePattern "tile_{r}_{c}.tiff" --gridOrigin "UL" --imageDir /image-document-store/db/08_03_2023_11_49_48/fiji/ --outputFullImage true --logLevel INFO --programType CUDA
# /usr/bin/java -d64 -Xmx4g -jar target/MIST_-2.1-jar-with-dependencies.jar --gridHeight 25 --gridWidth 25 -startTileRow 0 --startTileCol 0 --extentHeight 25 --extentWidth 25 --horizontalOverlap 49 --verticalOverlap 49 --overlapUncertainty 10 --outputPath /image-document-store/db/27_03_2023_15_15_50/fiji/ --startTileCol 0 --startTileRow 0 --filenamePatternType "ROWCOL" --filenamePattern "stack_{r}_{c}.tiff" --gridOrigin "UL" --imageDir /image-document-store/db/27_03_2023_15_15_50/fiji/ --outputFullImage true --logLevel INFO --programType CUDA
# 11_13
# /usr/bin/java -d64 -Xmx4g -jar target/MIST_-2.1-jar-with-dependencies.jar --gridHeight 12 --gridWidth 14 --extentHeight 12 --extentWidth 14 --horizontalOverlap 10 --verticalOverlap 10 --overlapUncertainty 10 --outputPath /image-document-store/db/29_03_2023_12_24_56/fiji/ --startTileCol 2 --startTileRow 0 --filenamePatternType "ROWCOL" --filenamePattern "tile_{r}_{c}.tiff" --gridOrigin "UL" --imageDir /image-document-store/db/29_03_2023_12_24_56/fiji/ --outputFullImage true --logLevel INFO --programType CUDA

# /usr/bin/java -d64 -Xmx4g -jar target/MIST_-2.1-jar-with-dependencies.jar --gridHeight 22 --gridWidth 28 --extentHeight 3 --extentWidth 5 --startTileCol 20 --startTileRow 12 --horizontalOverlap 49 --verticalOverlap 49 --overlapUncertainty 10 --outputPath /image-document-store/db/fiji/ --filenamePatternType "ROWCOL" --filenamePattern "tile_{r}_{c}.tiff" --gridOrigin "UL" --imageDir /image-document-store/db/fiji/ --outputFullImage true --logLevel INFO --programType CUDA

