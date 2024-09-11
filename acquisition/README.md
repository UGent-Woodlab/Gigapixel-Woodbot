### create requirements.txt 
```shell
pipreqs acquisition-py/. --savepath ./.container_build/requirements.txt
```

### build container
```shell
docker build --build-arg USER=$USER --build-arg UID=$UID --build-arg GID=$GID --build-arg PW=docker -f Dockerfile . -t acquisition-image
```

### run container
```shell
docker run -it --name acquisition-container --network host acquisition-image 
```

### Exec bash prompt in running container 
```shell
docker exec -it acquisition-container bash
```
