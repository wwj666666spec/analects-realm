/**
 * 界面语言：默认英文。典籍正文、书名、人物生平保持中文。
 * 问答在英文界面用英文作答，引用的古文原句仍保留中文。
 */
const LANG_KEY = "lunyu.lang";
const SUPPORTED = ["en", "zh"];

const META = {
  en: {
    title: "Realm of Confucius · Wisdom of The Analects",
    description:
      "An immersive Chinese classics learning and creative platform: read The Analects, explore with AI-guided inquiry, converse with Confucius’s disciples, and create your own classical-style recitation video.",
  },
  zh: {
    title: "孔子之境 · 智启论语",
    description:
      "《孔子之境，智启论语》一站式沉浸式学习与创作平台：典籍书库、三维度智能问答、孔门群聊先贤对话、国风人设与诵读短视频创作。",
  },
};

/** @type {Record<string, Record<string, string>>} */
const DICT = {
  en: {
    "lang.switch": "Switch Language",
    "lang.zh": "中文",
    "lang.en": "English",
    "lang.toZh": "Switch to Chinese",
    "lang.toEn": "Switch to English",
    "lang.switchedZh": "Switched to Chinese",
    "lang.switchedEn": "Switched to English",
    "lang.booksRemainZh": "Book content remains in Chinese.",
    "lang.close": "Close",

    "nav.brand": "Lunyu Academy — Home",
    "nav.main": "Main Navigation",
    "nav.home": "Home",
    "nav.library": "Library",
    "nav.ask": "AI Q&A",
    "nav.sages": "Sages",
    "nav.create": "Studio",
    "nav.me": "Account",
    "nav.search": "Search the Classics",
    "nav.account": "Open Account",
    "nav.menu": "Open Menu",
    "nav.guest": "Not signed in",
    "nav.guestChar": "学",

    "foot.tagline": "Realm of Confucius · Immersive Classics Studio",
    "foot.line": "Read · Inquire · Converse · Create",

    "home.kicker": "Eastern Classics · A Living Cultural Heritage",
    "home.title": "Confucius' Realm, Wisdom from The Analects",
    "home.titleEm": "",
    "home.titleBrand": "",
    "home.subline": "Sit with the sages · Pursue self-cultivation through the classics",
    "home.lead":
      "Begin with The Analects: progress from close textual reading and AI-guided inquiry to discussions among Confucius’s disciples and your own original creative work. Read, inquire, converse, create<br>— a four-step journey into classical Chinese scholarship.",
    "home.ctaLibrary": "Explore the Classics",
    "home.ctaAsk": "Seek Guidance",
    "home.rail": "The Analects in Twenty Books · Opening with “Xue Er”",
    "home.gates": "Four Ways to Explore",
    "home.gate1": "Classics Library",
    "home.gate1d": "Classics, histories & commentaries · Immersive scroll-style reading",
    "home.gate2": "AI Q&A",
    "home.gate2d": "Textual Study · Inner Reflection · Self-Cultivation",
    "home.gate3": "Sages & Disciples",
    "home.gate3d": "Join the Confucian Circle · Message the Master",
    "home.gate4": "Creative Studio",
    "home.gate4d": "Classical-style persona · Recitation video",
    "home.n1": "01",
    "home.n2": "02",
    "home.n3": "03",
    "home.n4": "04",
    "home.today": "Today’s Analects",
    "home.todayEn": "Passage of the Day",
    "home.todayDesc": "A daily passage illuminating the present through ancient wisdom",
    "home.another": "Another Passage",
    "home.askThis": "Inquire About This",
    "home.copy": "Copy Passage",
    "home.hearMaster": "Hear from the Master",
    "home.picks": "Selected Classics",
    "home.picksEn": "Selected Classics",
    "home.viewAll": "View All Classics",
    "home.pickFallback": "Open this work in the library.",
    "home.copied": "Passage copied to clipboard.",
    "home.refreshed": "Another passage selected.",
    "home.todayLabel": "Passage of the Day",
    "home.ganzhi": "Year of {ganzhi} ({raw})",

    "lib.title": "Classics Library",
    "lib.desc":
      "Explore The Analects and its major commentaries, alongside The Book of Rites, The Hereditary House of Confucius from The Records of the Grand Historian, and The Family Sayings of Confucius.",
    "lib.searchPh": "Search by title, commentator or keyword — e.g. ren, Zhu Xi, Zilu",
    "lib.searchAria": "Search the Classics",
    "lib.searchBtn": "Search",
    "lib.index": "Index",
    "lib.emptyLoad": "Library content is still loading.",
    "lib.emptyLoadHint":
      "Refresh the page, or verify the server is running and the data folder contains .md work files.",
    "lib.emptyQuery": "No works directly related to “{query}” were found in the library.",
    "lib.emptyHint": "Try another title, or explore this topic in AI Q&A.",
    "lib.filter": "Current Filter",
    "lib.fav": "Save",
    "lib.favTitle": "Save {title}",
    "lib.favOn": "Saved to your library.",
    "lib.favOff": "Removed from your library.",
    "lib.authorFallback": "Classics Library",

    "read.crumb": "Reading",
    "read.home": "Home",
    "read.library": "Classics Library",
    "read.back": "Back to Library",
    "read.ask": "Inquire with AI About This Section",
    "read.tipHome": "Back to Home",
    "read.tipPrev": "Previous Section",
    "read.tipNext": "Next Section",
    "read.tipUp": "Up One Level",
    "read.tipFav": "Save This Section",
    "read.tipAsk": "Inquire with AI",
    "read.hint": "Use ← → keys to navigate sections. Vertical text reads right-to-left, as with an unrolled scroll.",
    "read.noBook": "No work selected.",
    "read.noBookHint": "Select a classic work from the library.",
    "read.opening": "Opening the scroll…",
    "read.truncated": "This section is lengthy; only the opening excerpt is displayed.",
    "read.emptySection": "(No original text available for this section.)",
    "read.atStart": "You have reached the start of the volume.",
    "read.atEnd": "You have reached the end of the volume.",
    "read.favOn": "Section saved.",
    "read.favOff": "Removed from saved items.",
    "read.askPrompt":
      "You are now reading “{book}” — {section}. You may inquire about its phrasing, structure or historical background.",
    "read.askTitle": "《{book}》{section} · Inquiry",

    "ask.title": "AI Q&A",
    "ask.desc":
      "An AI assistant grounded in The Analects and related classics. Choose Textual Study, Inner Growth, or Practical Guidance for insights on research, reflection and everyday conduct.",
    "ask.modes": "Q&A Modes",
    "ask.modesSub": "Study · Growth · Guidance",
    "ask.modeStudy": "Textual Study",
    "ask.modeHeart": "Inner Growth",
    "ask.modeBody": "Practical Guidance",
    "ask.new": "+ New Chat",
    "ask.newTitle": "New Chat",
    "ask.clear": "Clear Current Chat",
    "ask.send": "Send",
    "ask.inputPh": "Enter your inquiry… (Enter to send; Shift+Enter for new line)",
    "ask.composerHint":
      "Insights draw from The Analects and historical commentaries. Interpretations by later scholars or AI are clearly marked.",
    "ask.welcome":
      "Feel free to submit your inquiry — about passages, personal concerns or difficult dilemmas. Switch between Textual Study, Inner Reflection & Growth, and Practical Guidance on the left. Insights are generated from retrieved classical sources.",
    "ask.waiting": "Consulting classical texts…",
    "ask.noReply": "No response was returned.",
    "ask.cleared": "Current chat cleared.",
    "ask.noMsgs": "No messages yet",
    "ask.me": "Me",
    "ask.currentMode": "Current Mode · {label}",
    "ask.agent": "Analects AI",
    "ask.agentDesc": "Insights rooted in classical texts · Sources cited",

    "mode.study.who": "Analects AI",
    "mode.study.desc": "Wording · Structure · Historical context · Textual inquiry",
    "mode.study.label": "Textual Study",
    "mode.study.defaultConv": "New chat · Textual Inquiry",
    "mode.study.chip0": "What does “To learn and practice it in due time” mean?",
    "mode.study.chip1": "What does “The exemplary person is not a vessel” mean?",
    "mode.study.chip2": "How is ren understood across The Analects?",
    "mode.study.chip3": "Why did Confucius reply, “I stand with Dian”?",
    "mode.heart.who": "Inner Reflection Guide",
    "mode.heart.desc": "Reflection guided by the Mean, ren, and equanimity",
    "mode.heart.label": "Inner Reflection & Growth",
    "mode.heart.defaultConv": "New chat · Feeling Anxious",
    "mode.heart.chip0": "I’ve felt anxious and cannot settle my mind.",
    "mode.heart.chip1": "I often feel inadequate beside others.",
    "mode.heart.chip2": "I feel mentally strained. How may I find balance?",
    "mode.heart.chip3": "I feel a sense of inner emptiness.",
    "mode.body.who": "Practical Guidance",
    "mode.body.desc": "Relationships · Work · Self-discipline · Family conduct",
    "mode.body.label": "Practical Guidance",
    "mode.body.defaultConv": "New chat · Getting Along with Others",
    "mode.body.chip0": "Should I share my true thoughts with my parents?",
    "mode.body.chip1": "How can I reconcile after a disagreement with a colleague?",
    "mode.body.chip2": "I keep procrastinating. How can I cultivate self-discipline?",
    "mode.body.chip3": "Should I lend money to a friend?",

    "sages.title": "Conversations with the Sages",
    "sages.desc":
      "Chat privately with a disciple or join the Confucian Circle for group discussion. Select an avatar to view their discipline, biography and the Master’s observations.",
    "sages.searchPh": "Search Disciples",
    "sages.group": "The Confucian Circle",
    "sages.groupLast": "Roundtable · Confucius is present; other participants rotate",
    "sages.justNow": "Just now",
    "sages.disciples": "Fellow Disciples · {count} total",
    "sages.membersRound": "{count} participant · Roundtable",
    "sages.membersRound_plural": "{count} participants · Roundtable",
    "sages.empty":
      "Share your situation — Confucius speaks first, then rotating disciples. Or revisit a classic dialogue above.",
    "sages.sceneNote": "{name} · From {src} · Original dialogue",
    "sages.typing": "{name} is typing…",
    "sages.profile": "View Profile",
    "sages.join": "Join the conversation",
    "sages.me": "Me",
    "sages.tip": "Enter to send · Shift+Enter for a new line",
    "sages.inputPh": "Share your circumstances or engage in scholarly discussion with fellow disciples…",
    "sages.master": "the Master",
    "sages.disciple": "Disciple of Confucius",
    "sages.supreme": "The Supreme Sage-Teacher",
    "sages.keAll": "Master of the Four Disciplines · The Supreme Sage-Teacher",
    "sages.keOf": "Traditional Discipline · {subject}",
    "sages.keFallback": "Traditional Discipline · Disciple of Confucius",
    "sages.ke.德行": "Moral Conduct",
    "sages.ke.言语": "Rhetoric",
    "sages.ke.政事": "Statecraft",
    "sages.ke.文学": "Classical Learning",
    "sages.markMaster": "Master",
    "sages.markPrimary": "Primary",
    "sages.ping": "The Master’s Observations",
    "sages.chat": "Start a Chat",
    "sages.say0": "Should I resign without securing another role first?",
    "sages.say1": "My parents urge me to marry.",
    "sages.say2": "I often feel inadequate beside others.",
    "sages.say3": "I feel anxious and cannot quiet my mind.",
    "sages.join.group0": "I hold a different view.",
    "sages.join.group1": "How should this be understood?",
    "sages.join.group2": "I would welcome further elaboration.",
    "sages.join.group3": "I have encountered similar circumstances.",
    "sages.join.kongzi0": "I often feel inadequate beside others.",
    "sages.join.kongzi1": "I feel anxious and cannot quiet my mind.",
    "sages.join.kongzi2": "This weighs heavily on my mind.",
    "sages.join._0": "What is your perspective?",
    "sages.join._1": "I would welcome further elaboration.",
    "sages.join._2": "What followed?",
    "sages.time.今日": "Today",
    "sages.time.刚刚": "Just now",
    "sages.time.昨天": "Yesterday",
    "sages.time.前天": "2 days ago",
    "sages.time.三天前": "3 days ago",
    "sages.time.四天前": "4 days ago",
    "sages.time.五天前": "5 days ago",

    "create.title": "Moral Fibre & Aesthetic-Bearing Studio",
    "create.desc":
      "Shape a Five-Virtue persona, craft a classical portrait, choose a voice, and turn your reflection into a recitation video.",
    "create.step1": "Personality Quiz",
    "create.step2": "Persona Card",
    "create.step3": "Portrait",
    "create.step4": "Voice",
    "create.step5": "Recitation Video",
    "create.n1": "01",
    "create.n2": "02",
    "create.n3": "03",
    "create.n4": "04",
    "create.n5": "05",
    "create.back": "Back",
    "create.next": "Next",
    "create.hint": "Step {current} of {total}",
    "create.nextBtn0": "Generate Persona Card",
    "create.nextBtn1": "Next · Portrait",
    "create.nextBtn2": "Next · Voice",
    "create.nextBtn3": "Next · Script",
    "create.nextBtn4": "Create Recitation Video",
    "create.quizTitle": "Personality Quiz",
    "create.quizTitleEn": "Quiz",
    "create.quizDesc":
      "When you finish, AI builds your persona from the Five Virtues: warmth, goodness, reverence, frugality and deference.",
    "create.answered": "Completed {n} / {total}",
    "create.quizSubmit": "Generate My Persona Card",
    "create.quizReset": "Retake Quiz",
    "create.quizMiss": "{count} question remaining",
    "create.quizMiss_plural": "{count} questions remaining",
    "create.personaTitle": "Your Persona Card",
    "create.personaTitleEn": "Persona",
    "create.personaDesc": "Generated from quiz responses and your Five-Virtue profile",
    "create.retake": "Retake Quiz",
    "create.nextFigure": "Next · Customize Portrait",
    "create.figureTitle": "Customize Your Portrait",
    "create.figureTitleEn": "Portrait",
    "create.uploadPhoto": "Upload Your Photo",
    "create.uploadPhotoHint": "JPG or PNG. Use a front-facing half-body photo with even lighting.",
    "create.noPhoto": "No photo selected",
    "create.gender": "Portrait Gender",
    "create.male": "Male",
    "create.female": "Female",
    "create.genFigure": "Generate Classical Portrait",
    "create.figPreview": "Portrait Preview",
    "create.figWait": "Waiting for a photo",
    "create.voiceTitle": "Voice & Narration",
    "create.voiceTitleEn": "Voice",
    "create.voiceDesc":
      "Choose a preset male or female narrator, or upload 10–20 seconds of clear speech to clone your own voice.",
    "create.uploadAudio": "Upload Audio to Clone My Voice",
    "create.uploadAudioHint": "Read a short passage from The Analects.",
    "create.currentVoice": "Current Voice",
    "create.noClone": "No cloned voice yet",
    "create.preview": "Generate Preview",
    "create.useVoice": "Use This Voice · Next",
    "create.scriptTitle": "Create Recitation Video",
    "create.scriptTitleEn": "Script & Video",
    "create.scriptDesc":
      "Write what The Analects prompted you to think about, or reflect on self-cultivation, relationships, learning and life.",
    "create.scriptLabel": "Recitation Script",
    "create.scriptPh": "Begin with a passage from The Analects, then connect it to what you are facing now…",
    "create.chars": "{count} character",
    "create.chars_plural": "{count} characters",
    "create.demo": "Use Sample Text",
    "create.genScript": "Generate Script from Persona",
    "create.genVideo": "Create Recitation Video",
    "create.download": "Download Video",
    "create.videoWait": "Waiting to generate · Your portrait, script, and voice will be combined",
    "create.videoTitle": "Recitation Video Preview",
    "create.videoSub": "Your video will appear here.",
    "create.redo": "Start a New Version",
    "create.voicesMale": "Male Voices",
    "create.voicesFemale": "Female Voices",
    "create.voicesMine": "My Voice",
    "create.cloned": "Cloned",
    "create.myClone": "My Cloned Voice",
    "create.systemVoice": "System Voice",
    "create.needQuiz": "Complete the personality quiz and generate your persona card first.",
    "create.needFigure": "Generate your classical-style portrait first.",
    "create.needPhoto": "Upload a photo first.",
    "create.needGender": "Choose a male or female portrait first.",
    "create.needPersonaQuiz": "Complete the personality quiz and generate your persona card first.",
    "create.needQuizOnly": "Complete the personality quiz first.",
    "create.needScript": "Enter a recitation script first.",
    "create.needPhotoOrFigure": "Upload a photo or generate a classical-style portrait first.",
    "create.needClone": "Upload audio and finish cloning your voice first.",
    "create.needCloneShort": "Upload audio and clone your voice first.",
    "create.cloneHint": "To hear the cloned voice, select “Generate Preview.”",
    "create.refining": "AI is refining your persona profile…",
    "create.personaCreated": "Persona card generated: {name}",
    "create.aiFallback": "AI profile generation unavailable; a locally computed profile has been applied.",
    "create.uploading": "Uploading · {filename}",
    "create.uploaded": "Uploaded · {filename}",
    "create.uploadedCloning": "Uploaded · {filename}. Cloning voice…",
    "create.photoOk": "Photo uploaded.",
    "create.uploadFail": "Upload failed. Please try again.",
    "create.pickGender": "Select a portrait gender, then generate the portrait.",
    "create.uploadingPhoto": "Uploading photo…",
    "create.genFigureBusy": "Generating a classical-style portrait based on your facial features and selected gender…",
    "create.figDone": "Portrait generated · You can continue",
    "create.figDoneToast": "Classical-style portrait generated.",
    "create.genFail": "Generation failed.",
    "create.figFail": "Portrait generation failed.",
    "create.audioStart": "Audio uploaded. Cloning voice…",
    "create.cloneDone": "Cloning complete · “My Cloned Voice” selected",
    "create.cloneOk": "Voice cloned successfully. Select “Generate Preview” to listen.",
    "create.cloneFail": "Voice cloning failed.",
    "create.previewBusy": "Generating preview…",
    "create.previewFail": "Preview failed.",
    "create.previewPlay": "Preview · {sample}",
    "create.scriptOk": "Script generated from your persona.",
    "create.scriptFail": "Script generation failed.",
    "create.videoSubmit": "Task submitted. Generating narration…",
    "create.videoBusy": "Creating your recitation video…",
    "create.videoDone": "Video ready. Preview or download it now.",
    "create.videoOk": "Recitation video created.",
    "create.noJob": "No video task ID was returned.",
    "create.videoSlow": "Generation is taking longer than expected. Please try again later.",
    "create.videoFail": "Video generation failed.",
    "create.noDownload": "No finished video is available to download yet.",
    "create.downloadName": "Character-and-Style_Recitation_{ts}.mp4",
    "create.videoReady": "Preview or download",
    "create.videoTitleNamed": "{name} · Recitation",
    "create.wudeTag": "Five-Virtue Profile · Centred on {virtue}",
    "create.motto": "Motto",
    "create.tags": "Behavioural Traits",
    "create.analysis": "Primary virtue: {primary}; secondary virtue: {secondary}. {line}",
    "create.noPersona": "No persona card generated yet",

    "wude.温": "Warmth",
    "wude.良": "Goodness",
    "wude.恭": "Reverence",
    "wude.俭": "Frugality",
    "wude.让": "Deference",
    "wudeDesc.温": "Warm",
    "wudeDesc.良": "Good-hearted",
    "wudeDesc.恭": "Respectful",
    "wudeDesc.俭": "Frugal",
    "wudeDesc.让": "Deferential",

    "persona.温.name": "The Composed Upright Scholar",
    "persona.温.line": "Calm and introspective, warm toward others, and first looks inward when problems arise.",
    "persona.温.tag0": "Patient and composed",
    "persona.温.tag1": "Considerate of others",
    "persona.温.tag2": "Reflective and self-disciplined",
    "persona.良.name": "The Sincere Practitioner",
    "persona.良.line": "Sincere and grounded, values promises and action, and avoids overstatement.",
    "persona.良.tag0": "Words and deeds in harmony",
    "persona.良.tag1": "Honours commitments",
    "persona.良.tag2": "Focuses on the matter at hand",
    "persona.恭.name": "The Respectful and Principled Scholar",
    "persona.恭.line": "Measured and principled, respectful in duty, and careful with boundaries.",
    "persona.恭.tag0": "Diligent and trustworthy in duties",
    "persona.恭.tag1": "Punctual and temperate",
    "persona.恭.tag2": "Self-restrained and temperate",
    "persona.俭.name": "The Simple and Self-Possessed Scholar",
    "persona.俭.line": "Simple and self-possessed, unswayed by extravagance, focused on what truly matters.",
    "persona.俭.tag0": "Exercises moderation in consumption",
    "persona.俭.tag1": "Unenticed by ostentation",
    "persona.俭.tag2": "Devoted to one’s proper calling",
    "persona.让.name": "The Humble and Magnanimous Scholar",
    "persona.让.line": "Humble and spacious, listens before speaking, and leaves room for others.",
    "persona.让.tag0": "Listens before speaking",
    "persona.让.tag1": "Seeks no personal merit",
    "persona.让.tag2": "Treat others as oneself would wish to be treated",

    "quiz.0.dim": "Approach to Learning",
    "quiz.0.q": "Which do you favour: broad learning through culture, or the unity of knowledge and action?",
    "quiz.0.o0": "Study texts first to grasp underlying principles.",
    "quiz.0.o1": "Act first and refine understanding through real-world practice.",
    "quiz.0.o2": "Learn and act in tandem, adjusting accordingly.",
    "quiz.1.dim": "Approach to Affairs",
    "quiz.1.q": "When conflict emerges, how would you tend to respond?",
    "quiz.1.o0": "Seek dialogue first before weighing trade-offs.",
    "quiz.1.o1": "Uphold core principles first, then consider adaptability.",
    "quiz.1.o2": "Choose forbearance where appropriate.",
    "quiz.2.dim": "Inward Disposition",
    "quiz.2.q": "Which disposition resonates more with you?",
    "quiz.2.o0": "Calm and introspective, given to self-reflection.",
    "quiz.2.o1": "Warm-hearted and open, ready to voice thoughts.",
    "quiz.2.o2": "Reserved and composed, cautious in public pronouncements.",
    "quiz.3.dim": "Social Disposition",
    "quiz.3.q": "In group settings, which aligns closer to you?",
    "quiz.3.o0": "I take initiative to assist others.",
    "quiz.3.o1": "I quietly attend to my own duties.",
    "quiz.3.o2": "I listen first and refrain from hasty judgement.",
    "quiz.4.dim": "Core Values",
    "quiz.4.q": "Which do you prize most: integrity, trustworthiness, benevolence or humility?",
    "quiz.4.o0": "Integrity",
    "quiz.4.o1": "Trustworthiness",
    "quiz.4.o2": "Benevolence",
    "quiz.4.o3": "Humility",
    "quiz.5.dim": "Approach to Life",
    "quiz.5.q": "Which kind of life do you aspire to?",
    "quiz.5.o0": "Dignified and self-disciplined, observing moderation in daily routines.",
    "quiz.5.o1": "Plain-living and natural, unenticed by ostentation.",
    "quiz.5.o2": "Composed and adaptable, content amid circumstances.",
    "quiz.6.dim": "Facing Criticism & Misjudgement",
    "quiz.6.q": "When met with misunderstanding or criticism, how do you typically respond?",
    "quiz.6.o0": "Practise self-reflection first, then explain calmly.",
    "quiz.6.o1": "State the facts clearly and move forward.",
    "quiz.6.o2": "Exercise forbearance where fitting; not every matter calls for argument.",
    "quiz.7.dim": "Aspiration & Vision",
    "quiz.7.q": "Where do you seek to position yourself?",
    "quiz.7.o0": "Refine and steadfastly fulfil the task at hand.",
    "quiz.7.o1": "Expand my vision and dare to think and experiment.",
    "quiz.7.o2": "First tend to those and matters near at hand.",

    "voice.longxiang.name": "Ancient Resonance",
    "voice.longxiang.desc": "Deep and resonant; suited to reflective recitation",
    "voice.longshu.name": "Steady Narrator",
    "voice.longshu.desc": "Calm and even, with clear articulation",
    "voice.longxiaocheng.name": "Clear & Open",
    "voice.longxiaocheng.desc": "Bright and open, with a clear tone",
    "voice.longlaotie.name": "Resolute & Crisp",
    "voice.longlaotie.desc": "Strong, incisive delivery",
    "voice.longshuo.name": "Rich & Grounded",
    "voice.longshuo.desc": "Full and grounded; suited to formal recitation",
    "voice.longcheng.name": "Clear & Composed",
    "voice.longcheng.desc": "Crisp and clear, unhurried and steady",
    "voice.longxiaochun.name": "Serene & Gentle",
    "voice.longxiaochun.desc": "Soft, thoughtful, and gently paced",
    "voice.longyuan.name": "Warm & Refined",
    "voice.longyuan.desc": "Gentle and elegant; suited to slow reading",
    "voice.longwan.name": "Soft & Unhurried",
    "voice.longwan.desc": "Gentle, flowing, and sustained",
    "voice.longjing.name": "Poised & Thoughtful",
    "voice.longjing.desc": "Calm, courteous, and suited to narration",
    "voice.longyue.name": "Warm & Calm",
    "voice.longyue.desc": "Warm, soft, and approachable",
    "voice.longxiaobai.name": "Quiet & Elegant",
    "voice.longxiaobai.desc": "Restrained, composed, and unhurried",
    "voice.mine.name": "My Cloned Voice",
    "voice.mine.desc": "Generated after you upload a voice sample",

    "me.title": "My Account",
    "me.login": "Sign In",
    "me.register": "Register",
    "me.username": "Username",
    "me.password": "Password",
    "me.userPhLogin": "Enter your username",
    "me.userPhReg": "Choose a username for your studies",
    "me.pwdPh": "Enter your password",
    "me.loginBtn": "Sign In",
    "me.regBtn": "Create Account",
    "me.fillBoth": "Enter your username and password.",
    "me.welcome": "Welcome back, {name}",
    "me.regOk": "Account created.",
    "me.logout": "Signed out.",
    "me.logoutBtn": "Sign Out",
    "me.note": "Sign in to continue your chats, discussions, and reading. Saved books remain on this device.",
    "me.favCount": "{count} saved book",
    "me.favCount_plural": "{count} saved books",
    "me.toCreate": "Create Persona Card",
    "me.local": "On This Device",
    "me.localEn": "Local Activity",
    "me.localDesc": "Q&A and saved books",
    "me.statAsk": "Questions Asked",
    "me.statAskSub": "Textual Study / Inner Reflection / Self-Cultivation",
    "me.statFav": "Saved Books",
    "me.statFavSub": "Use the star to save",
    "me.statConv": "Chat Sessions",
    "me.statConvSub": "Stored on this device",
    "me.favs": "Saved Books",
    "me.favsEn": "Favorites",
    "me.favCard": "Saved · Continue reading",
    "me.favEmpty": "You have not saved any books yet. Select the star at the top right of a book cover to save it.",
    "me.recent": "Recent Questions",
    "me.recentEn": "Ask",
    "me.fromAsk": "AI Q&A",
    "me.noAsk": "No questions yet.",

    "err.request": "The request could not be completed.",
    "err.timeout": "This is taking longer than expected. Please try again.",
    "err.legacyAsk": "Earlier Q&A",
    "err.notLogin": "You are not signed in.",
    "err.badCreds": "Incorrect username or password.",
    "err.userTaken": "This username is already registered.",
    "err.userLen": "Your username must be 2–20 characters and may contain Chinese characters, letters, or numbers.",
    "err.pwdLen": "Your password must be at least 6 characters.",
    "err.photoFmt": "Use a JPG, PNG, or WEBP photo.",
    "err.audioFmt": "Use an MP3, WAV, or M4A audio file.",
    "err.fileSize": "The file is too large. Keep it under 12 MB.",
    "err.noUpload": "The uploaded file could not be found.",
    "err.needScript": "Enter a recitation script first.",
    "err.scriptLen": "Keep the recitation script under 800 characters.",
    "err.needPhotoFigure": "Upload a photo or create a classical-style portrait first.",
    "err.face": "Face detection failed: {message}",
    "err.faceHint": "Use a clear, unobstructed, front-facing half-body photo.",
    "err.portraitDetect": "Portrait detection failed. Use a front-facing half-body photo.",
    "err.emptyQ": "The question is empty.",
  },
  zh: {
    "lang.switch": "切换语言",
    "lang.zh": "中文",
    "lang.en": "EN",
    "lang.toZh": "切换至中文",
    "lang.toEn": "切换至英文",
    "lang.switchedZh": "已切换至中文",
    "lang.switchedEn": "已切换至英文",
    "lang.booksRemainZh": "书籍内容仍以中文显示",
    "lang.close": "关闭",

    "nav.brand": "智启论语 首页",
    "nav.main": "主导航",
    "nav.home": "首页",
    "nav.library": "典籍书库",
    "nav.ask": "智能问答",
    "nav.sages": "先贤对话",
    "nav.create": "风骨创作",
    "nav.me": "个人中心",
    "nav.search": "检索典籍",
    "nav.account": "打开个人中心",
    "nav.menu": "展开菜单",
    "nav.guest": "未登录",
    "nav.guestChar": "学",

    "foot.tagline": "孔子之境 · 一站式沉浸式学习与创作平台",
    "foot.line": "读典籍 · 问疑惑 · 听群言 · 立风骨",

    "home.kicker": "東方典籍 · 千年文脈",
    "home.title": "孔子之境 · 智启论语",
    "home.titleEm": "",
    "home.titleBrand": "",
    "home.subline": "與先賢同席 · 以國學修身",
    "home.lead":
      "以《论语》为舟，从典籍精读到智能答疑，从孔门群言到一手风骨创作——阅览 · 问答 · 对话 · 创作，四步走完一条沉浸式国学研习之路。",
    "home.ctaLibrary": "入典藏书库",
    "home.ctaAsk": "问一句疑惑",
    "home.rail": "論語二十篇 · 學而始",
    "home.gates": "四大功能入口",
    "home.gate1": "典藏书库",
    "home.gate1d": "经史注疏 · 竖排卷轴精读",
    "home.gate2": "智能问答",
    "home.gate2d": "治学 · 修心 · 修身三维度",
    "home.gate3": "先贤对话",
    "home.gate3d": "孔门群聊 · 私聊夫子",
    "home.gate4": "个人创作",
    "home.gate4d": "国风人设 · 诵读短视频",
    "home.n1": "壹",
    "home.n2": "貳",
    "home.n3": "參",
    "home.n4": "肆",
    "home.today": "今日论语",
    "home.todayEn": "Passage of the Day",
    "home.todayDesc": "每日一句，以古照今",
    "home.another": "另取一句",
    "home.askThis": "就此提问",
    "home.copy": "抄录此句",
    "home.hearMaster": "听听夫子怎么说",
    "home.picks": "典册撷英",
    "home.picksEn": "Selected Classics",
    "home.viewAll": "查看全部典籍",
    "home.pickFallback": "点此进入书库阅读。",
    "home.copied": "已抄录到剪贴板",
    "home.refreshed": "已另取一句",
    "home.todayLabel": "今日一句",
    "home.ganzhi": "{raw}",

    "lib.title": "典籍书库",
    "lib.desc": "收《论语》原典及历代注疏，旁及《礼记》《史记·孔子世家》《孔子家语》诸书。",
    "lib.searchPh": "输入书名、注家或关键词，如「仁」「朱熹」「子路」",
    "lib.searchAria": "检索典籍",
    "lib.searchBtn": "搜索",
    "lib.index": "书目",
    "lib.emptyLoad": "书目尚未加载",
    "lib.emptyLoadHint": "请刷新页面，或确认后端已启动且 data 目录中有 .md 书册",
    "lib.emptyQuery": "书库中暂未收录与「{query}」直接相关的书册",
    "lib.emptyHint": "可换个书名，或到智能问答中检索该主题",
    "lib.filter": "当前筛选",
    "lib.fav": "收藏",
    "lib.favTitle": "收藏 {title}",
    "lib.favOn": "已收进我的书箧",
    "lib.favOff": "已移出我的书箧",
    "lib.authorFallback": "典籍书库",

    "read.crumb": "阅读",
    "read.home": "首页",
    "read.library": "典籍书库",
    "read.back": "返回书库",
    "read.ask": "就此篇向 Agent 提问",
    "read.tipHome": "返回首页",
    "read.tipPrev": "上一篇",
    "read.tipNext": "下一篇",
    "read.tipUp": "返回上一级",
    "read.tipFav": "收藏本篇",
    "read.tipAsk": "向 Agent 提问",
    "read.hint": "← → 翻篇 · 竖排自右向左 如展卷轴",
    "read.noBook": "没有指定书名",
    "read.noBookHint": "请从书库选择一部典籍。",
    "read.opening": "正在打开书卷。",
    "read.truncated": "这一节很长，这里只显示开头。",
    "read.emptySection": "（本节暂无正文）",
    "read.atStart": "已是全卷之首",
    "read.atEnd": "已到本卷之末",
    "read.favOn": "已收藏本篇",
    "read.favOff": "已取消收藏",
    "read.askPrompt": "已翻到《{book}》{section}。你可以直接问这一篇里的字词、篇章或背景。",
    "read.askTitle": "《{book}》{section} · 求解",

    "ask.title": "智能问答",
    "ask.desc":
      "《论语》专属知识库 Agent，依「治学 · 修心 · 修身」三维度作答——字词篇章可考据，心绪起伏可疏导，处世行事可落地。",
    "ask.modes": "问答模式",
    "ask.modesSub": "治学 · 修心 · 修身",
    "ask.modeStudy": "答疑解惑",
    "ask.modeHeart": "心理疏导",
    "ask.modeBody": "行为指导",
    "ask.new": "＋ 新建会话",
    "ask.newTitle": "新建会话",
    "ask.clear": "清空当前会话",
    "ask.send": "发送",
    "ask.inputPh": "请输入您的问题…（按 Enter 发送，Shift+Enter 换行）",
    "ask.composerHint": "答案取自《论语》原文与历代注疏；凡后世推定之说，Agent 会另行注明。",
    "ask.welcome":
      "有什么想问的，尽管说——章句、心事、难处都可以。左侧可切换治学、修心、修身三种模式。答案依典籍检索生成。",
    "ask.waiting": "正在查阅典籍…",
    "ask.noReply": "这一次没有收到回答。",
    "ask.cleared": "已清空当前会话",
    "ask.noMsgs": "尚无对话",
    "ask.me": "我",
    "ask.currentMode": "当前模式 · {label}",
    "ask.agent": "论语 Agent",
    "ask.agentDesc": "依典籍作答 · 引文标注篇目",

    "mode.study.who": "治学 Agent",
    "mode.study.desc": "字词 · 篇章 · 历史背景 · 典籍考据",
    "mode.study.label": "答疑解惑（治学维度）",
    "mode.study.defaultConv": "新会话 · 章句求解",
    "mode.study.chip0": "「学而时习之」怎么解？",
    "mode.study.chip1": "「君子不器」是什么意思？",
    "mode.study.chip2": "「仁」在《论语》里的层次",
    "mode.study.chip3": "孔子为什么说「吾与点也」？",
    "mode.heart.who": "修心 Agent",
    "mode.heart.desc": "基于中庸、仁爱、豁达的国学疏导",
    "mode.heart.label": "心理疏导（修心维度）",
    "mode.heart.defaultConv": "新会话 · 我很焦虑",
    "mode.heart.chip0": "我最近很焦虑，静不下来",
    "mode.heart.chip1": "总觉得自己不如别人",
    "mode.heart.chip2": "内耗很重，怎么办",
    "mode.heart.chip3": "心里空落落的",
    "mode.body.who": "修身 Agent",
    "mode.body.desc": "人际 · 职场 · 自律 · 家风的落地建议",
    "mode.body.label": "行为指导（修身维度）",
    "mode.body.defaultConv": "新会话 · 与人相处",
    "mode.body.chip0": "要不要跟父母说出真实想法",
    "mode.body.chip1": "和同事起了争执怎么收场",
    "mode.body.chip2": "总是拖延，怎么自律",
    "mode.body.chip3": "朋友借钱该不该借",

    "sages.title": "先贤对话 · 孔门群聊",
    "sages.desc":
      "可与同门私聊，也可在孔门三千群聊里参与研讨。点击头像可查看好友四科归属、生平简介与夫子锐评。",
    "sages.searchPh": "搜索同门",
    "sages.group": "孔门三千",
    "sages.groupLast": "围坐 · 孔子在座，其余每次不同",
    "sages.justNow": "刚刚",
    "sages.disciples": "同 门 · 共 {count} 人",
    "sages.membersRound": "{count} 位成员 · 围坐",
    "sages.membersRound_plural": "{count} 位成员 · 围坐",
    "sages.empty": "说一件事，孔子会先开口，其余同门每次不同。也可点上方名场面，回看原文对白。",
    "sages.sceneNote": "{name} · 出自 {src} · 原文对白回放",
    "sages.typing": "{name} 正在输入…",
    "sages.profile": "查看资料卡",
    "sages.join": "我也说一句",
    "sages.me": "我",
    "sages.tip": "Enter 发送 · Shift+Enter 换行",
    "sages.inputPh": "说说你的处境，或与同门论学…",
    "sages.master": "夫子",
    "sages.disciple": "孔门弟子",
    "sages.supreme": "至圣先师",
    "sages.keAll": "四科总持 · 至圣先师",
    "sages.keOf": "四科归属 · {subject}",
    "sages.keFallback": "四科归属 · 孔门弟子",
    "sages.ke.德行": "德行",
    "sages.ke.言语": "言语",
    "sages.ke.政事": "政事",
    "sages.ke.文学": "文学",
    "sages.markMaster": "师表",
    "sages.markPrimary": "所属",
    "sages.ping": "夫 子 锐 评",
    "sages.chat": "找他说话",
    "sages.say0": "要不要裸辞",
    "sages.say1": "爸妈催婚",
    "sages.say2": "总觉得不如别人",
    "sages.say3": "很焦虑，静不下来",
    "sages.join.group0": "我有不同看法",
    "sages.join.group1": "这话何解？",
    "sages.join.group2": "愿闻其详",
    "sages.join.group3": "我也遇过此事",
    "sages.join.kongzi0": "请夫子指点",
    "sages.join.kongzi1": "我该如何自处",
    "sages.join.kongzi2": "心里过不去",
    "sages.join._0": "你怎么看？",
    "sages.join._1": "愿闻其详",
    "sages.join._2": "后来呢？",
    "sages.time.今日": "今日",
    "sages.time.刚刚": "刚刚",
    "sages.time.昨天": "昨天",
    "sages.time.前天": "前天",
    "sages.time.三天前": "三天前",
    "sages.time.四天前": "四天前",
    "sages.time.五天前": "五天前",

    "create.title": "风骨创作",
    "create.desc": "以五德立人设，以古风立形象，以声线立气息。写一段心迹，即可生成你的诵读短片。",
    "create.step1": "性格测试",
    "create.step2": "专属人设卡",
    "create.step3": "人设形象",
    "create.step4": "专属音色",
    "create.step5": "诵读短片",
    "create.n1": "壹",
    "create.n2": "貳",
    "create.n3": "參",
    "create.n4": "肆",
    "create.n5": "伍",
    "create.back": "上一步",
    "create.next": "下一步",
    "create.hint": "第 {current} 步 / 共 {total} 步",
    "create.nextBtn0": "生成人设卡",
    "create.nextBtn1": "下一步 · 形象",
    "create.nextBtn2": "下一步 · 音色",
    "create.nextBtn3": "下一步 · 诵读",
    "create.nextBtn4": "生成短视频",
    "create.quizTitle": "性格测试",
    "create.quizTitleEn": "Quiz",
    "create.quizDesc": "完成后由 AI 结合儒家「温、良、恭、俭、让」生成专属人设。",
    "create.answered": "已答 {n} / {total}",
    "create.quizSubmit": "生成我的专属人设卡",
    "create.quizReset": "重新作答",
    "create.quizMiss": "还有 {count} 题未作答",
    "create.quizMiss_plural": "还有 {count} 题未作答",
    "create.personaTitle": "专属人设卡",
    "create.personaTitleEn": "Persona",
    "create.personaDesc": "由性格测试与五德画像生成",
    "create.retake": "重新测试",
    "create.nextFigure": "下一步 · 定制人设形象",
    "create.figureTitle": "人设形象定制",
    "create.figureTitleEn": "Portrait",
    "create.uploadPhoto": "上传个人照片",
    "create.uploadPhotoHint": "JPG / PNG，建议正面半身、光线均匀",
    "create.noPhoto": "尚未选择照片",
    "create.gender": "形象性别",
    "create.male": "男性",
    "create.female": "女性",
    "create.genFigure": "生成古风形象",
    "create.figPreview": "古风形象预览",
    "create.figWait": "待上传照片",
    "create.voiceTitle": "配音音色",
    "create.voiceTitleEn": "Voice",
    "create.voiceDesc": "从系统预设男声、女声中选择诵读配音，或上传 10～20 秒清晰人声克隆自己的声线",
    "create.uploadAudio": "上传音频，克隆我的声音",
    "create.uploadAudioHint": "朗读一段《论语》即可",
    "create.currentVoice": "当前配音",
    "create.noClone": "尚未克隆声线",
    "create.preview": "生成试听",
    "create.useVoice": "用此音色 · 下一步",
    "create.scriptTitle": "诵读短文 · 生成短视频",
    "create.scriptTitleEn": "Recitation",
    "create.scriptDesc": "写下读《论语》后的思考，或一段关于修身、处世、学习与人生态度的文字",
    "create.scriptLabel": "诵读文字",
    "create.scriptPh": "从一句《论语》写起，说到自己这一时的处境……",
    "create.chars": "{count} 字",
    "create.chars_plural": "{count} 字",
    "create.demo": "用示例文本",
    "create.genScript": "按人设生成文案",
    "create.genVideo": "生成诵读短视频",
    "create.download": "下载成片",
    "create.videoWait": "待生成 · 将整合「古风形象 + 文字 + 音色」",
    "create.videoTitle": "诵读短视频预览",
    "create.videoSub": "成片将在此处预览",
    "create.redo": "重做一版",
    "create.voicesMale": "男声",
    "create.voicesFemale": "女声",
    "create.voicesMine": "我的声线",
    "create.cloned": "已克隆",
    "create.myClone": "我的克隆声线",
    "create.systemVoice": "系统音色",
    "create.needQuiz": "请先完成性格测试并生成人设卡",
    "create.needFigure": "请先生成古风形象",
    "create.needPhoto": "请先上传个人照片",
    "create.needGender": "请先选择男性或女性形象",
    "create.needPersonaQuiz": "请先完成性格测试并生成人设卡",
    "create.needQuizOnly": "请先完成性格测试",
    "create.needScript": "请先填写诵读文字",
    "create.needPhotoOrFigure": "请先上传照片或生成古风形象",
    "create.needClone": "请先上传音频并完成声音克隆",
    "create.needCloneShort": "请先上传音频完成克隆",
    "create.cloneHint": "克隆声线请点击「生成试听」",
    "create.refining": "正在由 AI 细化人设分析…",
    "create.personaCreated": "已生成人设卡：{name}",
    "create.aiFallback": "AI 分析暂不可用，已使用本地画像",
    "create.uploading": "上传中 · {filename}",
    "create.uploaded": "已上传 · {filename}",
    "create.uploadedCloning": "已上传 · {filename}，正在克隆…",
    "create.photoOk": "照片上传成功",
    "create.uploadFail": "上传失败，请重试",
    "create.pickGender": "请选择形象性别后生成古风形象",
    "create.uploadingPhoto": "正在上传照片…",
    "create.genFigureBusy": "正在按五官与性别提示词生成古风形象…",
    "create.figDone": "古风形象已生成 · 可进入下一步",
    "create.figDoneToast": "古风形象已生成",
    "create.genFail": "生成失败",
    "create.figFail": "古风形象生成失败",
    "create.audioStart": "音频已上传，开始克隆音色…",
    "create.cloneDone": "克隆完成 · 已选中「我的克隆声线」",
    "create.cloneOk": "音色克隆成功，可点击「生成试听」",
    "create.cloneFail": "音色克隆失败",
    "create.previewBusy": "正在合成试听…",
    "create.previewFail": "试听失败",
    "create.previewPlay": "试听 · {sample}",
    "create.scriptOk": "已按人设生成文案",
    "create.scriptFail": "文案生成失败",
    "create.videoSubmit": "任务已提交，正在合成语音…",
    "create.videoBusy": "正在生成诵读短视频…",
    "create.videoDone": "成片已生成，可预览或下载",
    "create.videoOk": "诵读短视频已生成",
    "create.noJob": "没有拿到视频任务编号",
    "create.videoSlow": "生成时间较长，可稍后再试一次",
    "create.videoFail": "短视频生成失败",
    "create.noDownload": "还没有可下载的成片",
    "create.downloadName": "风骨诵读_{ts}.mp4",
    "create.videoReady": "可预览与下载",
    "create.videoTitleNamed": "{name} · 诵读短片",
    "create.wudeTag": "五德画像 · 以「{virtue}」为主",
    "create.motto": "座右铭",
    "create.tags": "行为标签",
    "create.analysis": "主德「{primary}」，次德「{secondary}」。{line}",
    "create.noPersona": "尚未生成人设卡",

    "wude.温": "温",
    "wude.良": "良",
    "wude.恭": "恭",
    "wude.俭": "俭",
    "wude.让": "让",
    "wudeDesc.温": "温和",
    "wudeDesc.良": "良善",
    "wudeDesc.恭": "恭敬",
    "wudeDesc.俭": "俭素",
    "wudeDesc.让": "谦让",

    "persona.温.name": "温润守正之士",
    "persona.温.line": "沉静自省，待人温和，遇事先看自己那一处。",
    "persona.温.tag0": "不急不躁",
    "persona.温.tag1": "体谅他人",
    "persona.温.tag2": "内省自持",
    "persona.良.name": "良善笃行之士",
    "persona.良.line": "诚恳笃实，重承诺与行动，不愿把话说过头。",
    "persona.良.tag0": "言行相顾",
    "persona.良.tag1": "守信践诺",
    "persona.良.tag2": "就事论事",
    "persona.恭.name": "恭谨端方之士",
    "persona.恭.line": "持重有度，敬事而信，习惯把分寸放在前面。",
    "persona.恭.tag0": "敬事而信",
    "persona.恭.tag1": "守时有节",
    "persona.恭.tag2": "克己有度",
    "persona.俭.name": "俭素自持之士",
    "persona.俭.line": "简素自守，不慕浮华，把心思放在真正要紧的事上。",
    "persona.俭.tag0": "取用有度",
    "persona.俭.tag1": "不慕浮华",
    "persona.俭.tag2": "专注本业",
    "persona.让.name": "谦让有容之士",
    "persona.让.line": "谦和有容，先听后言，善于给别人留余地。",
    "persona.让.tag0": "先听后言",
    "persona.让.tag1": "不争其功",
    "persona.让.tag2": "推己及人",

    "quiz.0.dim": "学习态度",
    "quiz.0.q": "你更倾向于「博学于文」还是「知行合一」？",
    "quiz.0.o0": "先读书，把道理弄明白",
    "quiz.0.o1": "先动手，在事上磨",
    "quiz.0.o2": "边读边做，随时校正",
    "quiz.1.dim": "处事方式",
    "quiz.1.q": "遇到矛盾时，你更愿意怎么做？",
    "quiz.1.o0": "先沟通，再定取舍",
    "quiz.1.o1": "先把原则立住，再谈变通",
    "quiz.1.o2": "能退一步就退一步",
    "quiz.2.dim": "情绪倾向",
    "quiz.2.q": "你更接近哪一种状态？",
    "quiz.2.o0": "沉静自省，惯于内观",
    "quiz.2.o1": "温和开朗，愿意说出来",
    "quiz.2.o2": "内敛持重，不轻易表态",
    "quiz.3.dim": "社交风格",
    "quiz.3.q": "在人多的场合，你更像谁？",
    "quiz.3.o0": "主动帮助别人，先伸手",
    "quiz.3.o1": "默默做好自己的事",
    "quiz.3.o2": "先倾听，不急着评判",
    "quiz.4.dim": "价值取向",
    "quiz.4.q": "你更看重「正直」「诚信」「仁爱」「谦逊」中的哪一项？",
    "quiz.4.o0": "正直",
    "quiz.4.o1": "诚信",
    "quiz.4.o2": "仁爱",
    "quiz.4.o3": "谦逊",
    "quiz.5.dim": "生活态度",
    "quiz.5.q": "你更追求哪一种生活？",
    "quiz.5.o0": "庄重自持，起居有节",
    "quiz.5.o1": "简素自然，不慕浮华",
    "quiz.5.o2": "从容随和，随遇而安",
    "quiz.6.dim": "面对非议",
    "quiz.6.q": "别人误解你时，你通常会？",
    "quiz.6.o0": "先自省，再慢慢解释",
    "quiz.6.o1": "把事实说清楚就好",
    "quiz.6.o2": "能让则让，不必事事辩",
    "quiz.7.dim": "志向格局",
    "quiz.7.q": "你更愿意把自己放在哪一处？",
    "quiz.7.o0": "把眼前一事做精做稳",
    "quiz.7.o1": "把格局打开，敢想敢试",
    "quiz.7.o2": "先安顿身边的人与事",

    "voice.longxiang.name": "苍古沉雄",
    "voice.longxiang.desc": "磁性醇厚，适合沉吟诵读",
    "voice.longshu.name": "沉稳解说",
    "voice.longshu.desc": "从容平稳，吐字清晰",
    "voice.longxiaocheng.name": "明朗通达",
    "voice.longxiaocheng.desc": "阳光清朗，气息开阔",
    "voice.longlaotie.name": "刚健铿锵",
    "voice.longlaotie.desc": "短句有力，骨力较足",
    "voice.longshuo.name": "厚实稳重",
    "voice.longshuo.desc": "声线饱满，适合庄重朗读",
    "voice.longcheng.name": "清朗稳重",
    "voice.longcheng.desc": "干净利落，不疾不徐",
    "voice.longxiaochun.name": "清和冲淡",
    "voice.longxiaochun.desc": "轻声缓语，知性温润",
    "voice.longyuan.name": "温润清雅",
    "voice.longyuan.desc": "柔和雅致，适合慢读",
    "voice.longwan.name": "柔婉从容",
    "voice.longwan.desc": "温柔舒缓，气息绵长",
    "voice.longjing.name": "知性端方",
    "voice.longjing.desc": "沉静有礼，适合讲读",
    "voice.longyue.name": "温暖平和",
    "voice.longyue.desc": "暖声细语，亲近自然",
    "voice.longxiaobai.name": "沉静雅致",
    "voice.longxiaobai.desc": "含蓄内敛，不急不躁",
    "voice.mine.name": "我的克隆声线",
    "voice.mine.desc": "上传音频后生成",

    "me.title": "个人中心",
    "me.login": "登 录",
    "me.register": "注 册",
    "me.username": "名 号",
    "me.password": "密 码",
    "me.userPhLogin": "请输入用户名",
    "me.userPhReg": "取一个研习用的名号",
    "me.pwdPh": "请输入密码",
    "me.loginBtn": "登 录",
    "me.regBtn": "注 册 并 进 入",
    "me.fillBoth": "请填写名号和密码",
    "me.welcome": "欢迎回来，{name}",
    "me.regOk": "注册成功",
    "me.logout": "已退出登录",
    "me.logoutBtn": "退出登录",
    "me.note": "登录后可继续问答、围坐与读书。收藏仍记在这台浏览器里。",
    "me.favCount": "收藏 {count} 部",
    "me.favCount_plural": "收藏 {count} 部",
    "me.toCreate": "生成人设卡",
    "me.local": "本机记录",
    "me.localEn": "Local",
    "me.localDesc": "问答与收藏",
    "me.statAsk": "问答条数",
    "me.statAskSub": "治学 / 修心 / 修身",
    "me.statFav": "书箧收藏",
    "me.statFavSub": "点星收入",
    "me.statConv": "问答会话",
    "me.statConvSub": "留在本机",
    "me.favs": "我的收藏",
    "me.favsEn": "Favorites",
    "me.favCard": "已收藏 · 点此续读",
    "me.favEmpty": "还没有收藏的典籍。在书库点书册右上角的星标，即可收入书箧。",
    "me.recent": "最近问答",
    "me.recentEn": "Ask",
    "me.fromAsk": "智能问答",
    "me.noAsk": "还没有问过。",

    "err.request": "请求没有完成",
    "err.timeout": "等得太久了，可以再试一次",
    "err.legacyAsk": "早先的问答",
    "err.notLogin": "还没有登录。",
    "err.badCreds": "用户名或密码不对。",
    "err.userTaken": "这个用户名已经注册过。",
    "err.userLen": "用户名用 2 到 20 个字，可以是汉字、字母或数字。",
    "err.pwdLen": "密码至少 6 位。",
    "err.photoFmt": "照片请使用 JPG / PNG / WEBP。",
    "err.audioFmt": "音频请使用 MP3 / WAV / M4A。",
    "err.fileSize": "文件过大，请控制在 12MB 以内。",
    "err.noUpload": "没有找到这份上传文件。",
    "err.needScript": "请先填写诵读文字。",
    "err.scriptLen": "诵读文字请控制在 800 字以内。",
    "err.needPhotoFigure": "请先上传照片或生成古风形象。",
    "err.face": "人脸检测未通过：{message}",
    "err.faceHint": "请换一张脸部清晰、无遮挡的正面半身照",
    "err.portraitDetect": "人像检测未通过，请换一张正面半身照",
    "err.emptyQ": "问题是空的。",
  },
};

