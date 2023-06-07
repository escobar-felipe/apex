import time
from concurrent.futures import ThreadPoolExecutor
import openai
import pandas as pd
from newspaper import Article

#classe com os métodos para realizar as análises
class MonitoringAndAnalysis:
    def __init__(self, tokenizer,articles, openai_api_key):
        self.tokenizer = tokenizer
        self.articles =articles
        self.embeddings =None
        self.error = None
        self.df = pd.DataFrame()
        
        openai.api_key = openai_api_key

    def truncate_text(self,text, max_tokens):
        """
        Truncate the input text to the specified maximum number of tokens using the GPT-2 tokenizer.

        Args:
            text (str): The input text to be tokenized and truncated.
            max_tokens (int): The maximum number of tokens to keep.

        Returns:
            str: The truncated text.
        """
        text = text[:4500]
        # Tokenize the text and get the token IDs
        token_ids = self.tokenizer.encode(text)
        #cria lista de IDs de token

        # Truncate the token IDs if they exceed the maximum number of tokens
        if len(token_ids) > max_tokens:
            token_ids = token_ids[:max_tokens]
        #Aqui a função verifica o comprimento do texto tokenizado, representado como uma lista de IDs de token.
        #Se o comprimento exceder o número máximo especificado de tokens (max_tokens), 
        # a função irá limitar a lista de IDs de token para manter apenas os primeiros tokens max_tokens.

        # Convert the truncated token IDs back to text
        truncated_text = self.tokenizer.decode(token_ids)
        #Aqui converte a lista de IDS de token de volta em um texto usando a função de decodificação.
        return truncated_text

    def fetch_articles(self, articles):
        #gerando os vetores de entrada de acordo com os textos(artigos pesquisados)
        #rótulos de cluster previstos para cada entrada
        article_list = []
        #cria uma lista vazia
        for i, article in enumerate(articles):
            #utiliza a classe enumerate() para iterar por todos os elementos da lista(articles)
            # para cada artigo - crie um dicionário contendo:
            article_dict = {
                'brand': article['brand'], #tópico pesquisado
                'title': article['title'], #título
                'link': article['link'], #link
                'source': article['source'], #fonte
                'text': self.scrape_article(article['link']),  #texto extraido
            }
            article_list.append(article_dict)
            #adiciona o dicionário no variável article_list
        df = pd.DataFrame(article_list)
        #transforma a lista article_list in dataframe 
        return df
        #retorna o dataframe contendo as informações do dicionário em cada linha.

    def scrape_article(self,url): #função que realiza o webscreaping dos textos
        article = Article(url)
        #passando a url para classe Argicle para extração deo conteúdo do texto.
        try:
            article.download()
            #chamando o method download
            article.parse()
            print(f"Sucess to download Article: {article.title}")
        except Exception as e:
            print(f"Failed to Download Article: {e}")
        return article.title + " " + article.text
        #retorna uma string: título + " " + texto

    def analyze_articles(self,df:pd.DataFrame):
        with ThreadPoolExecutor() as executor:
            #ThreadPoolExecutor() é uma classe que gerencia o pool de threads para realizar a execução simultânea ou paralela de tarefas em um ambiente multithread
            #Com a classe instânciada você pode enviar várias tarefas simultaneamente e ela serão executadas em paralelo pelos threads com o número máximo de trabalhadores especificados
            #wokers - padrão
            futures = []
            #cria uma lista vazia futures
            for i, row in df.iterrows():
                #method iterrows para percorrer as linhas do dataframe
                time.sleep(2)
                #timer para ajustar as requisições
                article_text = row["text"]
                #extrai o texto de acordo com a coluna texto
                article_text = self.truncate_text(article_text, 1800)
                print(article_text)
                #limita 2000 o texto a partir da função truncate_text baseado no tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
                prompt = (
                f"Por favor, analise este artigo de notícias e forneça um resumo abrangente com base nas seguintes categorias. Por favor, responda a todas as partes do seguinte:\n\n"
                f"Temas principais: Identifique os tópicos centrais discutidos no artigo.\n"
                f"Resumo: Crie um breve resumo desse artigo\n"
                f"Narrativas: Descreva quaisquer histórias ou mensagens abrangentes presentes no artigo.\n"
                f"Opiniões: Mencione os principais pontos de vista ou perspectivas expressos no artigo, juntamente com suas fontes (se mencionadas).\n"
                f"Porta-vozes: Liste quaisquer indivíduos ou organizações mencionados como fontes, juntamente com seus papéis ou afiliações.\n"
                f"Viés: Aponte quaisquer possíveis preconceitos no artigo, seja por meio de linguagem, perspectiva ou foco.\n"
                f"Emoção do artigo: Determine a(s) emoção(ões) dominante(s) transmitida(s) pelo artigo (por exemplo, positiva, negativa, neutra, etc.).\n\n"
                f"Por favor, forneça sua análise em um formato bem estruturado e conciso. Use marcadores ou listas numeradas para tornar sua resposta mais fácil de ler e entender.\n\n"
                f"Este é o artigo de notícias a ser avaliado. Forneça apenas os dados solicitados e nada mais antes de Temas principais: \n\n {article_text}"
                )
                #cria a variável string(prompt) no qual recebe o texto que contém as instruções para a análise a ser executada pelo modelo GPT-3 
                # juntamente com o texto do artigo (limitado)

                future = executor.submit(
                    openai.Completion.create,
                    model="text-davinci-003",
                    prompt=prompt,
                    max_tokens=1800,
                    n=1,
                    stop=None,
                    temperature=0.7,
                )
                #envia a tarega para o pool de threads usando o método submit()
                #passando a função openai.Completion.create
                #com os parâmetros necessários, como nome do modelo GPT-3, prompt, número máximo de tokens, número de conclusões (definido como 1),
                #sequência de parada (definido como None) e temperatura para controlar a aleatoriedade do texto gerado.
                futures.append((i, future))
                #adiciona uma tupla a lista futures contendo (i:posição,future: objeto "future" que representa a tarefa executada dentro do pool threads )

            for i, future in futures:
                #itera sobre a lista futures para recuperar os dados do resultado das tarefas executadas dentro do pool
                retries = 0 #variável auxiliar
                max_retries = 1 #variável auxiliar
                while retries < max_retries:
                    #loop para caso de algum erro ou o resultado não é o esperado para tentar novamente
                    try:
                        response = future.result()
                        """ exemple of response
                        {
                            "choices": [
                                {
                                "finish_reason": "stop",
                                "index": 0,
                                "logprobs": null,
                                "text": "\n\nMain Themes:\n-Therapist compensation at behavioral health tech companies\n-Differences in salaries based on stage of startup and education level\n-Funding for the behavioral health tech industry\n-Recent layoffs at digital behavioral health companies\n\nNarratives:\n-Therapists working at behavioral health tech companies have a wide range of salaries, with an average of $90,000.\n-Salaries vary depending on the stage of the startup and the therapist's education level.\n-The behavioral health tech industry has seen a significant funding boom, but layoffs have become more common. \n\nOpinions:\n-Jaclyn Satchel, executive director of Therapists in Tech: \"This report echoes many of the trends we saw in 2021. There is still a lot of variability in what people get paid. There is still a lack of representation of people of color in leadership positions. For all of the increased company valuations over the pandemic, salaries are still about the same.\"\n\nSpokespersons:\n-Jaclyn Satchel, executive director of Therapists in Tech \n-Therapists in Tech\n-Rock Health\n\nBiases:\n-The report does not provide information about the gender or race of therapists who are not psychologists.\n\nArticle Emotion: \nNeutral"
                                }
                            ],
                            "created": 1681672429,
                            "id": "cmpl-7626nyC5DYujuuEeyyVG9tqXP2qbw",
                            "model": "text-davinci-003",
                            "object": "text_completion",
                            "usage": {
                                "completion_tokens": 274,
                                "prompt_tokens": 767,
                                "total_tokens": 1041
                            }
                        }
                        """
                        output_text = response.choices[0].text.strip() #extrair do dicionário(response) o valor da chave choice(lista) na posição zero, extrair da chave text o valor e passar o método strip
                        #strip remove os espaços do início e do fim do texto
                        output_list = output_text.split("\n\n") #divide o texto das respostas em uma lista baseado no parâmetro "\n\n"
                        #dividindo os tópicos em main_themes, narratives, opinions, spokespersons, biases e emotion
                        parsed_data = {}
                        #cria um dicionário vazio
                        for item in output_list:
                            #percorre a lista output_list 
                            #para cada item:
                            key, value = item.split(":", 1) #excecuta o mêtodo split no item com parâmetro ":" pegando a posição 1
                            parsed_data[key.strip()] = value.strip()
                            #armazenando a variável key and value no parserd_data(dict)

                        # Check if all required keys are present in the parsed_data dictionary
                        required_keys = ["Temas principais", "Resumo"]
                        if all(key in parsed_data for key in required_keys):
                            #verificando se no dicionário parsed_data contém os valores da lista required_keys
                            #adiciona ao dataframe as seguintes colunas contendo os valores da variável parsed_data
                            df.loc[i, "main_themes"] = parsed_data.get("Temas principais", "")
                            df.loc[i, "resume"] = parsed_data.get("Resumo", "Nossa Inteligência Artificial não conseguiu gerar um resumo para esse artigo.")
                            df.loc[i, "narratives"] = parsed_data.get("Narrativas", "")
                            df.loc[i, "opinions"] = parsed_data.get("Opiniões", "")
                            df.loc[i, "spokespersons"] = parsed_data.get("Porta-vozes", "")
                            df.loc[i, "biases"] = parsed_data.get("Viés", "")
                            df.loc[i, "emotion"] = parsed_data.get("Emoção do artigo", "")
                            break
                        else:
                            #caso não encontre as chaves "required_keys" no dicionário parsed_date tente novamente
                            retries += 1 #soma 1 na variável auxiliar
                            print(f"Incomplete data for row {i}, retrying {retries}/{max_retries}...")
                            future = executor.submit(
                                openai.Completion.create,
                                model="text-davinci-003",
                                prompt=prompt,
                                max_tokens=1800,
                                n=1,
                                stop=None,
                                temperature=0.5,
                            )
                            #instância um novo obj na variável future com uma nova pesquisa na API
                    except Exception as e:
                        self.error= str(e)

        return df
    
    def get_analyze_from_articles(self):
        self.df = self.fetch_articles(self.articles)
        self.df = self.analyze_articles(self.df)
        return self.df
    


    def generate_report(self,most_common, spokesperson_counts, bias_counts):
        prompt = (
        f"Por favor, gere um relatório de monitoramento de mídia com base nos seguintes dados resumidos:\n\n"
        f"Informações mais comuns:\n{most_common}\n\n"
        f"Porta-vozes mais frequentemente mencionados:\n{spokesperson_counts}\n\n"
        f"Artigos ou fontes mais tendenciosos:\n{bias_counts}\n\n"
        f"Escreva um relatório bem estruturado e conciso resumindo as principais descobertas dos dados fornecidos."
        )
        #cria uma váriavel(prompt) com o texto de pesquisa na OpenIA API baseado nas informações passadas (most_common, cluster_counts, emotion_by_cluster, spokesperson_counts, bias_counts)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = [
            {"role": "system", "content": "Por favor, simule um especialista em análise de mídia com sólida formação em psicologia e comportamento humano, que seja um especialista mundial em Relações Públicas."},
            {"role": "user", "content": prompt}],
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )
        #utiliza a biblioteca Openia para realizar a requisação na api com os
        #parâmetros necessários, como nome do modelo gpt-3.5-turbo, messages, número máximo de tokens, número de conclusões (definido como 1),
        #sequência de parada (definido como None) e temperatura para controlar a aleatoriedade do texto gerado.
        #salva a resposta(response)

        output_text = response['choices'][0]['message']['content'].strip()
        #extrair do dicionário(response) o valor da chave choice(lista) na posição zero, extrair da chave message > content o valor e chama o método strip
        #strip remove os espaços do início e do fim do texto
        return output_text
        #retorna o valor

    def analyze_dataframe(self):
        if len(self.df.index)>0:
            df = self.df.drop_duplicates()
            if 'main_themes' in df.columns:
                
                result = ""
            # Extract summary information
                most_common = df['main_themes'].value_counts().head(5).to_dict()
                spokesperson_counts = df['spokespersons'].value_counts().head(5).to_dict()
                bias_counts = df['biases'].value_counts().head(5).to_dict()
                #extrai as informações do dataframe baseado nas colunas para utilizar na função generate_report
                for i, j in df.iterrows():
                    if not pd.isna(j['resume']):
                        result += f"""<h3>{j['title']}</h3>"""
                        result +=  f"""<p style="font-size:16;margin:0 0 20px 0;font-family:Arial,sans-serif;">{j['resume']}</p>"""
                        result += f"""<p style="font-size:16;margin:0 0 20px 0;font-family:Arial,sans-serif;">Fonte: {j['source']} </p>"""
                        result += "<br>"
                    else:
                        result += f"""<h3>{j['title']}</h3>"""
                        result +=  f"""<p style="font-size:16;margin:0 0 20px 0;font-family:Arial,sans-serif;">Nossa Inteligência Artificial não conseguiu gerar um resumo para esse artigo.</p>"""
                        result += f"""<p style="font-size:16;margin:0 0 20px 0;font-family:Arial,sans-serif;">Fonte: {j['source']} </p>"""
                        result += "<br>"
                # Generate the GPT-based report
                report = self.generate_report(most_common, spokesperson_counts, bias_counts),
                #passa os parâmetros para a função generate a report
                result += f"""<h3>Análise</h3><br><p style="font-size:16;margin:0 0 20px 0;font-family:Arial,sans-serif;">{report[0]}</p>"""
                return result 
            else:
                if self.error:
                    raise Exception(self.error)
        else:
            raise Exception("Resultado incompleto, falha na integração com GPT. Entre em contato com o suporte para ajustar")