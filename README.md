##typekit-dl

###ESPAÑOL

tipekit-dl es un script en Python para descargar tipografías de Typekit.com.

Para funcionar correctamente necesita Fontforge y su módulo para Python
(http://fontforge.org/python.html). En Ubuntu/Debian el módulo puede instalarse con:

<pre>~$ apt-get install python-fontforge</pre>

El script descarga el css que contiene la tipografía codificada en base64.
A continuación la extrae y usando Fontforge crea fuentes en formato ttf, eot, otf,
woff y svg. También construye un "facefont kit" para usar la tipografía
como webfont sin necesidad de depender de Typekit.

Modo de uso:

<pre>~$ ./typekit-dl.py [URL de la tipografía] [Ruta a carpeta de destino]</pre>

Ejemplo:

<pre>~$ ./typekit-dl.py https://typekit.com/fonts/myriad-pro /home/jorge/Myriad</pre>

Este software está publicado bajo [licencia MIT](http://opensource.org/licenses/MIT).

##ENGLISH

tipekit-dl is a Python script for downloading typefaces from Typekit.com

It needs Fontforge and its Python module (http://fontforge.org/python.html) for working correctly. You can install the module on Ubuntu/Debian with:

<pre>~$ apt-get install python-fontforge</pre>

The script downloads the css containing the typografy coded on base64. Then extracts it and using Fontforge creates font on ttf, eot, otf, woff and svg format. Also It builds a fontface kit for using the typeface as webfont without Typekit dependence.

Usage:

<pre>~$ ./ImgurDownloader.py [album URL] [destination folder]</pre>

Example:

<pre>~$ ./ImgurDownloader.py http://imgur.com/a/LXS9b /home/jorge/fotos</pre>

This software is publised under [MIT license](http://opensource.org/licenses/MIT).