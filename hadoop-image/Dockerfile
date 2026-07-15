FROM ubuntu:24.04

ARG ARCH=amd64

####################
# JAVA
####################

ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-${ARCH}

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y openjdk-8-jdk && \
    rm -rf /var/lib/apt/lists/*



####################
# HADOOP
####################

ENV HADOOP_VERSION=3.3.6
ENV HADOOP_HOME=/usr/local/hadoop
ENV HADOOP_OPTS=-Djava.library.path=/usr/local/hadoop/lib/native
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

ENV YARN_RESOURCEMANAGER_USER=root
#ENV HADOOP_SECURE_DN_USER root
ENV YARN_NODEMANAGER_USER=root

COPY ./install-hadoop.sh /tmp/install-hadoop.sh
RUN chmod +x /tmp/install-hadoop.sh && bash /tmp/install-hadoop.sh && rm /tmp/install-hadoop.sh

# Creating data folder
RUN mkdir -p /data/dfs/data /data/dfs/name /data/dfs/namesecondary
VOLUME /data

COPY start-namenode.sh /usr/local/bin/start-namenode.sh
RUN chmod +x /usr/local/bin/start-namenode.sh

####################
# PORTS
####################
#
# http://docs.hortonworks.com/HDPDocuments/HDP2/HDP-2.3.0/bk_HDP_Reference_Guide/content/reference_chap2.html
# http://www.cloudera.com/content/cloudera/en/documentation/core/latest/topics/cdh_ig_ports_cdh5.html
# http://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-common/core-default.xml
# http://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/hdfs-default.xml

# HDFS: NameNode (NN):
#	 9820 = fs.defaultFS			(IPC / File system metadata operations)
#						(9000 is also frequently used alternatively)
#	 9871 = dfs.namenode.https-address	(HTTPS / Secure UI)
#	 9870 = dfs.namenode.https-address	(HTTPS / Secure UI)
# HDFS: DataNode (DN):
#	9866 = dfs.datanode.address		(Data transfer)
#	9867 = dfs.datanode.ipc.address	(IPC / metadata operations)
#	9864 = dfs.datanode.https.address	(HTTPS / Secure UI)
# HDFS: Secondary NameNode (SNN)
#	9868 = dfs.secondary.http.address	(HTTP / Checkpoint for NameNode metadata)
EXPOSE 9000 9870 9866 9867 9864 9868 8088 8042



CMD ["hdfs"]