import discord, asyncio
from discord.ext import commands
from discord.ext.commands import Bot
import sys, subprocess, traceback, logging
from dotenv import load_dotenv
load_dotenv()
import math
import numpy as np
import re, regex
import json, csv
from sympy import *
x, y, z, t, a, b, c = symbols('x y z t a b c')


#############################################
TOKEN = 		### PUT TOKEN STRING HERE ###
#############################################


description = """TeXas is a bot that can render LaTeX and solve equations."""

help_message = '```TeXas help \n----------------------\n latex: render LaTeX. Ex. latex \int_{-\infty}^\infty \\frac{1}{\sqrt{2\pi}} e^{-\\frac{x^2}{2}}\; \\text{d}x \n solve: solve expressions with the Giac API. see command "solve help" for more details\n graph: graphs using SymPy and matplotlib (kinda slow; please use "gnuplot" for faster/better graphs). Ex. graph x**2\n gnuplot: uses gnuplot to render a graph. Ex. "gnuplot x**2 -10 10" Remember to specify a range.```'

solve_help_message = '```TeXas help: solve function\n----------------------\nThis command provides a solution using the Xcas/Giac backend. It\'s much more stable than the previous backend and can handle crazy calculations quickly since it\'s using C++ and not Python, which means it can go fast! I don\'t feel like writing up a whole ass help thing for example commands for Xcas since they\'re all pretty simple and intuitive; look Xcas/Giac up on DuckDuckGo if you want to check it out.```'

inline_bot = discord.Client()

@inline_bot.event
async def on_ready():
    print('logged in as: ')
    print(inline_bot.user.name)
    print(inline_bot.user.id)
    print('-----')
    activity = discord.Activity(name='for "TeXas help"', type=discord.ActivityType.watching)
    await inline_bot.change_presence(activity=activity)

def PNGify(latex, big=False):
    ## read user input (argument) as a latex equation
    le = "$$" + latex + "$$"
    ## skeleton for latex .tex file
    before_eq_string = r"\documentclass{article}\usepackage[margin=0.1in]{geometry} \usepackage{amsmath} \usepackage{amssymb} \begin{document} \thispagestyle{empty} \setlength{\parindent}{0pt}"
    after_eq_string = r"\end{document}"
    ## set latex_filename parameter
    lf = "tempfile"
    ## create the .tex file from the skeleton
    tex_file_contents = before_eq_string + le + after_eq_string
    tex_file = open(lf + ".tex", "w")
    tex_file.write(tex_file_contents)
    tex_file.close()
    ## create the pdf (`pdflatex -jobname='filename to write' file.tex`)
    # to specify output name: -jobname=STRING flag before the FILE flag at the end
    os.system('pdflatex ' + lf + '.tex > /dev/null 2>&1')
    ## crop the pdf to remove excess whitespace
    os.system('pdfcrop -margin 3 ' + lf + '.pdf ' + lf + '.pdf > /dev/null 2>&1')
    ## create the png from the pdf (`convert -density 3000 file.pdf -quality 90 file.png`)
    density = 3000 if big else 300
    os.system('convert -quiet -density ' + str(density) + ' -background white -alpha remove -alpha off ' + lf + '.pdf -quality 90 ' + lf + '.png')
    ## remove all the useless (.aux, .log, .pdf, .tex) latex files
    os.system('rm ' + lf + '.log ' + lf + '.aux ' + lf + '.pdf ' + lf + '.tex')
    return lf + '.png'

def giac_solve(expression, latex):
    os.system('giac "' + expression + '" > example.txt')
    os.system('giac "latex(' + expression + ')" >> example.txt')
    o = open('example.txt', 'r')
    result = o.readline()
    ltx = o.readline()[1:-2]
    o.close()
    return ltx if latex else result

def sympy_graph(expr):
    p = plot(expr, show=False)
    p.save('graph.png')
    return 'graph.png'

def gnuplot_graph(expr, r1, r2):
    os.system('gnuplot -e "set terminal png size 500,450; set output \'xyz.png\'; plot [' + r1 + ':' + r2 + '] ' + expr + '"')
    return 'xyz.png' if os.path.getsize('xyz.png') >= 50 else "invalid"
	
def check_no_unicode(s):
    ok_string = 'abcdefghijklmnopqrstuvwxyz'
    ok_string += ok_string.upper() + '\\,/?.><-=+_!@#$%^&*()1234567890[]{}|`~;:"\' '
    for i in s:
        if not i in ok_string:
            return False
    return True

@inline_bot.event
async def on_message(message):
    if message.author.bot:
        return
    content = message.content
    reply = ''
    if content == 'solve help':
        await message.channel.send(solve_help_message)
        return
    if content[:8] == 'gnuplot ':
        arguments = content[8:].split(' ')
        if len(arguments) != 3:
            await message.channel.send("The `gnuplot` command takes 3 arguments, two for range and one for expression.")
            return
        expr, r1, r2 = arguments[0], arguments[1], arguments[2]
        try:
            float(r1)
            float(r2)
            out = gnuplot_graph(expr,r1,r2)
            if out == 'invalid':
                await message.channel.send("Invalid expression.")
                return
            await message.channel.send(file=discord.File(out))
            return
        except ValueError:
            await message.channel.send("Invalid range.")
            return
    if content[:6] == 'graph ':
        expr = content[6:]
        await message.channel.send(file=discord.File(sympy_graph(expr)))
        return
    if content[:6] == 'solve ':
        expression = content[6:]
        latex = False
        result = giac_solve(expression, latex)
        print(repr(result))
        if result == '"calculation size limit exceeded"\n':
            await message.channel.send("Calculation size limit exceeded. Try again.")
            return
        if result[0] == '"':
            await message.channel.send("Unable to perform given calculation. Try something else.")
            return
        if result[:2] == '[]':
            await message.channel.send("No solutions.")
            return
        if len(result) <= 1900:
            await message.channel.send('`' + result + '`')
        else: await message.channel.send("Result too long to display.")
        return
    if content[:7] == 'lsolve ':
        big = False
        expression = content[7:]
        if content[7:11] == 'big ':
            big = True
            expression = content[11:]
        latex = True
        result = giac_solve(expression, latex)
        print(result)
        if result != 'calculation size limit exceeded':
            reply += PNGify(result, big)
        else:
            await message.channel.send("Calculation size limit exceeded. Try again.")
            return
    if content[:6] == 'latex ':
        # turn latex code into a PNG
        if not check_no_unicode(content[6:]):
            await message.channel.send("Illegal character(s) in input.")
            return
        expr = content[6:]
        big = False
        if content[6:10] == 'big ':
            big = True
            expr = content[10:]
        reply += PNGify(expr, big)
    elif content == 'TeXas help':
        await message.channel.send(help_message)
        return
    if reply != '':
        await message.channel.send(file=discord.File(reply))
        os.system('rm ' + reply)

inline_bot.run(TOKEN)
