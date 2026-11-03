# Локальные шрифты Woman

Актуальный набор подключается в `../../typography.css` без внешнего шрифтового сервиса.

| Роль | Гарнитура | Начертание |
| --- | --- | --- |
| Заголовки и названия фаз | Noto Serif | Regular 400 |
| Крупные числовые показатели | Noto Serif Display | Regular 400 |
| Основной текст, темы, кнопки, навигация | Inter | Regular 400 |
| Акцент «ЗАДЕРЖКА» | Inter | SemiBold 600 |

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

Service worker предварительно сохраняет четыре основных WOFF-файла. Региональные гарнитуры загружаются по мере использования и затем сохраняются для офлайн-работы. Полный CJK-набор не скачивается при установке русского приложения. Старые шрифты сохранены для исторических CSS-слоёв, но новая типографика их переопределяет.
