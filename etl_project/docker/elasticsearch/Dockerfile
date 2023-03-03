FROM elasticsearch:7.10.1

ENV "discovery.type"="single-node"
ENV ELASTICSEARCH_HOST=elasticsearch
ENV ELASTICSEARCH_PORT=9200

USER elasticsearch

COPY preload.sh genres.json persons.json movies.json /tmp/data/

EXPOSE 9200

CMD [ "/tmp/data/entrypoint.sh" ]