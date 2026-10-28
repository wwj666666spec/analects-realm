# Frontend setup

这一版前端是多页 HTML，由同一套 Python 服务直接送出。打开站点不需要 Node，也不需要单独起一个前端进程。

## 1. Decisions

先做过一版 Vite + React，页面能跑，但接收方还要装 Node、跑构建。后来改成纯 HTML：每个页面一个 `.html`，交互写在旁边的 `.js` 里，样式集中在一份 CSS。FastAPI 既提供接口，也把这些文件当页面返回。

后端原有的检索、问答、先贤对话没有重写。`rag/server.py` 只是包一层 HTTP，再把 `web/` 里的页面送出去。

## 2. Stack

| 部分 | 选用 | 说明 |
| --- | --- | --- |
| 页面 | HTML | 每个功能一页，浏览器直接打开 |
| 交互 | 原生 JavaScript，`<script type="module">` | 用 `fetch` 调接口，没有 jQuery、没有打包器 |
| 样式 | 一份 `site.css` | CSS 变量、网格布局，没有 UI 框架 |
| 服务 | FastAPI + Uvicorn | `python -m rag serve`，监听 `127.0.0.1:8787` |
| 账号 | 现有 Postgres | 表 `users`、`auth_sessions`，第一次登录或注册时自动建 |
| 密码 | 标准库 `pbkdf2_hmac` | SHA-256，12 万次，盐和摘要用 `$` 拼在一起 |
| 登录态 | Cookie `lunyu_session` | HttpOnly、SameSite=Lax、14 天、路径 `/` |
| 问答和先贤记录 | 浏览器 `localStorage` | 还没有挂到账号上 |
| 书库正文 | 本地 Markdown | 按 `##` 拆节，不重新入库，也不走向量检索 |
| 依赖 | `fastapi>=0.115`、`uvicorn>=0.32` | 写在 `rag/requirements.txt`，装在系统 Python 里 |

页面字体：正文用思源宋体、Noto Serif SC、宋体这一串衬线字体；按钮和输入框用系统无衬线字体。配色是纸色 `#f3eee6`、墨色 `#1e1a16`、印章红 `#8d3b32`。

## 3. Layout

```
web/
  site.css          全站样式
  api.js            请求、超时、转义和本地存储
  auth.js           导航上的登录名和退出
  gate.js           登录、注册表单
  index.html        首页
  ask.html / ask.js 问答
  sages.html / sages.js
                    先贤
  library.html / library.js
                    书库书架
  book.html / book.js
                    阅读
  presence.html     风骨占位
  me.html / me.js   我的
  login.html
  register.html

rag/server.py       页面路由和 /api
rag/auth.py         注册、登录、退出
rag/books.py        书目、分节、正文
```

静态文件挂在 `/static`，目录就是整个 `web/`。所以 `/static/ask.js` 对应 `web/ask.js`。页面路由写在这个挂载之前，避免 `/ask` 这类地址被当成静态文件。

CSS 和脚本带了查询参数，例如 `site.css?v=5`。改样式或脚本后把数字加大，浏览器才会丢掉旧缓存。Python 代码改了必须停掉进程再执行 `python -m rag serve`，服务没有热重载。只改 HTML、JS、CSS 时，只要查询参数变了，刷新即可。

## 4. How to start

在项目根目录 `E:\研究生\课程\人工智能+\项目` 执行：

```
python -m rag serve
```

浏览器打开 http://127.0.0.1:8787 。

数据库要先起来：在 `rag/` 里 `docker compose up -d`。问答、先贤和登录都会连这套库（宿主机端口 5434）。书库只读 `data/` 里的 Markdown，阅读本身不查向量。

不要在 `rag/` 目录里用 `python server.py` 启动。那样 `import rag` 会失败。从项目根目录用 `python -m rag serve`。

## 5. Page structure

每个页面都是同一套壳：

- 桌面宽度：左侧固定导航，宽 168px。
- 窄屏（760px 以下）：左侧导航隐藏，底部出现一排入口。
- 导航：首页、问答、先贤、书库、风骨、我的，以及登录。
- 已登录时，`auth.js` 请求 `GET /api/me`，把「登录」换成用户名和「退出」。

首页是两扇门：问答、先贤。旁边再链到书库和风骨。

## 6. How a request moves

```
浏览器页面
  -> fetch /api/...
  -> rag/server.py
  -> 已有的 ask / sage / search / books / auth
  -> JSON 回到页面
```

`web/api.js` 统一发请求。超时后中止，并提示「等得太久了，可以再试一次」。问答 150 秒，围坐 200 秒，私聊 120 秒。这些时间留给检索和模型，不是前端自己在生成文字。

接口返回的错误文案在 JSON 的 `detail` 里，页面直接显示这句。

## 7. Page flows

### Q&A `/ask`

左侧是治学、修心、修身，加上「新建会话」和历史列表。右侧是对话。

