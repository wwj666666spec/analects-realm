# Analects Realm

A local learning app for the *Analects* and related classics. Readers can browse the texts, ask questions grounded in retrieved passages, talk with Confucius and his disciples, and turn a short reflection into a portrait, a voice, and a recitation video.

Built for the Nebius x NVIDIA Global AI Hackathon. Dialogue calls [Nebius Token Factory](https://tokenfactory.nebius.com/) and uses NVIDIA open-source Nemotron models.

## What calls Token Factory

| Call | Model |
| --- | --- |
| Full answers (Textual Study, Inner Growth, Practical Guidance), sage chat, and studio copy | `nvidia/nemotron-3-super-120b-a12b` |
| Mode routing and short greetings | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` |

Embeddings stay local: Ollama `bge-m3` (1024 dimensions) and Postgres with pgvector. Portrait, voice, and video stay on Alibaba DashScope and are not part of the Token Factory path.

When the interface language is English, answers are in English. Quoted classical Chinese is kept in Chinese and followed by an English translation.

## Run it

You need Docker Desktop, Python 3.10+, and an NVIDIA GPU for the local embedding model.

The database and the embedding model are **not** in this Git repository. Each archive is larger than GitHub’s 100 MB file limit. They are published as Release assets:

- `rag/lunyu_pg.tar.gz` restores the Postgres volume
- `rag/lunyu_ollama.tar.gz` restores the Ollama volume (`bge-m3`)

Do not run `python -m rag ingest` if you restore those volumes. The library is already loaded.

```powershell
cd rag
copy .env.example .env
# Put your Token Factory key in NEBIUS_API_KEY. No quotes, no spaces.

docker compose create
docker run --rm -v rag_lunyu_pg:/data -v ${PWD}:/backup alpine sh -c "tar -xzf /backup/lunyu_pg.tar.gz -C /data"
docker run --rm -v rag_lunyu_ollama:/data -v ${PWD}:/backup alpine sh -c "tar -xzf /backup/lunyu_ollama.tar.gz -C /data"
docker compose up -d
cd ..
pip install -r rag/requirements.txt
python -m rag serve
```

Open http://127.0.0.1:8787 . Run `python -m rag serve` from this directory, not from inside `rag/`.

Next time, start Docker Desktop, then:

```powershell
cd rag
docker compose up -d
cd ..
python -m rag serve
```

## Layout

- `web/` — the site
- `rag/` — API, retrieval, and Token Factory client
- `数据/` — Markdown sources for the library viewer
- `docs/` — notes in Chinese

## License

MIT. See [LICENSE](LICENSE).
