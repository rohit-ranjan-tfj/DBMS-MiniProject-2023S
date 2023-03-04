# Welcome to Hospital Management System!

The HMS was implemented as a min-term project for ``CS39202 DATABASE MANAGEMENT SYSTEMS LABORATORY`` in Spring '23. 

## Run Instructions
```
Provide the URI to your database server in config.py.
$ flask db migrate
$ flask run

On first startup, only admin user account is available. 
>User Category: admin
>Username: admin
>Password: admin

Use admin account to create accounts for front_desk operator, data_entry, operator and doctor.
Respective User Categories are front_desk, data_entry and doctor.
```
## Install and Setup Instructions
[ElasticSearch Setup Instructions](https://stackoverflow.com/questions/39447617/failed-to-establish-a-new-connection-errno-111-connection-refusedelasticsear)
```
$ pip install -r requirements.txt
```
## Known issues with Elastic Search API
The API defaults to read-only mode for its index when disk space is low. Use the below commands to change the default behaviour. [Refer here for details](https://stackoverflow.com/questions/50609417/elasticsearch-error-cluster-block-exception-forbidden-12-index-read-only-all)

```
curl -XPUT -H "Content-Type: application/json" http://localhost:9200/_cluster/settings -d '{ "transient": { "cluster.routing.allocation.disk.threshold_enabled": false } }'
curl -XPUT -H "Content-Type: application/json" http://localhost:9200/_all/_settings -d '{"index.blocks.read_only_allow_delete": null}'
```
