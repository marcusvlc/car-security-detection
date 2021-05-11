# Car Security (Módulo de Detecção)

Esse módulo é responsável por fornecer uma API-Rest para a aplicação CarSecurity, de modo a oferecer um CRUD para todos os objetos do sistema.
Também é responsável por realizar as detecções em tempo real.

## Antes de executar (IMPORTANTE)

Antes de executar este módulo, é necessário baixar os arquivos do YoloV3 disponíveis [neste link](https://drive.google.com/drive/folders/1w2ooBNA4NDaEB7AQJO3zXhF9t6jNonz3) e colocá-los dentro da pasta [weights](https://github.com/marcusvlc/carsecurity-detection/tree/master/app/detection/weights).

Caso você esteja utilizando um sistema Linux, é necessário também mudar o formato dos path's encontrados na função `__init__` do arquivo [stream.py](https://github.com/marcusvlc/carsecurity-detection/blob/master/app/detection/stream.py)

Também será necessário que você tenha instalado o Python3 juntamente com o virtualenv para instalar as dependências do projeto.

## Como instalar as dependências

Primeiramente, crie um ambiente virtual utilizando o virtualenv

```sh
python3 -m venv nome_da_sua_env
```

Após isso, entre no ambiente com o comando (Windows):
```sh
.\nome_da_sua_env\Scripts\activate
```

Após ativar seu ambiente virtual, é necessário instalar as dependências do projeto. Para isso, execute o comando:

```sh
pip install -r requirements.txt
```

## Como executar a aplicação

Para iniciar a aplicação, basta executar o seguinte comando na pasta raiz:

```sh
python run.py
``` 

Após isso, a aplicação por padrão estará disponível em http://localhost:5000

