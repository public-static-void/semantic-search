##### Start up the cluster.

    docker-compose up

##### Copy the certificate from the cluster to the local machine.

    docker cp {project_dir}-es01-1:/usr/share/elasticsearch/config/certs/ca/ca.crt {cert_dir}

###### `project_dir` is the root folder of the project where `docker-compose up` has been run in, and `cert_dir` is the directory where to put the certificates on the local machine, could be `/tmp/.`.

##### Verify connecting to the cluster using the certificates created is working correctly.

    curl --cacert {cert_dir}/ca.crt -u elastic:{ELASTIC_PASSWORD} https://localhost:9200

###### `cert_dir` is the directory where the certificates are located on the local machine, could be `/tmp/.`.
