from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
from textwrap import wrap

modelo_importado = 'mrm8488/distill-bert-base-spanish-wwm-cased-finetuned-spa-squad2-es'
tokenizer  = AutoTokenizer.from_pretrained(modelo_importado, do_lower_case = False)
modelo = AutoModelForQuestionAnswering.from_pretrained(modelo_importado)
print(modelo)

contexto='El RMS Titanic fue un transatlántico británico, el mayor barco de pasajeros del mundo al finalizar su construcción, que naufragó en las aguas del océano Atlántico durante la noche del 14 y la madrugada del 15 de abril de 1912, mientras realizaba su viaje inaugural desde Southampton a Nueva York, tras chocar con un iceberg. En el hundimiento murieron 1496 personas de las 2208 que iban a bordo, lo que convierte a esta catástrofe en uno de los mayores naufragios de la historia ocurridos en tiempos de paz. Siendo construido entre 1909 y 1912 en los astilleros de Harland & Wolff de Belfast, el Titanic constituía el segundo buque de un trío de grandes transatlánticos (siendo el primero el RMS Olympic y el tercero el HMHS Britannic), propiedad de la compañía naviera White Star Line, conocidos como la clase Olympic. Entre sus pasajeros estaban algunas de las personas más ricas del mundo, además de cientos de inmigrantes de nacionalidad irlandesa, británica y escandinava que iban en busca de una mejor vida en Norteamérica. El barco fue diseñado para ser lo último en lujo y comodidad, contaba con gimnasio, piscina cubierta, biblioteca, restaurantes de lujo y opulentos camarotes para los viajeros de primera clase, así como con una potente estación de telegrafía disponible para el uso de pasajeros y tripulantes. Sumado a todo esto, el barco estaba equipado con algunas medidas de seguridad avanzadas para la época, como los mamparos de su casco y compuertas estancas activadas a distancia. Sin embargo otras medidas resultaron insuficientes, ya que solo portaba botes salvavidas para 1178 personas,6​ poco más de la mitad de las que iban a bordo en su viaje inaugural y un tercio de su capacidad total de 3547 personas. Tras zarpar de Southampton el 10 de abril de 1912, el Titanic recaló en Cherburgo (Francia) y en Queenstown (actual Cobh), en Irlanda, antes de poner rumbo al océano Atlántico. A las 23:40 del 14 de abril, cuatro días después de zarpar y a unos 600 km al sur de Terranova, el buque chocó contra un iceberg. La colisión abrió varias planchas del casco en el lado de estribor bajo la línea de flotación, a lo largo de cinco de sus dieciséis compartimentos estancos, que comenzaron a inundarse. Durante dos horas y media, el barco se fue hundiendo gradualmente por su sección de proa mientras la popa se elevaba y, en este tiempo, varios cientos de pasajeros y tripulantes fueron evacuados en los botes salvavidas, de los cuales casi ninguno fue ocupado hasta su máxima capacidad. Un número muy elevado de hombres perecieron debido al estricto protocolo de salvamento que se siguió en el proceso de evacuación, conocido como «Las mujeres y los niños primero».7​8​ A las 2:17 del 15 de abril, el barco se partió en dos y se hundió con cientos de personas todavía a bordo. La mayoría de los que quedaron flotando en la superficie fallecieron de hipotermia, aunque algunos consiguieron ser rescatados por los botes salvavidas. Los 712 supervivientes fueron recogidos por el transatlántico RMS Carpathia a las 4:00. El naufragio del Titanic conmocionó e indignó al mundo entero por el elevado número de víctimas mortales y por los errores cometidos en el accidente. Las investigaciones públicas realizadas en Reino Unido y los Estados Unidos llevaron a la implementación de importantes mejoras en la seguridad marítima y a la creación en 1914 del Convenio Internacional para la Seguridad de la Vida Humana en el Mar (SOLAS, por sus siglas en inglés), que todavía hoy rige la seguridad marítima. Muchos de los supervivientes, que perdieron todo su patrimonio en la tragedia, fueron ayudados gracias a la caridad pública, pero otros, como el presidente de la White Star, J. Bruce Ismay, fueron acusados de cobardía por su prematuro abandono de la nave y condenados al ostracismo social. El pecio del Titanic fue descubierto el 1 de septiembre de 1985 por el oceanógrafo estadounidense Robert Ballard en el fondo del Atlántico Norte a una profundidad de 3784 m. Los restos están muy dañados y sufren un progresivo deterioro pero desde su descubrimiento han sido recuperados miles de objetos del barco y estos están exhibidos en numerosos museos del mundo. El Titanic es quizá el barco más famoso de la historia y su memoria se mantiene muy viva gracias a numerosos libros, canciones, películas, documentales, exposiciones, diversos trabajos de historiadores y memoriales.'
pregunta='¿quien soy?'


encode = tokenizer.encode_plus(pregunta, contexto, return_tensors='pt')
inputs_ids = encode['input_ids'].tolist()
tokens = tokenizer.convert_ids_to_tokens(inputs_ids[0])

nlp = pipeline('question-answering',model=modelo, tokenizer=tokenizer)
salida = nlp({'question':pregunta,'context':contexto})
print(salida)

def pregunta_respuesta(model,contexto,nlp):
    print('Contexto')
    print('-----------------')
    print('\n'.join(wrap(contexto)))

    continuar=True
    while continuar:
        print('\nPregunta:')
        print('-------------')
        pregunta=str(input())

        continuar = pregunta!=''

        if continuar:
            salida = salida = nlp({'question':pregunta,'context':contexto})
            print('\nRespuesta:')
            print('-----------------')
            print(salida['answer'])

pregunta_respuesta(modelo, contexto, nlp)