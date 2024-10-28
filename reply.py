import os
import random
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# قائمة الكلمات والردود المحددة
WATCH_WORDS_RESPONSES = {
    'كوكب': ['موجود عايز اى بوشك ده😒', 'ثانيه واحده بتشقط وجى🙄', 'شفلك كلبه❤️😂', 'عندك امانة الكوفي؟ ☕', 'كوكب الصباح أحلى معك 😍'],
    'بحبك': ['وانا كمان بعشقك يا {mention} 💋🥰', 'لو تدري كم أحبك يا عمري 😍', 'أنت النجم اللي بيضوي في سما قلبي ❤️', 'ما في أحلى من حبك يا غالي 🌹', 'كل يوم وأنا أحبك أكثر وأكثر ❤️'],
    'خاص': ['عيب 🌚', 'هتعمل اي في الخاص يسافل 🤓', 'ممنوع تقول هكذا في الخاص 😡', 'لا تتجاوز الخطوط يا صاحب الأخلاق 🌟', 'فكر في غيرك قبل نفسك يا حبيبي 😌'],
    'حصل': ['عباس بيتصل', 'حصل وجبنه😂❤️', 'حصل حصل يا فاتن 😄', 'حصل والله وحصل 😎', 'كل شيء بيحصل بإذن الله 🌟'],
    'بقولك': ['قول اي؟..', 'قول 🧐 ', 'حاضر قول 🤔', 'قول وما تقول كتير 🤨', 'لكن قلت قبل كده 😄'],
    'مرحبا': ['مرحباً {mention} 🌟', 'مرحبا يا أهل الخير 🤗', 'هلا وغلا يا عسل 🍯', 'مرحباً يا صديقي، كيف حالك؟ 🌞', 'مرحباً يا غالي، اشتقت لك 🥰'],
    'تعبان': ['لا تتعب نفسك كثير، ارتاح شوي 🤗', 'خذ قسطًا من الراحة، تستاهل ❤️', 'الله يعينك، راحة البال أهم 😌', 'كلنا بنمر بأوقات صعبة، اتمسك يا غالي 🌟', 'احكي لي، ربما يخفف عنك شوي 🤗'],
    'جميل': ['أنت الجميل في عيني يا {mention} 😍', 'كل يوم وأنت أجمل 🌹', 'جمالك بيجذب القلوب ❤️', 'الجمال داخلي قبل خارجي يا غالي 🌟', 'الجمال موجود في كل شيء حولنا، بس يبقى أحلى فيك 😍'],
    'هلو': ['هلو يا {mention} 🙋‍♂️', 'هلو هلو هلووو 🎉', 'هلا بالغالي 🤗', 'هلو كيف حالك اليوم؟ 🌞', 'هلو يا غالي، اتفضل 🥳'],
    'غريب': ['الدنيا مليئة بالغرائب والعجائب يا صديقي 😄', 'كل يوم فيه شيء جديد وغريب 🤔', 'غريب اللي بتقوله بصراحة 😅', 'الحياة مليئة بالمفاجآت والغرائب، استمتع بكل لحظة 🌟', 'غريب أنت لما تقول كده 😄'],
    'صباح': ['صباح الخير يا {mention} 🌞', 'صباح النور والسرور 🌟', 'صباحك ورد يا غالي 🌹', 'صباح الحب والأمل والسعادة يا صديقي 🌅', 'صباح الخير يا غالي، كيف كانت ليلتك؟ 🌟'],
    'مساء': ['مساء الخير يا {mention} 🌙', 'مساء الورد والياسمين 🌸', 'مساء النور والسرور يا أحلى وردة 🌹', 'مساء الأمل والسعادة والحب يا غالي 🌟', 'مساء الخير يا صديقي، كيف كان يومك؟ 🌟'],
    'تحب': ['أحب الأشياء الجميلة، مثلك يا {mention} 😍', 'أنا أحب كل شيء يجلب السعادة 🥰', 'الحب هو لغة القلوب يا صديقي ❤️', 'أحب الحياة وأحب الناس الطيبة مثلك 🌟', 'الحب هو الشيء الوحيد الذي يجعل العالم أجمل 🌍❤️'],
    'عرفان': ['عرفان رائع ومميز، أحب الحديث معه 🌟', 'عرفان يا روحي وقلبي، كيفك؟ ❤️', 'أنا سعيد جدًا بالتعرف على عرفان 🤗', 'عرفان يا غالي، أنت شخص رائع ومحبوب من الجميع 🌟', 'عرفان هو الصديق الوفي الذي نتمنى أن يكون لدينا دائمًا 🌟'],
    'ربنا': ['ربنا يحفظك ويبارك فيك يا {mention} 🙏', 'ربنا يسهل أمورك ويوفقك في كل خطوة 🌟', 'ربنا يديم عليك الصحة والعافية يا غالي 🙌', 'ربنا يرزقك السعادة والهناء يا صديقي 🌟', 'ربنا يحفظك من كل شر ويقويك على الخير 🙏'],
    'هيه': ['هيه هيه، شو الجديد؟ 😄', 'هيه يا غالي، كيف الحال؟ 🤗', 'هيه هيه، وشوفنا شو الأخبار 🌟', 'هيه يا صديقي، اتفضل وحكي 🎉', 'هيه يا غالي، كيف كان يومك؟ 😊'],
    'ياه': ['ياه يا {mention}، وش هالحلاوة؟ 😍', 'ياه يا حلو، تحفة الله يحفظك 🌸', 'ياه يا غالي، لا تحرمنا من وجودك 🙏', 'ياه يا صديقي، كيف الحال؟ 🤗', 'ياه يا غالي، شو الجديد معك؟ 🌟'],
    'ههه': ['ههههههه، دائمًا تضحكني يا {mention} 😂', 'هههه، أنت دائمًا تضيف الفرحة للجميع 🌟', 'هههه، يا رب دائمًا تبقى مبتسمًا وسعيدًا 😄', 'ههههه، أنا أحب أن أراك تضحك وتستمتع 🤗', 'ههه، الضحكة الجميلة تزيد الحياة روعة 🌟'],
    'أمور': ['كل شيء تمام، أموري بخير والحمد لله 🙌', 'أموري طيبة، شكرًا على السؤال يا {mention} 🌟', 'أموري تمام، أنا هنا للإستمتاع بوقتي معكم 🥰', 'أموري ممتازة، أنا هنا للإستمتاع بوقتي معكم 🌟', 'كل شيء على ما يرام، شكرًا على السؤال 🌟'],
    'أمل': ['الأمل هو دائمًا السماء الزرقاء في حياتنا يا {mention} 🌈', 'الأمل هو الشمعة التي تضيء ظلام الحياة 🕯️', 'الأمل هو القوة التي تجعلنا نواصل المسير في الحياة 🚀', 'الأمل هو السر وراء كل بداية جديدة 🌟', 'الأمل هو الذي يجعل الحياة جميلة وقيمة 🌟'],
    'يوم': ['كل يوم جديد هو فرصة لبداية جديدة ومشرقة يا {mention} 🌅', 'اليوم هو هدية، لذلك نستمتع به ونقدره 🎁', 'كل يوم هو فرصة لتكون أفضل من الأمس 🌟', 'اليوم هو فرصة جديدة لتحقيق الأحلام والأهداف 🌟', 'كل يوم هو مغامرة جديدة، استمتع بكل لحظة 🌟'],
  'كويس': ['كويس يا {mention}، ازيك؟ 😄', 'الحمد لله، كويس وأنت؟ 😊', 'كويس ومبسوط لما أتواجد معاكم 🌟', 'الله يخليك، كويس يا غالي 🌹', 'كويس والله، اتمنى أنك كمان كويس 🌟'],
    'حبيبي': ['أنت حبيبي يا {mention}، انت الغالي عليا ❤️', 'حبيبي دائماً معاكم يا غالي 🥰', 'أنت الحبيب يا صديقي، مش حتقدر تكون أحلى 😍', 'حبيبي أنت اللي بتضيء يومي 🌟', 'حبيبي يا روحي، كيف حالك؟ 🌹'],
    'مصر': ['مصر أم الدنيا وأنا فتخي، يا رب دايماً تحفظها 🇪🇬', 'مصر في قلبي وروحي، دايماً فخور بأصولي 🌟', 'أنا من مصر وأفتخر، أرض الأمان والحضارة 🌹', 'مصر أحلى بلد في الدنيا والله 🥰', 'مصر أم الدنيا وفخور إني مصري 🇪🇬'],
    'بلد': ['مصر أجمل بلد في الدنيا، انت فاكر غير كده؟ 🌟', 'مصر بلد الحضارات والتاريخ العريق، وأنا فخور بأني مصري 🇪🇬', 'بلدنا مصر دايماً بتفتخر بتاريخها وحضارتها 🌹', 'مصر بلد الجمال والأمان، أنا مش بحب غيرها 🥰', 'مصر أحلى بلد في الدنيا وكلها حب وجمال 🇪🇬'],
    'يا حبيبي': ['يا حبيبي أنت الغالي يا {mention}، كيفك؟ 🌟', 'يا حبيبي يا روحي، متميز كالعادة 😍', 'يا حبيبي يا صديقي، متى ما اتصلت بيني تكون الدنيا طيبة 🌹', 'يا حبيبي يا غالي، كل يوم وأنت أحلى 🥰', 'يا حبيبي، معاك دايماً كويس 🌟'],
    'يلا': ['يلا يا {mention}، نشد الرحال ونمشي 😄', 'يلا يا غالي، ورايحين فين؟ 🌟', 'يلا يا صديقي، ونتفاعل ونضحك شوية 😂', 'يلا يا حبيبي، ونبدأ اليوم بنشاط وحيوية 🌹', 'يلا يا غالي، ونتحرك ونتمتع بالحياة 🥰'],
    'عامل ايه': ['عامل ايه يا {mention}، ازيك؟ 🌟', 'عامل ايه يا حبيبي، كيف الحال؟ 😄', 'عامل ايه يا غالي، أنا هنا لأسمعك وأتفاعل معاك 🌹', 'عامل ايه يا صديقي، كيف يومك؟ 🌟', 'عامل ايه يا حبيبي، وينك كل هذا الوقت؟ 🥰'],
    'هناك': ['هناك مكان جميل إسمه مصر، انت عارفه؟ 🇪🇬', 'هناك في القلب دائماً، مش بعيد 🌹', 'هناك في الذاكرة والقلب، ليس بعيدًا 🌟', 'هناك مكان يسمى مصر وأنا أفتخر أني منها 🇪🇬', 'هناك مكان في القلب، وفيه الحب والمودة للجميع 🌹'],
    'كلمة': ['كلمة مصرية دايماً بتحمس وبتبهج القلب، انت شايف؟ 🇪🇬', 'كلمة مصرية مثل الحلاوة، أحلى منها مش هتلاقي 🍯', 'كلمة مصرية دايماً بتحمل معاني وجمال 🌟', 'كلمة مصرية بترجع الروح للقلب والنشاط للحوار 🌹', 'كلمة مصرية دايماً بتشعرك بالطاقة والحيوية 🌟'],
    'مصر': ['مصر أم الدنيا 🇪🇬', 'مصري وأفتخر 🌟', 'من مصر والفخر معاها 🇪🇬', 'مصر الحضارة والتاريخ 🌍', 'مصر الحب والسلام 🌹'],
    'حبيبي': ['حبيبي دائمًا جنبي ❤️', 'حبيبي والله 😍', 'حبيبي أنت الأغلى 🥰', 'حبيبي يا غالي 🌹', 'حبيبي يا حلو 🌟'],
    'كويس': ['كويس ومتميز 🌟', 'كويس يا حبيبي 😄', 'كويس والله 🥰', 'كويس والحمدلله 🌹', 'كويس وعلى الأحسن 🌟'],
    'يلا': ['يلا يا غالي نروح 🚀', 'يلا يا حبيبي نتكلم 🗨️', 'يلا ونتفاعل شوية 😄', 'يلا يا صديقي نبدأ 🌟', 'يلا ونضحك شوية 😂'],
    'عامل ايه': ['عامل ايه يا حبيبي؟ 😄', 'عامل ايه يا غالي؟ 🌹', 'عامل ايه يا صديقي؟ 😍', 'عامل ايه يا حلو؟ 🌟', 'عامل ايه يا حبيبي؟ 🥰'],
    'يا حبيبي': ['يا حبيبي والله دايمًا 🌟', 'يا حبيبي والله عليك 😍', 'يا حبيبي انت الأغلى 🌹', 'يا حبيبي مش زيك 🥰', 'يا حبيبي يا غالي 🌟'],
    'تمام': ['تمام والله 🌹', 'تمام ومبسوط 🌟', 'تمام والحمدلله 🌹', 'تمام والله على الأحسن 🥰', 'تمام يا حبيبي 😄'],
    'وحشتني': ['وحشتني يا حبيبي 🥺', 'وحشتني والله 😍', 'وحشتني يا غالي 🌹', 'وحشتني يا حبيبي الغالي 🌟', 'وحشتني يا حلو 🥰'],
    'فرحان': ['فرحان بحضوركم 🌟', 'فرحان ومبسوط 🥰', 'فرحان والله 🌹', 'فرحان بأوقاتكم 🌟', 'فرحان وعلى الأحسن 🌹'],
    'هناك': ['هناك في القلب دائمًا 🌹', 'هناك والروح معاها 🌟', 'هناك وأفتكركم 🥰', 'هناك في ذاكرتي 🌹', 'هناك ودائمًا معكم 🌟'],
    'كلمة': ['كلمة مصرية والقلب معاها 🇪🇬', 'كلمة بتضيف على الحياة 😄', 'كلمة مصرية والروح معاها 🌹', 'كلمة تفتح القلب 🥰', 'كلمة وبس 🌟'],
    'كوكب': ['موجود عايز اى بوشك ده😒', 'ثانيه واحده بتشقط وجى🙄', 'شفلك كلبه❤️😂'],
    'بحبك': ['وانا كمان بعشقك يا {mention} 💋🥰'],
    'خاص': ['عيب 🌚', 'هتعمل اي في الخاص يسافل 🤓'],
    'احا': ['ايه ده احا يا مان 😂', 'احا مين احنا لسه هنا 😅'],
    'مالك': ['مالك حبيبى🥺', 'مالك يا جميل 😎'],
    'اري': ['اري مثل هاذا 🙄', 'اري إيه يعني؟ 😅'],
    'جميلة': ['أنتي الجميلة ديه يا حبي 😍', 'جميلة مثلك يا {mention} ❤️'],
    'سافل': ['هتعمل اي في الخاص يسافل 🤓', 'لا تكون سافل يا {mention} 😂'],
    'كلبه': ['شفلك كلبه❤️😂', 'مين ده كلبه ده يا {mention} 🤔'],
    'حبيبى': ['حبيبى انت يا {mention} 😘', 'حبيبى ده اللى يتكلم 🤨'],
    'تمام': ['تمام يا معلم 😎', 'كله تمام يا {mention} 👍'],
    'مشغول': ['مشغول في ايه يا {mention}؟', 'مشغول ولا ايه يا {mention} 😒'],
    'كده': ['كده ايه يا {mention}؟', 'كده ده اللى هتقوله؟ 😅'],
    'هنا': ['احنا هنا ده اللى يهمنا 🙌', 'هنا ده العيش والفلوس 😂'],
    'شغل': ['شغل في ايه يا {mention}؟', 'ايه الشغل ده يا {mention}? 😕'],
    'ايه': ['ايه ده يا {mention}؟', 'ايه الجديد يا {mention}? 🤔'],
    'نجوم': ['نجوم في السما ونجوم في الأرض، متليش عليهم 😂', 'نجوم وكمان قمر على الرصيف يا {mention} 🌟'],
    'حلو': ['حلو قوي يا {mention} 😍', 'حلو يا حبيبي، زيك يا {mention} ❤️'],
    'مالك': ['مالك حبيبى🥺', 'مالك يا جميل 😎'],
    'اري': ['اري مثل هاذا 🙄', 'اري إيه يعني؟ 😅'],
    'جميلة': ['أنتي الجميلة ديه يا حبي 😍', 'جميلة مثلك يا {mention} ❤️'],
    'سافل': ['هتعمل اي في الخاص يسافل 🤓', 'لا تكون سافل يا {mention} 😂'],
    'كلبه': ['شفلك كلبه❤️😂', 'مين ده كلبه ده يا {mention} 🤔'],
    'حبيبى': ['حبيبى انت يا {mention} 😘', 'حبيبى ده اللى يتكلم 🤨'],
    'تمام': ['تمام يا معلم 😎', 'كله تمام يا {mention} 👍'],
    'مشغول': ['مشغول في ايه يا {mention}؟', 'مشغول ولا ايه يا {mention} 😒'],
    'كده': ['كده ايه يا {mention}؟', 'كده ده اللى هتقوله؟ 😅'],
    'هنا': ['احنا هنا ده اللى يهمنا 🙌', 'هنا ده العيش والفلوس 😂'],
    'شغل': ['شغل في ايه يا {mention}؟', 'ايه الشغل ده يا {mention}? 😕'],
    'ايه': ['ايه ده يا {mention}؟', 'ايه الجديد يا {mention}? 🤔'],
    'نجوم': ['نجوم في السما ونجوم في الأرض، متليش عليهم 😂', 'نجوم وكمان قمر على الرصيف يا {mention} 🌟'],
    'حلو': ['حلو قوي يا {mention} 😍', 'حلو يا حبيبي، زيك يا {mention} ❤️'],

    # إضافة ردود ضحك وتحشيش
    'اه': ['الشارع الي وراه 🤣', 'وجع ولا دلع'],
}

TELEGRAM_TOKEN = "7937133144:AAFoe6xt2zyyRl7Gqf8FRQ087xgYmXbqcSA"

def reply_to_watch_word(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text.lower()
    for word, responses in WATCH_WORDS_RESPONSES.items():
        if word in message_text:
            random_response = random.choice(responses)
            
            user_id = update.message.from_user.id
            first_name = update.message.from_user.first_name
            
            # إنشاء منشن أزرق لاسم المستخدم
            user_mention = f"<a href='tg://user?id={user_id}'>{first_name}</a>"
            
            # تنسيق الرد مع ذكر اسم المستخدم كرابط
            response_with_mention = random_response.format(mention=user_mention)
            update.message.reply_html(response_with_mention)
            break

def main() -> None:
    updater = Updater(TELEGRAM_TOKEN)

    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), reply_to_watch_word))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
