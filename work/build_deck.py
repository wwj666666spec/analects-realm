# -*- coding: utf-8 -*-
"""生成《孔子之境 · 智启论语》课程汇报 PPT。"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_LINE_DASH_STYLE

from deck_kit import (  # noqa: E402
    SW, SH, E, KAI, SONG, HEI,
    PAPER, PAPER_TOP, PAPER_DEEP, CARD, INK, INK_SOFT, MUTED, FAINT, SEAL, SEAL_LT,
    JADE, JADE_LT, GOLD, LINE, WATER,
    blank, frame, head, watermark, text, card, chip, placeholder, grid, ribbon, flow,
    rect, hline, vline, shape_text, gradient, no_shadow, cur_page,
)
from pptx.dml.color import RGBColor  # noqa: E402

TOTAL = 30
WHITE = RGBColor(0xFF, 0xF8, 0xEE)


def labeled(label, body, label_color=SEAL):
    """返回两段式条目：小标 + 正文。调用方拼进 text(items=...)。"""
    return [
        {"t": label, "s": 11, "c": label_color, "f": KAI, "b": True, "sa": 3},
        {"t": body, "s": 11.4, "c": INK_SOFT, "f": HEI, "ls": 1.36, "sa": 10},
    ]


# ---------------------------------------------------------------- 章封面
def chapter(prs, num, title, en, desc, keywords, glyph):
    """章节封面页：大号章序印 + 章名 + 一句话导读 + 关键词。"""
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "")
    # 右侧巨型幽灵字
    watermark(s, glyph, x=9.72, y=1.02, size=210)
    # 左侧装饰竖线
    vline(s, 1.24, 1.98, 3.42, color=RGBColor(0xDD, 0xD0, 0xB6), lw=2.5)

    # 章序大印
    sq = rect(s, 1.54, 1.98, 1.40, 1.40, fill=SEAL,
              shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06)
    shape_text(sq, [{"t": num, "s": 60, "c": WHITE, "f": KAI, "b": True}], margins=0.0)

    # 英文小标 + 章名
    text(s, 3.28, 2.00, 8.2, 0.30,
         [{"t": en, "s": 12, "c": GOLD, "f": HEI}])
    text(s, 3.24, 2.30, 8.4, 1.06,
         [{"t": title, "s": 42, "c": INK, "f": KAI, "b": True}])

    # 分隔线 + 导读
    hline(s, 1.58, 3.86, 10.9, color=RGBColor(0xE0, 0xD4, 0xBB), lw=1.0)
    text(s, 1.58, 4.02, 9.4, 0.62,
         [{"t": desc, "s": 15.5, "c": INK_SOFT, "f": HEI, "ls": 1.5}])

    # 关键词
    cx = 1.58
    for k in keywords:
        w = 0.20 * len(k) + 0.60
        chip(s, cx, 5.06, w, 0.50, k, color=JADE, size=12.5, font=KAI, bold=True)
        cx += w + 0.22
    return s


def c1(prs):
    return chapter(prs, "壹", "缘起与定位", "CHAPTER ONE · 第一章",
                   "这个想法从哪来，做出来给谁用",
                   ["灵感来源", "学习痛点", "项目定位", "目标用户", "核心路径"], "源")


def c2(prs):
    return chapter(prs, "贰", "功能全景", "CHAPTER TWO · 第二章",
                   "四个入口，串起一条完整的使用流程",
                   ["首页", "书库阅读", "智能问答", "人物对话", "创作生成"], "器")


def c3(prs):
    return chapter(prs, "叁", "技术实现", "CHAPTER THREE · 第三章",
                   "知识库放在本地，生成交给云端",
                   ["总体架构", "技术选型", "知识库构建", "生成流程", "设计原则"], "技")


def c4(prs):
    return chapter(prs, "肆", "边界与演进", "CHAPTER FOUR · 第四章",
                   "现在还不完善的地方，以及接下来怎么改",
                   ["现有不足", "后续计划"], "界")


def c5(prs):
    return chapter(prs, "伍", "现场演示", "CHAPTER FIVE · 第五章",
                   "用八到十二分钟，演示一遍完整流程",
                   ["演示流程", "时间安排"], "演")


# ---------------------------------------------------------------- 01 封面
def s01(prs):
    s = blank(prs)
    watermark(s, "學", x=10.15, y=1.05, size=120)
    seal = rect(s, 11.35, 1.05, 1.15, 1.15, fill=SEAL, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
                radius=0.05)
    shape_text(seal, [{"t": "論語", "s": 20, "c": WHITE, "f": KAI, "b": True, "sa": 2}], margins=0.04)

    text(s, 1.05, 1.20, 8.0, 0.34,
         [{"t": "《人工智能+X》课程作业汇报", "s": 12, "c": GOLD, "f": HEI}])
    text(s, 1.05, 1.62, 10.0, 1.0,
         [{"t": "孔子之境 · 智启论语", "s": 42, "c": INK, "f": KAI, "b": True}])
    hline(s, 1.10, 2.82, 3.6, color=SEAL, lw=2.0)
    text(s, 1.10, 2.98, 9.5, 0.4,
         [{"t": "一站式《论语》沉浸式学习与创作平台", "s": 17, "c": INK_SOFT, "f": HEI}])

    words = ["读典籍", "问疑惑", "听群言", "立风骨"]
    cx = 1.08
    for i, w in enumerate(words):
        c = chip(s, cx, 3.72, 1.32, 0.46, w, fill=RGBColor(0xF6, 0xF0, 0xE2),
                 color=JADE, size=12.5, font=KAI, bold=True)
        cx += 1.48

    vline(s, 1.10, 4.62, 1.35, color=RGBColor(0xDD, 0xD0, 0xB6), lw=1.0)
    text(s, 1.30, 4.60, 9.0, 1.4, [
        {"t": "汇报小组：深藏blue", "s": 13, "c": INK, "f": HEI, "b": True, "sa": 7},
        {"t": "小组成员：张馨文、善文玲", "s": 12.5, "c": INK_SOFT, "f": HEI, "sa": 7},
        {"t": "汇报日期：2026 年 10 月 13 日", "s": 12.5, "c": MUTED, "f": HEI},
    ])
    return s


# ---------------------------------------------------------------- 02 目录
def s02(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "CONTENTS", seal_text="")
    watermark(s, "目", x=11.6, y=4.5, size=130)
    text(s, 1.05, 0.62, 8.0, 0.6,
         [{"t": "目录", "s": 27, "c": INK, "f": KAI, "b": True}])
    hline(s, 1.10, 1.30, 11.3, color=RGBColor(0xE0, 0xD4, 0xBB), lw=1.0)

    items = [
        ("壹", "缘起与定位", "这个想法从哪来，做出来给谁用"),
        ("贰", "功能全景", "四个入口，串起一条完整的使用流程"),
        ("叁", "技术实现", "知识库放在本地，生成交给云端"),
        ("肆", "边界与演进", "现在还不完善的地方，以及接下来怎么改"),
        ("伍", "现场演示", "用八到十二分钟，演示一遍完整流程"),
    ]
    y = 1.72
    for num, title, desc in items:
        text(s, 1.10, y, 1.0, 0.6,
             [{"t": num, "s": 26, "c": SEAL, "f": KAI, "b": True}])
        text(s, 2.20, y + 0.03, 4.0, 0.4,
             [{"t": title, "s": 17.5, "c": INK, "f": KAI, "b": True}])
        text(s, 5.30, y + 0.13, 7.1, 0.36,
             [{"t": desc, "s": 12.5, "c": MUTED, "f": HEI}])
        hline(s, 2.20, y + 0.72, 10.2, color=RGBColor(0xE6, 0xDC, 0xC6), lw=0.75)
        y += 1.02
    return s


# ---------------------------------------------------------------- 03 缘起
def s03(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "壹 · 缘起与定位")
    top = head(s, "缘起：一个会说话的孔子，能带来什么",
               sub="灵感来自济南发布的 9.28 米巨型 AI 机器人孔子互动叙事作品《子曰》")
    block = []
    block += labeled("背景", "《子曰》让观众不再只是看展板、听讲解，而是能直接和孔子对话。"
                            "它说明传统文化换个讲法，照样有人愿意看。")
    block += labeled("启发一", "孔子不一定只站在博物馆里当塑像，也可以是一个随时能聊两句的角色。")
    block += labeled("启发二", "真正让人沉浸的是场景和对话；光把古文重新排一遍版，达不到这个效果。")
    block += labeled("启发三", "互动做得再好看，也得有典籍依据，不然很容易变成戏说。")
    block += labeled("我们的判断", "《子曰》是一次性的现场体验，我们想把它变成随手就能打开的网页；"
                                "而且不只是看看，还能顺手做点自己的东西。", label_color=JADE)
    text(s, 0.95, top + 0.10, 6.35, 4.6, block)

    placeholder(s, 7.65, top + 0.10, 4.80, 4.10, "图片位 · 可选",
                "《子曰》装置或相关报道截图",
                "此页为背景铺垫，图片非必需。\n若使用，建议放济南《子曰》\nAI 机器人孔子的现场照片，\n"
                "或 1 张相关报道截图。", slot="建议尺寸 16:9，横图，不放也无妨")
    return s


# ---------------------------------------------------------------- 04 痛点
def s04(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "壹 · 缘起与定位")
    top = head(s, "今天学《论语》，难在哪里",
               sub="从学习者、传播者、内容本身三侧看，问题各不相同")
    cards = [
        ("学习者一侧", SEAL, [
            "入门门槛高：字词、章句、人物、篇次分散在多本书里。",
            "读完用不上：情绪、人际、学习习惯找不到对应章句。",
            "看不到争论：知道孔子讲仁，却听不到孔门内部怎么辩同一件事。",
            "精读一章要来回翻几本书，很多人读到一半就停了。",
        ]),
        ("传播一侧", JADE, [
            "展板、电子书、剪辑视频留不住人，缺乏「再来一次」的理由。",
            "要么完全娱乐，出处混乱；要么一味训诂，把人挡在门外。",
            "静态展示多，能真正上手交互、又能留下成果的少。",
            "讲解多靠讲解员现场发挥，讲完就散了，留不下东西。",
        ]),
        ("内容一侧", GOLD, [
            "大模型容易编造「孔子语录」，把注疏说成原文。",
            "原文、注疏、礼书、史传混为一谈，出处经不起核对。",
            "缺少分层知识库，回答看似流利，实际无从追溯。",
            "后儒的解释和孔子原话常常摆在同一层，读的人分不清。",
        ]),
    ]
    x = 0.95
    for title, accent, lines in cards:
        card(s, x, top + 0.08, 3.60, 3.55, title, lines, accent=accent, title_size=14.5, size=11.6)
        x += 3.95
    ribbon(s, 0.95, top + 3.88, 11.50, 0.95, [
        {"t": "我们的回答", "s": 11, "c": GOLD, "f": KAI, "b": True, "sa": 4},
        {"t": "用查得到出处的检索来约束生成；把「读懂原文 / 看待自己 / 怎么去做」"
              "分成三种问法；再用孔门群像，代替只有一个孔子。", "s": 12.5, "c": WHITE, "f": HEI},
    ], fill=JADE)
    return s


# ---------------------------------------------------------------- 05 定位
def s05(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "壹 · 缘起与定位")
    top = head(s, "项目定位：一句话说清楚")
    ribbon(s, 0.95, top + 0.02, 11.50, 0.95, [
        {"t": "读完一本《论语》，还能接着提问、和孔门聊两句，"
              "最后留下一段属于自己的国风短片。", "s": 15.5, "c": WHITE, "f": KAI, "b": True},
    ], fill=SEAL)
    rows = [
        ["能力", "使用者得到什么"],
        ["典藏书库", "竖排卷轴式阅读：原典、注疏、礼书与史传，按五类上架"],
        ["智能问答", "治学、修心、修身三种用法，回答附「检索依据」"],
        ["先贤对话", "与孔子及十六位孔门弟子围坐群聊，或一对一私聊"],
        ["风骨创作", "五德人设、古风形象、专属音色与诵读短视频"],
        ["个人中心", "账号登录，以及本机的问答、对话与收藏记录"],
    ]
    grid(s, 0.95, top + 1.20, 11.50, [2.1, 7.9], rows, row_h=0.66,
         aligns=[PP_ALIGN.CENTER, PP_ALIGN.LEFT], size=12, head_size=12.5)
    return s


# ---------------------------------------------------------------- 06 用户与场景
def s06(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "壹 · 缘起与定位")
    top = head(s, "给谁用，用在什么场合")
    rows = [
        ["目标群体", "他们带着什么进来", "系统怎么接住"],
        ["青少年与研学团队", "课堂任务、第一次接触《论语》", "今日一句、书库翻阅、治学答疑、先贤群聊"],
        ["国学爱好者与自修者", "想对照注疏，追问一句到底怎么讲", "四层书库 + 治学模式 + 出处卡片"],
        ["有现实困扰的读者", "比较、焦虑、冲突、拖延", "修心 / 修身模式：先理解处境，再谨慎引用"],
        ["教师与讲解员", "需要可以引用、可以展示的材料", "检索依据直接给出篇目与摘录"],
    ]
    grid(s, 0.95, top + 0.02, 11.50, [2.3, 3.7, 5.0], rows, row_h=0.70,
         aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.LEFT], size=11.4, head_size=12)

    y = top + 3.62
    text(s, 0.95, y, 3.0, 0.34,
         [{"t": "六类使用场合", "s": 12.5, "c": SEAL, "f": KAI, "b": True}])
    scenes = ["课前导入", "精读课", "讨论课", "独处自修", "研学成果输出", "展陈互动"]
    cw = (11.50 - 5 * 0.16) / 6
    cx = 0.95
    for sc in scenes:
        chip(s, cx, y + 0.42, cw, 0.48, sc, color=JADE, size=11.5, font=KAI)
        cx += cw + 0.16
    text(s, 0.95, y + 1.10, 11.5, 0.5,
         [{"t": "站点不强制登录：不登录也能读书、提问、围坐；注册主要是为了记住身份和记录。",
           "s": 11.2, "c": MUTED, "f": HEI}])
    return s


# ---------------------------------------------------------------- 07 主路径
def s07(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "壹 · 缘起与定位")
    top = head(s, "一条主路径：读 → 问 → 听 → 立",
               sub="四个入口都放在首页，从哪个进去都行；走完一遍，就是一次完整的学习过程")
    flow(s, top + 0.30, ["首页 · 今日论语", "典藏书库", "智能问答", "先贤对话", "风骨创作", "个人中心"],
         h=0.76, size=11.5)
    card(s, 0.95, top + 1.35, 5.55, 1.85, "书库是「翻原文」", [
        "竖排自右向左，按篇翻页，看到的始终是典籍本身。",
        "正文直接读本地 Markdown，不经过向量库。",
    ], accent=JADE, title_size=13)
    card(s, 6.90, top + 1.35, 5.55, 1.85, "问答是「查相关段落」", [
        "同一个问题，先从三十余种典籍里检索最相关的几块材料。",
        "两条路共用同一批文本，运行方式完全不同。",
    ], accent=SEAL, title_size=13)
    ribbon(s, 0.95, top + 3.40, 11.50, 0.80, [
        {"t": "四个环节用的是同一批典籍、同一套界面，不用在几个工具之间来回切换。",
         "s": 12.2, "c": WHITE, "f": HEI},
    ], fill=JADE)
    return s


# ---------------------------------------------------------------- 08 功能全景
def s08(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "贰 · 功能全景")
    top = head(s, "功能全景：五个模块，共用一套知识库")
    tops = [
        ("典藏书库", "31", "种", "原典、注疏、礼书、史传、家语五类上架，竖排卷轴精读，可按书名与注家筛选。" , SEAL),
        ("智能问答", "3", "种用法", "同一个知识库，治学回答怎么理解，修心回答怎么看自己，修身回答怎么去做。", JADE),
        ("先贤对话", "17", "位先贤", "孔子与十六位弟子各有 SKILL 人设，可围坐群聊，也可与同门一对一私聊。", GOLD),
    ]
    x = 0.95
    for title, num, unit, desc, accent in tops:
        box = card(s, x, top + 0.05, 3.60, 2.25, title, [desc], accent=accent,
                   title_size=14.5, size=11.4)
        text(s, x + 0.26, top + 1.42, 1.6, 0.6,
             [{"t": num, "s": 32, "c": accent, "f": KAI, "b": True}])
        text(s, x + 1.32, top + 1.68, 2.0, 0.4,
             [{"t": unit, "s": 11, "c": MUTED, "f": HEI}])
        x += 3.95
    bots = [
        ("风骨创作", "5", "步向导",
         "测 → 卡 → 形 → 声 → 片：先做性格测试生成人设，再依次生成形象、音色和诵读短片。生成失败会自动退回模板，演示不会中断。", SEAL),
        ("个人中心", "1", "套记录",
         "注册登录、问答与对话统计、本地收藏；清空只删本机痕迹，不动账号。", JADE),
    ]
    x = 0.95
    for title, num, unit, desc, accent in bots:
        rect(s, x, top + 2.45, 5.55, 1.90, fill=CARD, line=RGBColor(0xE2, 0xD7, 0xBF),
             shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.05)
        rect(s, x, top + 2.59, 0.055, 1.62, fill=accent)
        text(s, x + 0.24, top + 2.62, 3.55, 1.4, [
            {"t": title, "s": 14.5, "c": INK, "f": KAI, "b": True, "sa": 8},
            {"t": desc, "s": 11.6, "c": INK_SOFT, "f": HEI, "ls": 1.36},
        ])
        text(s, x + 4.15, top + 2.62, 1.2, 0.7,
             [{"t": num, "s": 28, "c": accent, "f": KAI, "b": True, "al": PP_ALIGN.RIGHT}])
        text(s, x + 4.15, top + 3.36, 1.2, 0.34,
             [{"t": unit, "s": 10.6, "c": MUTED, "f": HEI, "al": PP_ALIGN.RIGHT}])
        x += 5.95
    return s


# ---------------------------------------------------------------- 09 首页
def s09(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "贰 · 功能全景")
    top = head(s, "首页：一句今日论语，四扇门")
    text(s, 0.95, top + 0.05, 3.55, 4.5, [
        {"t": "界面气质", "s": 12.2, "c": SEAL, "f": KAI, "b": True, "sa": 5},
        {"t": "纸色底、墨色字、印章红点缀。",
         "s": 11.8, "c": INK_SOFT, "f": HEI, "ls": 1.4, "sa": 4},
        {"t": "正文用衬线字体。",
         "s": 11.8, "c": INK_SOFT, "f": HEI, "ls": 1.4, "sa": 4},
        {"t": "整体像一本摊开的书，不像一个控制台。",
         "s": 11.8, "c": INK_SOFT, "f": HEI, "ls": 1.4, "sa": 18},
        {"t": "今日论语", "s": 12.2, "c": SEAL, "f": KAI, "b": True, "sa": 5},
        {"t": "按日期轮换一句原文，附白话理解；可以抄录、可以就此提问，也可以请夫子说。",
         "s": 11.8, "c": INK_SOFT, "f": HEI, "ls": 1.4, "sa": 18},
        {"t": "四个入口", "s": 12.2, "c": SEAL, "f": KAI, "b": True, "sa": 5},
        {"t": "典藏书库、智能问答、先贤对话、个人创作并排放，后面要讲的功能都从这里进。",
         "s": 11.8, "c": INK_SOFT, "f": HEI, "ls": 1.4},
    ])
    placeholder(s, 4.95, top - 0.05, 7.50, 4.65, "图片位 01",
                "首页整屏截图",
                "建议截取内容：\n"
                "① 顶部标题「孔子之境 · 智启论语」与副标题；\n"
                "② 「今日论语」卡片（原文、出处、白话理解、三个按钮）；\n"
                "③ 四个功能入口条（典藏书库 / 智能问答 / 先贤对话 / 个人创作）。\n"
                "整屏截图即可，不需要裁切。",
                slot="浏览器 1920×1080 全屏截图，深色像素可另存为 PNG")
    return s


# ---------------------------------------------------------------- 10 书库
def s10(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "贰 · 功能全景")
    top = head(s, "典藏书库：把三十余种典籍摆上书架")
    chips = [("31", "种典籍"), ("约 825", "万字正文"), ("4", "层材料")]
    cx = 0.95
    for num, unit in chips:
        box = rect(s, cx, top + 0.02, 1.80, 0.72, fill=CARD, line=RGBColor(0xE2, 0xD7, 0xBF),
                   shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.1)
        text(s, cx + 0.16, top + 0.12, 1.5, 0.55, [
            {"t": num, "s": 19, "c": SEAL, "f": KAI, "b": True, "sa": 0},
        ])
        text(s, cx + 0.16, top + 0.42, 1.5, 0.3,
             [{"t": unit, "s": 10.4, "c": MUTED, "f": HEI}])
        cx += 1.95

    text(s, 0.95, top + 0.98, 5.9, 3.4, [
        {"t": "上架分类（按文件名判定）", "s": 12.2, "c": JADE, "f": KAI, "b": True, "sa": 7},
        {"t": "论语 ｜ 论语.md 归为原典", "s": 11.4, "c": INK_SOFT, "f": HEI, "sa": 5},
        {"t": "注疏 ｜ 其余以「论语」开头，如集注、注疏、集释", "s": 11.4, "c": INK_SOFT, "f": HEI, "sa": 5},
        {"t": "礼记 ｜ 文件名含「礼记」，如礼记正义、礼记集说", "s": 11.4, "c": INK_SOFT, "f": HEI, "sa": 5},
        {"t": "史传 ｜ 史记孔子世家、仲尼弟子列传", "s": 11.4, "c": INK_SOFT, "f": HEI, "sa": 5},
        {"t": "家语 ｜ 孔子家语、孔子集语（入库检索时并入史传层）", "s": 11.4, "c": INK_SOFT,
         "f": HEI, "sa": 14},
        {"t": "阅读方式", "s": 12.2, "c": JADE, "f": KAI, "b": True, "sa": 7},
        {"t": "竖排自右向左、左右翻篇；按 Markdown 二级标题分节；"
              "单节超过约 8000 字只显示开头，保证翻页流畅。", "s": 11.4, "c": INK_SOFT,
         "f": HEI, "ls": 1.4},
    ])
    placeholder(s, 7.15, top + 0.02, 5.30, 2.10, "图片位 02", "书架页截图",
                "建议截取：书库整页，能看到五类书架标签\n与书脊卡片（如「論語」「注疏」「史傳」）。",
                slot="可截取整屏")
    placeholder(s, 7.15, top + 2.24, 5.30, 2.10, "图片位 03", "竖排阅读页截图",
                "建议截取：打开《论语》某一篇后的阅读界面，\n能看到竖排正文、翻篇按钮与「就此篇提问」。",
                slot="可截取整屏")
    return s


# ---------------------------------------------------------------- 11 三模式
def s11(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "贰 · 功能全景")
    top = head(s, "智能问答：一个知识库，三种用法")
    cards = [
        ("治学 Agent ｜ 怎么理解", SEAL, [
            ("面向", "字词、翻译、章句、人物、概念、篇际联系"),
            ("顺序", "原文与译文 → 关键词与语境 → 与仁、礼、君子的联系"),
            ("可演示", "「学而时习之」怎么解？「君子不器」是什么意思？"),
            ("边界", "多种注疏并存时分开讲差别，不合成唯一答案"),
        ]),
        ("修心 Agent ｜ 怎么看待自己", JADE, [
            ("面向", "情绪、比较、内耗、心里空落的时候"),
            ("顺序", "先理解处境 → 梳理困扰 → 引 1 到 2 条材料 → 给一个小行动"),
            ("可演示", "总觉得自己不如别人；最近很焦虑，静不下来"),
            ("边界", "不开口就训人；明确不是心理医生，危机情况先引导现实求助"),
        ]),
        ("修身 Agent ｜ 怎么去做", GOLD, [
            ("面向", "冲突、沟通、拖延、家庭与待人接物"),
            ("顺序", "判断核心 → 一条最相关的原则 → 2 到 4 步做法 → 一句今天能说的话"),
            ("可演示", "和同事起了争执怎么收场；总是拖延，怎么自律"),
            ("边界", "给能落地的步骤，不停留在讲道理"),
        ]),
    ]
    x = 0.95
    for title, accent, rows in cards:
        box = rect(s, x, top + 0.05, 3.60, 3.85, fill=CARD, line=RGBColor(0xE2, 0xD7, 0xBF),
                   shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.05)
        rect(s, x, top + 0.19, 0.055, 3.57, fill=accent)
        items = [{"t": title, "s": 13.5, "c": INK, "f": KAI, "b": True, "sa": 9}]
        for lb, body in rows:
            items.append({"t": lb, "s": 10.2, "c": accent, "f": KAI, "b": True, "sa": 2})
            items.append({"t": body, "s": 11.1, "c": INK_SOFT, "f": HEI, "ls": 1.36, "sa": 9})
        text(s, x + 0.24, top + 0.16, 3.20, 3.6, items)
        x += 3.95
    ribbon(s, 0.95, top + 4.10, 11.50, 1.00, [
        {"t": "三种模式共用全部四层材料，区别在提示词与回答顺序，不在「能看哪些书」。",
         "s": 12.4, "c": WHITE, "f": HEI, "sa": 5},
        {"t": "共同底线：不编造出处；不用扮演古人的口吻；不把用户困境归因于「修养不够」。",
         "s": 11.6, "c": RGBColor(0xE8, 0xDE, 0xC8), "f": HEI},
    ], fill=JADE)
    return s


# ---------------------------------------------------------------- 12 问答示例
def s12(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "贰 · 功能全景")
    top = head(s, "问答现场：回答长什么样")
    placeholder(s, 0.95, top + 0.02, 5.55, 4.48, "图片位 04",
                "治学问答截图",
                "建议截取：提问「『学而时习之』怎么解？」后的完整回答，\n"
                "重点拍到回答下方的「检索依据」一行，\n"
                "例如「原文 《论语》学而第一」。",
                slot="含提问气泡 + 回答 + 检索依据")
    placeholder(s, 6.90, top + 0.02, 5.55, 4.48, "图片位 05",
                "修心 / 修身问答截图",
                "建议截取：提问「总觉得自己不如别人」后的回答，\n"
                "能看出「先理解处境、再引材料、最后给小行动」的顺序；\n"
                "左栏同时能看到治学 / 修心 / 修身三个模式。",
                slot="含三种模式的左栏切换")
    text(s, 0.95, top + 4.62, 11.5, 0.4,
         [{"t": "回答是一边生成一边显示的：先给出检索依据，再一个字一个字地写出正文；"
               "像问候、道谢、告别这类话，后端直接回应，不检索、也不引古文。",
           "s": 11.4, "c": MUTED, "f": HEI}])
    return s


# ---------------------------------------------------------------- 13 先贤
def s13(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "贰 · 功能全景")
    top = head(s, "先贤对话：孔门十七人，各有各的性情",
               sub="每个人单独一份 SKILL.md：写清思想重心、说话节奏和说话禁忌；这样资料和生成逻辑就分开了")
    rows = [
        ("德行", "颜回 · 闵子骞 · 仲弓 · 曾参 · 曾点 · 樊迟 · 司马牛 · 高柴", JADE),
        ("政事", "子路 · 冉求", SEAL),
        ("言语", "子贡 · 宰予 · 子张 · 公西华", GOLD),
        ("文学", "子游 · 子夏", JADE_LT),
        ("总持", "孔子（每次围坐必到，并且先开口）", SEAL),
    ]
    y = top + 0.05
    for label, names, color in rows:
        lb = chip(s, 0.95, y, 1.05, 0.58, label, fill=color, color=WHITE, size=12.5, font=KAI, bold=True)
        rect(s, 2.12, y, 10.33, 0.58, fill=CARD, line=RGBColor(0xE2, 0xD7, 0xBF),
             shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.12)
        text(s, 2.40, y + 0.06, 9.8, 0.46,
             [{"t": names, "s": 12.8, "c": INK_SOFT, "f": HEI}], anchor=MSO_ANCHOR.MIDDLE)
        y += 0.72
    ribbon(s, 0.95, y + 0.12, 11.50, 1.18, [
        {"t": "为什么要写人设文件", "s": 11, "c": GOLD, "f": KAI, "b": True, "sa": 4},
        {"t": "没有约束的话，十七个人会变成一个腔调：都温和、都引同一句话。",
         "s": 11.9, "c": WHITE, "f": HEI, "sa": 4},
        {"t": "所以每个人单独写一份人设文件，例如注明「不要把子路写成只会冲动的粗人」。",
         "s": 11.9, "c": WHITE, "f": HEI},
    ], fill=JADE)
    return s


# ---------------------------------------------------------------- 14 围坐
def s14(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "贰 · 功能全景")
    top = head(s, "围坐与私聊：十七个人，十七种腔调")
    text(s, 0.95, top + 0.05, 6.35, 4.4, [
        {"t": "围坐的规则", "s": 13, "c": SEAL, "f": KAI, "b": True, "sa": 9},
        {"t": "孔子必到，而且先开口；其余同门随机，一场约 4 到 5 人发言。",
         "s": 11.7, "c": INK_SOFT, "f": HEI, "ls": 1.38, "bullet": "·", "sa": 9},
        {"t": "后说的人看得到前面的话，但不许「我赞同某某」，也不许重复同一层意思。",
         "s": 11.7, "c": INK_SOFT, "f": HEI, "ls": 1.38, "bullet": "·", "sa": 9},
        {"t": "篇幅按性格调整：子路短促，子贡、子张可以稍长，高柴话短。",
         "s": 11.7, "c": INK_SOFT, "f": HEI, "ls": 1.38, "bullet": "·", "sa": 9},
        {"t": "闲聊问候时，只有孔子简单回一句，不去查库；问正经问题才检索典籍。",
         "s": 11.7, "c": INK_SOFT, "f": HEI, "ls": 1.38, "bullet": "·", "sa": 15},
        {"t": "私聊", "s": 13, "c": SEAL, "f": KAI, "b": True, "sa": 9},
        {"t": "也可以单独点一位弟子对话，他会记得最近几轮聊过什么，适合把一个话题追下去。"
              "演示时建议选性格反差大的两位，例如子路与颜回。",
         "s": 11.7, "c": INK_SOFT, "f": HEI, "ls": 1.38},
    ])
    text(s, 7.60, top + 0.05, 4.85, 0.34,
         [{"t": "七段名场面（可一键回放原文对白）", "s": 12.2, "c": JADE, "f": KAI, "b": True}])
    scenes = ["各言尔志", "侍坐言志", "宰予昼寝", "樊迟学稼", "武城弦歌", "在陈绝粮", "子见南子"]
    for i, sc in enumerate(scenes):
        col, row = i % 3, i // 3
        chip(s, 7.60 + col * 1.63, top + 0.48 + row * 0.50, 1.53, 0.44, sc, size=11, font=KAI)
    placeholder(s, 7.60, top + 2.05, 4.85, 2.55, "图片位 06", "群聊与私聊截图",
                "建议放两张图并排或上下拼接：\n"
                "① 孔门三千群聊：能看到座位、多位先贤先后发言；\n"
                "② 与子路或颜回的私聊：能看到一对一对话。",
                slot="两张图可拼成一张")
    text(s, 0.95, top + 3.55, 6.35, 1.1, [
        {"t": "演示建议", "s": 12.2, "c": JADE, "f": KAI, "b": True, "sa": 5},
        {"t": "同一个问题先问治学 Agent，再丢进群聊。观众能直接看出「解释一句经典」"
              "和「孔门内部怎么争论」是两回事。", "s": 11.4, "c": INK_SOFT, "f": HEI, "ls": 1.38},
    ])
    return s


# ---------------------------------------------------------------- 15 风骨五步
def s15(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "贰 · 功能全景")
    top = head(s, "风骨创作：从性格测试到诵读短片", sub="五步向导，底部可以前进后退，中途退出也能接着做")
    steps = [
        ("壹", "性格测试", "八道题，覆盖学习态度、处事、情绪、社交、价值取向、生活态度、面对非议、志向格局。"),
        ("贰", "专属人设卡", "按主德、次德生成名号、座右铭、标签与约百字分析；座右铭出自《论语》并标注篇名。"),
        ("叁", "人设形象", "上传正面半身照，选择形象性别，生成古风定妆照，保留五官神态，不复制现代服装与背景。"),
        ("肆", "专属音色", "12 个 CosyVoice 预设音色可试听；也可上传 10 到 20 秒清晰人声，做音色克隆。"),
        ("伍", "诵读短片", "自己写一段话，或一键生成 150 到 180 字旁白，合成语音驱动形象口型，产出可预览、可下载的短片。"),
    ]
    x = 0.95
    bw = (11.50 - 4 * 0.22) / 5
    for num, title, desc in steps:
        rect(s, x, top + 0.10, bw, 2.60, fill=CARD, line=RGBColor(0xE2, 0xD7, 0xBF),
             shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.05)
        numbox = rect(s, x + 0.22, top + 0.28, 0.46, 0.46, fill=SEAL,
                      shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.2)
        shape_text(numbox, [{"t": num, "s": 13.5, "c": WHITE, "f": KAI, "b": True}], margins=0.0)
        text(s, x + 0.22, top + 0.88, bw - 0.44, 1.7, [
            {"t": title, "s": 13, "c": INK, "f": KAI, "b": True, "sa": 7},
            {"t": desc, "s": 10.8, "c": INK_SOFT, "f": HEI, "ls": 1.38},
        ])
        if x + bw < 12.4:
            text(s, x + bw, top + 0.10, 0.22, 2.60,
                 [{"t": "→", "s": 13, "c": GOLD, "f": HEI, "al": PP_ALIGN.CENTER}],
                 anchor=MSO_ANCHOR.MIDDLE)
        x += bw + 0.22
    ribbon(s, 0.95, top + 2.88, 11.50, 1.15, [
        {"t": "现场演示的几条经验", "s": 11, "c": GOLD, "f": KAI, "b": True, "sa": 5},
        {"t": "模型生成失败时会退回五德模板，演示不会中断；视频优先用 LivePortrait"
              "（动作幅度小，适合诵读），失败再退回悦动人像；成片一般要等几分钟，界面会分阶段提示进度。",
         "s": 11.9, "c": WHITE, "f": HEI},
    ], fill=JADE)
    return s


# ---------------------------------------------------------------- 16 创作成果
def s16(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "贰 · 功能全景")
    top = head(s, "创作成果：属于自己的形象和短片")
    placeholder(s, 0.95, top + 0.02, 3.60, 3.98, "图片位 07", "专属人设卡",
                "建议截取：人设卡界面，\n包含名号、座右铭（含篇名出处）、\n标签与五德画像条形图。",
                slot="竖版卡片，注意拍全座右铭")
    placeholder(s, 4.90, top + 0.02, 3.60, 3.98, "图片位 08", "古风形象",
                "建议截取：重绘前后的对照图\n（左边原照片、右边古风定妆照），\n最能说明「保留五官」这一点。",
                slot="两张图并排对照")
    placeholder(s, 8.85, top + 0.02, 3.60, 3.98, "图片位 09", "诵读短片",
                "建议截取：视频播放界面或成片首帧，\n旁边能看到音色选择与\n旁白文案。",
                slot="也可放 15 秒录屏")
    ribbon(s, 0.95, top + 4.18, 11.50, 0.90, [
        {"t": "重绘只参照你的五官，服装和背景按性别重新生成；脸还是你本人的脸，"
              "不会换上一张「标准古人脸」。", "s": 12.2, "c": WHITE, "f": HEI},
    ], fill=JADE)
    return s


# ---------------------------------------------------------------- 17 架构
def s17(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "叁 · 技术实现")
    top = head(s, "总体架构：检索在本地，生成在云端")

    def box(x, y, w, h, title, lines, accent):
        rect(s, x, y, w, h, fill=CARD, line=RGBColor(0xE2, 0xD7, 0xBF),
             shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.05)
        rect(s, x, y, w, 0.44, fill=accent)
        text(s, x + 0.20, y + 0.07, w - 0.4, 0.34,
             [{"t": title, "s": 12.5, "c": WHITE, "f": KAI, "b": True}])
        items = [{"t": t, "s": 11, "c": INK_SOFT, "f": HEI, "ls": 1.38, "sa": 5}
                 for t in lines]
        text(s, x + 0.20, y + 0.58, w - 0.4, h - 0.68, items)

    box(0.95, top + 0.05, 2.30, 3.30, "客户端", [
        "国风 SPA",
        "index.html",
        "app.js ｜ site.css",
        "零 Node 构建",
        "路径切换在前端完成",
        "纸色、墨色、印章红",
        "正文用衬线字体",
        "窄屏时隐藏左栏",
    ], SEAL)
    box(3.60, top + 0.05, 3.50, 3.30, "业务进程  FastAPI :8787", [
        "问答编排 · ask",
        "先贤对话 · sage",
        "风骨创作 · presence",
        "书库与阅读 · books",
        "账号 · auth",
        "问答与围坐走流式输出",
        "视频任务放后台轮询",
    ], JADE)
    box(7.45, top + 0.05, 5.00, 1.58, "云服务", [
        "DeepSeek Chat：意图路由、问答、先贤发言、人设与旁白",
        "阿里云百炼：CosyVoice 语音、人像重绘、LivePortrait / EMO",
    ], GOLD)
    box(7.45, top + 1.77, 5.00, 1.58, "本地数据面", [
        "Postgres 16 + pgvector :5434（篇、章、层与向量同库）",
        "Ollama 托管 bge-m3 :11434（1024 维嵌入）",
        "数据/ 典籍 Markdown ｜ rag/output 媒体缓存",
    ], JADE_LT)
    for ax, cap in ((3.28, "HTTP"), (7.12, "API")):
        text(s, ax, top + 1.32, 0.34, 0.4,
             [{"t": "→", "s": 15, "c": GOLD, "f": HEI, "al": PP_ALIGN.CENTER}])
        text(s, ax - 0.20, top + 1.00, 0.74, 0.3,
             [{"t": cap, "s": 8.5, "c": FAINT, "f": HEI, "al": PP_ALIGN.CENTER}])
    ribbon(s, 0.95, top + 3.55, 11.50, 1.05, [
        {"t": "设计原则", "s": 11, "c": GOLD, "f": KAI, "b": True, "sa": 4},
        {"t": "检索和元数据放在本地，生成和视频交给云端。上课用的机器只要显卡跑得动嵌入模型就行，"
              "不需要在本机部署大模型。数据库和嵌入模型都能随 Docker 卷一起导出。",
         "s": 11.9, "c": WHITE, "f": HEI},
    ], fill=JADE)
    return s


# ---------------------------------------------------------------- 18 技术选型
def s18(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "叁 · 技术实现")
    top = head(s, "技术选型：每一层为什么这么选")
    rows = [
        ["层级", "选用", "原因"],
        ["前端", "单页 HTML + ES Module + 一份 CSS", "零构建，发出去对方打开浏览器就能看"],
        ["后端", "Python 3.10+ / FastAPI / Uvicorn", "检索、文件与后台视频线程同进程，部署简单"],
        ["向量库", "PostgreSQL 16 + pgvector", "篇、章、层等结构化字段与向量存在同一个库"],
        ["全文检索", "tsvector + GIN 索引", "用来命中原句与短语，弥补向量对文言短句的不足"],
        ["嵌入模型", "Ollama 托管 bge-m3（1024 维）", "多语言、长文本友好，可随数据卷导出，现场不必拉模型"],
        ["对话模型", "DeepSeek Chat API", "中文与古文阐释较稳，接口兼容 Chat Completions"],
        ["多模态", "百炼 CosyVoice / 人像重绘 / LivePortrait", "语音、形象和数字人都在云端完成"],
        ["认证与编排", "HttpOnly Cookie + PBKDF2；Docker Compose", "演示够用，数据层和业务进程分开部署"],
    ]
    grid(s, 0.95, top + 0.02, 11.50, [1.5, 4.4, 5.6], rows, row_h=[0.48] + [0.58] * 8,
         aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.LEFT], size=11, head_size=11.5)
    return s


# ---------------------------------------------------------------- 19 知识工程
def s19(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "叁 · 技术实现")
    top = head(s, "知识工程：按文献结构切块，再混合检索")
    card(s, 0.95, top + 0.05, 5.55, 3.30, "入库前，按文献结构切块", [
        "原文：一块一章，带篇名与章号，如「学而第一 · 1.1」。",
        "注疏：按篇切开，用原文开头约八个汉字对齐章号；"
        "异体字做折叠（於 / 于、说 / 悦），只影响对齐，不改写正文。",
        "礼与史传：按二级标题切，超过约 1200 字再按句号细分为子块。",
        "每块都带完整锚点：书名 ｜ 篇 ｜ 章 ｜ part ｜ 源文件。",
    ], accent=JADE, title_size=13.5, size=11.4)
    card(s, 6.90, top + 0.05, 5.55, 3.30, "检索不是纯向量，七步叠加", [
        "① 短语全文（权重最高）② 子串包含：适合粘贴原句",
        "③ 向量近邻：适合「总爱和别人比较」这类白话",
        "④ RRF 融合三路排序　⑤ 章号补全：命中原文后并入同章注疏",
        "⑥ 业务加分：正文含原句、章号精确、原典层优先",
        "⑦ 每本书最多取两块，避免被同一个注本占满",
    ], accent=SEAL, title_size=13.5, size=11.4)
    ribbon(s, 0.95, top + 3.80, 11.50, 1.20, [
        {"t": "为什么值得这么做", "s": 11, "c": GOLD, "f": KAI, "b": True, "sa": 4},
        {"t": "用户既会粘贴原句，也会用大白话提问。只靠向量，容易漏掉原文里有据可查的句子；"
              "只靠关键词，又接不住口语化的说法。",
         "s": 11.9, "c": WHITE, "f": HEI, "sa": 4},
        {"t": "两种一起用，才既查得准，又问得顺。", "s": 11.9, "c": WHITE, "f": HEI},
    ], fill=JADE)
    return s


# ---------------------------------------------------------------- 20 生成链路
def s20(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "叁 · 技术实现")
    top = head(s, "三条生成流程与关键接口")
    rows = [
        ("问答", SEAL, "输入 → 判断是寒暄还是提问 → 寒暄直接回应（不检索），提问走 search → "
                       "拼接「模式 + 问题 + 检索内容」→ DeepSeek 生成 → 回答 + 出处"),
        ("先贤", JADE, "输入 → search 取材料（块截断约 700 字）→ 排座 → "
                       "按人设依次生成（带入已发言上下文）→ 围坐或私聊回答"),
        ("风骨", GOLD, "测试计分 → DeepSeek 出人设 JSON → 照片风格重绘 → 选音色或克隆 → "
                       "生成旁白 → 合成语音 → LivePortrait 驱动 → 后台轮询取成片"),
    ]
    y = top + 0.05
    for label, color, chain in rows:
        chip(s, 0.95, y, 1.20, 0.78, label, fill=color, color=WHITE, size=13, font=KAI, bold=True)
        rect(s, 2.28, y, 10.17, 0.78, fill=CARD, line=RGBColor(0xE2, 0xD7, 0xBF),
             shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.1)
        text(s, 2.52, y + 0.06, 9.6, 0.66,
             [{"t": chain, "s": 11.2, "c": INK_SOFT, "f": HEI, "ls": 1.34}],
             anchor=MSO_ANCHOR.MIDDLE)
        y += 0.96
    text(s, 0.95, y + 0.10, 11.5, 0.3,
         [{"t": "关键接口", "s": 12.2, "c": SEAL, "f": KAI, "b": True}])
    rect(s, 0.95, y + 0.50, 11.50, 1.15, fill=RGBColor(0xF4, 0xEE, 0xDF),
         line=RGBColor(0xE2, 0xD7, 0xBF), shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06)
    text(s, 1.20, y + 0.62, 11.0, 1.0, [
        {"t": "问答　/api/ask　流式 /api/ask/stream", "s": 11, "c": INK_SOFT, "f": HEI, "sa": 5},
        {"t": "先贤　/api/sages　/api/seat　/api/round　/api/talk", "s": 11, "c": INK_SOFT,
         "f": HEI, "sa": 4},
        {"t": "风骨　/api/presence/persona · figure · voice · script · video　｜　"
              "书库　/api/books · book · book/text　｜　账号　/api/register · login · logout · me",
         "s": 11, "c": INK_SOFT, "f": HEI},
    ])
    return s


# ---------------------------------------------------------------- 21 设计原则
def s21(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "叁 · 技术实现")
    top = head(s, "设计原则与内容伦理", sub="技术决定我们能做什么，原则决定做出来之后靠不靠谱")
    items = [
        ("准确性优先于古雅", "宁可写「现有资料不足以确认」，也不编造章句。"),
        ("典籍是资源，不是戒尺", "不把焦虑、失败、冲突归因于「修养不够」。"),
        ("分层引用", "原文、后儒注疏、史传与今人推演必须分开说。"),
        ("角色与助手分开", "治学 / 修心 / 修身明确不是孔门扮演。"),
        ("修心有边界", "不是医疗；出现自伤或伤害他人的表达，先引导现实求助。"),
        ("创作保留人的面孔", "重绘强调五官一致，不做「标准古人脸」。"),
        ("密钥与隐私", "密钥只放本机环境文件；上传媒体限制格式与体积。"),
    ]
    left = items[:4]
    right = items[4:]
    y = top + 0.05
    for title, desc in left:
        card(s, 0.95, y, 5.55, 1.08, title, [desc], accent=SEAL, title_size=12.8, size=11.2)
        y += 1.20
    y = top + 0.05
    for title, desc in right:
        card(s, 6.90, y, 5.55, 1.08, title, [desc], accent=JADE, title_size=12.8, size=11.2)
        y += 1.20
    text(s, 6.90, y + 0.10, 5.55, 0.8, [
        {"t": "这七条不只是在文档里写着：语气靠提示词约束，引用和回退靠代码约束。",
         "s": 11.4, "c": MUTED, "f": HEI, "ls": 1.4},
    ])
    return s


# ---------------------------------------------------------------- 22 局限
def s22(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "肆 · 边界与演进")
    top = head(s, "现状边界：我们清楚它还不完善",
               sub="以下都是当前实现里真实存在的问题，不做美化")
    cards = [
        ("数据与账号", SEAL, [
            "问答、先贤、收藏都存在浏览器本地，换设备就丢。",
            "问答偏单轮，适合一问一答，不适合长程导师式追问。",
        ]),
        ("成本与依赖", JADE, [
            "围坐要依次生成多位先贤，耗时与调用次数明显高于单次问答。",
            "风骨依赖外网与额度，成片常需数分钟，人脸检测对照片质量敏感。",
        ]),
        ("工程细节", GOLD, [
            "注疏对齐是启发式的，遇到异文或极端版式可能漏掉章号。",
            "服务没有热重载，改了 Python 代码必须手动重启。",
        ]),
        ("质量保障", JADE_LT, [
            "还没有系统化评测集：命中率、出处幻觉率、角色串味都没有量化看板。",
            "默认只绑本机回环地址，适合课堂演示，尚未按公网多用户加固。",
        ]),
    ]
    pos = [(0.95, top + 0.05), (6.90, top + 0.05), (0.95, top + 2.00), (6.90, top + 2.00)]
    for (title, accent, lines), (x, y) in zip(cards, pos):
        card(s, x, y, 5.55, 1.95, title, lines, accent=accent, title_size=13.5, size=11.4)
    ribbon(s, 0.95, top + 4.15, 11.50, 0.80, [
        {"t": "先把做不到的地方讲清楚，演示时才不会把话说满，后面该先做什么也更清楚。",
         "s": 12.2, "c": WHITE, "f": HEI},
    ], fill=JADE)
    return s


# ---------------------------------------------------------------- 23 演进
def s23(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "肆 · 边界与演进")
    top = head(s, "下一步：近期补体验，中期做教研")
    cols = [
        ("近期 · 体验完整度", SEAL, [
            "会话与收藏落库，登录后跨设备同步。",
            "问答支持多轮：先对历史做摘要，再检索。",
            "书库命中的章与问答出处互相跳转。",
            "围坐改成一次输出多人发言，减少等待。",
        ]),
        ("中期 · 内容与教研", JADE, [
            "建立「原句 / 白话 / 易幻觉问题」评测集，用来回归检索与提示词。",
            "为课堂加教师模式：指定篇目、指定在座弟子、导出讨论记录。",
            "注疏对齐做成半自动校对工具，提高章号覆盖率。",
        ]),
        ("远期 · 推广方向", GOLD, [
            "移动端与研学平板适配。",
            "展陈场景做「大屏先贤 + 手机创作」双端。",
            "在审核与版权前提下，扩展到《孟子》《大学》等，复用四层知识架构。",
        ]),
    ]
    x = 0.95
    for title, accent, lines in cols:
        card(s, x, top + 0.05, 3.60, 3.50, title, lines, accent=accent, title_size=13.5, size=11.2)
        x += 3.95
    ribbon(s, 0.95, top + 3.82, 11.50, 0.90, [
        {"t": "演进时仍然守住一条底线：先贤可以说话，但不能变成没有出处的网红。",
         "s": 12.6, "c": WHITE, "f": KAI, "b": True},
    ], fill=JADE)
    return s


# ---------------------------------------------------------------- 24 演示安排
def s24(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "伍 · 现场演示")
    top = head(s, "现场演示：用八到十二分钟走一遍完整流程")
    rows = [
        ["时间", "页面", "动作", "想证明什么"],
        ["1 分钟", "首页", "读今日一句，点四个入口", "界面气质和完整流程"],
        ["2 分钟", "书库与阅读", "打开《论语》一篇，竖排翻页", "这是典籍空间，不是聊天框"],
        ["3 分钟", "问答 · 治学", "问一句原句", "流式回答，并且给出检索依据"],
        ["1 分钟", "问答 · 修心 / 修身", "问一句当下的处境", "三种模式的目标确实不同"],
        ["3 分钟", "先贤对话", "同一主题进群聊，再点开子路或颜回私聊", "群像与性格差异"],
        ["2 分钟", "风骨创作", "展示已生成的人设卡与成片", "学完还能做出自己的形象和短片"],
    ]
    grid(s, 0.95, top + 0.02, 11.50, [1.2, 2.4, 4.5, 3.4], rows,
         row_h=[0.48] + [0.62] * 6, aligns=[PP_ALIGN.CENTER, PP_ALIGN.LEFT, PP_ALIGN.LEFT,
                                            PP_ALIGN.LEFT], size=11.2, head_size=11.5)
    ribbon(s, 0.95, top + 4.38, 11.50, 0.90, [
        {"t": "备用方案", "s": 11, "c": GOLD, "f": KAI, "b": True, "sa": 4},
        {"t": "DeepSeek 不可用时，书库与阅读照常演示；百炼不可用时，停在人设卡这一步；"
              "视频可以提前生成好再播放。演示过程中不打开密钥文件。",
         "s": 11.9, "c": WHITE, "f": HEI},
    ], fill=JADE)
    return s


# ---------------------------------------------------------------- 25 结语
def s25(prs):
    s = blank(prs)
    frame(s, cur_page(), TOTAL, "", seal_text="")
    watermark(s, "語", x=10.15, y=1.05, size=120)
    seal = rect(s, 11.35, 1.05, 1.15, 1.15, fill=SEAL, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
                radius=0.05)
    shape_text(seal, [{"t": "論語", "s": 20, "c": WHITE, "f": KAI, "b": True, "sa": 2}], margins=0.04)
    text(s, 1.10, 1.55, 9.0, 1.2,
         [{"t": "读典籍　问疑惑", "s": 34, "c": INK, "f": KAI, "b": True, "sa": 8},
          {"t": "听群言　立风骨", "s": 34, "c": INK, "f": KAI, "b": True}])
    hline(s, 1.15, 3.35, 3.6, color=SEAL, lw=2.0)
    text(s, 1.15, 3.55, 9.6, 1.5, [
        {"t": "希望使用者最后记住的，不是一句编出来的「孔子说」，"
              "而是一句查得到出处的原文，一次被认真对待的处境；",
         "s": 13, "c": INK_SOFT, "f": HEI, "ls": 1.52, "sa": 5},
        {"t": "如果愿意，再留下一段由自己面孔和声音完成的诵读。", "s": 13, "c": INK_SOFT, "f": HEI},
    ])
    ribbon(s, 1.10, 5.15, 5.6, 0.72, [
        {"t": "感谢聆听，请老师和同学指正", "s": 13.5, "c": WHITE, "f": KAI, "b": True},
    ], fill=JADE)
    text(s, 1.15, 6.10, 8.0, 0.4,
         [{"t": "深藏blue ｜ 张馨文、善文玲 ｜ 2026 年 10 月 13 日", "s": 11,
           "c": MUTED, "f": HEI}])
    return s


def main():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "汇报PPT")
    os.makedirs(out_dir, exist_ok=True)
    prs = Presentation()
    prs.slide_width = E(SW)
    prs.slide_height = E(SH)
    order = (
        s01, s02,
        c1, s03, s04, s05, s06, s07,
        c2, s08, s09, s10, s11, s12, s13, s14, s15, s16,
        c3, s17, s18, s19, s20, s21,
        c4, s22, s23,
        c5, s24, s25,
    )
    for fn in order:
        fn(prs)
    path = os.path.join(out_dir, "孔子之境·智启论语_课程汇报_深藏blue.pptx")
    prs.save(path)
    print("saved:", path)
    print("slides:", len(order), "total-const:", TOTAL)


if __name__ == "__main__":
    main()
