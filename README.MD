## Wallpaper api 

A free wallpaper api written in python using fast api. This have some basic features :
- Get a random wallpaper according to specified category 
- Get server status 

This is still in WIP, so there are many things to be done.

#### End points
- `GET /get-wallpaper/`: Gives a random wallpaper.
- `GET /categories`: Provides available categories.
- `GET /list-wallpapers`: Give a list of available wallpapers in the default category.
- `GET /status`: Gives the status of the server.
- `GET /get-wallpaper/?category=${category}`: Gives a random wallaper from given category (default, gruvbox, nordic).

### setup 

Clone the repo

```
git clone https://github.com/sandesh2007/api.git
```

Setup python venv 

```
python -m venv venv 
```

Activate python venv

```
source venv/bin/activate
```

Install required packages
```
pip install -r requirements.txt
```

Run server 
```
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Access the Testing web template at `http://localhost:8080/`

#### the api is hosted at Railway.

### This is just a test thing i made for future by using some yt tutorials and claude ai.