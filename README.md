# Cove Voice

**“Oi Cove, papai chegou.”** Uma frase para abrir o ChatGPT e, se estiver instalado, o Codex CLI no Windows.

Projeto de Nicolas Oliveira ([niloou001](https://github.com/niloou001)), desenvolvido com assistência do Codex e validado em uso no Windows com microfone Fifine.

## Como funciona

O ouvinte roda em segundo plano e reconhece a frase em português usando Vosk. Ao reconhecer o comando, executa `Cove.bat`. O instalador configura o início automático no login do Windows: depois disso, não é necessário clicar no atalho a cada uso.

- Reconhecimento local, sem enviar o áudio para um serviço de transcrição.
- Variações de pronúncia do nome Cove e pausas de até 8 segundos entre trechos da frase.
- Intervalo de 20 segundos entre ativações para evitar várias janelas seguidas.
- Nova tentativa automática em caso de falha de captura do microfone.
- Apenas uma instância do ouvinte por sessão.

O computador precisa estar ligado, acordado e com sua sessão iniciada. O programa abre a página do ChatGPT; não inicia uma conversa por voz dentro dela. O reconhecimento pode falhar ou ativar por engano conforme o ruído e a pronúncia. Qualquer voz que reproduza a frase pode acionar o programa: ele não autentica o usuário.

## Requisitos

- Windows 10 ou 11.
- Python 3.10 ou superior, **64 bits**.
- Microfone configurado como entrada padrão do Windows e acesso permitido para aplicativos da área de trabalho.
- Internet para baixar as dependências e o modelo na instalação. Abrir o ChatGPT também requer internet; o reconhecimento da frase funciona localmente.
- Codex CLI é opcional. Quando o comando `codex` estiver disponível no PATH, ele também será aberto.

## Instalação

Baixe o ZIP deste repositório pelo botão **Code → Download ZIP** e extraia os arquivos. Abra o PowerShell na pasta extraída e execute:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

O script instala os arquivos em `%LOCALAPPDATA%\Cove`, cria um ambiente Python separado, baixa o [modelo português oficial do Vosk](https://alphacephei.com/vosk/models) e adiciona os atalhos de ativação e inicialização. Não precisa executar como administrador. Não execute o instalador enquanto uma versão anterior estiver ouvindo; encerre-a antes de atualizar.

Abra **Ativar Cove por voz** na Área de Trabalho uma vez para começar agora. Espere cerca de 10 segundos e diga:

> Oi Cove, papai chegou.

Nas próximas entradas no Windows, o ouvinte inicia sozinho. Fechar as janelas do ChatGPT e do Codex não encerra o ouvinte.

Se o Python não for encontrado:

```powershell
.\install.ps1 -PythonExe 'C:\caminho\para\python.exe'
```

Para instalar sem adicionar inicialização automática, use `-NoStartup`. Essa opção não remove um atalho de inicialização criado em uma instalação anterior.

## Personalização

Edite `%LOCALAPPDATA%\Cove\Cove.bat` para mudar o que abre quando o comando é reconhecido. O arquivo pode executar programas com as permissões da sua conta; mantenha apenas comandos que você conhece.

A frase e suas variantes estão em `listener.py`, nas funções `is_wake_phrase` e `main`. O modelo não contém a palavra “Cove” no vocabulário; o reconhecimento usa aproximações como “couve”, “coube” e “ouve”. Para outra frase, ajuste tanto a verificação quanto a gramática do reconhecedor e reinicie pelo atalho.

## Diagnóstico e privacidade

O áudio é processado em memória e não é salvo em arquivos. O registro local `%LOCALAPPDATA%\Cove\listener.log` contém erros, nome do dispositivo, nível de sinal, ativações e possíveis trechos reconhecidos relacionados ao comando. Os registros têm rotação e não devem ser publicados sem revisão.

Se não funcionar, procure no registro a mensagem `Ouvindo no microfone`. Confira a entrada padrão, as permissões de microfone e se outro aplicativo está usando o dispositivo em modo exclusivo. Para reiniciar após uma alteração, abra novamente o atalho.

## Desativar ou remover

1. Pressione `Win + R`, digite `shell:startup` e remova **Cove Voz** para impedir o início automático.
2. Para encerrar agora, no Gerenciador de Tarefas, identifique os processos `pythonw.exe` cuja linha de comando aponta para `%LOCALAPPDATA%\Cove\listener.py` e encerre somente esses processos. Sair da sessão do Windows também encerra o ouvinte.
3. Após encerrar, remova `%LOCALAPPDATA%\Cove` e o atalho **Ativar Cove por voz** da Área de Trabalho.

## Validação

```powershell
python .\listener.py --test
python -m compileall -q listener.py install.py
```

Os testes de frase verificam exemplos positivos e negativos; não substituem um teste real de reconhecimento no microfone. O fluxo original foi confirmado pelo autor em uso. O instalador distribuído deve ser validado no computador de destino.

## Tecnologias e créditos

Python, PowerShell, [Vosk](https://github.com/alphacep/vosk-api) e [python-sounddevice](https://python-sounddevice.readthedocs.io/). O modelo e as dependências são baixados separadamente e mantêm suas próprias licenças. Este é um projeto independente, sem afiliação oficial com a OpenAI.
