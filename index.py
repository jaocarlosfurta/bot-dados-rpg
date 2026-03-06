import discord
import re
import random
from dotenv import load_dotenv
import os

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} pronto pra ação!!!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    texto = message.content.lower().strip()
    texto = re.sub(r'\s*([+#-])\s*', r'\1', texto)

    repeticoes = 1
    prefixo = re.match(r'^(\d+)#', texto)
    if prefixo:
        repeticoes = int(prefixo.group(1))
        texto = texto[prefixo.end():]
        texto = re.sub(r'(^|(?<=[+-]))d', r'\g<1>1d', texto) 
        if repeticoes < 2 or repeticoes > 20:
            await message.reply('Repita entre 2 e 20 vezes!')
            return

    if not re.search(r'\d+d\d+', texto):
        return

    if not re.fullmatch(r'[+-]?(\d+d\d+|\d+)([+-](\d+d\d+|\d+))*', texto):
        return

    def rolar_expressao(expressao):
        partes = re.findall(r'([+-]?)(\d+d\d+|\d+)', expressao)
        total = 0
        segmentos = []

        for sinal, valor in partes:
            multiplicador = -1 if sinal == '-' else 1
            sinal_txt = sinal if sinal else ''

            if 'd' in valor:
                qtd, lados = map(int, valor.split('d'))
                if qtd > 100 or lados > 1000:
                    return None, f'`{valor}` está fora do limite!'

                resultados = [random.randint(1, lados) for _ in range(qtd)]
                subtotal = sum(resultados) * multiplicador
                total += subtotal

                resultados_ordenados = sorted(resultados, reverse=True)
                nums = ', '.join(f'**{r}**' if r == lados else str(r) for r in resultados_ordenados)
                segmentos.append(f'`{sinal_txt}{valor}` {{{nums}}} = **{subtotal}**')

            else:
                fixo = int(valor) * multiplicador
                total += fixo
                segmentos.append(f'`{sinal_txt}{valor}`')

        tem_modificador = len(segmentos) > 1
        linha = '  +  '.join(segmentos) + (f'  →  **{total}**' if tem_modificador else '')
        return total, linha

    autor = message.author.display_name
    linhas = [f'× {repeticoes} rolagens de `{texto}`:'] if repeticoes > 1 else []

    for i in range(repeticoes):
        total, linha = rolar_expressao(texto)
        if total is None:
            await message.reply(linha)
            return
        if repeticoes > 1:
            linhas.append(f'**#{i+1}** {linha}')
        else:
            linhas.append(linha)

    await message.reply('\n'.join(linhas))

load_dotenv()
client.run(os.getenv('TOKEN'))
