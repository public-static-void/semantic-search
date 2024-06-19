# Semantic Search using Elasticsearch and BERT with a Streamlit UI.

### The dataset is fashion themed so that useful search might include some fashion item and some properties such as color, e.g. `blue shirt` or `red pants`, as well as something more sophisticated.

##### Set up environment variables, such as:

    ELASTIC_PASSWORD=changeme

    STACK_VERSION=8.14.1

    CLUSTER_NAME=es-semantic-cluster

    LICENSE=basic

    ES_PORT=9200

    ES_MEM_LIMIT=1073741824

    CERT_DIR=/tmp/

###### Put them in an `.env` file in the root directory of the project, set them temporarily in the command line, e.g. `export VAR=VAL`, or prepend them directly to docker-compose, e.g. `VAR=VAL docker-compose up`.

##### Start up the cluster.

    docker-compose up

###### This might take some 10-15 mins. Once finished, Streamlit will be running on port 8501. First time running might take some extra time due to Elasticsearch indexing the data.

##### Copy the certificate from the cluster to the local machine.

    docker cp {project_dir}-es01-1:/usr/share/elasticsearch/config/certs/ca/ca.crt {cert_dir}

###### `project_dir` is the root folder of the project where `docker-compose up` has been run in, and `cert_dir` is the directory where to put the certificates on the local machine, could be `/tmp/.`.

##### Verify connecting to the cluster using the certificates created is working correctly.

    curl --cacert {cert_dir}/ca.crt -u elastic:{ELASTIC_PASSWORD} https://localhost:9200

###### `cert_dir` is the directory where the certificates are located on the local machine, could be `/tmp/.`.
