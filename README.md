# FHIRstruct 
Набор программных модулей для структурирования текстовых медицинских записей с использованием международного медицинских стандартов FHIR и SNOMED CT для обеспечения интероперабельности данных. Структурирование производится на примере аллергологических анамнезов. 

UML-диаграмма модулей 
![image](https://user-images.githubusercontent.com/47714995/136579591-c74e326e-5047-406b-81fe-5ed4af0425f1.png)

Класс **Preprocessor** соответствует модулю предобработки текстовых медицинских записей. Данный модуль предназначен для предварительной очистки и корректировки текстовых данных.

Класс **TermParser** предназначен для сбора информации из открытых русскоязычных терминологических и других специализированных источников (справочников, словарей, баз знаний) и создания частотного словаря для последующего исправления опечаток в медицинских текстах. 
Для этой цели были использованы следующие источники:
- https://www.vidal.ru/
- https://grls.rosminzdrav.ru/
- https://helix.ru/kb
- https://nsi.rosminzdrav.ru/
- https://mkb-10.com/

Класс **ErrorCorrector** соответствует модулю сегментации текста одного регистра и исправления опечаток в тексте. В рамках данного модуля реализован алгоритм исправления опечаток с использованием частотного словаря на основе расстояния Дамерау-Левенштейна.

Класс **Filtration** соответствует модулю фильтрации и категоризации медицинских записей. Модуль осуществляет основной процесс фильтрации медицинских документов. В случае с обработкой аллергологических анамнезов модуль формирует пять классификаторов: классификатор для фильтрации записей, имеющих отношение к аллергии и непереносимости, классификатор для фильтрации записей, в которых указаны аллергические реакции, а также три классификатора для определения категории аллергии согласно справочнику категорий ресурса AllergyIntolerance FHIR (средовая, пищевая и медикаментозная).  

Класс **Extraction** соответствует модулю извлечения терминов из медицинских текстов. Процесс извлечения основан на правилах, а также использует списки ключевых слов (дополненные кодами SNOMED CT), полученные на этапе фильтрации и категоризации.

Класс **FHIRMapper** соответствует модулю стандартизации медицинских данных, использует структуру ресурса AllergyIntolerance FHIR.

Класс **Ontology** соответствует модулю формирования предметной терминологической онтологии, как средства хранения полученных знаний. 

### Для ссылок:
1. ID Lenivtceva., G Kopanitsa. The Pipeline for Standardizing Russian Unstructured Allergy Anamnesis Using FHIR AllergyIntolerance Resource // Methods Inf. Med. Methods Inf Med, 2021. doi: 10.1055/s-0041-1733945
2. Ленивцева Ю.Д., Копаница Г.Д. Метод сопоставления форматов обмена медицинскими данными и терминологий // Врач и информационные технологии -2021. - № 1. - С. 75-83
3. Ленивцева Ю.Д., Копаница Г.Д. Определение типа аллергии на основании неструктурированных медицинских записей // Врач и информационные технологии -2021. - № 1. - С. 18-24
4. Ленивцева Ю.Д., Копаница Г.Д. Автоматическое определение типа аллергии из неструктурированных медицинских текстов на русском языке [Automatic allergy classification based
on russian unstructured medical texts] // Научнотехнический вестник информационных технологий, механики и оптики [Scientific and Technical Journal of Information Technologies, Mechanics and Optics] -2021. - Т. 21. - № 3(133). - С. 433-436
5. Lenivtceva I.D., Slasten E.S., Kashina M., Kopanitsa G.D. Applicability of Machine Learning Methods to Multi-label Medical Text Classification//Lecture Notes in Computer Science (including subseries Lecture Notes in Artificial Intelligence and Lecture Notes in Bioinformatics), 2020, Vol. 12140 LNCS, pp. 509-522
6 Kashina M., Lenivtceva I.D., Kopanitsa G.D. Preprocessing of unstructured medical data: the impact of each preprocessing stage on classification//Procedia Computer Science, 2020, Vol. 178, pp. 284-290
7. Lenivtceva I.D., Kashina M., Kopanitsa G.D. Category Scopus, Web of Science of Allergy Identification from Free-Text Medical Records for Data Interoperability//Studies in health technology and informatics, 2020, Vol. 273, pp. 170-175
8. Lenivtseva Y.D., Kopanitsa G.D. Investigation of Content Overlap in Proprietary Medical Mappings//Studies in health technology and informatics, 2019, Vol. 258, pp. 41-45
9. Lenivtceva I.D., Kopanitsa G.D. Evaluating Manual Mappings of Russian Proprietary Formats and Terminologies to FHIR//Methods of information in medicine, 2019, Vol. 58, No. 4-5, pp. 151-159