const ERROR_MAP = [
  ["还没有登录。", "err.notLogin"],
  ["用户名或密码不对。", "err.badCreds"],
  ["这个用户名已经注册过。", "err.userTaken"],
  ["用户名用 2 到 20 个字，可以是汉字、字母或数字。", "err.userLen"],
  ["密码至少 6 位。", "err.pwdLen"],
  ["照片请使用 JPG / PNG / WEBP。", "err.photoFmt"],
  ["音频请使用 MP3 / WAV / M4A。", "err.audioFmt"],
  ["文件过大，请控制在 12MB 以内。", "err.fileSize"],
  ["没有找到这份上传文件。", "err.noUpload"],
  ["请先填写诵读文字。", "err.needScript"],
  ["诵读文字请控制在 800 字以内。", "err.scriptLen"],
  ["请先上传照片或生成古风形象。", "err.needPhotoFigure"],
  ["请换一张脸部清晰、无遮挡的正面半身照", "err.faceHint"],
  ["人像检测未通过，请换一张正面半身照", "err.portraitDetect"],
  ["问题是空的。", "err.emptyQ"],
  ["请求没有完成", "err.request"],
  ["等得太久了，可以再试一次", "err.timeout"],
];

let currentLang = "en";
const listeners = new Set();

function readStoredLang() {
  try {
    const raw = localStorage.getItem(LANG_KEY);
    if (SUPPORTED.includes(raw)) return raw;
  } catch {
    /* ignore */
  }
  return "en";
}

