import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

type Theme = "light" | "dark";
type Language = "uz_latn" | "uz_cyrl" | "ru";

interface ThemeContextType {
  theme: Theme;
  language: Language;
  setTheme: (theme: Theme) => void;
  setLanguage: (language: Language) => void;
  t: (key: string) => string;
}

// Tarjimalar
const translations: Record<"uz_latn" | "ru", Record<string, string>> = {
  uz_latn: {
    // Analysis – results & details (missing)
    "analysis.total_score": "Umumiy ball",
    "analysis.match": "Moslik",
    "analysis.risk_level": "Xavf darajasi",
    "analysis.strengths": "Kuchli tomonlar",
    "analysis.weaknesses": "Zaif tomonlar",
    "analysis.price": "Narx",
    "analysis.restart": "Qayta boshlash",
    "analysis.history_price": "Narx",
    "analysis.history_details": "Batafsil",

    // History (missing)
    "history.total": "Jami",
    "history.analyses": "ta tahlil",
    "history.reanalyze": "Qayta tahlil qilish",
    "history.delete_all": "Barchasini o‘chirish",
    "history.details": "Batafsil",
    "history.hide": "Yashirish",
    "history.price": "Narx",

    // Risk levels (missing entirely)
    "risk.low": "Past xavf",
    "risk.medium": "O‘rtacha xavf",
    "risk.high": "Yuqori xavf",
    "risk.critical": "Kritik xavf",
    "risk.undefined": "Aniqlanmagan",

    // Common (missing)
    "common.confirm": "Tasdiqlash",
    "common.success": "Muvaffaqiyatli",

    // Anti-fraud (some headers missing)
    "antifraud.price_anomaly": "Narx anomaliyalari",
    "antifraud.doc_similarity": "Hujjatlar o‘xshashligi",
    "antifraud.collusion": "Kelishilgan takliflar",
    "antifraud.summary": "Xulosa",
    "antifraud.evidence": "Dalillar",

    // Menu
    "menu.dashboard": "Dashboard",
    "menu.analysis": "Tender Tahlili",
    "menu.history": "Tahlil Tarixi",
    "menu.antifraud": "Anti-Fraud",
    "menu.settings": "Sozlamalar",

    // Dashboard
    "dashboard.title": "Bosh sahifa",
    "dashboard.subtitle": "Tanlov AI - Tender tahlil tizimi",
    "dashboard.total_tenders": "Jami Tenderlar",
    "dashboard.active": "faol",
    "dashboard.participants": "Ishtirokchilar",
    "dashboard.applications": "ta ariza",
    "dashboard.evaluations": "Baholashlar",
    "dashboard.ai_analyses": "Sun'iy intellekt tahlillari",
    "dashboard.fraud_risks": "Fraud Xavflari",
    "dashboard.high_risk": "ta yuqori xavf",
    "dashboard.compliance": "Compliance",
    "dashboard.passed": "ta o'tdi",
    "dashboard.refresh": "Yangilash",
    "dashboard.loading": "Yuklanmoqda...",
    "dashboard.error_stats": "Statistika olishda xatolik",
    "dashboard.error_server": "Server bilan aloqa xatosi",
    "dashboard.tender_analysis": "Tender Tahlili",
    "dashboard.tender_analysis_desc":
      "Sun'iy intellekt yordamida tender shartnomasini tahlil qiling va ishtirokchilarni baholang.",
    "dashboard.feature1": "Tender talablarini avtomatik aniqlash",
    "dashboard.feature2": "Ishtirokchilarni har taraflama tahlil",
    "dashboard.feature3": "G'olibni aniqlash va tavsiyalar",
    "dashboard.start_analysis": "Tahlilni Boshlash",
    "dashboard.antifraud_title": "Anti-Fraud Tizimi",
    "dashboard.antifraud_desc":
      "Korrupsiya va firibgarlik belgilarini avtomatik aniqlash.",
    "dashboard.antifraud_feature1": "Metadata o'xshashligini tahlil",
    "dashboard.antifraud_feature2": "Narx anomaliyalarini aniqlash",
    "dashboard.antifraud_feature3": "Kelishilgan takliflarni aniqlash",
    "dashboard.antifraud_btn": "Anti-Fraud Tahlili",

    // Analysis
    "analysis.title": "Tender Tahlili",
    "analysis.subtitle":
      "Sun'iy intellekt yordamida tender hujjatlarini va ishtirokchilarni tahlil qiling",
    "analysis.tender_title": "Tender Hujjati",
    "analysis.tender_desc":
      "Sun'iy intellekt yordamida tahlil qilish uchun tender hujjatini yuklang",
    "analysis.upload_tender": "Tender Hujjatini Yuklang",
    "analysis.upload_tender_desc":
      "Tender hujjatini PDF, DOCX yoki TXT formatda yuklang",
    "analysis.upload_click": "Faylni yuklash uchun bosing",
    "analysis.upload_drag": "yoki faylni shu yerga torting",
    "analysis.analyze_tender": "Tenderni Tahlil Qilish",
    "analysis.analyzing": "Tahlil qilinmoqda...",
    "analysis.tender_info": "Tender Haqida Ma'lumot",
    "analysis.purpose": "Maqsad",
    "analysis.type": "Turi",
    "analysis.requirements_count": "Talablar soni",
    "analysis.mandatory": "majburiy",
    "analysis.main_requirements": "Asosiy Talablar",
    "analysis.weight": "Vazn",
    "analysis.participants": "Ishtirokchilar",
    "analysis.add": "Qo'shish",
    "analysis.participants_desc": "Har bir ishtirokchi hujjatlarini yuklang",
    "analysis.analyzed_participants": "Tahlil Qilingan Ishtirokchilar",
    "analysis.add_more_desc": "Qo'shimcha ishtirokchilar qo'shishingiz mumkin",
    "analysis.add_participant_hint":
      "Ishtirokchi qo'shish uchun \"Qo'shish\" tugmasini bosing",
    "analysis.add_participant": "Ishtirokchi Qo'shish",
    "analysis.company_name": "Kompaniya Nomi",
    "analysis.evaluate_participants": "Ishtirokchilarni Baholash",
    "analysis.at_least_one": "Kamida bitta ishtirokchi qo'shing",
    "analysis.completed": "Tahlil Yakunlandi",
    "analysis.auto_saved": "Natijalar avtomatik saqlandi",
    "analysis.history": "Tarix",
    "analysis.new_analysis": "Yangi tahlil",
    "analysis.history_title": "Tahlil Tarixi",
    "analysis.history_winner": "G'olib",
    "analysis.history_participant": "ishtirokchi",
    "analysis.history_view": "Ko'rish",
    "analysis.start_analysis_wait":
      "Sun'iy intellekt tahlil jarayonini boshlagan, iltimos kuting.",

    // Steps
    "analysis.steps.tender": "Tender",
    "analysis.steps.participants": "Ishtirokchilar",
    "analysis.steps.results": "Natijalar",
    "analysis.error_upload": "Tender faylini yuklang",
    "analysis.error_analysis": "Tahlilda xatolik",
    "analysis.error_server": "Server bilan aloqa xatoligi",
    "analysis.start_analysis": "Tahlilni boshlash",
    "analysis.add_new_participant": "Yangi ishtirokchi qo'shish",
    "analysis.ranking": "Reyting",
    "analysis.winner": "G'olib",
    "analysis.summary": "Xulosa",

    // History
    "history.title": "Tahlil Tarixi",
    "history.subtitle": "Barcha tahlil qilingan tenderlar va natijalar",
    "history.empty": "Tahlil tarixi bo'sh",
    "history.empty_desc": "Tahlil natijalari bu yerda saqlanadi",
    "history.start_first": "Birinchi tahlilni boshlang",
    "history.select": "Tahlilni tanlang",
    "history.select_desc": "Chapdagi ro'yxatdan tahlilni tanlang",
    "antifraud.collusion_desc":
      "Bog'liq kompaniyalar, oldindan kelishilgan g'olib",
    "antifraud.tender_info": "Tender Ma'lumotlari (ixtiyoriy)",
    "antifraud.tender_name": "Tender nomi",
    "antifraud.budget": "Byudjet",
    "antifraud.deadline": "Muddat",
    "antifraud.participants": "Ishtirokchilar",
    "antifraud.participants_desc":
      "Har bir ishtirokchining taklif narxi va hujjatlari haqida ma'lumot kiriting",
    "antifraud.company_name": "Kompaniya nomi",
    "antifraud.offer_price": "Taklif narxi",
    "antifraud.docs_info": "Hujjatlar haqida",
    "antifraud.additional_info": "Qo'shimcha ma'lumot",
    "antifraud.participant": "Ishtirokchi",
    "antifraud.analyze": "Tahlil qilish",
    "antifraud.analyzing": "Sun'iy intellekt tahlil qilmoqda...",
    "antifraud.min_participants": "Kamida 2 ta ishtirokchi kiritish kerak",
    "antifraud.server_error": "Server bilan aloqa xatosi",
    "antifraud.analysis_error": "Tahlilda xatolik",
    "antifraud.new_analysis": "Yangi tahlil",
    "antifraud.overall_risk": "Umumiy xavf darajasi",
    "antifraud.risk_score": "Xavf balli",
    "antifraud.indicators": "Xavf ko'rsatkichlari",
    "antifraud.price_analysis": "Narx tahlili",
    "antifraud.min_price": "Minimal narx",
    "antifraud.max_price": "Maksimal narx",
    "antifraud.avg_price": "O'rtacha narx",
    "antifraud.price_spread": "Narx tarqalishi",
    "antifraud.suspicious_prices": "Shubhali narxlar",
    "antifraud.similarity_analysis": "O'xshashlik tahlili",
    "antifraud.similarity_score": "O'xshashlik darajasi",
    "antifraud.suspicious_patterns": "Shubhali patternlar",
    "antifraud.collusion_analysis": "Kelishuv tahlili",
    "antifraud.collusion_probability": "Kelishuv ehtimoli",
    "antifraud.collusion_indicators": "Kelishuv belgilari",
    "antifraud.recommendations": "Tavsiyalar",

    "antifraud.involved": "Ishtirokchilar",

    // Settings
    "settings.title": "Sozlamalar",
    "settings.subtitle": "Tizim sozlamalarini boshqarish",
    "settings.interface": "Interfeys",
    "settings.theme": "Mavzu",
    "settings.light": "Yorug'",
    "settings.dark": "Qorong'u",
    "settings.language": "Til",
    "settings.analysis_params": "Tahlil Parametrlari",
    "settings.similarity_threshold": "Moslik chegarasi",
    "settings.similarity_desc":
      "Ishtirokchining tender talablariga moslik foizi chegarasi",
    "settings.price_deviation": "Narx og'ishi chegarasi",
    "settings.price_deviation_desc":
      "Narx og'ishi shubhali deb hisoblanadigan chegara",
    "settings.min_participants": "Minimal ishtirokchilar",
    "settings.min_participants_desc":
      "Tahlil uchun minimal ishtirokchilar soni",
    "settings.save": "Saqlash",
    "settings.saved": "Saqlandi!",
    "settings.about": "Tizim haqida",
    "settings.version": "Versiya",
    "settings.about_desc":
      "Tanlov AI - tender jarayonlarini sun'iy intellekt yordamida tahlil qilish tizimi. Ishtirokchilarni baholash, firibgarlikni aniqlash va muvofiqlikni tekshirish imkoniyatlarini taqdim etadi.",
    "settings.features": "Imkoniyatlar",
    "settings.feature1":
      "Sun'iy intellekt yordamida tender hujjatlarini tahlil qilish",
    "settings.feature2": "Ishtirokchilarni avtomatik baholash va reyting",
    "settings.feature3": "Firibgarlik va korrupsiya belgilarini aniqlash",
    "settings.feature4": "O'RQ talablariga muvofiqlikni tekshirish",

    // Common
    "common.loading": "Yuklanmoqda...",
    "common.error": "Xatolik",
    "common.cancel": "Bekor qilish",
    "common.delete": "O'chirish",
    "common.edit": "Tahrirlash",
    "common.view": "Ko'rish",
    "common.search": "Qidirish",
    "common.filter": "Filtr",
    "common.new": "Yangi",
    "common.add": "Qo'shish",
    "common.remove": "Olib tashlash",

    // Login
    "login.title": "Tizimga kirish",
    "login.subtitle": "Davom etish uchun login va parolni kiriting",
    "login.username": "Login",
    "login.password": "Parol",
    "login.username_placeholder": "Login kiriting",
    "login.password_placeholder": "Parol kiriting",
    "login.submit": "Kirish",
    "login.submitting": "Kirish...",
    "login.error": "Login yoki parol noto'g'ri",
    "login.system_desc": "Tender tahlil tizimi",
    "login.copyright": "© 2026 Tanlov AI. Barcha huquqlar himoyalangan.",
  },
  ru: {
    // Menu
    "menu.dashboard": "Панель управления",
    "menu.analysis": "Анализ тендера",
    "menu.history": "История анализов",
    "menu.antifraud": "Анти-мошенничество",
    "menu.settings": "Настройки",

    // Dashboard
    "dashboard.title": "Главная",
    "dashboard.subtitle": "Tanlov AI - Система анализа тендеров",
    "dashboard.total_tenders": "Всего тендеров",
    "dashboard.active": "активных",
    "dashboard.participants": "Участники",
    "dashboard.applications": "заявок",
    "dashboard.evaluations": "Оценки",
    "dashboard.ai_analyses": "ИИ анализы",
    "dashboard.fraud_risks": "Риски мошенничества",
    "dashboard.high_risk": "высокий риск",
    "dashboard.compliance": "Соответствие",
    "dashboard.passed": "прошло",
    "dashboard.refresh": "Обновить",
    "dashboard.loading": "Загрузка...",
    "dashboard.error_stats": "Ошибка получения статистики",
    "dashboard.error_server": "Ошибка соединения с сервером",
    "dashboard.tender_analysis": "Анализ Тендера",
    "dashboard.tender_analysis_desc":
      "Анализируйте тендерные документы и оценивайте участников с помощью ИИ.",
    "dashboard.feature1": "Автоматическое определение требований",
    "dashboard.feature2": "Всесторонний анализ участников",
    "dashboard.feature3": "Определение победителя и рекомендации",
    "dashboard.start_analysis": "Начать Анализ",
    "dashboard.antifraud_title": "Система Анти-мошенничества",
    "dashboard.antifraud_desc":
      "Автоматическое выявление признаков коррупции и мошенничества.",
    "dashboard.antifraud_feature1": "Анализ сходства метаданных",
    "dashboard.antifraud_feature2": "Обнаружение ценовых аномалий",
    "dashboard.antifraud_feature3": "Выявление согласованных предложений",
    "dashboard.antifraud_btn": "Анализ мошенничества",

    // Analysis
    "analysis.title": "Анализ Тендера",
    "analysis.subtitle":
      "Анализируйте тендерные документы и участников с помощью ИИ",
    "analysis.tender_title": "Тендерный Документ",
    "analysis.tender_desc":
      "Загрузите тендерный документ для анализа с помощью ИИ",
    "analysis.upload_tender": "Загрузите Тендерный Документ",
    "analysis.upload_tender_desc":
      "Загрузите тендерный документ в формате PDF, DOCX или TXT",
    "analysis.upload_click": "Нажмите для загрузки файла",
    "analysis.upload_drag": "или перетащите файл сюда",
    "analysis.analyze_tender": "Анализировать Тендер",
    "analysis.analyzing": "Анализируется...",
    "analysis.tender_info": "Информация о Тендере",
    "analysis.purpose": "Цель",
    "analysis.type": "Тип",
    "analysis.requirements_count": "Количество требований",
    "analysis.mandatory": "обязательных",
    "analysis.main_requirements": "Основные Требования",
    "analysis.weight": "Вес",
    "analysis.participants": "Участники",
    "analysis.add": "Добавить",
    "analysis.participants_desc": "Загрузите документы каждого участника",
    "analysis.analyzed_participants": "Проанализированные участники",
    "analysis.add_more_desc": "Вы можете добавить дополнительных участников",
    "analysis.add_participant_hint":
      'Нажмите "Добавить" для добавления участника',
    "analysis.add_participant": "Добавить участника",
    "analysis.company_name": "Название компании",
    "analysis.evaluate_participants": "Оценить Участников",
    "analysis.at_least_one": "Добавьте хотя бы одного участника",
    "analysis.completed": "Анализ завершён",
    "analysis.auto_saved": "Результаты автоматически сохранены",
    "analysis.history": "История",
    "analysis.add_new_participant": "Добавить нового участника",
    "analysis.new_analysis": "Новый анализ",
    "analysis.restart": "Начать заново",
    "analysis.winner": "Победитель",
    "analysis.total_score": "Общий балл",
    "analysis.match": "Соответствие",
    "analysis.risk_level": "Уровень риска",
    "analysis.ranking": "Рейтинг Участников",
    "analysis.strengths": "Преимущества",
    "analysis.weaknesses": "Недостатки",
    "analysis.price": "Цена",
    "analysis.history_title": "История Анализов",
    "analysis.history_winner": "Победитель",
    "analysis.history_participant": "участник",
    "analysis.history_view": "Просмотр",
    "analysis.start_analysis": "Начать анализ",
    // Steps
    "analysis.steps.tender": "Тендер",
    "analysis.steps.participants": "Участники",
    "analysis.steps.results": "Результаты",
    "analysis.error_upload": "Загрузите файл тендера",
    "analysis.error_analysis": "Ошибка анализа",
    "analysis.error_server": "Ошибка соединения с сервером",

    // History
    "history.title": "История Анализов",
    "history.subtitle": "Все проанализированные тендеры и результаты",
    "history.empty": "История анализов пуста",
    "history.empty_desc": "Результаты анализа будут сохранены здесь",
    "history.start_first": "Начать первый анализ",
    "history.total": "Всего",
    "history.analyses": "анализов",
    "history.select": "Выберите анализ",
    "history.select_desc": "Выберите анализ из списка слева",
    "history.reanalyze": "Повторить анализ",
    "history.delete_all": "Удалить всё",
    "history.details": "Подробнее",
    "history.hide": "Скрыть",
    "history.price": "Цена",

    // Anti-Fraud
    "antifraud.title": "Анти-мошенничество",
    "antifraud.subtitle":
      "Выявление признаков коррупции и мошенничества с помощью ИИ",
    "antifraud.price_anomaly": "Ценовые аномалии",
    "antifraud.price_anomaly_desc":
      "Необычно низкие/высокие цены, согласованные цены, демпинг",
    "antifraud.doc_similarity": "Сходство документов",
    "antifraud.doc_similarity_desc":
      "Одинаковые шаблоны, метаданные, ошибки форматирования",
    "antifraud.collusion": "Согласованные предложения",
    "antifraud.collusion_desc":
      "Связанные компании, заранее согласованный победитель",
    "antifraud.tender_info": "Информация о тендере (необязательно)",
    "antifraud.tender_name": "Название тендера",
    "antifraud.budget": "Бюджет",
    "antifraud.deadline": "Срок",
    "antifraud.participants": "Участники",
    "antifraud.participants_desc":
      "Введите информацию о предложении и документах каждого участника",
    "antifraud.company_name": "Название компании",
    "antifraud.offer_price": "Цена предложения",
    "antifraud.docs_info": "О документах",
    "antifraud.additional_info": "Дополнительная информация",
    "antifraud.participant": "Участник",
    "antifraud.analyze": "Анализировать",
    "antifraud.analyzing": "ИИ анализирует...",
    "antifraud.min_participants": "Необходимо минимум 2 участника",
    "antifraud.server_error": "Ошибка соединения с сервером",
    "antifraud.analysis_error": "Ошибка анализа",
    "antifraud.new_analysis": "Новый анализ",
    "antifraud.overall_risk": "Общий уровень риска",
    "antifraud.risk_score": "Балл риска",
    "antifraud.indicators": "Индикаторы риска",
    "antifraud.price_analysis": "Анализ цен",
    "antifraud.min_price": "Минимальная цена",
    "antifraud.max_price": "Максимальная цена",
    "antifraud.avg_price": "Средняя цена",
    "antifraud.price_spread": "Разброс цен",
    "antifraud.suspicious_prices": "Подозрительные цены",
    "antifraud.similarity_analysis": "Анализ сходства",
    "antifraud.similarity_score": "Степень сходства",
    "antifraud.suspicious_patterns": "Подозрительные паттерны",
    "antifraud.collusion_analysis": "Анализ сговора",
    "antifraud.collusion_probability": "Вероятность сговора",
    "antifraud.collusion_indicators": "Признаки сговора",
    "antifraud.recommendations": "Рекомендации",
    "antifraud.summary": "Заключение",
    "antifraud.involved": "Участники",
    "antifraud.evidence": "Доказательство",

    // Settings
    "settings.title": "Настройки",
    "settings.subtitle": "Управление настройками системы",
    "settings.interface": "Интерфейс",
    "settings.theme": "Тема",
    "settings.light": "Светлая",
    "settings.dark": "Тёмная",
    "settings.language": "Язык",
    "settings.analysis_params": "Параметры Анализа",
    "settings.similarity_threshold": "Порог соответствия",
    "settings.similarity_desc":
      "Порог процента соответствия участника требованиям тендера",
    "settings.price_deviation": "Порог отклонения цены",
    "settings.price_deviation_desc":
      "Порог, при котором отклонение цены считается подозрительным",
    "settings.min_participants": "Минимум участников",
    "settings.min_participants_desc":
      "Минимальное количество участников для анализа",
    "settings.save": "Сохранить",
    "settings.saved": "Сохранено!",
    "settings.about": "О системе",
    "settings.version": "Версия",
    "settings.about_desc":
      "Tanlov AI - система анализа тендерных процессов с помощью искусственного интеллекта. Предоставляет возможности оценки участников, выявления мошенничества и проверки соответствия.",
    "settings.features": "Возможности",
    "settings.feature1": "Анализ тендерных документов с помощью ИИ",
    "settings.feature2": "Автоматическая оценка и рейтинг участников",
    "settings.feature3": "Выявление признаков мошенничества и коррупции",
    "settings.feature4": "Проверка соответствия требованиям ОРК",

    // Common
    "common.loading": "Загрузка...",
    "common.error": "Ошибка",
    "common.success": "Успешно",
    "common.cancel": "Отмена",
    "common.confirm": "Подтвердить",
    "common.delete": "Удалить",
    "common.edit": "Редактировать",
    "common.view": "Просмотр",
    "common.search": "Поиск",
    "common.filter": "Фильтр",
    "common.new": "Новый",
    "common.add": "Добавить",
    "common.remove": "Удалить",

    // Risk levels
    "risk.low": "Низкий риск",
    "risk.medium": "Средний риск",
    "risk.high": "Высокий риск",
    "risk.critical": "Критический риск",

    // Login
    "login.title": "Вход в систему",
    "login.subtitle": "Введите логин и пароль для продолжения",
    "login.username": "Логин",
    "login.password": "Пароль",
    "login.username_placeholder": "Введите логин",
    "login.password_placeholder": "Введите пароль",
    "login.submit": "Войти",
    "login.submitting": "Вход...",
    "login.error": "Неверный логин или пароль",
    "login.system_desc": "Система анализа тендеров",
    "login.copyright": "© 2026 Tanlov AI. Все права защищены.",
  },
};

