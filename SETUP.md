# Setup

Dialogue uses NVIDIA Nemotron on Nebius Token Factory. Put the key in `NEBIUS_API_KEY` inside `rag/.env`. See [README.md](README.md) and `rag/.env.example`.

Follow the steps below after you unpack the archives. The database and the embedding model are already exported. Do not ingest them again.

## 1. Requirements

- Docker Desktop, already running
- An NVIDIA GPU and a working driver. The embedding model uses the GPU
- Python 3.10 or newer
- Network access to Nebius Token Factory
- Ports 5434, 11434, and 8787 free

The package should contain:

```
project\
  rag\                 code, docker-compose.yml, and two tar.gz archives
  web\                 the site
  data\                Markdown files for the library
```

The inner folder must stay named `rag`. You can rename the outer folder. Do not rename `rag`.

## 2. Add your key

Create `rag/.env`:

```
NEBIUS_API_KEY=your-key-here
NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1
```

No spaces around `=`, and no quotes. Do not share this file.

## 3. Install Python dependencies

From the project root (the folder that contains `rag`, `web`, and `data`):

```powershell
pip install -r rag/requirements.txt
```

## 4. Restore the database and the embedding model

Enter `rag`. Create the volumes, unpack the archives, then start the containers. Do not run `docker compose up` first.

```powershell
cd rag
docker compose create
docker run --rm -v rag_lunyu_pg:/data -v ${PWD}:/backup alpine sh -c "tar -xzf /backup/lunyu_pg.tar.gz -C /data"
docker run --rm -v rag_lunyu_ollama:/data -v ${PWD}:/backup alpine sh -c "tar -xzf /backup/lunyu_ollama.tar.gz -C /data"
docker compose up -d
```

Each `docker run` pulls a small Alpine image and loads one archive into a volume. Do this once.

Check that both containers are running:

```powershell
docker compose ps
```

The database is published on port 5434. Ollama is published on port 11434.

If pulling `pgvector/pgvector:pg16` or `ollama/ollama` times out, pull through a mirror and retag:

```powershell
docker pull docker.m.daocloud.io/pgvector/pgvector:pg16
docker tag docker.m.daocloud.io/pgvector/pgvector:pg16 pgvector/pgvector:pg16
docker pull docker.m.daocloud.io/ollama/ollama:latest
docker tag docker.m.daocloud.io/ollama/ollama:latest ollama/ollama:latest
```

Then run `docker compose create` and `docker compose up -d` again. If the volumes are already loaded, do not delete them and do not unpack again.

## 5. Open the site

Return to the project root:

```powershell
cd ..
python -m rag serve
```

Open [http://127.0.0.1:8787](http://127.0.0.1:8787).

Leave that window open. Closing it stops the site. The database and Ollama keep running in Docker.

Do not run `python server.py` or `python -m rag` inside `rag/`. Run `python -m rag serve` from the project root.

## 6. What each page uses

- Library and reading: local Markdown in `data`. They do not call Token Factory.
- Q&A and Conversations with the Sages: the database, the local embedding model, and Nemotron on Nebius Token Factory. The first question loads `bge-m3` into GPU memory and is slower.
- Sign-in and registration: the restored database. The first registration creates the user table.

Textual Study, Inner Growth, and Practical Guidance are three answer styles. Conversations with the Sages is a separate area for the group circle and private chats.

## 7. Do not

- Do not run `python -m rag ingest`. The books are already in the exported database.
- Do not pull or rebuild the embedding model. `bge-m3` is inside `lunyu_ollama.tar.gz`.
- Do not rename the `rag` folder. The volume names depend on it.
- Do not put `.env` into an archive and send it to someone else.

## 8. Start it again later

After Docker Desktop is running:

```powershell
cd rag
docker compose up -d
cd ..
python -m rag serve
```

Then open [http://127.0.0.1:8787](http://127.0.0.1:8787).

## 9. If it does not open

- The page does not load: check that the `python -m rag serve` window is still open and the address is [http://127.0.0.1:8787](http://127.0.0.1:8787).
- Q&A or the sages report a connection error: run `docker compose ps`. Both containers should be running, and ports 5434 and 11434 should be free.
- A missing-key error: in `rag/.env`, `NEBIUS_API_KEY` must be on one line, with no space or quotes after `=`.
- Ollama does not start: this machine needs an NVIDIA GPU.
- Chinese text looks garbled in PowerShell: that is the console encoding. The website is unaffected.
