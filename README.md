# ArduinoControlSystem
```
Программа на pyton, позволяющая управлять ардуиной при помощи созданного интерфейса

ОЧЕНЬ КРАТКАЯ ИНСТРУКЦИЯ! ОБЯЗАТЕЛЬНО!
1. Заходим в последний файл ACS(ArduinoControlSystem), видим ссылку, открываем её и скачиваем exe файл программы.

2. Запускаем программу, видим пустое окно и меню вверху(если программа не открылась, делаем баг репорт)
Есть 3 меню:
  Файл - Сохранение, открытие, автор проекта
  
  Создать - Создание элементов интерфейса, с настройками каждого разберётесь методом тыка.
  
  Подключение - Тут происходит подключение ардуино. В подменю "Порт" мы выбираем необходимый нам порт, 
  если при запуске программа нашла только один порт, он буде выбран автоматически.
  "Скорость" - Скорость общения c ардуиной, по умолчанию - 9600 бод
  "Подключить" - Подключает плату, при успехе поменяется на "Подключено"
  "Отключить" - Думаю понятно что делает
  "Тип сигнала" - В дальнейших обновлениях будет менять оформление посылаемой команды, 
  по умолчаню - начало - $, середина - пробел, Конец - ; 
  
3. Принцип работы программы(Самое важное) Каждый раз когда вы нажимаете на кнопку или передвигаете слайдер,
  программа посылает на ардуину команду, состоящую из двух частей, индекса команды и её значения.
  Индекс это число, которое настраивается в каждом блоке интерфейса(я их называю нодами) индивидуально, это число
  показывает ардуине, к какому конкретно исполнителю стоит применять данную команду.
  Значение(команда, сигнал) это собственно что конкретно нужно сделать с исполнителем, который мы выбрали при помощи индекса
  Все команды оформлены в виде:  ${индекс} {значение};
  Примеры:
  $1 1; - Включить светодиод с индексом 1
  $1 0; - Выключить светодиод с индексом 1
  $2 1; - Включить светодиод с индексом 2
  $2 0; - Выключить светодиод с индексом 2
  $10 90; - Повернуть сервопривод с индексом 10 в положение 90 градусов
  Привязывание исполнителя и индекса происходит в программе самой ардуины
  
Вот и всё, почитать подробнее про каждый пункт программы можно в основной инструкции(а так же про нод "Вход данных")

ОСНОВНАЯ И ПОЛНАЯ ИНСТРУКЦИЯ:

Нод - элемент интерфейса(примечание)

Элементы меню с пояснением

Файл - "Новый" - отчищает окно, не сохраняет текущее
       "Открыть" - открытие файлов с расширением ans - aruino node save, при открытии окно программы закроется,
       а потом снова откроется с интерфейсом.
       "Сохранить" - Сохраняет текущий интерфейс, вместе с координатами и настройками каждого нода.
          Если файл не создан, предложит его создать. После перехода на более свежую версию программы файл сохранения может
          вызывать вылет программы, об этом и как это исправить будет написано в обновлении.
          Файл сохранения поддерживает коментарии, для этого в ПЕРВОМ символе строки пишем "#", и эта 
          строка не будет считана при открытии файла.
       "Сохранить как" - Создание нового сохранения
       "Автор" - Данные о создателе(в будующем о создателях)
       
Создать - Создаёт один из четырёх нодов(пока что четырёх), при создании окно программы закроется и откроется:
      Общая информация о нодах:
          У каждого нода есть несколько стандартных виджетов(виджет - кнопка, строка, поле для ввода, слайдер и т. д.):
            "..." - кнопка перемещения - при зажатии позволяет перемещать виджет
            "▲" - кнопка открытия настроек.
            Все дальнейшие виджеты находятся в настройках и проявляются при их открытии
            "✖" - Удалить нод
            "❐" - Дублировать нод
            "Имя нода" - Меняет имя нода, оно отображается справа от настрое
          Все настройки применяются в реальном времени, кроме размера нода, для 
          него нужно нажать на enter или выбрать другое поле ввода
          
     "Кнопка" - Нод кнопки, потдерживает несколько режимов.
                1 режим - Один сигнал - При нажатии на кнопку просто отправляет сигнал 1(с индексом)
                2 режим - Два сигнала попеременно - при первом нажатии отправляет "сигнал 1" и меняет надпись не кнопке на
                "имя кнопки 1", при втором нажатии отправляет "сигнал 2" и меняет надпись на кнопке на имя "кнопки 2",
                при третьем нажатии отправляет "сигнал 1" и меняет надпись не кнопке на "имя кнопки 1" и т. д.
                3 режим - Два сигнала "нажал-отпустил" - при нажатии отправляет "сигнал 2", при отпускании - "сигнал 1"

                Чекбокс - "Использовать клавиши" позволяет привязать клавишу клавиатуры к кнопке, для этого выбираем чекбокс,
                    нажимаем любую клавишу, и она закрепляется за эти нодом, так же выбранная клавиша появляется под кнопкой
                    Раскладка имеет значение, если вы ввели "F", то при переключении на русскую раскладку программа не отреагирует
                    на "F".
            
     "Слайдер" - Нод слайдера, так же есть несколько режимов:
                1 Режим - "Отправка при отпуске" - отправка сигнала идёт когда вы отпусукаете слайдер
                2 Режим - "Отправка при изменении" - Отправка идёт в реальном времени
                "Минимум" и "Максимум" - устанавливает минимальное и максимальное значение слайдера, 
                    отрицательные числа поддерживаются, обратные нет(min - 100, max - 0)
                "Привязка" - Если введено целое число, то при отпускании слайдера он вернётся в это положение.

     "Поле для ввода" - Просто поле, в которое можно вручную ввести число, и оно вместе с заданым индексом отправится в ардуину
                    Последние 3 числа отображаются под полем

     "Вход данных" - Самый интересный нод, обеспечивает принятие чисел из ардуино, при  этом так же имеются индексы,
              которые позволяют распределять сигналы от ардуино по нескольким нодам.
              для формирования коректного сигнала необходимо послать строку вида - | {индекс} {значение}\n | 
              - (\n - знак переноса строки)
              пример кода для ардуино:
    
              Serial.print("1"); // Индекс, который нужно поставить в ноде
              Serial.print(" "); // Пробел для разделения
              Serial.println(temperature); // Переменная, которая будет выводится в окне

              Внимание! первые две строки это "print", а последняя это "println", так как необходимо в конце команды ставить \n

Для приёма данных рекомендуется исползовать функцию, разработанную AlexGyver, она позволит обеспечить быструю обработку даных


void parsing() {                              // Сама функция, вызываем в начале(или где нужно) void loop()
  if (Serial.available() > 0) {
    char incomingByte = Serial.read();        // обязательно ЧИТАЕМ входящий символ
    if (getStarted) {                         // если приняли начальный символ (парсинг разрешён)
      if (incomingByte != ' ' && incomingByte != ';') {   // если это не пробел И не конец
        string_convert += incomingByte;       // складываем в строку
      } else {                                // если это пробел или ; конец пакета
        intData[index] = string_convert.toInt();  // преобразуем строку в int и кладём в массив
        string_convert = "";                  // очищаем строку
        index++;                              // переходим к парсингу следующего элемента массива
      }
    }
    if (incomingByte == '$') {                // если это $
      getStarted = true;                      // поднимаем флаг, что можно парсить
      index = 0;                              // сбрасываем индекс
      string_convert = "";                    // очищаем строку
    }
    if (incomingByte == ';') {                // если таки приняли ; - конец парсинга
      getStarted = false;                     // сброс
      recievedFlag = true;                    // флаг на принятие
    }


// Переменные, необходимые для работы функции
#define PARSE_AMOUNT 2         // Функция обрабатывает фиксированное количевство чисел, нам ножно 2
int intData[PARSE_AMOUNT];     // массив численных значений после парсинга
boolean recievedFlag;
boolean getStarted;
String string_convert = "";

// Полный пример кода есть в файлах проекта