export const latinToCyrillicUz = (input: string): string => {
  if (!input) return input;
  const preserveCase = (src: string, lower: string, upper: string) => {
    if (src === src.toUpperCase()) return upper;
    if (src[0] === src[0].toUpperCase())
      return upper[0] + upper.slice(1).toLowerCase();
    return lower;
  };

  const digraphs: Array<[RegExp, (m: string) => string]> = [
    [/O['’]/g, (m) => preserveCase(m, "Ў", "Ў")],
    [/o['’]/g, () => "ў"],
    [/G['’]/g, (m) => preserveCase(m, "Ғ", "Ғ")],
    [/g['’]/g, () => "ғ"],
    [/Sh/g, () => "Ш"],
    [/sh/g, () => "ш"],
    [/Ch/g, () => "Ч"],
    [/ch/g, () => "ч"],
    [/Ng/g, () => "Нг"],
    [/ng/g, () => "нг"],
    [/Ya/g, () => "Я"],
    [/ya/g, () => "я"],
    [/Yu/g, () => "Ю"],
    [/yu/g, () => "ю"],
    [/Yo/g, () => "Ё"],
    [/yo/g, () => "ё"],
  ];

  let out = input;
  for (const [re, fn] of digraphs) out = out.replace(re, (m) => fn(m));

  const map: Record<string, string> = {
    A: "А",
    a: "а",
    B: "Б",
    b: "б",
    D: "Д",
    d: "д",
    E: "Э",
    e: "э",
    F: "Ф",
    f: "ф",
    G: "Г",
    g: "г",
    H: "Ҳ",
    h: "ҳ",
    I: "И",
    i: "и",
    J: "Ж",
    j: "ж",
    K: "К",
    k: "к",
    L: "Л",
    l: "л",
    M: "М",
    m: "м",
    N: "Н",
    n: "н",
    O: "О",
    o: "о",
    P: "П",
    p: "п",
    Q: "Қ",
    q: "қ",
    R: "Р",
    r: "р",
    S: "С",
    s: "с",
    T: "Т",
    t: "т",
    U: "У",
    u: "у",
    V: "В",
    v: "в",
    X: "Х",
    x: "х",
    Y: "Й",
    y: "й",
    Z: "З",
    z: "з",
  };

  out = out
    .split("")
    .map((ch) => map[ch] ?? ch)
    .join("");

  out = out.replace(/[’']/g, "");
  return out;
};

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [theme, setThemeState] = useState<Theme>(() => {
    const saved = localStorage.getItem("theme");
    return (saved as Theme) || "light";
  });

  const [language, setLanguageState] = useState<Language>(() => {
    const saved = localStorage.getItem("language");
    if (saved === "uz") return "uz_latn";
    if (saved === "ru") return "ru";
    if (saved === "uz_latn" || saved === "uz_cyrl") return saved;
    return "uz_latn";
  });

  useEffect(() => {
    localStorage.setItem("theme", theme);
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  useEffect(() => {
    localStorage.setItem("language", language);
  }, [language]);

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
  };

  const setLanguage = (newLanguage: Language) => {
    setLanguageState(newLanguage);
  };

  const t = (key: string): string => {
    if (language === "uz_cyrl") {
      const base = translations.uz_latn[key] || key;
      return latinToCyrillicUz(base);
    }
    return translations[language]?.[key] || key;
  };

  return (
    <ThemeContext.Provider
      value={{ theme, language, setTheme, setLanguage, t }}
    >
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};

export default ThemeContext;
