# Define a imagem base
FROM python:3.9

# Configuração da variável de ambiente
ENV PYTHONUNBUFFERED 1

# Criação e definição do diretório de trabalho
RUN mkdir /app
WORKDIR /app

# Copia o código para o contêiner
COPY . /app/

# Instalação das dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta utilizada pelo Flask
EXPOSE 5000

# Comando para executar o aplicativo
CMD ["python", "app.py"]