export function getLang() {
  return currentLang;
}

export function isEn() {
  return currentLang === "en";
}

function fill(template, params = {}) {
  return String(template).replace(/\{(\w+)\}/g, (_, key) =>
    params[key] == null ? `{${key}}` : String(params[key]),
  );
}

export function t(key, params) {
  const table = DICT[currentLang] || DICT.en;
  const fallback = DICT.en[key] ?? DICT.zh[key] ?? key;
  const value = table[key] ?? fallback;
  return params ? fill(value, params) : value;
}

/** English-aware plural: use key_plural when count !== 1 */
export function tp(key, count, params = {}) {
  const pluralKey = `${key}_plural`;
  const table = DICT[currentLang] || DICT.en;
  const usePlural = currentLang === "en" ? count !== 1 : false;
  const chosen = usePlural && table[pluralKey] != null ? pluralKey : table[key] != null ? key : pluralKey;
  return t(chosen, { count, ...params });
}

export function te(message) {
  if (!message) return t("err.request");
  const text = String(message);
  for (const [zh, key] of ERROR_MAP) {
    if (text === zh || text.includes(zh)) {
      if (key === "err.face") {
        const m = text.replace(/^人脸检测未通过：/, "");
        return t(key, { message: m });
      }
      return t(key);
    }
  }
  return text;
}