1. 打开页面时从 `localStorage` 键 `lunyu.ask` 读出 `{ sessions, currentId }`。
2. 如果读到的是旧的数组，整段收成一条 id 为 `legacy` 的会话。
3. 「新建会话」先只是草稿，发出第一句才写入列表。
4. 发送时 `POST /api/ask`，正文是 `{ query, mode }`。
5. 返回 `agent`、`answer`、`sources`。依据放在回答气泡里，标题是「检索依据」，格式如 `原文 《论语》学而第一`。
6. 问候、道谢、告别走后端的接谈，不查库，气泡里没有检索依据。
7. 每一问都是单独一次请求，模型不记住上一句。
8. 改名用浏览器的 `prompt`，删除用 `confirm`。最多留下 30 条会话。
9. Enter 发送，Shift+Enter 换行。

会话存在这台浏览器里，不跟账号走。换浏览器或清站点数据，历史就没了。

### Sages `/sages`

围坐和私聊是两个入口，互不混用。

围坐：

1. `POST /api/seat`，先拿到这一场的人，页面先把座位画出来。
2. 再 `POST /api/round`，把这些人的 id 送回去，等他们说完。
3. 人数由后端定：孔子第一个，其余随机，一共 5 到 16 人。
4. 「你好」这类招呼只留孔子，不检索。

私聊：

1. 打开页面时 `GET /api/sages`，列出 17 人。围坐时这份名单藏起来。
2. 默认对子路说。点一个人再发送。
3. `POST /api/talk`，正文是 `{ who, query }`，`who` 是人物 id，例如 `zilu`。

记录存在 `lunyu.sages`。某人还没返回时，那一行显示「还在想。」

### Library `/library` and reading `/book`

书架按四类排：原文、注疏、礼、史传。分类来自文件名，规则在 `rag/chunk.py` 的 `layer_of`：`论语.md` 是原文，其余以「论语」开头的是注疏，文件名含「礼记」的是礼，剩下的是史传。

1. `GET /api/books` 返回四类和书名。
2. 分类和书名筛选在浏览器里做，不另发请求。
3. 点一本书进入 `/book?name=书名`。
4. `GET /api/book?name=` 返回节标题。
5. 点一节，`GET /api/book/text?name=&index=` 返回正文。
6. 一节超过 8000 字时只返回开头，页面写「这一节很长，这里只显示开头。」

阅读按 Markdown 的 `##` 分节。没有 `##` 的书整本作为「正文」。这和问答用的向量检索是两条路：书架是翻原文，问答是查相关段落。

旧的句子检索 `GET /api/search` 还在，当前书架页面不再调用它。

### Sign in `/login` and registration `/register`

表单把用户名和密码用 JSON 交给 `/api/login` 或 `/api/register`。注册成功会直接登录，然后回到首页。

- 用户名：2 到 20 个字，汉字、字母或数字。
- 密码：6 到 64 位。
- 重名：「这个用户名已经注册过。」
- 登录失败：「用户名或密码不对。」

站点不强制登录。未登录也能问答、围坐和翻书。

### Account `/me`

读本机的三份记录：最近问答、最近先贤、收藏。收藏键是 `lunyu.marks`。「清空」只删这三份本地记录，不删账号。书架改版之后，页面上还没有新的收藏入口。

### Studio `/presence`

占位页。声音和影像还没接，页内链到先贤。

## 8. API list

| 方法 | 路径 | 作用 |
| --- | --- | --- |
| GET | `/api/health` | 服务是否在 |
| GET | `/api/me` | 当前用户，未登录返回 401 |
| POST | `/api/register` | 注册并写 Cookie |
| POST | `/api/login` | 登录并写 Cookie |
| POST | `/api/logout` | 退出并删 Cookie |
| GET | `/api/books` | 四类书目 |
| GET | `/api/book?name=` | 一本书的节目录 |
| GET | `/api/book/text?name=&index=` | 一节正文 |
| GET | `/api/sages` | 17 人的 id、名字、一句简介 |
| GET | `/api/search?q=` | 句子检索，书架未使用 |
| POST | `/api/ask` | 问答 |
| POST | `/api/seat` | 围坐先排座 |
| POST | `/api/round` | 围坐发言 |
| POST | `/api/talk` | 私聊 |

页面地址是 `/`、`/ask`、`/sages`、`/library`、`/book`、`/presence`、`/me`、`/login`、`/register`，各自返回对应的 HTML。

## 9. Relation to the reference pages

问答、登录、注册、书库的版式参照了另一套古代智慧系统的模板：左侧会话、居中登录框、竖排书脊和分类搜索。参照的是结构和交互，没有把那套 Flask、jQuery、Font Awesome 搬过来。

对应到这一版时做了这些取舍：

- 问答模式仍是治学、修心、修身。
- 书库分类是原文、注疏、礼、史传，因为手头的书就是这四层。
- 书库副标题是「学而时习之，不亦说乎」。
- 先贤不出现治学、修心、修身这几个名字。

## 10. Not connected yet

- 问答和先贤的历史还在 `localStorage`，换设备不会跟着账号走。
- 问答没有多轮记忆，每次问题单独送给模型。
- 风骨还没有声音和影像。
- 改服务端代码后要手动重启 `python -m rag serve`。
