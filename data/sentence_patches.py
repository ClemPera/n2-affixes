"""Replacement sentences that fix length, register, or clarity issues.

These are forced ahead of corpus picks during the merge.
"""

PATCHES = {
    "hi_non": [
        {"sense": 1, "ja": "あんなことを彼女に言うなんて、非常識だ。", "en": "It is thoughtless to say such a thing to her."},
        {"sense": 1, "ja": "この資料は非公開なので、見せられない。", "en": "These documents are private, so they cannot be shown."},
    ],
    "mu": [
        {"sense": 2, "ja": "彼の無遠慮な質問に、皆が困った。", "en": "Everyone was troubled by his blunt question."},
    ],
    "mi": [
        {"sense": 1, "ja": "彼は未経験だが、仕事を覚えるのが早い。", "en": "He has no experience, but he learns the job quickly."},
    ],
    "kyuu": [
        {"sense": 1, "ja": "彼女は結婚して旧姓を変えた。", "en": "She got married and changed her maiden name."},
    ],
    "shin": [
        {"sense": 2, "ja": "彼は真剣に将来のことを考えている。", "en": "He is thinking seriously about his future."},
    ],
    "han": [
        {"sense": 1, "ja": "反社会的な行動は法律で禁止されている。", "en": "Antisocial behavior is prohibited by law."},
    ],
    "betsu": [
        {"sense": 1, "ja": "それはまったく別問題なので、後で話し合おう。", "en": "That is a completely separate issue, so let's discuss it later."},
    ],
    "tei": [
        {"sense": 1, "ja": "彼女は低血圧で、朝はいつも具合が悪い。", "en": "She has low blood pressure and always feels ill in the morning."},
        {"sense": 1, "ja": "低価格の商品が人気だが、安全も大事だ。", "en": "Low-priced products are popular, but safety matters too."},
    ],
    "chou_over": [
        {"sense": 1, "ja": "コンサートの会場は超満員で、入れなかった。", "en": "The concert venue was packed, and I could not get in."},
    ],
    "bou": [
        {"sense": 1, "ja": "私のカメラは防水なので、雨の日も使える。", "en": "My camera is waterproof, so I can use it on rainy days."},
        {"sense": 1, "ja": "地震に備えて防災の準備をしておこう。", "en": "Let's prepare for disasters in case of an earthquake."},
    ],
    "hon": [
        {"sense": 1, "ja": "その会社の本社はこの町に移った。", "en": "The company's head office moved to this town."},
    ],
    "sha": [
        {"sense": 1, "ja": "労働者たちは自分の仕事に誇りを持っている。", "en": "The workers take pride in their work."},
    ],
    "ka": [
        {"sense": 1, "ja": "彼は医療の専門家に相談することにした。", "en": "He decided to consult a medical specialist."},
    ],
    "in": [
        {"sense": 1, "ja": "彼女は地方公務員として働いている。", "en": "She works as a local government employee."},
        {"sense": 1, "ja": "私は会社員として五年間働いている。", "en": "I have worked as an office employee for five years."},
    ],
    "chi": [
        {"sense": 1, "ja": "彼の出身地は海に近い小さな町だ。", "en": "His hometown is a small town near the sea."},
    ],
    "ki": [
        {"sense": 1, "ja": "すみません、洗濯機の使い方を教えてもらえませんか。", "en": "Excuse me, could you show me how to use the washing machine?"},
    ],
    "ki_device": [
        {"sense": 1, "ja": "誰かiPhoneの充電器を持っていませんか。", "en": "Does anyone have an iPhone charger?"},
    ],
    "fuu": [
        {"sense": 1, "ja": "日本風の庭を作りたいと思っている。", "en": "I want to make a Japanese-style garden."},
    ],
    "you": [
        {"sense": 1, "ja": "子供用の椅子を買って、部屋に置いた。", "en": "I bought a chair for children and put it in the room."},
    ],
    "shiki": [
        {"sense": 1, "ja": "この部屋は日本式の建物だ。", "en": "This room is a Japanese-style building."},
    ],
    "kan": [
        {"sense": 1, "ja": "彼は責任感が強く、仕事を最後まで続ける。", "en": "He has a strong sense of responsibility and finishes his work."},
    ],
    "ryoku": [
        {"sense": 1, "ja": "彼は想像力が豊かで、いつも新しい話を考える。", "en": "He is imaginative and always thinks up new stories."},
    ],
    "jou_doc": [
        {"sense": 1, "ja": "私は招待状の封筒に住所を書いた。", "en": "I wrote the address on the invitation envelope."},
    ],
    "shou": [
        {"sense": 1, "ja": "試験の日は学生証を忘れないでください。", "en": "Please do not forget your student ID on the exam day."},
    ],
    "chou_book": [
        {"sense": 1, "ja": "彼は電話帳で中古車販売店を探した。", "en": "He looked for a used car dealer in the phone book."},
    ],
    "ban": [
        {"sense": 1, "ja": "この辞書は最新版なので、言葉の意味が新しい。", "en": "This dictionary is the latest edition, so its definitions are current."},
        {"sense": 1, "ja": "この小説の日本語版は来月発売される。", "en": "The Japanese edition of this novel goes on sale next month."},
    ],
    "sei_nature": [
        {"sense": 1, "ja": "この問題の重要性を皆に説明する必要がある。", "en": "We need to explain the importance of this issue to everyone."},
    ],
    "ki_period": [
        {"sense": 1, "ja": "新学期が始まってから、とても忙しい。", "en": "I have been very busy since the new term started."},
    ],
    "kai": [
        {"sense": 1, "ja": "彼は政界に敵が多く、一人で行動している。", "en": "He has many enemies in politics and is isolated."},
    ],
    "gai_out": [
        {"sense": 1, "ja": "今年の夏は海外で過ごしたいと思っている。", "en": "I want to spend this summer abroad."},
        {"sense": 2, "ja": "事故の場合以外は、このボタンを押さないでください。", "en": "Do not press this button except in the case of an accident."},
    ],
    "nai": [
        {"sense": 1, "ja": "国内の旅行なら、電車が便利だ。", "en": "For domestic travel, trains are convenient."},
    ],
    "zumi": [
        {"sense": 1, "ja": "この番号はすでに登録済みなので、変更できない。", "en": "This number is already registered, so it cannot be changed."},
    ],
    "gachi": [
        {"sense": 1, "ja": "今日は曇りがちの天気だが、雨は降らないだろう。", "en": "Today is mostly cloudy, but it probably will not rain."},
    ],
    "ppoi": [
        {"sense": 1, "ja": "彼は飽きっぽい性格で、何をしても続かない。", "en": "He is quick to lose interest, so nothing lasts long with him."},
    ],
    "mi_state": [
        {"sense": 1, "ja": "雪の重みで小屋の屋根が壊れた。", "en": "The roof of the hut broke under the weight of the snow."},
    ],
    "ryuu": [
        {"sense": 1, "ja": "私はギターを自己流で覚えて、今は毎日弾いている。", "en": "I taught myself guitar, and now I play every day."},
    ],
}