const CONV_TITLE_KEYS = ["study", "heart", "body"].flatMap((mode) => [
  `mode.${mode}.defaultConv`,
  ...[0, 1, 2, 3].map((i) => `mode.${mode}.chip${i}`),
]);

export function modeUi(mode) {
  const chipCount = currentLang === "en" ? 2 : 4;
  return {
    who: t(`mode.${mode}.who`),
    desc: t(`mode.${mode}.desc`),
    label: t(`mode.${mode}.label`),
    defaultConv: t(`mode.${mode}.defaultConv`),
    chips: Array.from({ length: chipCount }, (_, i) => t(`mode.${mode}.chip${i}`)),
  };
}

/** Show a stored chat title in the current UI language. */
export function localizeConvTitle(stored, mode) {
  const raw = String(stored || "").trim();
  const modeKey = ["study", "heart", "body"].includes(mode) ? mode : "study";
  if (!raw) return t(`mode.${modeKey}.defaultConv`);

  for (const key of CONV_TITLE_KEYS) {
    if (raw === DICT.zh[key] || raw === DICT.en[key]) return t(key);
  }

  if (raw.length >= 8) {
    const hits = CONV_TITLE_KEYS.filter((key) => {
      const zh = DICT.zh[key] || "";
      const en = DICT.en[key] || "";
      return (zh && zh.startsWith(raw)) || (en && en.startsWith(raw));
    });
    if (hits.length === 1) return t(hits[0]);
  }

  if (currentLang === "en" && /·\s*求解$/.test(raw)) return raw.replace(/·\s*求解$/, "· Inquiry");
  if (currentLang === "zh" && /·\s*Inquiry$/.test(raw)) return raw.replace(/·\s*Inquiry$/, "· 求解");
  return raw;
}

