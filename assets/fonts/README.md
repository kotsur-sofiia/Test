# Локальные шрифты Woman

Актуальный набор подключается в `../../typography.css` без внешнего шрифтового сервиса.

| Роль | Гарнитура | Начертание |
| --- | --- | --- |
| Главные заголовки h1/h2 | Cormorant Garamond | Medium 500 |
| Названия фаз цикла | Croogla (временно Inter) | SemiBold 600 для аналога |
| Подзаголовки h3–h6 и подписи групп | Noto Serif | Regular 400 |
| Число дня цикла | Lora | Regular 400 |
| Другие крупные числовые показатели | Noto Serif Display | Regular 400 |
| Основной текст, темы, кнопки, навигация | Inter | Regular 400 |
| Акцент «ЗАДЕРЖКА» в блоке цикла | Lora | Bold 700 |

Блок цикла воспроизводит отдельный референс 1080 × 1080: оригинальная Lora
(локальный variable WOFF, 400/700) используется для «фаза», числа и «ЗАДЕРЖКА».
Croogla Regular/Light и Circe Regular не предоставлены. С согласия пользователя
временно используются Inter SemiBold 600, настоящий Inter Light 300 и Inter
Regular 400 соответственно. Имена оригинальных гарнитур оставлены первыми в
переменных `--cycle-phase-font`, `--cycle-label-font`, `--cycle-caption-font`.
При появлении файлов оригиналов нужно подключить их и повторно сверить метрики.
Lora и Inter получены из официальных `google/fonts/ofl/lora` и `ofl/inter`;
лицензии SIL OFL находятся рядом. Контрольная композиция —
`../../docs/cycle-type-reference.html`.

Прямые статические WOFF-файлы получены из официальных variable TTF в [google/fonts](https://github.com/google/fonts/tree/main/ofl) с помощью fontTools `instantiateVariableFont`: ось `wght` установлена в 400/600, остальные оси — в значения по умолчанию. Искусственные жирность и курсив отключены. Лицензии SIL OFL лежат рядом с каждой гарнитурой.

Исходные каталоги Google Fonts: `notoserif`, `notoserifdisplay`, `inter`, `notosansarabic`, `notonaskharabic`, `notosanshebrew`, `notoserifhebrew`, `notosansdevanagari`, `notoserifdevanagari`, `notosanssc`, `notoserifsc`, `notosanstc`, `notoseriftc`, `notosansjp`, `notoserifjp`, `notosanskr`, `notoserifkr`.

Для локализованного документа или фрагмента нужно установить корректный HTML-атрибут `lang`. CSS сохраняет иерархию и выбирает:

| Языковой набор | Основной текст | Заголовки |
| --- | --- | --- |
| Арабский / персидский / урду | Noto Sans Arabic | Noto Naskh Arabic |
| Иврит / идиш | Noto Sans Hebrew | Noto Serif Hebrew |
| Хинди / маратхи / непальский | Noto Sans Devanagari | Noto Serif Devanagari |
| Китайский, упрощённый (`zh`, `zh-Hans`) | Noto Sans SC | Noto Serif SC |
| Китайский, традиционный (`zh-Hant`, `zh-TW`, `zh-HK`, `zh-MO`) | Noto Sans TC | Noto Serif TC |
| Японский | Noto Sans JP | Noto Serif JP |
| Корейский | Noto Sans KR | Noto Serif KR |

Латиница, кириллица и греческий используют основной набор. Для крупных чисел первым остаётся Noto Serif Display с региональной serif-гарнитурой для отсутствующих знаков. Региональные Sans содержат настоящие 400 и 600. Это шрифтовая подготовка локализации; тексты интерфейса остаются русскими.

Service worker предварительно сохраняет основные WOFF-файлы, включая Cormorant Garamond. Региональные гарнитуры загружаются по мере использования и затем сохраняются для офлайн-работы. Полный CJK-набор не скачивается при установке русского приложения. Cormorant Garamond подключён локально как variable WOFF с настоящими начертаниями 300–700; главные заголовки используют 500, названия фаз — 600. Остальные прежние шрифты сохранены для исторических CSS-слоёв.
