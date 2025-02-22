---
title: "Installation: Containers"
pdf: true
toc: true
---

# Installation: Start Containers

Whether you build or not, the compose command will bring up the application 
(and download containers provided on Docker Hub, if they aren't in your cache).

## What containers are provided?

Singularity Registy Server uses the following images, all provided on Docker Hub 
(or you can build the registry-specific ones locally):

 - [vanessa/sregistry](https://hub.docker.com/r/vanessa/sregistry): is the core application image, generated from the Dockerfile in the base of the repository.
 - [vanessa/sregistry_nginx](https://hub.docker.com/r/vanessa/sregistry_nginx/): Is the nginx container installed with the nginx upload module, intended for use with speedy uploads. It is generated from the subfolder "nginx" in the repository.

To use these images provided, you can bring up the containers like so:

## Start Containers

```bash
$ docker-compose up -d
```

The `-d` means detached, and that you won't see any output (or errors) to the 
console. You can easily restart and stop containers, either specifying the 
container name(s) or leaving blank to apply to all containers. Note that these 
commands must be run in the folder with the `docker-compose.yml`:

```bash
$ docker-compose restart uwsgi worker nginx
$ docker-compose stop
```

When you do `docker-compose up -d` the application should be available at 
`http://127.0.0.1/`, and if you've configured https, `https://127.0.0.1/`. 
If you need to shell into the application, for example to debug with 
`python manage.py shell` you can get the container id with `docker ps` 
and then do:

```bash
NAME=$(docker ps -aqf "name=sregistry_uwsgi_1")
docker exec -it ${NAME} bash
```

## Debugging Containers

Sometimes you might want to start containers and debug. The first thing to do is to stop and remove old containers,
and if necessary, remove old images.

```
docker-compose stop
docker-compose rm
```

If you want to re-pull (or for other reason, remove) the core images, do that too:

```
docker rmi vanessa/sregistry
docker rmi vanessa/sregistry_nginx
```

You can inspect any container by looking at its logs:

```
docker-compose logs uwsgi

# Only the last 30 lines
docker-compose logs --tail=30 uwsgi

# Hanging
docker-compose logs --tail=30 -f uwsgi
```

It's also helpful to (after stopping and removing) bring up the containers but leave out the `-d`
This can commonly show issues related to starting up (and ordering of it).

```
docker-compose up
```

And then press Control+C to kill the command and continue.

## Interactive Debugging

This is my preference for debugging - because you can shell into any of the containers and inspect 
things in real time (interactively). For example, let's say uwsgi is running and the container
has `CONTAINER_ID` of `37b0f7d1332a` (do `docker ps` to get the identifiers). We could
shell into it via:

```bash
docker exec -it 37b0f7d1332a bash
```

and then find the code base at `/code`. You can get an interactive django shell:

```bash
cd /code
python manage.py shell
```

or an interactive database shell.

```bash
python manage.py dbshell
```

## Restart Containers

If you make some change to the container code (the Python, or a configuration value, etc.,) then you
should restart the container for changes to take effect. It's good to be conservative and only restart
those containers that are needed (e.g, usually nginx and uwsgi). 

```bash
docker-compose restart uwsgi nginx    # uwsgi and nginx
docker-compose restart                # all containers
```


## Build Containers

If you make changes to either of the images locally (or have other reason to build them on your own), 
you can do this!  In the base of the repository:

```bash
docker build -t vanessa/sregistry .
```

And then to build nginx:

```
cd nginx
docker build -t vanessa/sregistry_nginx .
```

That's it! Likely the easiest thing to do is just `docker-compose up -d` and let the containers
be pulled and started, and debug only if necessary. Once you have issued the commands to generate and start your containers,
it's time to read the [setup](../setup) guide to better understand how to configure and interact with your Singularity Registry.
