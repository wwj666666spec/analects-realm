# Nebius Token Factory 开通流程

比赛：[Nebius x NVIDIA Global AI Hackathon](https://nebiusglobalaihackathon.devpost.com/)

截止：2026 年 10 月 30 日 10:00（太平洋时间），北京时间 10 月 31 日 01:00。

开发只用官方额度，不要自己充值。两笔额度加起来约 50 美元，另外注册通常还有 1 美元试用额度。余额还是正数时，银行卡不会被扣。

按顺序做。每一步做完再做下一步。

## 1. 领第一笔 25 美元

打开 [比赛资源页](https://nebiusglobalaihackathon.devpost.com/resources)，找到 **Token Factory Credits** 第 1 条，点 **this form**。

- 激活码填 `NEBIUS-DEVPOST-GLOBAL26`
- 邮箱填能收到信的地址，学校邮箱优先
- 提交后看收件箱和垃圾箱

这张表只是申请额度，不会马上给出 API 密钥。

## 2. 领第二笔 25 美元

在 Devpost 比赛页的待办里点 **Signup for the Nebius Builder Program for credits**，或直接打开 [Nebius Builder Program](https://dev.nebius.com/builders)。

- 用第 1 步同一个邮箱注册
- 去邮箱点验证链接
- 进去之后领取 **Token Factory** 的 25 美元
- 页面上的 Tavily、Academy 先不用管
- 如果表单拒绝 `gmail.com`，换学校邮箱再交一次

## 3. 开通 Token Factory

打开 [https://tokenfactory.nebius.com](https://tokenfactory.nebius.com)，用 Google 或 GitHub 登录。不要用 Devpost 账号。

登录后会被送到账单页。选 **Individual（个人）**，国家选 **China**。

- 列表里有中国：绑一张 Visa 或 Mastercard。这一步是验证，不是充值。不要点任何带金额的 **Top up**。卡里可以没有钱，验证通过即可。
- 列表里没有中国，或卡一直被拒：停在这里，去做第 4 步。不要改选别的国家。

## 4. 被拦住就找主办方

打开 [Discord 邀请](https://discord.com/invite/eXYTGhgnhK)。

链接失效时，到这个帖子下回复，赛务 Janet 会换新链接：[中国参赛者开通被拦](https://nebiusglobalaihackathon.devpost.com/forum_topics/45402-token-factory-onboarding-blocked-for-china-based-participant)。

进 Discord 后找 Nebius 的帮助频道，贴下面这段英文。把两处邮箱换成自己的。不要在 Discord 里发银行卡号或 API 密钥。

```text
I am a student in mainland China, registered on Devpost for the Nebius x NVIDIA Global AI Hackathon.

I submitted the Token Factory credits form with code NEBIUS-DEVPOST-GLOBAL26 and joined the Nebius Builder Program. I need the promotional credits only. I will not top up with my own money.

Token Factory sends me to Billing Details. China is not in the country list, so I cannot reach Balance, redeem a promo code, or create an API key.

Please manually enable Token Factory for my account, or tell me the approved way to redeem the hackathon credits. I will not select another country.

Devpost email: （你的邮箱）
Token Factory login email: （登录用的 Google 或 GitHub 邮箱）
```

## 5. 进了控制台再兑换、建密钥

右上角能看到余额，才算开通。

1. 点余额，选 **Top up**，再选 **With promo code**。
2. 先填邮件里的兑换码。没有邮件，就试 `NEBIUS-DEVPOST-GLOBAL26`。Builder Program 如果另给了一串码，再兑一次。
3. 打开 **Transactions**，确认余额增加。
4. 打开 **API keys**，点 **Create API key**，立刻复制。这把密钥只显示一次。

密钥只放在本机 `rag/.env`，不要放进仓库，也不要贴到聊天或 Discord。

接口地址：

```text
https://api.tokenfactory.nebius.com/v1/
```

## 做到哪一步算完成

同时满足这三件，就可以改项目里的模型调用：

- 能留在 [tokenfactory.nebius.com](https://tokenfactory.nebius.com) 控制台里
- 右上角余额大于 0
- **API keys** 里已经创建出密钥
