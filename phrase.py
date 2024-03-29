from database import add_daily_phrase, get_phrases, get_all_users, set_phrases, user_promotion_exists

audio_easy_phrases = [
    "Hello, nice to meet you!",
    "I enjoy sunny days.",
    "What's your favorite food?",
    "Do you have any hobbies?",
    "I like playing games.",
    "How's your day going?",
    "I have a pet cat.",
    "Do you like to read?",
    "What's your favorite color?",
    "I like watching movies.",
    "Have you traveled much?",
    "What's your dream job?",
    "I enjoy listening to music.",
    "Do you have any siblings?",
    "Let's grab a coffee sometime.",
    "I love nature walks.",
    "What's your favorite season?",
    "I like taking photos.",
    "Pizza or pasta?",
    "I enjoy simple pleasures.",
    "What's your morning routine?",
    "I like to learn new things.",
    "Any weekend plans?",
    "I like to laugh a lot.",
    "Favorite childhood game?",
]

audio_medium_phrases = [
    "The quick brown fox jumps over the lazy dog.",
    "Learning a new language is a fun challenge.",
    "My favorite hobby is programming.",
    "Let's have a cup of coffee.",
    "I can introduce myself in English.",
    "Have you traveled to other countries?",
    "I'm planning to attend a coding meetup soon.",
    "Let's meet for coffee and chat.",
    "The sun sets behind the mountains.",
    "I recently picked up painting as a hobby.",
    "Coffee or tea? What's your preference?",
    "I enjoy exploring new cuisines.",
    "Have you ever tried rock climbing?",
    "I'm planning a weekend getaway.",
    "What's your take on mindfulness meditation?",
    "I love attending outdoor music festivals.",
    "Do you have a favorite quote or saying?",
    "I find architecture and design intriguing.",
    "Let's plan a picnic in the park.",
    "I like to discuss philosophy with friends.",
    "What's the most beautiful place you've visited?",
    "I'm fascinated by ancient history.",
    "Do you have a favorite podcast?",
    "I enjoy building things with my hands.",
    "Have you ever attended a live theater performance?",
    "Let's try cooking a new recipe together.",
    "I find stargazing on clear nights calming.",
    "What's your opinion on virtual reality?",
    "I'm planning to start a book club.",
    "Do you like attending art exhibitions?",
    "I appreciate a good sense of humor.",
    "Let's plan a day at the amusement park.",
    "What's your favorite way to spend a lazy Sunday?",
    "I'm considering taking up a dance class.",
]

audio_hard_phrases = [
    "Ubiquitous serendipity illuminates the human experience.",
    "Ineffable beauty lies within the simplicity of existence.",
    "Nebulous thoughts coalesce into profound insights.",
    "Tranquil rivers weave through the tapestry of nature.",
    "Ephemeral moments crystallize into everlasting memories.",
    "Metamorphosing challenges sculpt the essence of character.",
    "Peregrination unveils the hidden gems of the world.",
    "In the crucible of adversity, resilience is forged.",
    "Arcane knowledge fuels the fires of innovation.",
    "Cacophony dissipates in the presence of mindful silence.",
    "Ambivalence navigates the delicate balance of decisions.",
    "A symphony of ideas orchestrates the creative process.",
    "The quintessence of empathy transcends societal boundaries.",
    "Profound questions echo in the corridors of contemplation.",
    "Abyssal depths of curiosity yield treasures of understanding.",
    "The perennial quest for knowledge is a noble pursuit.",
    "Divergent paths converge in the mosaic of destiny.",
    "Metacognition unveils the labyrinth of self-awareness.",
    "In the crucible of time, legacies are forged.",
    "Surreptitious whispers unveil the secrets of the cosmos.",
    "Epistemological endeavors enrich the human intellect.",
    "Symbiotic relationships harmonize the rhythm of life.",
    "Esoteric wisdom emanates from the ancient scrolls of philosophy.",
    "In the cauldron of innovation, ideas undergo alchemy.",
    "The kaleidoscope of existence refracts myriad perspectives.",
    "Philosophical discourse is the crucible of intellectual refinement.",
]


pronunciation_easy_phrases = [
    "Hello, how are you?",
    "I like pizza.",
    "Can I help you?",
    "Thank you very much!",
    "Have a nice day!",
    "Excuse me, do you have the time?",
    "I'm hungry.",
    "My favorite color is blue.",
    "Nice to meet you.",
    "How do you spell that?",
    "I'm sorry.",
    "Where can I find the train station?",
    "How much does this cost?",
    "Do you speak English?",
    "I need a taxi, please.",
    "Please, pass the salt.",
    "Which programming languages do you know?",
    "When is your birthday?",
    "What is your name?",
    "How are you feeling today?",
]

