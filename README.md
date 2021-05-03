# TeXas

TeXas is a bot that can render LaTeX, solve equations, and create graphs.

[Demo and overview of functionality](https://bots.benrosenberg.info/#TeXas)

### Requirements

 - Python
 - [SymPy](https://www.sympy.org/en/index.html)
 - `pdflatex` (comes with a working [TeX Live](https://www.tug.org/texlive/) installation)
 - `pdfcrop` (use `sudo apt-get install texlive-extra-utils` or whatever relevant command is necessary to install; comes with `texlive-full` if you installed that)
 - [ImageMagick](https://imagemagick.org/index.php)
 - [`gnuplot`](http://www.gnuplot.info/)
 - [Xcas/Giac](https://www-fourier.ujf-grenoble.fr/~parisse/giac.html)
 - discord.py

### Usage

1. Put your bot's token into the bot.py file where specified by the comment
2. Run with `python bot.py` (or `python3 bot.py`, depending on your Python installation)