export function quizUi(index) {
  const optCount = index === 4 ? 4 : 3;
  return {
    dim: t(`quiz.${index}.dim`),
    q: t(`quiz.${index}.q`),
    opts: Array.from({ length: optCount }, (_, i) => ({ t: t(`quiz.${index}.o${i}`) })),
  };
}

export function voiceUi(id, fallbackName = "", fallbackDesc = "") {
  const nameKey = `voice.${id}.name`;
  const descKey = `voice.${id}.desc`;
  const table = DICT[currentLang] || DICT.en;
  return {
    name: table[nameKey] != null ? t(nameKey) : fallbackName || id,
    desc: table[descKey] != null ? t(descKey) : fallbackDesc,
  };
}

export function personaUi(virtue, fallback) {
  const name = t(`persona.${virtue}.name`);
  const line = t(`persona.${virtue}.line`);
  const tags = [0, 1, 2].map((i) => t(`persona.${virtue}.tag${i}`));
  if (!DICT.en[`persona.${virtue}.name`] && fallback) {
    return { name: fallback.name, line: fallback.line, tags: fallback.tags };
  }
  return { name, line, tags };
}

export function wudeDesc(key) {
  return t(`wudeDesc.${key}`);
}

export function wudeLabel(key) {
  return t(`wude.${key}`);
}