pronunciation_medium_phrases = [
    "Could you please clarify that point?",
    "The implications of this decision are significant.",
    "I'm interested in learning more about your culture.",
    "How do you reconcile these conflicting viewpoints?",
    "The intricacies of international relations are intriguing.",
    "This concept requires further exploration.",
    "What do you think is the root cause of this issue?",
    "Can you provide some context for that statement?",
    "I'm not entirely convinced by your argument.",
    "The nuances of language can be challenging to grasp.",
    "Could you elaborate on that point?",
    "What are the underlying assumptions here?",
    "I appreciate your perspective on this matter.",
    "How can we mitigate the potential risks?",
    "I'm intrigued by the complexities of human behavior.",
    "What are the implications for future generations?",
]

pronunciation_hard_phrases = [
    "The intricacies of quantum mechanics are fascinating.",
    "Engaging in philosophical discourse enriches the mind.",
    "Linguistic nuances play a pivotal role in effective communication.",
    "Computational algorithms underpin modern artificial intelligence systems.",
    "The dynamics of global geopolitics are constantly evolving.",
    "The human brain is a marvel of complexity.",
    "The ethics of genetic engineering are highly contentious.",
    "Quantum computing has the potential to revolutionize industries.",
    "The intricacies of constitutional law are fascinating to study.",
    "The complexities of the human psyche are endlessly intriguing.",
    "The principles of sustainable development are crucial for our future.",
    "The philosophy of science raises profound questions about reality.",
    "The intricacies of financial markets require careful analysis.",
    "The implications of social media on society are multifaceted.",
    "The complexities of healthcare policy warrant thorough examination.",
    "The interplay between technology and society shapes our future.",
]


daily_phrases = [
    "Break a leg! - Ни пуха, ни пера!",
    "It's a piece of cake. - Это проще простого.",
    "The ball is in your court. - Теперь твой ход.",
    "Bite the bullet. - Зуб даю!",
    "Hit the hay. - Иди ко сну.",
    "Burn the midnight oil. - Работать всю ночь.",
    "Jump on the bandwagon. - Пойти в ногу со временем.",
    "Cost an arm and a leg. - Стоить целое состояние.",
    "See eye to eye. - Понимать друг друга.",
    "The early bird catches the worm. - Кто рано встаёт, тому Бог подаёт.",
    "Hit the nail on the head. - Попасть в самую точку.",
    "The best of both worlds. - Лучшее из обоих миров.",
    "Throw in the towel. - Сдаться.",
    "Burn bridges. - Сжечь мосты.",
    "Bite off more than you can chew. - Взять слишком много на себя.",
    "Under the weather. - Под погодой.",
    "Cut to the chase. - Перейти к сути.",
    "Hit the books. - Учиться, зубрить.",
    "The world is your oyster. - Мир у твоих ног.",
    "Every cloud has a silver lining. - Нет худа без добра.",
    "Straight from the horse's mouth. - Из первых уст.",
    "Let the cat out of the bag. - Выдать секрет.",
    "A drop in the ocean. - Капля в море.",
    "Actions speak louder than words. - Дела говорят громче слов.",
    "Barking up the wrong tree. - Пошёл не туда.",
    "Better late than never. - Лучше поздно, чем никогда.",
    "The devil is in the details. - Дьявол кроется в деталях.",
    "Don't count your chickens before they hatch. - Не говори гоп, пока не перепрыгнешь.",
    "Caught between a rock and a hard place. - Между молотом и наковальней.",
    "Let sleeping dogs lie. - Не буди лихо, пока оно тихо.",
    "In the heat of the moment. - В порыве страсти.",
    "All bark and no bite. - Много слов, мало дела.",
    "Beat around the bush. - Ходить вокруг да около.",
    "Cost a pretty penny. - Стоить целое состояние.",
    "Cutting corners. - Идти на понижение.",
    "Fish out of water. - Рыба без воды.",
    "Keep your eyes peeled. - Быть начеку.",
    "Let bygones be bygones. - Забыть прошлое.",
    "Take with a grain of salt. - Не воспринимать всерьёз.",
    "When it rains, it pours. - Беда не приходит одна.",
]


# Добавляем в бд новые фразы, для функции "Фраза дня"
def add_daily_phases(new_phrases):
    for phrase in new_phrases:
        add_daily_phrase(phrase)


# Добавляем в бд новые фразы для режима "Аудирование"
def add_phrase(difficult_lvl, new_phrases):
    users = get_all_users()
    for user in users:
        if user_promotion_exists("user_audio_promotion", user):
            phrases = get_phrases("user_audio_promotion", user, difficult_lvl)
            phrases.extend(new_phrases)
            set_phrases("user_audio_promotion", user, difficult_lvl, phrases)
