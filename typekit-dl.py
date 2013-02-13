#!/usr/bin/env python
#encoding: utf-8

from urllib2 import *
import fontforge


HELP_MESSAGE = '''
Script en Python para descargar tipografías de Typekit.com

Para funcionar correctamente necesita Fontforge y su módulo para Python
(http://fontforge.org/python.html). En Ubuntu/Debian el módulo puede instalarse con:

~$ apt-get install python-fontforge

El script descarga el css que contiene la tipografía codificada en base64.
A continuación la extrae y usando Fontforge crea fuentes en formato ttf, eot, otf,
woff y svg. También construye un "facefont kit" para usar la tipografía
como webfont sin necesidad de depender de Typekit.

Modo de uso:

~$ ./typekit-dl.py [URL de la tipografía] [Ruta a carpeta de destino]

Ejemplo:

~$ ./typekit-dl.py https://typekit.com/fonts/myriad-pro /home/jorge/Myriad
'''



class DownloaderError(Exception):
    def __init__(self, msg=False):
        self.msg = msg

class TypekitDownloader():
    def __init__(self, typekitUrl):
        self.typekitUrl = typekitUrl

        pattUrl = 'https://(www\.)?typekit\.com/fonts/(.+)'

        match = re.match(pattUrl, typekitUrl)
        if not match:
            raise DownloaderError('\nLa dirección no es valida.')

        self.fontName = match.group(2)

        self.response = urlopen(typekitUrl)
        if self.response.code != 200:
            raise DownloaderError('\nError al conectar con Typekit: %d' % self.response.code)

        html = self.response.read()
        pattCss = 'TypekitPreview\._loadInternal\("(\w+)","(.+)","(\w+)",'

        parameters = re.search(pattCss, html)

        self.fontfaceUrl = 'https://use.typekit.net/c/' + parameters.group(1) + '/' + \
            parameters.group(2) + '/d?' + parameters.group(3)

    
    def CssDownload(self, destinationFolder = False):

        if destinationFolder:
            self.fontfaceFolder = destinationFolder
        else:
            self.fontfaceFolder = self.fontName
        
        if not os.path.exists(self.fontfaceFolder):
            os.makedirs(self.fontfaceFolder)

        self.cssFile = self.fontfaceFolder + '/' + self.fontName + "-typekit" + '.css'

        opener = build_opener()
        opener.addheaders = {('Referer', self.typekitUrl)}
        css = opener.open(self.fontfaceUrl).read()

        open(self.cssFile,'w+').write(css)

    def FontExtractor(self):
        extensions = ['.eot', '.ttf', '.otf', '.svg', '.woff']
         
        css = open(self.cssFile, 'r').read()

        pattFontface = "@font-face \{\n?font-family:\"(font-file-\d+)\";\n?(src:url\(data:font/opentype;base64,(.+)\);)\n?font-style:(\w+);\n?font-weight:(\d+);\n?\}"   

        fontfaces = re.finditer(pattFontface, css)

        fontFolder = self.fontfaceFolder + '/' + 'fonts'
        if not os.path.exists(fontFolder):
                os.makedirs(fontFolder)
        
        
        for i, block in enumerate(fontfaces):
            dump = self.fontfaceFolder + '/' + 'dump' + str(i) +'.tmp'
            open(dump, 'w+').write(base64.b64decode(block.group(3)))
            font = fontforge.open(dump)
            
            print "Extrayendo %s." % (font.fontname)

            for ext in extensions:
                f = fontFolder + '/' + font.fontname + ext
                font.generate(f)

            template = "@font-face {\
            \n\tfont-family: '" + font.fontname + "';\
            \n\tsrc: url('/fonts/" + font.fontname + ".eot');\
            \n\tsrc: url('/fonts/" + font.fontname + ".eot?#iefix') format('embedded-opentype'),\
            \n\turl('/fonts/" + font.fontname + ".woff') format('woff'),\
            \n\turl('/fonts/" + font.fontname + ".ttf') format('truetype'),\
            \n\turl('/fonts/" + font.fontname + ".svg#ywftsvg') format('svg');\
            \n\tfont-style:" + block.group(4) + ";\
            \n\tfont-weight:" + block.group(5) + ";\
            \n}\n\n"
            
            css = self.fontfaceFolder + '/' + self.fontName + '.css'

            open(css, 'a').writelines(template)

            os.remove(dump)
            
            # for some reason, probably an error during conversion, an .afm file in created
            # the code bellow removes the .afm file if it does exists.
            try:
                os.remove(fontFolder + '/' + font.fontname + '.afm')
            except:
                pass


if __name__ == '__main__':
    args = sys.argv

    if len(args) == 1:
        
        print HELP_MESSAGE
        exit()

    try:
        downloader = TypekitDownloader(args[1])

        if len(args) == 3:
            destinationFolder = args[2]
        else:
            destinationFolder = False

        downloader.CssDownload(destinationFolder)
        print "Archivo %s descargado con éxito.\n" % (downloader.fontName + "-typekit" + '.css')
        downloader.FontExtractor()
        print "\nOperación completada con éxito."
        exit()
    except DownloaderError as error:
        print "\nError: %s\n" % error.msg
        exit(1)