export function joinPrompts(id) {
  const key = id === "group" || id === "kongzi" ? id : "_";
  let n = 3;
  if (key === "group" && currentLang !== "en") n = 4;
  if (key === "kongzi" && currentLang === "en") n = 2;
  return Array.from({ length: n }, (_, i) => t(`sages.join.${key}${i}`));
}

export function formatTodayDate(day) {
  if (currentLang === "en") {
    return `${day.toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    })} · ${t("home.todayLabel")}`;
  }
  const week = "日一二三四五六"[day.getDay()];
  return `${day.getFullYear()}年${day.getMonth() + 1}月${day.getDate()}日 · 星期${week} · ${t("home.todayLabel")}`;
}

export function formatGanzhi(raw) {
  if (currentLang === "en") {
    const stem = raw.replace(/年$/, "");
    return t("home.ganzhi", { ganzhi: stem, raw });
  }
  return t("home.ganzhi", { raw, ganzhi: raw });
}

export function localizeTimeLabel(label) {
  if (!label) return "";
  const key = `sages.time.${label}`;
  const table = DICT[currentLang] || DICT.en;
  return table[key] != null ? t(key) : label;
}

export function applyStaticI18n(root = document) {
  root.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (!key) return;
    const attr = el.getAttribute("data-i18n-attr");
    const value = t(key);
    if (attr) {
      attr.split(",").forEach((name) => el.setAttribute(name.trim(), value));
    } else {
      el.textContent = value;
    }
  });
  root.querySelectorAll("[data-i18n-html]").forEach((el) => {
    const key = el.getAttribute("data-i18n-html");
    if (key) el.innerHTML = t(key);
  });
  root.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (key) el.setAttribute("placeholder", t(key));
  });
  root.querySelectorAll("[data-i18n-aria]").forEach((el) => {
    const key = el.getAttribute("data-i18n-aria");
    if (key) el.setAttribute("aria-label", t(key));
  });
  root.querySelectorAll("[data-i18n-title]").forEach((el) => {
    const key = el.getAttribute("data-i18n-title");
    if (!key) return;
    const value = t(key);
    el.setAttribute("title", value);
    if (el.hasAttribute("data-tip")) el.setAttribute("data-tip", value);
  });

  document.title = META[currentLang]?.title || META.en.title;
  const desc = document.querySelector('meta[name="description"]');
  if (desc) desc.setAttribute("content", META[currentLang]?.description || META.en.description);
  document.documentElement.lang = currentLang === "zh" ? "zh-CN" : "en";

  const zhBtn = document.getElementById("langZh");
  const enBtn = document.getElementById("langEn");
  if (zhBtn && enBtn) {
    zhBtn.classList.toggle("on", currentLang === "zh");
    enBtn.classList.toggle("on", currentLang === "en");
    zhBtn.setAttribute("aria-pressed", currentLang === "zh" ? "true" : "false");
    enBtn.setAttribute("aria-pressed", currentLang === "en" ? "true" : "false");
    zhBtn.setAttribute("aria-label", t("lang.toZh"));
    enBtn.setAttribute("aria-label", t("lang.toEn"));
  }
}

export function onLangChange(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

export function setLang(lang, { silent = false, announce = true } = {}) {
  const next = SUPPORTED.includes(lang) ? lang : "en";
  const prev = currentLang;
  if (next === prev) {
    applyStaticI18n();
    return next;
  }
  currentLang = next;
  try {
    localStorage.setItem(LANG_KEY, next);
  } catch {
    /* ignore */
  }
  applyStaticI18n();
  listeners.forEach((fn) => {
    try {
      fn(next, prev);
    } catch {
      /* ignore */
    }
  });
  if (!silent && announce && typeof window !== "undefined") {
    const toast = window.__i18nToast;
    if (typeof toast === "function") {
      toast(t(next === "en" ? "lang.switchedEn" : "lang.switchedZh"));
      if (next === "en" && !sessionStorage.getItem("lunyu.lang.hint")) {
        sessionStorage.setItem("lunyu.lang.hint", "1");
        setTimeout(() => toast(t("lang.booksRemainZh")), 800);
      }
    }
  }
  return next;
}

export function initI18n() {
  currentLang = readStoredLang();
  applyStaticI18n();
  return currentLang;
}
